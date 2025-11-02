# -*- coding: utf-8 -*-
"""
GPose最小化构建脚本
避免复杂依赖，只打包核心功能
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# 设置控制台编码
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def build_minimal():
    """构建最小化版本"""
    print("开始构建GPose最小化版本...")
    
    # 清理之前的构建
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # 创建简化的spec文件
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_gpose.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'cv2',
        'numpy',
        'scipy',
        'loguru',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'torchvision', 
        'torchaudio',
        'onnx',
        'onnxruntime',
        'jax',
        'sympy',
        'networkx',
        'matplotlib',
        'mediapipe',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GPose_Minimal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
'''
    
    with open('GPose_Minimal.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # 使用spec文件构建
    cmd = [
        'pyinstaller',
        '--clean',
        'GPose_Minimal.spec'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            print("构建成功!")
            print(f"可执行文件位置: dist/GPose_Minimal.exe")
        else:
            print("构建失败:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("构建超时")
    except Exception as e:
        print(f"构建出错: {e}")

if __name__ == "__main__":
    build_minimal()
