#!/usr/bin/env python3
"""
GPose 模型优化脚本
将ONNX模型转换为OpenVINO IR格式，提升推理性能
适用于击剑动作分析的实时3D姿态估计
"""
import os
import sys
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_openvino():
    """设置OpenVINO环境"""
    try:
        import openvino as ov
        logger.info("OpenVINO 已安装，版本: %s", ov.__version__)
        return ov
    except ImportError:
        logger.error("OpenVINO 未安装，请运行: pip install openvino")
        return None

def convert_onnx_to_ir(onnx_path, output_dir, model_name):
    """将ONNX模型转换为OpenVINO IR格式"""
    try:
        ov = setup_openvino()
        if not ov:
            return False
            
        # 创建输出目录
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载ONNX模型
        logger.info(f"正在转换模型: {onnx_path}")
        core = ov.Core()
        
        # 从ONNX文件读取模型
        model = core.read_model(onnx_path)
        
        # 编译模型（CPU优化）
        compiled_model = core.compile_model(model, "CPU")
        
        # 保存为IR格式
        ir_path = output_dir / f"{model_name}.xml"
        ov.serialize(model, str(ir_path))
        
        logger.info(f"模型转换成功: {ir_path}")
        return True
        
    except Exception as e:
        logger.error(f"模型转换失败: {e}")
        return False

def create_placeholder_models():
    """创建占位模型（如果没有预训练模型）"""
    try:
        import numpy as np
        import onnx
        from onnx import helper, TensorProto
        
        # 创建简化的3D姿态提升模型
        # 输入: [batch_size, 2, 17, 2] (2D关键点)
        # 输出: [batch_size, 3, 17] (3D关键点)
        
        # 输入节点
        input_tensor = helper.make_tensor_value_info(
            'input_2d', TensorProto.FLOAT, [1, 2, 17, 2]
        )
        
        # 输出节点
        output_tensor = helper.make_tensor_value_info(
            'output_3d', TensorProto.FLOAT, [1, 3, 17]
        )
        
        # 创建简单的线性变换节点（Z=0 for 3D lift）
        # 这里使用简化的实现
        identity_node = helper.make_node(
            'Identity',
            inputs=['input_2d'],
            outputs=['output_3d']
        )
        
        # 创建图
        graph = helper.make_graph(
            [identity_node],
            'pose_3d_lift',
            [input_tensor],
            [output_tensor]
        )
        
        # 创建模型
        model = helper.make_model(graph)
        model.opset_imports[0].version = 11
        
        # 保存模型
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        onnx_path = models_dir / "pose_3d_lift.onnx"
        onnx.save(model, str(onnx_path))
        
        logger.info(f"占位模型已创建: {onnx_path}")
        return str(onnx_path)
        
    except Exception as e:
        logger.error(f"创建占位模型失败: {e}")
        return None

def main():
    """主函数：执行模型优化"""
    logger.info("开始GPose模型优化...")
    
    # 创建模型目录
    models_dir = Path("models")
    ir_dir = models_dir / "ir"
    ir_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查现有ONNX模型
    onnx_models = list(models_dir.glob("*.onnx"))
    
    if not onnx_models:
        logger.info("未找到ONNX模型，创建占位模型...")
        placeholder_path = create_placeholder_models()
        if placeholder_path:
            onnx_models = [Path(placeholder_path)]
    
    # 转换所有ONNX模型
    success_count = 0
    for onnx_path in onnx_models:
        model_name = onnx_path.stem
        if convert_onnx_to_ir(onnx_path, ir_dir, model_name):
            success_count += 1
    
    logger.info(f"模型优化完成！成功转换 {success_count}/{len(onnx_models)} 个模型")
    logger.info("Models optimized for CPU inference")
    
    # 创建模型索引文件
    create_model_index(ir_dir)
    
    return success_count > 0

def create_model_index(ir_dir):
    """创建模型索引文件"""
    try:
        index_data = {
            "models": {
                "pose_3d_lift": {
                    "path": "pose_3d_lift.xml",
                    "description": "3D姿态提升模型",
                    "input_shape": [1, 2, 17, 2],
                    "output_shape": [1, 3, 17]
                }
            },
            "version": "2.0",
            "optimized_for": "CPU",
            "fencing_analysis": True
        }
        
        import json
        index_path = ir_dir / "model_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"模型索引已创建: {index_path}")
        
    except Exception as e:
        logger.error(f"创建模型索引失败: {e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
