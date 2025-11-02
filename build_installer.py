#!/usr/bin/env python3
"""
GPose 击剑分析软件完整打包脚本
从Python项目到专业Windows安装包的自动化流程
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging
import time

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GPosePackager:
    """GPose 击剑分析软件打包器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.installer_dir = self.project_root / "installer"
        self.assets_dir = self.project_root / "assets"
        
    def check_environment(self):
        """检查打包环境"""
        logger.info("检查打包环境...")
        
        # 检查Python
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            logger.info(f"Python版本: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"Python检查失败: {e}")
            return False
        
        # 检查必要工具
        tools = {
            "pip": "pip --version",
            "nuitka": "python -c \"import nuitka; print('Nuitka已安装')\"",
        }
        
        for tool, cmd in tools.items():
            try:
                if tool == "nuitka":
                    subprocess.run(cmd.split(), check=True, capture_output=True)
                else:
                    subprocess.run(cmd.split(), check=True, capture_output=True)
                logger.info(f"{tool} 检查通过")
            except subprocess.CalledProcessError:
                logger.error(f"{tool} 未安装或不可用")
                return False
        
        return True
    
    def prepare_models(self):
        """准备和优化模型"""
        logger.info("准备和优化模型...")
        
        try:
            # 运行模型转换脚本
            result = subprocess.run([sys.executable, "convert_models.py"], 
                                 capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                logger.info("模型优化完成")
                return True
            else:
                logger.error(f"模型优化失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"模型准备失败: {e}")
            return False
    
    def create_assets(self):
        """创建击剑主题资源"""
        logger.info("创建击剑主题资源...")
        
        try:
            # 运行资源创建脚本
            result = subprocess.run([sys.executable, "create_assets.py"], 
                                 capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                logger.info("资源创建完成")
                return True
            else:
                logger.error(f"资源创建失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"资源创建失败: {e}")
            return False
    
    def compile_with_nuitka(self):
        """使用Nuitka编译EXE"""
        logger.info("开始Nuitka编译...")
        logger.info("这可能需要10-20分钟，请耐心等待...")
        
        try:
            # 运行编译脚本
            if os.name == 'nt':  # Windows
                result = subprocess.run(["build.bat"], shell=True, cwd=self.project_root)
            else:
                logger.error("Nuitka编译仅支持Windows系统")
                return False
            
            if result.returncode == 0:
                logger.info("Nuitka编译完成")
                return True
            else:
                logger.error("Nuitka编译失败")
                return False
        except Exception as e:
            logger.error(f"Nuitka编译失败: {e}")
            return False
    
    def create_installer(self):
        """创建安装包"""
        logger.info("创建安装包...")
        
        # 检查Inno Setup
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
                break
        
        if not inno_setup:
            logger.error("未找到Inno Setup，请安装Inno Setup 6.x")
            logger.info("下载地址: https://jrsoftware.org/isinfo.php")
            return False
        
        try:
            # 运行Inno Setup编译
            result = subprocess.run([inno_setup, "setup.iss"], 
                                 cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("安装包创建完成")
                return True
            else:
                logger.error(f"安装包创建失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"安装包创建失败: {e}")
            return False
    
    def test_installation(self):
        """测试安装包"""
        logger.info("测试安装包...")
        
        installer_path = self.installer_dir / "GPose_Setup_v2.0.exe"
        if not installer_path.exists():
            logger.error("安装包文件不存在")
            return False
        
        # 检查文件大小
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        logger.info(f"安装包大小: {size_mb:.1f} MB")
        
        if size_mb > 500:
            logger.warning("安装包较大，可能影响下载体验")
        
        logger.info("安装包测试完成")
        return True
    
    def create_release_package(self):
        """创建发布包"""
        logger.info("创建发布包...")
        
        release_dir = self.project_root / "release"
        release_dir.mkdir(exist_ok=True)
        
        # 复制安装包
        installer_path = self.installer_dir / "GPose_Setup_v2.0.exe"
        if installer_path.exists():
            shutil.copy2(installer_path, release_dir / "GPose_Setup_v2.0.exe")
            logger.info("安装包已复制到release目录")
        
        # 创建发布说明
        readme_content = """# GPose 击剑分析软件 v2.0

## 安装说明

1. 下载 `GPose_Setup_v2.0.exe`
2. 双击运行安装程序
3. 按照向导完成安装
4. 从桌面或开始菜单启动 GPose

## 系统要求

- Windows 10/11 (64位)
- 4GB RAM (推荐8GB)
- 2GB 可用磁盘空间
- 支持OpenGL的显卡

## 功能特性

- 实时击剑动作分析
- 3D姿态可视化
- 运动学参数计算
- 击剑专项指标分析
- 专业击剑主题界面
- 键盘快捷键控制
- 音频同步播放

## 技术支持

如有问题，请访问项目页面或提交Issue。

## 更新日志

v2.0:
- 击剑主题UI优化
- 键盘快捷键控制
- 音频同步播放
- 性能优化
- Nuitka编译优化

---
GPose Fencing Analyzer - Precision Motion Analysis for Fencing Training
"""
        
        readme_path = release_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info("发布包创建完成")
        return True
    
    def run_full_package(self):
        """运行完整打包流程"""
        logger.info("开始GPose击剑分析软件完整打包流程...")
        start_time = time.time()
        
        steps = [
            ("检查环境", self.check_environment),
            ("准备模型", self.prepare_models),
            ("创建资源", self.create_assets),
            ("Nuitka编译", self.compile_with_nuitka),
            ("创建安装包", self.create_installer),
            ("测试安装包", self.test_installation),
            ("创建发布包", self.create_release_package),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"执行步骤: {step_name}")
            if not step_func():
                logger.error(f"步骤失败: {step_name}")
                return False
            logger.info(f"步骤完成: {step_name}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("=" * 50)
        logger.info("GPose击剑分析软件打包完成！")
        logger.info(f"总耗时: {duration:.1f} 秒")
        logger.info("=" * 50)
        
        # 显示结果
        installer_path = self.installer_dir / "GPose_Setup_v2.0.exe"
        if installer_path.exists():
            size_mb = installer_path.stat().st_size / (1024 * 1024)
            logger.info(f"安装包位置: {installer_path}")
            logger.info(f"安装包大小: {size_mb:.1f} MB")
        
        logger.info("可以开始测试和发布了！")
        return True

def main():
    """主函数"""
    packager = GPosePackager()
    success = packager.run_full_package()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
