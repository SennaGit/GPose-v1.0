#!/usr/bin/env python3
"""
仅创建安装包（使用已有的GPose.exe）
适用于已经有可执行文件，只需要创建安装程序的情况
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
        logging.FileHandler('build_installer.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class InstallerBuilder:
    """安装包构建器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.release_dir = self.project_root / "release"
        self.installer_dir = self.project_root / "installer"
        self.dist_dir = self.project_root / "dist"
        self.version = "1.0"
        
    def print_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           GPose v1.0 安装包创建工具                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
        print(banner)
        logger.info("开始创建GPose v1.0安装包...")
        
    def check_exe(self):
        """检查可执行文件"""
        logger.info("步骤1/5: 检查可执行文件...")
        
        # 优先使用release目录中的EXE
        release_exe = self.release_dir / "GPose.exe"
        dist_exe = self.dist_dir / "GPose.exe"
        
        source_exe = None
        if release_exe.exists():
            source_exe = release_exe
            logger.info(f"找到release中的EXE: {release_exe}")
        elif dist_exe.exists():
            source_exe = dist_exe
            logger.info(f"找到dist中的EXE: {dist_exe}")
        else:
            logger.error("未找到GPose.exe文件")
            logger.error("请先构建可执行文件")
            return False
        
        # 检查文件大小
        size_mb = source_exe.stat().st_size / (1024 * 1024)
        logger.info(f"EXE大小: {size_mb:.1f} MB")
        
        # 确保dist目录存在并复制EXE
        self.dist_dir.mkdir(exist_ok=True)
        if source_exe != dist_exe:
            logger.info(f"复制EXE到dist目录...")
            shutil.copy2(source_exe, dist_exe)
        
        logger.info("✓ 可执行文件检查通过")
        return True
    
    def prepare_resources(self):
        """准备资源文件"""
        logger.info("步骤2/5: 准备资源文件...")
        
        try:
            # 确保必要目录存在
            (self.project_root / "config").mkdir(exist_ok=True)
            (self.project_root / "assets").mkdir(exist_ok=True)
            (self.project_root / "文档").mkdir(exist_ok=True)
            
            # 检查并创建许可证文件
            license_file = self.project_root / "assets" / "license.txt"
            if not license_file.exists():
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
                with open(license_file, 'w', encoding='utf-8') as f:
                    f.write(license_content)
            
            # 检查并创建图标文件（如果不存在，从resources复制）
            icon_file = self.project_root / "assets" / "icon.ico"
            if not icon_file.exists():
                resource_icon = self.project_root / "resources" / "icon.ico"
                if resource_icon.exists():
                    logger.info("复制图标文件...")
                    shutil.copy2(resource_icon, icon_file)
                else:
                    logger.warning("未找到图标文件，将使用默认图标")
            
            # 创建用户手册
            docs_dir = self.project_root / "文档"
            manual_file = docs_dir / "GPose_使用说明.txt"
            if not manual_file.exists():
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
                with open(manual_file, 'w', encoding='utf-8') as f:
                    f.write(manual_content)
            
            # 创建快速开始指南
            quickstart_file = docs_dir / "开始使用.txt"
            if not quickstart_file.exists():
                logger.info("创建快速开始指南...")
                quickstart_content = """GPose 快速开始指南

欢迎使用GPose击剑AI分析系统！

第一步：启动软件
- 从桌面或开始菜单启动GPose

第二步：打开视频
- 点击"文件" → "打开视频"
- 选择您的击剑训练视频

第三步：开始分析
- 点击播放按钮
- 查看实时分析结果

更多详细信息，请查看"GPose_使用说明.txt"

祝您使用愉快！
"""
                with open(quickstart_file, 'w', encoding='utf-8') as f:
                    f.write(quickstart_content)
            
            logger.info("✓ 资源文件准备完成")
            return True
            
        except Exception as e:
            logger.error(f"资源文件准备失败: {e}")
            return False
    
    def create_installer(self):
        """使用Inno Setup创建安装包"""
        logger.info("步骤3/5: 创建Windows安装包...")
        
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
            logger.warning("未找到Inno Setup")
            logger.info("下载地址: https://jrsoftware.org/isinfo.php")
            logger.info("您可以手动运行: iscc setup.iss")
            return False
        
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
                    logger.error(result.stdout)
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
        logger.info("步骤4/5: 创建发布包...")
        
        try:
            # 创建发布包目录
            final_release_dir = self.project_root / "GPose_v1.0_Release"
            final_release_dir.mkdir(exist_ok=True)
            
            # 复制安装包
            installer_src = self.installer_dir / "GPose_Setup_v1.0.exe"
            if installer_src.exists():
                installer_dst = final_release_dir / "GPose_Setup_v1.0.exe"
                shutil.copy2(installer_src, installer_dst)
                logger.info(f"复制安装包到: {installer_dst}")
            
            # 复制便携版EXE（可选）
            exe_src = self.dist_dir / "GPose.exe"
            if exe_src.exists():
                exe_dst = final_release_dir / "GPose_v1.0_Portable.exe"
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
            readme_path = final_release_dir / "发布说明.md"
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
            readme_txt_path = final_release_dir / "README.txt"
            with open(readme_txt_path, 'w', encoding='utf-8') as f:
                f.write(simple_readme)
            
            logger.info("✓ 发布包创建完成")
            logger.info(f"发布包位置: {final_release_dir}")
            return True
            
        except Exception as e:
            logger.error(f"发布包创建失败: {e}")
            return False
    
    def print_summary(self):
        """打印构建总结"""
        logger.info("步骤5/5: 生成构建总结...")
        
        print("\n" + "="*60)
        print("                   构建完成总结")
        print("="*60)
        
        # 检查生成的文件
        files_info = []
        
        installer_path = self.installer_dir / "GPose_Setup_v1.0.exe"
        if installer_path.exists():
            size_mb = installer_path.stat().st_size / (1024 * 1024)
            files_info.append(("安装程序", str(installer_path), f"{size_mb:.1f} MB"))
        
        final_release_dir = self.project_root / "GPose_v1.0_Release"
        if final_release_dir.exists():
            files_info.append(("发布包目录", str(final_release_dir), ""))
        
        if files_info:
            print("\n生成的文件：")
            for name, path, size in files_info:
                print(f"  ✓ {name}: {path}")
                if size:
                    print(f"    大小: {size}")
        
        print("\n后续步骤：")
        print("  1. 测试安装包是否能正常安装和运行")
        print("  2. 检查软件功能是否正常")
        print("  3. 上传到发布平台（GitHub Release等）")
        print("  4. 通知用户下载更新")
        
        print("\n" + "="*60)
        print("          🎉 GPose v1.0 安装包创建完成！🎉")
        print("="*60 + "\n")
    
    def run(self):
        """运行安装包创建流程"""
        self.print_banner()
        start_time = time.time()
        
        steps = [
            ("检查可执行文件", self.check_exe),
            ("准备资源文件", self.prepare_resources),
            ("创建安装包", self.create_installer),
            ("创建发布包", self.create_release_package),
            ("生成总结", lambda: True),  # print_summary doesn't return boolean
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    logger.error(f"步骤失败: {step_name}")
                    # 对于创建安装包失败，我们继续后续步骤
                    if step_name != "创建安装包":
                        return False
            except Exception as e:
                logger.error(f"步骤 {step_name} 执行出错: {e}")
                return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"\n总耗时: {duration:.1f} 秒")
        self.print_summary()
        
        return True

def main():
    """主函数"""
    builder = InstallerBuilder()
    success = builder.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

