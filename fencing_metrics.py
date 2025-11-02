"""
击剑专项运动学指标分析
计算击剑运动中的关键生物力学指标
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from .kinematics import KinematicsAnalyzer


@dataclass
class FencingMetrics:
    """击剑专项指标数据"""
    # 膝关节指标
    rear_knee_angle: float  # 后腿膝关节屈曲角（度）
    front_knee_angle: float  # 前腿膝关节屈曲角（度）
    
    # 重心指标
    center_of_mass: Tuple[float, float]  # 重心位置(x, y)
    com_displacement: float  # 重心水平位移（像素/米）
    com_velocity: float  # 重心速度
    
    # 剑尖指标
    weapon_tip_position: Optional[Tuple[float, float]]  # 剑尖位置
    weapon_tip_velocity: Optional[float]  # 剑尖速度（m/s）
    weapon_tip_acceleration: Optional[float]  # 剑尖加速度
    
    # 手臂指标
    arm_extension: float  # 持剑臂伸展程度（%）
    elbow_angle: float  # 肘关节角度
    
    # 姿态指标
    body_lean_angle: float  # 躯干前倾角度
    balance_score: float  # 平衡评分（0-100）
    
    # 时间戳
    timestamp: float


class FencingMetricsAnalyzer:
    """击剑专项指标分析器"""
    
    # 人体部位质量占比（用于重心计算）
    BODY_SEGMENT_MASS_RATIOS = {
        'head': 0.081,
        'torso': 0.497,
        'upper_arm': 0.028,
        'forearm': 0.016,
        'hand': 0.006,
        'thigh': 0.100,
        'shank': 0.0465,
        'foot': 0.0145
    }
    
    # 理想击剑姿态参数
    IDEAL_RANGES = {
        'rear_knee_angle': (120, 140),  # 后腿膝角120-140°为最佳发力角度
        'front_knee_angle': (140, 160),  # 前腿膝角相对较直
        'weapon_tip_velocity': (4.0, 6.0),  # 精英运动员剑尖速度4-6 m/s
        'arm_extension': (70, 90),  # 手臂伸展70-90%
    }
    
    def __init__(
        self,
        keypoint_format: str = 'mediapipe',
        pixels_per_meter: float = 100.0  # 像素到米的转换系数
    ):
        """
        初始化击剑指标分析器
        
        Args:
            keypoint_format: 关键点格式
            pixels_per_meter: 像素到米的转换比例
        """
        self.keypoint_format = keypoint_format
        self.pixels_per_meter = pixels_per_meter
        self.kinematics = KinematicsAnalyzer(keypoint_format)
        
        logger.info("击剑专项指标分析器初始化完成")
    
    def calculate_center_of_mass(
        self,
        keypoints: np.ndarray,
        use_simple: bool = True
    ) -> Tuple[float, float]:
        """
        计算人体重心位置
        
        Args:
            keypoints: 关键点数组 (N, 2/3)
            use_simple: 使用简化方法（髋部中点）还是加权方法
            
        Returns:
            重心坐标 (x, y)
        """
        if use_simple:
            # 简化方法：取髋部中点作为重心近似
            if self.keypoint_format == 'mediapipe':
                left_hip = keypoints[23, :2]
                right_hip = keypoints[24, :2]
            else:  # openpose
                left_hip = keypoints[12, :2]
                right_hip = keypoints[9, :2]
            
            com = (left_hip + right_hip) / 2.0
        else:
            # 加权方法（更精确但需要更多计算）
            # TODO: 实现基于体段质量分布的重心计算
            com = self.calculate_weighted_com(keypoints)
        
        return tuple(com)
    
    def calculate_weighted_com(self, keypoints: np.ndarray) -> np.ndarray:
        """基于体段质量分布计算重心（简化版）"""
        # 简化实现：主要考虑躯干和腿部
        if self.keypoint_format == 'mediapipe':
            # 躯干中心
            shoulders = (keypoints[11, :2] + keypoints[12, :2]) / 2
            hips = (keypoints[23, :2] + keypoints[24, :2]) / 2
            torso_center = (shoulders + hips) / 2
            
            # 加权重心
            com = (
                torso_center * 0.7 +  # 躯干权重
                hips * 0.3  # 腿部权重
            )
        else:
            # OpenPose简化版本
            neck = keypoints[1, :2]
            mid_hip = keypoints[8, :2]
            com = (neck * 0.3 + mid_hip * 0.7)
        
        return com
    
    def calculate_weapon_tip_velocity(
        self,
        weapon_tip_positions: List[Tuple[float, float]],
        timestamps: List[float]
    ) -> float:
        """
        计算剑尖速度
        
        Args:
            weapon_tip_positions: 剑尖位置序列
            timestamps: 时间戳序列
            
        Returns:
            剑尖速度（m/s）
        """
        if len(weapon_tip_positions) < 2:
            return 0.0
        
        # 转换为numpy数组
        positions = np.array(weapon_tip_positions)
        times = np.array(timestamps)
        
        # 计算速度
        velocities = KinematicsAnalyzer.calculate_velocity(positions, times)
        
        # 计算速度大小（欧几里得范数）
        speed = np.linalg.norm(velocities, axis=1)
        
        # 转换为m/s
        speed_ms = speed / self.pixels_per_meter
        
        # 返回平均速度或最大速度
        return float(np.max(speed_ms))
    
    def calculate_arm_extension(
        self,
        keypoints: np.ndarray,
        hand: str = 'right'
    ) -> float:
        """
        计算手臂伸展程度
        
        Args:
            keypoints: 关键点数组
            hand: 手臂选择 ('left' 或 'right')
            
        Returns:
            伸展程度百分比 (0-100)
        """
        if self.keypoint_format == 'mediapipe':
            if hand == 'right':
                shoulder = keypoints[12, :2]
                elbow = keypoints[14, :2]
                wrist = keypoints[16, :2]
            else:
                shoulder = keypoints[11, :2]
                elbow = keypoints[13, :2]
                wrist = keypoints[15, :2]
        else:  # openpose
            if hand == 'right':
                shoulder = keypoints[2, :2]
                elbow = keypoints[3, :2]
                wrist = keypoints[4, :2]
            else:
                shoulder = keypoints[5, :2]
                elbow = keypoints[6, :2]
                wrist = keypoints[7, :2]
        
        # 计算肘关节角度
        elbow_angle = KinematicsAnalyzer.calculate_angle(
            shoulder, elbow, wrist
        )
        
        # 角度越接近180°，伸展程度越高
        extension_percent = (elbow_angle / 180.0) * 100.0
        
        return float(extension_percent)
    
    def calculate_balance_score(
        self,
        com_positions: List[Tuple[float, float]],
        support_base: Optional[Tuple[float, float]] = None
    ) -> float:
        """
        计算平衡评分
        
        Args:
            com_positions: 重心位置序列
            support_base: 支撑基底（脚的位置范围）
            
        Returns:
            平衡评分 (0-100)
        """
        if len(com_positions) < 2:
            return 50.0
        
        # 计算重心移动的标准差（越小越稳定）
        com_array = np.array(com_positions)
        com_std = np.std(com_array, axis=0)
        
        # 标准差越小，平衡性越好
        # 简化评分：基于水平方向标准差
        horizontal_stability = 100.0 - min(com_std[0] / 10.0, 100.0)
        
        return float(np.clip(horizontal_stability, 0, 100))
    
    def analyze_frame(
        self,
        keypoints: np.ndarray,
        weapon_tip: Optional[Tuple[float, float]] = None,
        timestamp: float = 0.0,
        prev_metrics: Optional[FencingMetrics] = None
    ) -> FencingMetrics:
        """
        分析单帧的击剑指标
        
        Args:
            keypoints: 关键点数组
            weapon_tip: 剑尖位置（可选）
            timestamp: 时间戳
            prev_metrics: 前一帧的指标（用于计算速度）
            
        Returns:
            FencingMetrics对象
        """
        # 计算关节角度
        angles = self.kinematics.calculate_joint_angles(keypoints)
        
        # 膝关节角度
        rear_knee = angles.get('right_knee', 0.0)  # 假设右腿在后
        front_knee = angles.get('left_knee', 0.0)
        
        # 重心
        com = self.calculate_center_of_mass(keypoints)
        
        # 重心位移（相对于前一帧）
        if prev_metrics:
            prev_com = prev_metrics.center_of_mass
            com_disp = np.linalg.norm(np.array(com) - np.array(prev_com))
            
            # 重心速度
            dt = timestamp - prev_metrics.timestamp
            com_vel = com_disp / max(dt, 1e-6) / self.pixels_per_meter
        else:
            com_disp = 0.0
            com_vel = 0.0
        
        # 剑尖速度（需要历史数据）
        weapon_tip_vel = None
        weapon_tip_acc = None
        if weapon_tip and prev_metrics and prev_metrics.weapon_tip_position:
            dt = timestamp - prev_metrics.timestamp
            if dt > 0:
                tip_disp = np.linalg.norm(
                    np.array(weapon_tip) - np.array(prev_metrics.weapon_tip_position)
                )
                weapon_tip_vel = tip_disp / dt / self.pixels_per_meter
        
        # 手臂伸展
        arm_ext = self.calculate_arm_extension(keypoints, hand='right')
        elbow_ang = angles.get('right_elbow', 0.0)
        
        # 躯干倾角（简化计算）
        if self.keypoint_format == 'mediapipe':
            shoulder_center = (keypoints[11, :2] + keypoints[12, :2]) / 2
            hip_center = (keypoints[23, :2] + keypoints[24, :2]) / 2
        else:
            shoulder_center = keypoints[1, :2]
            hip_center = keypoints[8, :2]
        
        # 计算倾角（相对于垂直线）
        torso_vector = shoulder_center - hip_center
        lean_angle = np.degrees(np.arctan2(torso_vector[0], torso_vector[1]))
        
        # 平衡评分（简化版）
        balance = 80.0  # 默认值，实际需要多帧数据
        
        return FencingMetrics(
            rear_knee_angle=rear_knee,
            front_knee_angle=front_knee,
            center_of_mass=com,
            com_displacement=com_disp,
            com_velocity=com_vel,
            weapon_tip_position=weapon_tip,
            weapon_tip_velocity=weapon_tip_vel,
            weapon_tip_acceleration=weapon_tip_acc,
            arm_extension=arm_ext,
            elbow_angle=elbow_ang,
            body_lean_angle=lean_angle,
            balance_score=balance,
            timestamp=timestamp
        )
    
    def evaluate_technique(self, metrics: FencingMetrics) -> Dict[str, str]:
        """
        评估技术动作质量
        
        Args:
            metrics: 击剑指标
            
        Returns:
            各项指标的评估结果 {'指标名': '优秀/良好/需改进'}
        """
        evaluation = {}
        
        # 后腿膝角评估
        rear_knee_range = self.IDEAL_RANGES['rear_knee_angle']
        if rear_knee_range[0] <= metrics.rear_knee_angle <= rear_knee_range[1]:
            evaluation['后腿膝角'] = '优秀'
        elif abs(metrics.rear_knee_angle - sum(rear_knee_range)/2) < 20:
            evaluation['后腿膝角'] = '良好'
        else:
            evaluation['后腿膝角'] = '需改进'
        
        # 剑尖速度评估
        if metrics.weapon_tip_velocity:
            tip_vel_range = self.IDEAL_RANGES['weapon_tip_velocity']
            if tip_vel_range[0] <= metrics.weapon_tip_velocity <= tip_vel_range[1]:
                evaluation['剑尖速度'] = '优秀'
            elif metrics.weapon_tip_velocity > tip_vel_range[0] * 0.8:
                evaluation['剑尖速度'] = '良好'
            else:
                evaluation['剑尖速度'] = '需改进'
        
        # 手臂伸展评估
        arm_ext_range = self.IDEAL_RANGES['arm_extension']
        if arm_ext_range[0] <= metrics.arm_extension <= arm_ext_range[1]:
            evaluation['手臂伸展'] = '优秀'
        elif metrics.arm_extension > 60:
            evaluation['手臂伸展'] = '良好'
        else:
            evaluation['手臂伸展'] = '需改进'
        
        # 平衡性评估
        if metrics.balance_score > 80:
            evaluation['平衡性'] = '优秀'
        elif metrics.balance_score > 60:
            evaluation['平衡性'] = '良好'
        else:
            evaluation['平衡性'] = '需改进'
        
        return evaluation


# 示例用法
if __name__ == "__main__":
    logger.add("logs/fencing_metrics.log", rotation="10 MB")
    
    # 创建分析器
    analyzer = FencingMetricsAnalyzer(keypoint_format='mediapipe')
    
    # 模拟关键点数据
    keypoints = np.random.rand(33, 3)
    keypoints[:, 2] = 0.9
    
    # 分析
    metrics = analyzer.analyze_frame(
        keypoints,
        weapon_tip=(500, 300),
        timestamp=0.0
    )
    
    print(f"后腿膝角: {metrics.rear_knee_angle:.1f}°")
    print(f"重心位置: {metrics.center_of_mass}")
    print(f"手臂伸展: {metrics.arm_extension:.1f}%")
    print(f"平衡评分: {metrics.balance_score:.1f}")
    
    # 评估
    evaluation = analyzer.evaluate_technique(metrics)
    print(f"\n技术评估: {evaluation}")
    
    print("FencingMetricsAnalyzer模块测试完成")

