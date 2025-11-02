# -*- coding: utf-8 -*-
"""
GPose 简化构建脚本（修复版）
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def build_gpose():
    """构建GPose可执行文件"""
    try:
        print("=== GPose 构建开始 ===")
        
        # 创建构建目录
        build_dir = Path("build/simple")
        build_dir.mkdir(parents=True, exist_ok=True)
        
        print("构建目录:", build_dir.absolute())
        
        # 简化的Nuitka构建命令
        nuitka_cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile", 
            "--enable-plugin=pyqt6",
            "--windows-disable-console",
            "--output-filename=GPose.exe",
            f"--output-dir={build_dir}",
            "--assume-yes-for-downloads",
            "--show-progress",
            "--show-memory",
            "--jobs=1",
            "run_gpose.py"
        ]
        
        print("构建命令:")
        print(" ".join(nuitka_cmd))
        print("\n开始构建...")
        print("注意：构建过程可能需要30-60分钟，请耐心等待...")
        
        # 执行构建
        start_time = time.time()
        result = subprocess.run(nuitka_cmd, timeout=3600)
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n构建成功！耗时: {elapsed_time/60:.1f}分钟")
            
            # 检查生成的文件
            exe_path = build_dir / "GPose.exe"
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)
                print(f"可执行文件: {exe_path}")
                print(f"文件大小: {file_size:.1f} MB")
                return True
            else:
                print("可执行文件未生成")
                return False
        else:
            print(f"构建失败，返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("构建超时（1小时）")
        return False
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print("GPose 简化构建脚本")
    print("=" * 30)
    
    # 检查内存
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        print(f"当前可用内存: {available_gb:.1f}GB")
        
        if available_gb < 4:
            print("警告：可用内存不足4GB，构建可能失败")
            print("建议：")
            print("1. 关闭其他程序释放内存")
            print("2. 重启系统后再次尝试")
            print("3. 使用PyInstaller替代方案")
    except ImportError:
        print("无法检查内存状态")
    
    # 开始构建
    success = build_gpose()
    
    if success:
        print("\n构建完成！")
        print("可执行文件位置: build/simple/GPose.exe")
    else:
        print("\n构建失败")
        print("建议尝试PyInstaller方案:")
        print("pip install pyinstaller")
        print("pyinstaller --onefile --windowed --name=GPose run_gpose.py")

if __name__ == "__main__":
    main()
