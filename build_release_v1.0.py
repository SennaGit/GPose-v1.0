#!/usr/bin/env python3
"""
GPose v1.0 完整打包脚本
从Python项目到Windows安装包的一站式打包流程
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('build_release.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class GPoseReleaseBuilder:
    """GPose v1.0 发布包构建器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.installer_dir = self.project_root / "installer"
        self.release_dir = self.project_root / "release"
        self.version = "1.0"
        
    def print_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           GPose 击剑AI分析系统 v1.0                      ║
║              完整打包构建流程                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
        print(banner)
        logger.info("开始GPose v1.0打包流程...")
        
    def check_environment(self):
        """检查打包环境"""
        logger.info("步骤1/5: 检查打包环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        logger.info(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查必要文件
        required_files = [
            "run_gpose.py",
            "version.py",
            "GPose.spec",
            "setup.iss"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"缺少必要文件: {', '.join(missing_files)}")
            return False
        
        # 检查PyInstaller
        try:
            result = subprocess.run(
                [sys.executable, "-m", "PyInstaller", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"PyInstaller版本: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            logger.error("PyInstaller未安装，正在安装...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyinstaller"],
                    check=True
                )
                logger.info("PyInstaller安装成功")
            except subprocess.CalledProcessError:
                logger.error("PyInstaller安装失败")
                return False
        
        logger.info("✓ 环境检查通过")
        return True
    
    def build_exe(self):
        """使用PyInstaller构建EXE"""
        logger.info("步骤2/5: 使用PyInstaller构建EXE...")
        logger.info("这可能需要5-10分钟，请耐心等待...")
        
        # 清理旧的构建文件
        if self.dist_dir.exists():
            logger.info("清理旧的dist目录...")
            shutil.rmtree(self.dist_dir, ignore_errors=True)
        
        build_dir = self.project_root / "build"
        if build_dir.exists():
            logger.info("清理旧的build目录...")
            shutil.rmtree(build_dir, ignore_errors=True)
        
        try:
            # 运行PyInstaller
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--clean",
                "--noconfirm",
                "GPose.spec"
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 检查EXE是否生成
                exe_path = self.dist_dir / "GPose.exe"
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    logger.info(f"✓ GPose.exe构建成功！大小: {size_mb:.1f} MB")
                    return True
                else:
                    logger.error("GPose.exe未生成")
                    logger.error(result.stdout)
                    logger.error(result.stderr)
                    return False
            else:
                logger.error("PyInstaller构建失败")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"构建过程出错: {e}")
            return False
    
    def prepare_installer_files(self):
        """准备安装包所需文件"""
        logger.info("步骤3/5: 准备安装包文件...")
        
        try:
            # 确保必要目录存在
            (self.project_root / "config").mkdir(exist_ok=True)
            (self.project_root / "assets").mkdir(exist_ok=True)
            
            # 检查资源文件
            resource_files = {
                "assets/icon.ico": "图标文件",
                "assets/license.txt": "许可证文件",
                "config/default.yaml": "配置文件"
            }
            
            missing_resources = []
            for file, desc in resource_files.items():
                if not (self.project_root / file).exists():
                    logger.warning(f"缺少{desc}: {file}")
                    missing_resources.append(file)
            
            # 创建缺失的资源文件
            if not (self.project_root / "assets" / "license.txt").exists():
                logger.info("创建许可证文件...")
                license_content = """MIT License

Copyright (c) 2025 GPose Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
                with open(self.project_root / "assets" / "license.txt", 'w', encoding='utf-8') as f:
                    f.write(license_content)
            
            # 创建文档目录
            docs_dir = self.project_root / "文档"
            docs_dir.mkdir(exist_ok=True)
            
            # 创建用户手册
            if not (docs_dir / "GPose_使用说明.txt").exists():
                logger.info("创建用户手册...")
                manual_content = """GPose 击剑AI分析系统 v1.0 使用说明

一、快速开始

1. 启动软件
   - 双击桌面上的"GPose击剑AI分析系统"图标
   - 或从开始菜单启动

2. 加载视频
   - 点击菜单栏"文件" → "打开视频"
   - 选择击剑训练或比赛视频文件
   - 支持格式：MP4、AVI、MOV等

3. 播放与分析
   - 点击播放按钮开始分析
   - 软件会自动识别人体关键点
   - 实时显示运动学数据

4. 查看分析结果
   - 分析面板显示各项指标
   - 可查看关节角度、速度等数据
   - 支持数据导出

二、主要功能

1. 姿态估计
   - 自动识别人体关键点
   - 追踪剑尖位置
   - 显示骨架叠加

2. 运动学分析
   - 关节角度计算
   - 速度和加速度分析
   - 重心轨迹追踪

3. 数据导出
   - CSV格式导出
   - JSON格式导出
   - 生成分析报告

三、快捷键

- 空格键：播放/暂停
- 左箭头：后退一帧
- 右箭头：前进一帧
- Ctrl+O：打开视频
- Ctrl+S：保存数据
- Ctrl+E：导出报告

四、系统要求

- Windows 10/11（64位）
- 8GB内存或更高
- 2GB可用磁盘空间

五、技术支持

如遇问题，请访问项目主页或联系技术支持。

Copyright © 2025 GPose Team
"""
                with open(docs_dir / "GPose_使用说明.txt", 'w', encoding='utf-8') as f:
                    f.write(manual_content)
            
            logger.info("✓ 文件准备完成")
            return True
            
        except Exception as e:
            logger.error(f"文件准备失败: {e}")
            return False
    
    def create_installer(self):
        """使用Inno Setup创建安装包"""
        logger.info("步骤4/5: 创建Windows安装包...")
        
        # 查找Inno Setup
        inno_setup_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe"
        ]
        
        inno_setup = None
        for path in inno_setup_paths:
            if os.path.exists(path):
                inno_setup = path
                logger.info(f"找到Inno Setup: {path}")
                break
        
        if not inno_setup:
            logger.warning("未找到Inno Setup，跳过安装包创建")
            logger.info("下载地址: https://jrsoftware.org/isinfo.php")
            logger.info("您可以手动运行: iscc setup.iss")
            return True  # 不算失败，只是跳过
        
        try:
            # 创建installer目录
            self.installer_dir.mkdir(exist_ok=True)
            
            # 运行Inno Setup编译
            logger.info("正在编译安装包...")
            cmd = [inno_setup, "setup.iss"]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                installer_path = self.installer_dir / "GPose_Setup_v1.0.exe"
                if installer_path.exists():
                    size_mb = installer_path.stat().st_size / (1024 * 1024)
                    logger.info(f"✓ 安装包创建成功！大小: {size_mb:.1f} MB")
                    return True
                else:
                    logger.error("安装包文件未生成")
                    return False
            else:
                logger.error("Inno Setup编译失败")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"安装包创建失败: {e}")
            return False
    
    def create_release_package(self):
        """创建最终发布包"""
        logger.info("步骤5/5: 创建发布包...")
        
        try:
            # 创建release目录
            self.release_dir.mkdir(exist_ok=True)
            
            # 复制安装包
            installer_src = self.installer_dir / "GPose_Setup_v1.0.exe"
            if installer_src.exists():
                installer_dst = self.release_dir / "GPose_Setup_v1.0.exe"
                shutil.copy2(installer_src, installer_dst)
                logger.info(f"复制安装包到: {installer_dst}")
            else:
                logger.warning("安装包不存在，跳过复制")
            
            # 复制单文件EXE（可选）
            exe_src = self.dist_dir / "GPose.exe"
            if exe_src.exists():
                exe_dst = self.release_dir / "GPose_v1.0_Portable.exe"
                shutil.copy2(exe_src, exe_dst)
                logger.info(f"复制便携版到: {exe_dst}")
            
            # 创建发布说明
            release_notes = f"""# GPose 击剑AI分析系统 v{self.version} 发布包

## 📦 安装包内容

本发布包包含以下文件：

1. **GPose_Setup_v{self.version}.exe** - Windows安装程序（推荐）
   - 完整的安装向导
   - 自动创建桌面快捷方式
   - 注册文件关联
   - 支持一键卸载

2. **GPose_v{self.version}_Portable.exe** - 便携版（可选）
   - 单文件可执行程序
   - 无需安装，双击即用
   - 适合临时使用或U盘携带

## 💻 系统要求

- **操作系统**：Windows 10 / Windows 11（64位）
- **处理器**：Intel i5 或同等性能CPU
- **内存**：8GB RAM（推荐16GB）
- **硬盘**：2GB可用空间
- **显卡**：支持OpenGL的显卡

## 🚀 安装步骤

### 方法1：使用安装程序（推荐）

1. 双击 `GPose_Setup_v{self.version}.exe`
2. 按照安装向导提示操作
3. 选择安装路径（默认：C:\\Program Files\\GPose）
4. 完成安装后，从桌面或开始菜单启动

### 方法2：使用便携版

1. 将 `GPose_v{self.version}_Portable.exe` 复制到任意目录
2. 双击运行即可使用
3. 首次运行会在程序目录创建配置文件

## 📖 快速开始

1. **启动软件**
   - 双击桌面图标或从开始菜单启动

2. **加载视频**
   - 点击"文件" → "打开视频"
   - 选择击剑训练视频（支持MP4、AVI、MOV等格式）

3. **开始分析**
   - 点击播放按钮
   - 软件自动识别人体关键点和运动学数据

4. **查看结果**
   - 在分析面板查看各项指标
   - 可导出CSV/JSON格式数据

## ✨ 主要功能

- ✅ **智能姿态识别**：自动识别25个人体关键点 + 剑尖追踪
- ✅ **击剑专项分析**：膝关节角度、剑尖速度、重心位移等指标
- ✅ **实时分析**：低延迟处理，支持现场即时分析
- ✅ **数据导出**：支持CSV、JSON格式导出
- ✅ **现代界面**：专业的击剑主题UI设计

## 🎯 应用场景

- 击剑训练技术分析
- 运动员动作评估
- 教练员辅助教学
- 科研数据采集
- 比赛录像分析

## ⚠️ 注意事项

1. 首次运行时，Windows可能会显示安全警告，选择"仍要运行"即可
2. 软件需要访问视频文件，请确保有相应权限
3. 建议使用高质量的训练视频以获得最佳分析效果
4. 分析大视频文件时可能需要较长时间，请耐心等待

## 🔧 常见问题

**Q: 软件无法启动？**
A: 请确保系统是64位Windows 10/11，并且已安装最新的系统更新。

**Q: 分析结果不准确？**
A: 建议使用光线充足、背景简洁的视频，确保人物清晰可见。

**Q: 如何卸载软件？**
A: 使用安装程序安装的版本，可通过Windows设置中的"应用和功能"卸载。

## 📞 技术支持

- 项目主页：https://github.com/gpose/fencing-analyzer
- 问题反馈：提交GitHub Issue
- 使用文档：查看软件内置帮助文档

## 📝 更新日志

### v{self.version} (2025-10-27)

**首个正式版本发布**

- ✨ 完整的姿态估计功能
- ✨ 击剑专项运动学分析
- ✨ 现代化PyQt6界面
- ✨ 数据导出功能
- ✨ 视频播放控制
- ✨ 配置管理系统

## 📄 许可证

本软件采用 MIT License 开源协议。

---

**GPose Team**  
让AI助力击剑训练科学化 🤺

Copyright © 2025 GPose Team. All rights reserved.

构建日期：{time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 保存发布说明
            readme_path = self.release_dir / "发布说明.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(release_notes)
            logger.info(f"创建发布说明: {readme_path}")
            
            # 创建简短的README
            simple_readme = f"""GPose 击剑AI分析系统 v{self.version}

安装方法：
1. 双击 GPose_Setup_v{self.version}.exe
2. 按照向导完成安装
3. 从桌面启动软件

系统要求：
- Windows 10/11 (64位)
- 8GB内存
- 2GB磁盘空间

详细说明请查看"发布说明.md"

Copyright © 2025 GPose Team
"""
            readme_txt_path = self.release_dir / "README.txt"
            with open(readme_txt_path, 'w', encoding='utf-8') as f:
                f.write(simple_readme)
            
            logger.info("✓ 发布包创建完成")
            return True
            
        except Exception as e:
            logger.error(f"发布包创建失败: {e}")
            return False
    
    def print_summary(self):
        """打印构建总结"""
        print("\n" + "="*60)
        print("                   构建完成总结")
        print("="*60)
        
        # 检查生成的文件
        files_info = []
        
        exe_path = self.dist_dir / "GPose.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            files_info.append(("可执行文件", str(exe_path), f"{size_mb:.1f} MB"))
        
        installer_path = self.installer_dir / "GPose_Setup_v1.0.exe"
        if installer_path.exists():
            size_mb = installer_path.stat().st_size / (1024 * 1024)
            files_info.append(("安装程序", str(installer_path), f"{size_mb:.1f} MB"))
        
        portable_path = self.release_dir / "GPose_v1.0_Portable.exe"
        if portable_path.exists():
            size_mb = portable_path.stat().st_size / (1024 * 1024)
            files_info.append(("便携版", str(portable_path), f"{size_mb:.1f} MB"))
        
        if files_info:
            print("\n生成的文件：")
            for name, path, size in files_info:
                print(f"  ✓ {name}: {path}")
                print(f"    大小: {size}")
        
        print("\n发布目录：")
        print(f"  {self.release_dir}")
        
        print("\n后续步骤：")
        print("  1. 测试安装包是否能正常安装和运行")
        print("  2. 准备发布说明和更新日志")
        print("  3. 上传到发布平台（GitHub Release等）")
        print("  4. 通知用户下载更新")
        
        print("\n" + "="*60)
        print("          🎉 GPose v1.0 打包完成！🎉")
        print("="*60 + "\n")
    
    def run(self):
        """运行完整打包流程"""
        self.print_banner()
        start_time = time.time()
        
        steps = [
            ("检查环境", self.check_environment),
            ("构建EXE", self.build_exe),
            ("准备文件", self.prepare_installer_files),
            ("创建安装包", self.create_installer),
            ("创建发布包", self.create_release_package),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    logger.error(f"步骤失败: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"步骤 {step_name} 执行出错: {e}")
                return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"\n总耗时: {duration/60:.1f} 分钟")
        self.print_summary()
        
        return True

def main():
    """主函数"""
    builder = GPoseReleaseBuilder()
    success = builder.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

