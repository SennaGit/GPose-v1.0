# GPose 快速启动指南

## 🚀 5分钟快速开始

### 第1步：环境准备

确保您的系统满足以下要求：
- Windows 10/11 (64位)
- Python 3.8 或更高版本
- 至少 8GB 内存

### 第2步：安装依赖

```bash
# 克隆或进入项目目录
cd G-Pose

# 安装Python依赖
pip install -r requirements.txt
```

### 第3步：下载模型

```bash
# 运行模型下载脚本
python scripts/download_models.py
```

### 第4步：运行程序

```bash
# 启动GPose桌面应用
python gui/main_window.py
```

---

## 📁 项目结构说明

```
G-Pose/
├── core/                    # 核心功能模块
│   ├── io/                  # 数据输入（视频、CSI）
│   │   └── video_reader.py  # ✅ 已实现
│   ├── pose/                # 姿态估计
│   │   └── visual_estimator.py  # ✅ 已实现（MediaPipe/OpenPose）
│   └── config.py            # ✅ 配置管理
│
├── analysis/                # 分析模块
│   ├── kinematics.py        # ✅ 运动学计算
│   └── fencing_metrics.py   # ✅ 击剑专项指标
│
├── gui/                     # 图形界面
│   ├── main_window.py       # ✅ 主窗口
│   └── styles/              # ✅ 设计系统
│       ├── design_tokens.json
│       └── stylesheet.qss
│
├── config/                  # 配置文件
│   └── default.yaml         # ✅ 默认配置
│
├── utils/                   # 工具模块
│   └── logger.py            # ✅ 日志系统
│
├── scripts/                 # 脚本工具
│   ├── download_models.py   # ✅ 模型下载
│   └── run_tests.py         # ✅ 测试运行
│
├── tests/                   # 测试
│   ├── test_video_reader.py  # ✅ 
│   └── test_kinematics.py    # ✅
│
├── requirements.txt         # ✅ 依赖清单
├── setup.py                 # ✅ 安装配置
├── README.md                # ✅ 项目说明
└── LICENSE                  # ✅ MIT许可证
```

---

## 🎯 当前完成情况

### ✅ 已完成模块
1. **项目基础架构**
   - 目录结构完整
   - 配置系统（YAML）
   - 日志系统（Loguru）
   - 依赖管理

2. **数据输入层**
   - VideoReader：支持视频文件、摄像头、RTSP流
   - 自动降帧、尺寸调整
   - 帧跳转和进度管理

3. **姿态估计层**
   - MediaPipe集成（33关键点）
   - OpenPose占位接口（待完整实现）
   - 统一的PoseResult数据格式

4. **运动学分析层**
   - 关节角度计算（三点向量法）
   - 速度/加速度计算（有限差分）
   - 低通滤波（Butterworth/Savitzky-Golay）
   - 击剑专项指标（膝角、重心、剑速等）

5. **GUI界面**
   - PyQt6主窗口框架
   - Design System（配色、字体、布局）
   - QSS样式表
   - 菜单栏、工具栏、状态栏

6. **测试框架**
   - Pytest单元测试
   - 代码覆盖率报告

### 🔨 待开发模块

1. **剑尖追踪** (weapon_tracker.py)
   - HSV颜色检测
   - YOLO目标检测（可选）

2. **CSI模块集成**
   - MUSIC AoA算法
   - CNN-LSTM回归
   - 视觉+CSI融合

3. **动作分类**
   - Transformer模型
   - 击剑数据集收集
   - 模型训练脚本

4. **相似度分析**
   - DTW算法
   - 专家模板库
   - 在线聚类

5. **GUI增强**
   - 视频播放器控件
   - 实时骨架叠加
   - PyQtGraph图表
   - 导出向导

6. **性能优化**
   - ONNX模型导出
   - OpenVINO加速
   - 多线程推理

7. **打包部署**
   - Nuitka编译
   - 安装程序制作
   - 用户文档

---

## 🧪 测试运行

### 单元测试
```bash
# 运行所有测试
python scripts/run_tests.py

# 只运行单元测试
python scripts/run_tests.py unit

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

### 功能测试

#### 测试视频读取
```python
from core.io.video_reader import VideoReader

# 测试摄像头（如果有）
with VideoReader(0, target_fps=30) as reader:
    success, frame, timestamp = reader.read()
    if success:
        print(f"成功读取帧，尺寸: {frame.shape}")
```

#### 测试姿态估计
```python
from core.pose.visual_estimator import VisualPoseEstimator
import cv2

# 创建估计器
estimator = VisualPoseEstimator(backend='mediapipe')

# 读取测试图像
frame = cv2.imread("test_image.jpg")

# 执行估计
result = estimator.estimate(frame)
print(f"检测到 {result.num_keypoints} 个关键点")
```

#### 测试运动学分析
```python
from analysis.kinematics import KinematicsAnalyzer
import numpy as np

# 创建分析器
analyzer = KinematicsAnalyzer(keypoint_format='mediapipe')

# 模拟关键点
keypoints = np.random.rand(33, 3)
angles = analyzer.calculate_joint_angles(keypoints)
print(f"右膝角度: {angles['right_knee']:.1f}°")
```

---

## 🐛 常见问题

### Q: ImportError: No module named 'PyQt6'
**A:** 运行 `pip install PyQt6`

### Q: MediaPipe下载速度慢
**A:** 使用镜像源：
```bash
pip install mediapipe -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 如何启用GPU加速？
**A:** 
1. 安装CUDA 11.2+
2. 安装GPU版本的PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Q: 程序启动后看不到窗口
**A:** 检查日志文件 `logs/gpose_*.log`，查看错误信息

---

## 📚 下一步学习

1. **阅读完整文档**: [README.md](README.md)
2. **查看技术实施计划**: [--ai.plan.md](--ai.plan.md)
3. **参与开发**: 查看 GitHub Issues
4. **社区交流**: 加入QQ群 [待建立]

---

## 🎓 开发者指南

### 添加新功能
1. 在对应模块创建新文件
2. 编写单元测试
3. 更新文档
4. 提交Pull Request

### 代码规范
- 遵循PEP8
- 使用类型提示（Type Hints）
- 中文注释和文档字符串
- 测试覆盖率>70%

### 提交规范
```
feat: 添加剑尖追踪功能
fix: 修复角度计算bug
docs: 更新安装文档
test: 增加运动学测试用例
```

---

**祝您使用愉快！如有问题，请提交 Issue。** 🎉

