# GPose 安装指南

## 📋 系统要求

### 最低配置
- **操作系统**: Windows 10/11 (64位)
- **处理器**: Intel Core i5 或同等性能
- **内存**: 8GB RAM
- **磁盘空间**: 5GB
- **Python版本**: 3.8 或更高

### 推荐配置
- **操作系统**: Windows 11 (64位)
- **处理器**: Intel Core i7 或更高
- **内存**: 16GB RAM
- **显卡**: NVIDIA GPU（支持CUDA 11.2+）
- **磁盘空间**: 10GB SSD
- **摄像头**: 支持60-120FPS的高速摄像头（用于实时分析）

---

## 🚀 安装步骤

### 方法1：从源码安装（推荐开发者）

#### 步骤1：安装Python

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.8或更高版本
3. 安装时勾选"Add Python to PATH"

验证安装：
```bash
python --version
# 应显示: Python 3.8.x 或更高
```

#### 步骤2：克隆/下载项目

```bash
# 方式A：使用Git
git clone https://github.com/yourusername/gpose.git
cd gpose

# 方式B：直接下载ZIP并解压
# 下载后解压到 D:\G-Pose
cd D:\G-Pose
```

#### 步骤3：创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/Mac:
# source venv/bin/activate

# 激活后命令行前缀会显示 (venv)
```

#### 步骤4：安装依赖包

```bash
# 升级pip
python -m pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt

# 如果下载速度慢，使用国内镜像：
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 步骤5：下载模型文件

```bash
# 运行模型下载脚本
python scripts/download_models.py
```

#### 步骤6：验证安装

```bash
# 运行基础演示程序
python examples/demo_basic.py

# 如果看到演示成功完成，说明安装正确
```

#### 步骤7：启动GUI应用

```bash
# 启动GPose桌面应用
python gui/main_window.py
```

---

### 方法2：一键安装包（即将推出）

待v1.0正式发布后，我们将提供Windows安装程序：

1. 下载 `GPose_Setup_v1.0.exe`
2. 双击运行安装程序
3. 按照向导完成安装
4. 从桌面快捷方式启动GPose

---

## 🔧 高级配置

### 配置GPU加速（可选）

如果您有NVIDIA显卡并希望加速推理：

#### 1. 安装CUDA

1. 访问 [NVIDIA CUDA下载页面](https://developer.nvidia.com/cuda-downloads)
2. 下载并安装CUDA Toolkit 11.2或更高版本
3. 验证安装：
```bash
nvcc --version
```

#### 2. 安装GPU版PyTorch

```bash
# 卸载CPU版本
pip uninstall torch torchvision

# 安装GPU版本（CUDA 11.8示例）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### 3. 验证GPU可用

```python
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
# 应显示: CUDA可用: True
```

#### 4. 修改配置

编辑 `config/default.yaml`：
```yaml
performance:
  use_gpu: true
  gpu_device: 0
```

---

### 配置OpenPose（可选）

如果您需要使用OpenPose引擎（更高精度）：

#### 1. 下载OpenPose

访问 [OpenPose GitHub](https://github.com/CMU-Perceptual-Computing-Lab/openpose) 下载预编译版本

#### 2. 配置路径

1. 将OpenPose解压到某个位置（如 `C:\openpose`）
2. 复制以下文件到GPose的 `resource/` 目录：
   - `bin/` 文件夹
   - `models/` 文件夹
   - Python绑定文件（`pyopenpose.pyd` 等）

#### 3. 修改配置

编辑 `config/default.yaml`：
```yaml
pose:
  backend: "openpose"
  openpose:
    model_folder: "resource/models/"
    model_pose: "BODY_25"
```

---

## 🐛 常见问题

### Q1: 提示 "ModuleNotFoundError: No module named 'PyQt6'"

**解决方案:**
```bash
pip install PyQt6
```

### Q2: MediaPipe下载失败或速度慢

**解决方案:**
```bash
# 使用镜像源
pip install mediapipe -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或手动下载whl文件后安装
pip install mediapipe-0.9.0-cp38-cp38-win_amd64.whl
```

### Q3: 提示 "ImportError: DLL load failed"

**解决方案:**
1. 安装Microsoft Visual C++ Redistributable
   - 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. 重新安装Python包：
```bash
pip install --force-reinstall opencv-python
```

### Q4: GPU加速不生效

**解决方案:**
1. 检查CUDA是否正确安装：
```bash
nvcc --version
nvidia-smi
```

2. 确认PyTorch版本匹配：
```bash
python -c "import torch; print(torch.version.cuda)"
```

3. 查看日志文件 `logs/gpose_*.log` 检查错误信息

### Q5: 程序启动后窗口无响应

**解决方案:**
1. 检查是否有杀毒软件阻止
2. 以管理员权限运行
3. 查看日志文件定位问题

### Q6: 摄像头无法打开

**解决方案:**
1. 确认摄像头未被其他程序占用
2. 尝试更换摄像头编号（0, 1, 2...）
3. 检查摄像头驱动程序

---

## 📚 下一步

安装完成后，您可以：

1. **阅读快速启动指南**: [QUICKSTART.md](QUICKSTART.md)
2. **查看使用示例**: `examples/demo_basic.py`
3. **运行测试**: `python scripts/run_tests.py`
4. **阅读完整文档**: [README.md](README.md)

---

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**: `logs/gpose_*.log`
2. **搜索Issue**: [GitHub Issues](https://github.com/yourusername/gpose/issues)
3. **提交新Issue**: 提供详细的错误信息和系统配置
4. **加入社区**: QQ群 [待建立]

---

## 📝 更新日志

### v1.0.0 (2024-10-20)
- ✅ 初始版本发布
- ✅ MediaPipe姿态估计
- ✅ 运动学分析
- ✅ 击剑专项指标
- ✅ 剑尖追踪
- ✅ 数据导出
- ✅ PyQt6 GUI界面

---

**祝您安装顺利！如有问题，请随时提Issue。** 🎉

