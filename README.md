# GPose 击剑AI运动分析软件

<div align="center">

![GPose Logo](docs/assets/logo.png)

**基于人工智能的击剑运动分析系统**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[功能特性](#功能特性) • [安装指南](#安装指南) • [使用文档](#使用文档) • [打包部署](#打包部署) • [技术架构](#技术架构) • [贡献指南](#贡献指南)

</div>

---

## 📋 项目简介

GPose是一款专为击剑运动设计的AI视觉运动分析软件，基于OpenPose/MediaPipe姿态估计技术，结合WiFi-CSI无接触式检测，为教练员、运动员和科研工作者提供精准的运动学分析工具。

### 核心优势

- ✅ **智能姿态识别**：自动识别25个人体关键点 + 剑尖追踪
- ✅ **击剑专项分析**：膝关节角度、剑尖速度、重心位移等专业指标
- ✅ **混合传感技术**：视觉 + WiFi-CSI双模式，提升鲁棒性
- ✅ **实时反馈**：低延迟推理（<100ms），支持训练现场即时分析
- ✅ **动作识别**：AI自动分类刺击、撤步、假动作等8类击剑动作
- ✅ **模板匹配**：与专家动作对比，量化技术相似度

---

## 🎯 功能特性

### 1. 姿态估计
- 支持OpenPose（25关键点）和MediaPipe（33关键点）双引擎
- 2D关键点检测 + 可选3D提升
- 剑尖智能追踪（HSV颜色检测/YOLO目标检测）

### 2. 运动学分析
| 指标 | 说明 | 应用场景 |
|------|------|----------|
| 关节角度 | 膝、肘、髋等关节屈曲角度 | 评估弓步深度、发力姿态 |
| 角速度/加速度 | 关节运动速率 | 分析爆发力、动作流畅性 |
| 剑尖速度 | 武器末端运动速度（目标>4m/s） | 量化攻击威力 |
| 重心轨迹 | 身体质心位移路径 | 评估平衡性和步法稳定性 |

### 3. 动作智能分析
- **动作分类**：基于Transformer的8类击剑动作识别（刺击、撤步、假动作等）
- **相似度评分**：DTW算法对比标准模板，生成技术评分
- **轨迹预测**：Kalman滤波 + LSTM预测短期运动轨迹

### 4. 数据导出
- CSV格式：关键点坐标、运动学指标时序数据
- JSON格式：完整会话数据（含元信息）
- PDF报告：可视化图表 + 统计摘要

---

## 🚀 安装指南

### 系统要求
- **操作系统**：Windows 10/11（64位）
- **CPU**：Intel i5 或更高（推荐支持AVX2指令集）
- **内存**：8GB+（推荐16GB）
- **显卡**：可选NVIDIA GPU（CUDA 11.2+，用于加速）
- **摄像头**：支持60-120FPS（可选高速相机）

### 方法1：一键安装包（推荐）
1. 下载最新版安装包：[GPose_v1.0_Setup.exe]
2. 双击运行安装程序，按向导完成安装
3. 启动桌面快捷方式"GPose击剑分析"

### 方法2：Python环境安装
```bash
# 1. 克隆仓库
cd gpose

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载模型文件
python scripts/download_models.py

# 5. 运行程序
python gui/main_window.py
```


---

## 📖 使用文档

### 快速开始

1. **加载视频**
   - 点击"文件" → "打开视频"，选择击剑训练视频
   - 或连接摄像头进行实时分析

2. **选择分析模式**
   - 视觉模式：基于摄像头画面（推荐）
   - CSI模式：需WiFi CSI硬件（高级功能）
   - 混合模式：融合两种数据源

3. **开始分析**
   - 点击"播放"按钮，软件自动识别关键点
   - 实时显示骨架叠加、运动学曲线

4. **查看结果**
   - 图表面板：角度/速度时序曲线
   - 动作列表：识别的动作类型和时间戳
   - 统计面板：平均值、峰值等汇总指标

5. **导出数据**
   - "文件" → "导出" → 选择CSV/JSON/PDF格式


---

## 📦 打包部署

### ✅ v1.0 发布包已完成

GPose v1.0 已成功打包，可供用户下载使用！

#### 发布包内容

📁 **GPose_v1.0_Release** 目录包含：

1. **GPose_v1.0_Portable.exe** (182.6 MB)
   - 便携版，无需安装，双击即用
   - 适合临时使用或U盘携带
   - 包含完整功能

2. **发布说明.md**
   - 详细的安装和使用说明
   - 系统要求和常见问题
   - 更新日志

3. **README.txt**
   - 快速开始指南

#### 用户安装方式

**方式1：便携版（推荐）**
```
1. 下载 GPose_v1.0_Portable.exe
2. 双击运行即可使用
3. 无需安装任何依赖
```

**方式2：完整安装程序（可选）**

如需创建带安装向导的安装程序：
```bash
# 1. 安装 Inno Setup 6
#    下载：https://jrsoftware.org/isinfo.php

# 2. 编译安装程序
iscc setup.iss

# 3. 生成文件
installer/GPose_Setup_v1.0.exe
```

#### 打包技术栈

- **打包工具**：PyInstaller（已完成）
- **安装程序**：Inno Setup（可选）
- **包含组件**：
  - Python 3.11运行时
  - PyQt6 GUI框架
  - OpenCV视觉处理
  - MediaPipe姿态估计
  - PyTorch深度学习（CSI模块）
  - 所有依赖库

#### 重新打包

如需重新打包，运行：
```bash
python build_installer_only.py
```

**注意**：打包后的程序包含完整的运行环境，体积约180MB是正常现象。

---

## 🏗️ 技术架构

```
GPose架构（分层设计）
├── GUI层（PyQt6）
│   ├── 主窗口框架
│   ├── 视频播放器
│   ├── 图表可视化（PyQtGraph）
│   └── 导出向导
├── 应用服务层
│   ├── 会话管理
│   ├── 模板匹配
│   └── 用户统计
├── 分析层
│   ├── 运动学计算（角度/速度/加速度）
│   ├── 动作分类（Transformer）
│   ├── 相似度计算（DTW）
│   └── 轨迹预测（Kalman+LSTM）
├── 处理引擎层
│   ├── 姿态估计（OpenPose/MediaPipe）
│   ├── CSI姿态（MUSIC+CNN-LSTM）
│   ├── 融合算法（卡尔曼滤波）
│   └── 剑尖追踪（HSV/YOLO）
└── 数据输入层
    ├── 视频采集（文件/摄像头）
    ├── CSI数据采集
    └── 时间同步
```

核心算法：
- **姿态估计**：OpenPose BODY_25（COCO AP 61.8）/ MediaPipe（33关键点）
- **CSI处理**：MUSIC 2D AoA（180×180分辨率） + ResNet-CNN + BiLSTM
- **动作识别**：Transformer Encoder（准确率>85%）
- **运动学**：有限差分法 + 低通滤波

技术文档：[架构设计](docs/architecture.md) | [API文档](docs/api.md)

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 关键点识别准确率 | >75% PCKh | MPII数据集标准 |
| 动作分类准确率 | >85% | 8类击剑动作 |
| 实时推理速度 | >30 FPS | 1080p视频 |
| 推理延迟 | <100ms | 从输入到结果 |
| 关节定位误差 | <8cm | 标准环境 |
| 剑尖追踪误差 | <5cm | 带标记情况 |

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何参与
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交代码 (`git commit -m '添加某某功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 开发规范
- 代码风格：遵循PEP8，使用Black格式化
- 注释语言：中文（面向国内用户）
- 测试覆盖率：>70%
- 提交信息：使用中文描述性信息

详见：[开发指南](docs/development.md)

---

## 📝 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

---

<div align="center">

**让AI助力击剑训练科学化** 🤺

Made with ❤️ by GPose Team

</div>

