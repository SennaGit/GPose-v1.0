#!/usr/bin/env python3
"""
GPose 应用程序启动脚本
解决模块导入问题，确保从项目根目录启动
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 在导入其他模块之前设置日志配置
try:
    from utils.log_config import setup_clean_logging
    setup_clean_logging()
except ImportError:
    # 如果日志配置模块不可用，使用基本的环境变量设置
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['GLOG_minloglevel'] = '2'
    os.environ['FFREPORT'] = 'level=error'

# 导入并运行主程序
if __name__ == "__main__":
    from gui.main_window import main
    main()
