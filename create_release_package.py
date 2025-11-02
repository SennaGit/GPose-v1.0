# -*- coding: utf-8 -*-
"""
创建GPose发布包
"""
import os
import shutil
import zipfile
from pathlib import Path
import time

def create_release_package():
    """创建发布包"""
    print("开始创建GPose发布包...")
    
    # 创建发布目录
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_path = Path("dist/GPose_Minimal.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "GPose.exe")
        print(f"复制可执行文件: {exe_path} -> {release_dir / 'GPose.exe'}")
    
    # 复制资源文件
    resources = ["resources", "config"]
    for resource in resources:
        if Path(resource).exists():
            shutil.copytree(resource, release_dir / resource)
            print(f"复制资源目录: {resource}")
    
    # 创建README文件
    readme_content = """# GPose - AI击剑动作分析软件

## 系统要求
- Windows 10/11 (64位)
- 至少4GB内存
- 支持OpenGL的显卡

## 安装说明
1. 解压所有文件到任意目录
2. 双击GPose.exe启动程序
3. 首次运行可能需要较长时间加载

## 使用说明
1. 点击"打开视频"选择要分析的视频文件
2. 选择分析模式：视觉模式/CSI模式/混合模式
3. 点击播放按钮开始分析
4. 在人物选择器中切换目标人物
5. 调整运动学参数滑块
6. 点击"导出结果"保存分析数据

## 功能特性
- 多人检测与选择
- 实时姿态分析
- 多种分析模式
- 数据导出(CSV/JSON)
- 视频播放控制
- 运动学参数调节

## 技术支持
如遇问题，请检查：
1. 系统内存是否充足
2. 显卡驱动是否最新
3. 视频文件格式是否支持

版本: 1.0.0
构建时间: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """
"""
    
    with open(release_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 创建ZIP包
    zip_path = f"GPose_v1.0_{int(time.time())}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(release_dir)
                zipf.write(file_path, arc_path)
    
    print(f"发布包创建完成: {zip_path}")
    print(f"文件大小: {Path(zip_path).stat().st_size / 1024 / 1024:.1f} MB")
    
    return zip_path

if __name__ == "__main__":
    create_release_package()
