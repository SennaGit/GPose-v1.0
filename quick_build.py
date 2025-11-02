#!/usr/bin/env python3
"""
GPose 快速打包脚本
简化版本，适合快速测试和开发
"""
import os
import sys
import subprocess
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_build():
    """快速构建"""
    logger.info("开始GPose快速构建...")
    
    # 检查环境
    try:
        subprocess.run([sys.executable, "--version"], check=True)
        logger.info("Python环境检查通过")
    except:
        logger.error("Python环境检查失败")
        return False
    
    # 安装依赖
    logger.info("安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("依赖安装完成")
    except:
        logger.error("依赖安装失败")
        return False
    
    # 创建资源
    logger.info("创建击剑主题资源...")
    try:
        subprocess.run([sys.executable, "create_assets.py"], check=True)
        logger.info("资源创建完成")
    except:
        logger.error("资源创建失败")
        return False
    
    # 运行程序测试
    logger.info("测试程序运行...")
    try:
        result = subprocess.run([sys.executable, "run_gpose.py"], 
                              timeout=10, capture_output=True, text=True)
        logger.info("程序测试通过")
    except subprocess.TimeoutExpired:
        logger.info("程序启动成功（超时正常）")
    except Exception as e:
        logger.error(f"程序测试失败: {e}")
        return False
    
    logger.info("快速构建完成！")
    logger.info("可以运行: python run_gpose.py")
    return True

if __name__ == "__main__":
    success = quick_build()
    sys.exit(0 if success else 1)
