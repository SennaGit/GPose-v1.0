"""
运动学分析模块
计算关节角度、速度、加速度等运动学指标
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from scipy import signal
from dataclasses import dataclass
from loguru import logger


@dataclass
class JointAngle:
    """关节角度数据"""
    name: str  # 关节名称（如'right_knee'）
    angle: float  # 角度值（度）
    timestamp: float  # 时间戳


@dataclass
class KinematicsMetrics:
    """运动学指标集合"""
    angles: Dict[str, List[float]]  # 关节角度时序
    velocities: Dict[str, List[float]]  # 角速度时序
    accelerations: Dict[str, List[float]]  # 角加速度时序
    timestamps: List[float]  # 时间戳序列


class KinematicsAnalyzer:
    """运动学分析器"""
    
    # 关节定义（三个点定义一个关节角度）
    # 格式: 关节名称 -> (点1索引, 顶点索引, 点3索引)
    # 基于MediaPipe 33关键点索引
    JOINT_DEFINITIONS_MEDIAPIPE = {
        # 左臂
        'left_shoulder': (11, 13, 15),  # 躯干-肩-肘
        'left_elbow': (11, 13, 15),     # 肩-肘-腕
        'left_wrist': (13, 15, 19),     # 肘-腕-食指
        # 右臂
        'right_shoulder': (12, 14, 16),
        'right_elbow': (12, 14, 16),
        'right_wrist': (14, 16, 20),
        # 左腿
        'left_hip': (11, 23, 25),       # 肩-髋-膝
        'left_knee': (23, 25, 27),      # 髋-膝-踝
        'left_ankle': (25, 27, 31),     # 膝-踝-脚趾
        # 右腿
        'right_hip': (12, 24, 26),
        'right_knee': (24, 26, 28),
        'right_ankle': (26, 28, 32),
    }
    
    # OpenPose BODY_25关键点定义
    JOINT_DEFINITIONS_OPENPOSE = {
        'left_elbow': (5, 6, 7),   # 左肩-左肘-左腕
        'right_elbow': (2, 3, 4),  # 右肩-右肘-右腕
        'left_knee': (12, 13, 14), # 左髋-左膝-左踝
        'right_knee': (9, 10, 11), # 右髋-右膝-右踝
    }
    
    def __init__(
        self,
        keypoint_format: str = 'mediapipe',
        filter_type: Optional[str] = 'lowpass',
        filter_order: int = 4,
        cutoff_freq: float = 6.0
    ):
        """
        初始化运动学分析器
        
        Args:
            keypoint_format: 关键点格式 ('mediapipe' 或 'openpose')
            filter_type: 滤波器类型 ('lowpass', 'savgol', None)
            filter_order: 滤波器阶数
            cutoff_freq: 截止频率（Hz）
        """
        self.keypoint_format = keypoint_format
        self.filter_type = filter_type
        self.filter_order = filter_order
        self.cutoff_freq = cutoff_freq
        
        # 选择关节定义
        if keypoint_format == 'mediapipe':
            self.joint_defs = self.JOINT_DEFINITIONS_MEDIAPIPE
        elif keypoint_format == 'openpose':
            self.joint_defs = self.JOINT_DEFINITIONS_OPENPOSE
        else:
            raise ValueError(f"不支持的关键点格式: {keypoint_format}")
        
        logger.info(f"运动学分析器初始化完成，关键点格式: {keypoint_format}")
    
    @staticmethod
    def calculate_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        计算三点形成的角度
        
        Args:
            p1: 点1坐标 (x, y) 或 (x, y, z)
            p2: 顶点坐标（关节位置）
            p3: 点3坐标
            
        Returns:
            角度值（度数，0-180）
        """
        # 计算向量
        v1 = p1 - p2
        v2 = p3 - p2
        
        # 计算向量模长
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        # 避免除零
        if norm1 < 1e-6 or norm2 < 1e-6:
            return 0.0
        
        # 计算夹角余弦值
        cosine = np.dot(v1, v2) / (norm1 * norm2)
        
        # 限制在[-1, 1]范围内（避免浮点误差）
        cosine = np.clip(cosine, -1.0, 1.0)
        
        # 转换为角度
        angle = np.arccos(cosine)
        angle_degrees = np.degrees(angle)
        
        return angle_degrees
    
    def calculate_joint_angles(
        self,
        keypoints: np.ndarray,
        joint_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算指定关节的角度
        
        Args:
            keypoints: 关键点数组 (N, 2/3) - (x, y) 或 (x, y, confidence)
            joint_names: 要计算的关节名称列表（None表示全部）
            
        Returns:
            关节名称 -> 角度值的字典
        """
        if joint_names is None:
            joint_names = list(self.joint_defs.keys())
        
        angles = {}
        
        for joint_name in joint_names:
            if joint_name not in self.joint_defs:
                logger.warning(f"未定义的关节: {joint_name}")
                continue
            
            # 获取三个点的索引
            idx1, idx2, idx3 = self.joint_defs[joint_name]
            
            # 检查索引是否有效
            if max(idx1, idx2, idx3) >= len(keypoints):
                logger.warning(f"关节 {joint_name} 的索引超出范围")
                angles[joint_name] = 0.0
                continue
            
            # 提取坐标（前2维）
            p1 = keypoints[idx1, :2]
            p2 = keypoints[idx2, :2]
            p3 = keypoints[idx3, :2]
            
            # 检查置信度（如果有的话）
            if keypoints.shape[1] >= 3:
                conf_threshold = 0.3
                if (keypoints[idx1, 2] < conf_threshold or
                    keypoints[idx2, 2] < conf_threshold or
                    keypoints[idx3, 2] < conf_threshold):
                    angles[joint_name] = 0.0
                    continue
            
            # 计算角度
            angle = self.calculate_angle(p1, p2, p3)
            angles[joint_name] = angle
        
        return angles
    
    @staticmethod
    def calculate_velocity(
        positions: np.ndarray,
        timestamps: np.ndarray,
        method: str = 'finite_diff'
    ) -> np.ndarray:
        """
        计算速度（有限差分法）
        
        Args:
            positions: 位置时序数据 (T, 2/3)
            timestamps: 时间戳数组 (T,)
            method: 计算方法 ('finite_diff' 或 'gradient')
            
        Returns:
            速度数组 (T-1, 2/3) 或 (T, 2/3)
        """
        if len(positions) < 2:
            return np.zeros_like(positions)
        
        if method == 'finite_diff':
            # 一阶有限差分
            dt = np.diff(timestamps)
            dp = np.diff(positions, axis=0)
            
            # 避免除零
            dt = np.maximum(dt, 1e-6)
            
            # 速度 = 位移 / 时间
            velocity = dp / dt[:, np.newaxis]
            
            # 补齐维度（复制最后一个值）
            velocity = np.vstack([velocity, velocity[-1:]])
            
        elif method == 'gradient':
            # NumPy梯度法（中心差分）
            velocity = np.gradient(positions, timestamps, axis=0)
        
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        return velocity
    
    @staticmethod
    def calculate_acceleration(
        velocities: np.ndarray,
        timestamps: np.ndarray
    ) -> np.ndarray:
        """
        计算加速度
        
        Args:
            velocities: 速度时序数据
            timestamps: 时间戳数组
            
        Returns:
            加速度数组
        """
        return KinematicsAnalyzer.calculate_velocity(velocities, timestamps)
    
    def apply_filter(
        self,
        data: np.ndarray,
        fs: float,
        axis: int = 0
    ) -> np.ndarray:
        """
        应用低通滤波器
        
        Args:
            data: 输入数据
            fs: 采样频率（Hz）
            axis: 滤波轴
            
        Returns:
            滤波后的数据
        """
        if self.filter_type is None:
            return data
        
        if self.filter_type == 'lowpass':
            # Butterworth低通滤波器
            nyquist = fs / 2.0
            normalized_cutoff = self.cutoff_freq / nyquist
            
            # 限制截止频率
            if normalized_cutoff >= 1.0:
                logger.warning(f"截止频率过高，跳过滤波")
                return data
            
            b, a = signal.butter(
                self.filter_order,
                normalized_cutoff,
                btype='low'
            )
            
            # 应用滤波（双向滤波避免相位偏移）
            filtered = signal.filtfilt(b, a, data, axis=axis)
            
        elif self.filter_type == 'savgol':
            # Savitzky-Golay滤波器
            # 检查数据长度是否足够
            if len(data) < 16:  # 需要至少16个数据点
                logger.debug(f"数据点不足({len(data)} < 16)，使用简单移动平均")
                # 使用简单移动平均作为替代
                if len(data) < 3:
                    return data
                window_size = min(3, len(data))
                if axis == 0:
                    filtered = np.array([np.mean(data[max(0, i-window_size//2):i+window_size//2+1], axis=0) 
                                       for i in range(len(data))])
                else:
                    filtered = np.array([np.mean(data[:, max(0, i-window_size//2):i+window_size//2+1], axis=1) 
                                       for i in range(data.shape[1])]).T
                return filtered
            
            window_length = min(51, len(data) // 2 * 2 + 1)  # 奇数
            if window_length < 5:
                return data
            
            # 确保polyorder不超过window_length-1
            polyorder = min(3, window_length - 1)
            
            filtered = signal.savgol_filter(
                data,
                window_length,
                polyorder=polyorder,
                axis=axis
            )
        
        else:
            raise ValueError(f"不支持的滤波器类型: {self.filter_type}")
        
        return filtered
    
    def analyze_sequence(
        self,
        keypoints_sequence: List[np.ndarray],
        timestamps: List[float],
        joint_names: Optional[List[str]] = None
    ) -> KinematicsMetrics:
        """
        分析关键点序列的运动学指标
        
        Args:
            keypoints_sequence: 关键点序列 [(N, 3), ...]
            timestamps: 时间戳列表
            joint_names: 要分析的关节列表
            
        Returns:
            KinematicsMetrics对象
        """
        if len(keypoints_sequence) < 2:
            logger.warning("序列长度不足，无法计算运动学指标")
            return KinematicsMetrics({}, {}, {}, [])
        
        # 计算每帧的关节角度
        angles_sequence = []
        for keypoints in keypoints_sequence:
            angles = self.calculate_joint_angles(keypoints, joint_names)
            angles_sequence.append(angles)
        
        # 转换为时序数组格式
        joint_names_used = list(angles_sequence[0].keys())
        angles_dict = {
            name: [frame[name] for frame in angles_sequence]
            for name in joint_names_used
        }
        
        # 计算角速度和角加速度
        timestamps_array = np.array(timestamps)
        velocities_dict = {}
        accelerations_dict = {}
        
        for joint_name, angle_series in angles_dict.items():
            angle_array = np.array(angle_series)
            
            # 应用滤波
            fs = 1.0 / np.mean(np.diff(timestamps_array))
            angle_filtered = self.apply_filter(angle_array, fs)
            
            # 计算速度和加速度
            velocity = self.calculate_velocity(
                angle_filtered.reshape(-1, 1),
                timestamps_array
            ).flatten()
            
            acceleration = self.calculate_acceleration(
                velocity.reshape(-1, 1),
                timestamps_array
            ).flatten()
            
            velocities_dict[joint_name] = velocity.tolist()
            accelerations_dict[joint_name] = acceleration.tolist()
            
            # 更新滤波后的角度
            angles_dict[joint_name] = angle_filtered.tolist()
        
        return KinematicsMetrics(
            angles=angles_dict,
            velocities=velocities_dict,
            accelerations=accelerations_dict,
            timestamps=timestamps
        )


# 示例用法
if __name__ == "__main__":
    logger.add("logs/kinematics.log", rotation="10 MB")
    
    # 创建分析器
    analyzer = KinematicsAnalyzer(keypoint_format='mediapipe')
    
    # 模拟关键点数据（33个关键点）
    num_frames = 100
    keypoints_seq = []
    timestamps = []
    
    for i in range(num_frames):
        # 随机关键点（实际应用中来自姿态估计）
        kp = np.random.rand(33, 3)
        kp[:, 2] = 0.9  # 模拟高置信度
        keypoints_seq.append(kp)
        timestamps.append(i / 30.0)  # 30 FPS
    
    # 分析运动学
    metrics = analyzer.analyze_sequence(
        keypoints_seq,
        timestamps,
        joint_names=['right_knee', 'left_elbow']
    )
    
    print(f"分析了 {len(timestamps)} 帧")
    print(f"关节: {list(metrics.angles.keys())}")
    print(f"右膝角度范围: {min(metrics.angles['right_knee']):.1f}° - {max(metrics.angles['right_knee']):.1f}°")
    
    print("KinematicsAnalyzer模块测试完成")

