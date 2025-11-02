# -*- coding: utf-8 -*-
"""
GPose 优化构建脚本
针对内存不足的情况进行优化
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def build_optimized():
    """使用优化参数构建"""
    try:
        print("=== GPose 优化构建开始 ===")
        print("针对内存不足情况进行优化...")
        
        # 创建构建目录
        build_dir = Path("build/optimized")
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # 优化的Nuitka构建命令
        nuitka_cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",  # 使用standalone模式，减少内存使用
            "--onefile",     # 单文件模式
            "--enable-plugin=pyqt6",
            "--windows-disable-console",
            "--output-filename=GPose.exe",
            f"--output-dir={build_dir}",
            "--assume-yes-for-downloads",
            "--show-progress",
            "--show-memory",
            "--jobs=1",      # 限制并行编译，减少内存使用
            "--lto=no",       # 禁用LTO优化，减少内存使用
            "--no-pyi-file",  # 不生成.pyi文件
            "--remove-output", # 构建后清理临时文件
            "run_gpose.py"
        ]
        
        print("构建命令:")
        print(" ".join(nuitka_cmd))
        print("\n开始构建...")
        print("注意：构建过程可能需要30-60分钟，请耐心等待...")
        
        # 执行构建
        start_time = time.time()
        result = subprocess.run(nuitka_cmd, timeout=3600)  # 1小时超时
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ 构建成功！耗时: {elapsed_time/60:.1f}分钟")
            
            # 检查生成的文件
            exe_path = build_dir / "GPose.exe"
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"可执行文件: {exe_path}")
                print(f"文件大小: {file_size:.1f} MB")
                
                # 创建便携版
                create_portable_package(build_dir)
                return True
            else:
                print("❌ 可执行文件未生成")
                return False
        else:
            print(f"❌ 构建失败，返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 构建超时（1小时）")
        return False
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def create_portable_package(build_dir):
    """创建便携版包"""
    try:
        print("\n创建便携版包...")
        
        portable_dir = build_dir / "GPose_Portable"
        portable_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件
        exe_path = build_dir / "GPose.exe"
        if exe_path.exists():
            shutil.copy2(exe_path, portable_dir / "GPose.exe")
        
        # 复制资源文件
        if Path("resources").exists():
            shutil.copytree("resources", portable_dir / "resources", dirs_exist_ok=True)
        
        if Path("config").exists():
            shutil.copytree("config", portable_dir / "config", dirs_exist_ok=True)
        
        # 复制文档
        for doc_file in ["README.md", "LICENSE", "requirements.txt"]:
            if Path(doc_file).exists():
                shutil.copy2(doc_file, portable_dir / doc_file)
        
        # 创建启动脚本
        start_script = portable_dir / "启动GPose.bat"
        with open(start_script, 'w', encoding='gbk') as f:
            f.write("@echo off\n")
            f.write("echo 正在启动GPose...\n")
            f.write("echo 首次启动可能需要较长时间，请耐心等待...\n")
            f.write("GPose.exe\n")
            f.write("if errorlevel 1 (\n")
            f.write("    echo 程序运行出错，请检查系统要求\n")
            f.write("    pause\n")
            f.write(")\n")
        
        # 创建使用说明
        readme = portable_dir / "使用说明.txt"
        with open(readme, 'w', encoding='utf-8') as f:
            f.write("GPose 便携版使用说明\n")
            f.write("=" * 30 + "\n\n")
            f.write("使用方法:\n")
            f.write("1. 双击 '启动GPose.bat' 运行程序\n")
            f.write("2. 或者直接双击 'GPose.exe' 运行\n\n")
            f.write("系统要求:\n")
            f.write("- Windows 10/11 (64位)\n")
            f.write("- 至少4GB内存\n")
            f.write("- 支持OpenGL的显卡\n")
            f.write("- 至少2GB可用磁盘空间\n\n")
            f.write("注意事项:\n")
            f.write("- 首次运行可能需要较长时间加载\n")
            f.write("- 如遇到问题，请检查系统要求\n")
            f.write("- 建议关闭杀毒软件的实时保护\n")
        
        print(f"✅ 便携版已创建: {portable_dir}")
        
    except Exception as e:
        print(f"❌ 创建便携版失败: {e}")

def main():
    """主函数"""
    print("GPose 优化构建脚本")
    print("针对内存不足的情况进行优化")
    print("=" * 50)
    
    # 检查内存
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        print(f"当前可用内存: {available_gb:.1f}GB")
        
        if available_gb < 4:
            print("⚠️ 警告：可用内存不足4GB，构建可能失败")
            print("建议：")
            print("1. 关闭其他程序释放内存")
            print("2. 重启系统后再次尝试")
            print("3. 使用PyInstaller替代方案")
            
            response = input("\n是否继续构建？(y/n): ")
            if response.lower() != 'y':
                print("构建已取消")
                return
    except ImportError:
        print("⚠️ 无法检查内存状态")
    
    # 开始构建
    success = build_optimized()
    
    if success:
        print("\n🎉 构建完成！")
        print("便携版位置: build/optimized/GPose_Portable/")
    else:
        print("\n❌ 构建失败")
        print("建议尝试PyInstaller方案:")
        print("pip install pyinstaller")
        print("pyinstaller --onefile --windowed --name=GPose run_gpose.py")

if __name__ == "__main__":
    main()
