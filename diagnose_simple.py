# -*- coding: utf-8 -*-
# GPose构建环境诊断脚本（简化版）
import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    print(f"Python版本: {sys.version}")
    if sys.version_info < (3, 8):
        print("[ERROR] Python版本过低，需要3.8+")
        return False
    print("[OK] Python版本正常")
    return True

def check_dependencies():
    deps = ['PyQt6', 'cv2', 'mediapipe', 'numpy', 'scipy', 'loguru']
    missing = []
    for dep in deps:
        try:
            __import__(dep)
            print(f"[OK] {dep} 已安装")
        except ImportError:
            print(f"[ERROR] {dep} 未安装")
            missing.append(dep)
    return len(missing) == 0, missing

def check_nuitka():
    try:
        result = subprocess.run([sys.executable, '-m', 'nuitka', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] Nuitka版本: {result.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] Nuitka运行失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Nuitka检查失败: {e}")
        return False

def check_system_resources():
    try:
        import psutil
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        print(f"总内存: {memory.total / (1024**3):.1f}GB")
        print(f"可用内存: {memory.available / (1024**3):.1f}GB")
        print(f"可用磁盘: {disk.free / (1024**3):.1f}GB")
        
        if memory.available < 4 * (1024**3):  # 4GB
            print("[WARNING] 内存可能不足，建议至少4GB可用内存")
        if disk.free < 10 * (1024**3):  # 10GB
            print("[WARNING] 磁盘空间可能不足，建议至少10GB可用空间")
    except ImportError:
        print("[WARNING] 无法检查系统资源，请安装psutil: pip install psutil")

def check_project_structure():
    project_files = ['run_gpose.py', 'requirements.txt', 'gui/main_window.py']
    missing_files = []
    
    for file in project_files:
        if Path(file).exists():
            print(f"[OK] {file} 存在")
        else:
            print(f"[ERROR] {file} 缺失")
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

if __name__ == "__main__":
    print("=== GPose构建环境诊断 ===")
    print("=" * 50)
    
    # 检查Python版本
    print("\n1. 检查Python版本")
    print("-" * 20)
    python_ok = check_python_version()
    
    # 检查项目结构
    print("\n2. 检查项目结构")
    print("-" * 20)
    project_ok, missing_files = check_project_structure()
    
    # 检查依赖
    print("\n3. 检查核心依赖")
    print("-" * 20)
    deps_ok, missing_deps = check_dependencies()
    
    # 检查Nuitka
    print("\n4. 检查Nuitka")
    print("-" * 20)
    nuitka_ok = check_nuitka()
    
    # 检查系统资源
    print("\n5. 检查系统资源")
    print("-" * 20)
    check_system_resources()
    
    # 总结
    print("\n" + "=" * 50)
    print("=== 诊断总结 ===")
    
    issues = []
    if not python_ok:
        issues.append("Python版本过低")
    if not project_ok:
        issues.append(f"项目文件缺失: {missing_files}")
    if not deps_ok:
        issues.append(f"依赖缺失: {missing_deps}")
    if not nuitka_ok:
        issues.append("Nuitka有问题")
    
    if issues:
        print("[ERROR] 发现以下问题:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n建议解决方案:")
        if missing_deps:
            print("  1. 运行: pip install --upgrade -r requirements.txt")
        if not nuitka_ok:
            print("  2. 重新安装Nuitka: pip uninstall nuitka && pip install nuitka")
        if missing_files:
            print("  3. 检查项目文件是否完整")
    else:
        print("[OK] 环境检查通过，可以尝试构建")
        print("\n建议的构建命令:")
        print("python -m nuitka --standalone --onefile --enable-plugin=pyqt6 --windows-disable-console --output-filename=GPose.exe --output-dir=build/simple --assume-yes-for-downloads --show-progress --show-memory run_gpose.py")
    
    print("=" * 50)
