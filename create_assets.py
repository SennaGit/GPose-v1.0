#!/usr/bin/env python3
"""
GPose 资源创建脚本
生成击剑主题的图标、启动画面和安装资源
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_fencing_icon():
    """创建击剑主题图标"""
    try:
        # 创建256x256的图标
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 击剑主题配色：银灰+蓝色
        silver = (192, 192, 192, 255)
        blue = (0, 123, 255, 255)
        dark_blue = (0, 86, 179, 255)
        white = (255, 255, 255, 255)
        
        # 绘制剑刃（垂直）
        sword_width = 8
        sword_length = 180
        sword_x = size // 2 - sword_width // 2
        sword_y = size // 2 - sword_length // 2
        
        # 剑刃主体
        draw.rectangle([sword_x, sword_y, sword_x + sword_width, sword_y + sword_length], 
                      fill=blue, outline=dark_blue, width=2)
        
        # 剑尖
        tip_size = 12
        draw.polygon([(sword_x - tip_size//2, sword_y), 
                     (sword_x + sword_width + tip_size//2, sword_y),
                     (sword_x + sword_width//2, sword_y - tip_size)], 
                    fill=blue, outline=dark_blue)
        
        # 护手
        guard_width = 30
        guard_height = 6
        guard_x = sword_x - (guard_width - sword_width) // 2
        guard_y = sword_y + sword_length - 20
        draw.rectangle([guard_x, guard_y, guard_x + guard_width, guard_y + guard_height], 
                      fill=silver, outline=dark_blue, width=2)
        
        # 剑柄
        handle_width = 12
        handle_height = 40
        handle_x = sword_x - (handle_width - sword_width) // 2
        handle_y = sword_y + sword_length - 20
        draw.rectangle([handle_x, handle_y, handle_x + handle_width, handle_y + handle_height], 
                      fill=silver, outline=dark_blue, width=2)
        
        # 添加"GPose"文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "GPose"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (size - text_width) // 2
        text_y = sword_y + sword_length + 20
        
        # 文字阴影
        draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 128), font=font)
        # 文字主体
        draw.text((text_x, text_y), text, fill=blue, font=font)
        
        # 保存为ICO格式
        icon_path = Path("icon.ico")
        img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        
        logger.info(f"击剑主题图标已创建: {icon_path}")
        return str(icon_path)
        
    except Exception as e:
        logger.error(f"创建图标失败: {e}")
        return None

def create_splash_screen():
    """创建启动画面"""
    try:
        # 创建800x600的启动画面
        width, height = 800, 600
        img = Image.new('RGB', (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # 击剑主题渐变背景
        for y in range(height):
            ratio = y / height
            r = int(240 + (0 - 240) * ratio)
            g = int(240 + (123 - 240) * ratio)
            b = int(240 + (255 - 240) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 添加剑刃装饰
        sword_color = (0, 123, 255, 255)
        for i in range(3):
            x = 100 + i * 200
            y = 200
            # 剑刃
            draw.rectangle([x, y, x + 4, y + 100], fill=sword_color)
            # 剑尖
            draw.polygon([(x - 6, y), (x + 10, y), (x + 2, y - 8)], fill=sword_color)
        
        # 主标题
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # 标题文字
        title = "GPose"
        subtitle = "Precision Fencing Analytics"
        
        # 计算文字位置
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 2 - 50
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 60
        
        # 绘制文字阴影
        draw.text((title_x + 3, title_y + 3), title, fill=(0, 0, 0, 128), font=title_font)
        draw.text((subtitle_x + 2, subtitle_y + 2), subtitle, fill=(0, 0, 0, 128), font=subtitle_font)
        
        # 绘制文字主体
        draw.text((title_x, title_y), title, fill=(0, 123, 255), font=title_font)
        draw.text((subtitle_x, subtitle_y), subtitle, fill=(0, 86, 179), font=subtitle_font)
        
        # 版本信息
        version = "v2.0"
        version_bbox = draw.textbbox((0, 0), version, font=subtitle_font)
        version_width = version_bbox[2] - version_bbox[0]
        version_x = (width - version_width) // 2
        version_y = subtitle_y + 40
        
        draw.text((version_x, version_y), version, fill=(128, 128, 128), font=subtitle_font)
        
        # 保存启动画面
        splash_path = Path("splash.png")
        img.save(splash_path, format='PNG')
        
        logger.info(f"启动画面已创建: {splash_path}")
        return str(splash_path)
        
    except Exception as e:
        logger.error(f"创建启动画面失败: {e}")
        return None

def create_license_file():
    """创建许可证文件"""
    license_text = """MIT License

Copyright (c) 2024 GPose Fencing Analyzer

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

GPose Fencing Analyzer - Precision Motion Analysis for Fencing Training
Developed for the fencing community to enhance training and performance analysis.
"""
    
    license_path = Path("license.txt")
    with open(license_path, 'w', encoding='utf-8') as f:
        f.write(license_text)
    
    logger.info(f"许可证文件已创建: {license_path}")
    return str(license_path)

def main():
    """主函数：创建所有资源"""
    logger.info("开始创建GPose击剑主题资源...")
    
    # 创建资源目录
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # 创建各种资源
    icon_path = create_fencing_icon()
    splash_path = create_splash_screen()
    license_path = create_license_file()
    
    # 移动资源到assets目录
    if icon_path:
        import shutil
        shutil.move(icon_path, assets_dir / "icon.ico")
        logger.info("图标已移动到assets目录")
    
    if splash_path:
        import shutil
        shutil.move(splash_path, assets_dir / "splash.png")
        logger.info("启动画面已移动到assets目录")
    
    if license_path:
        import shutil
        shutil.move(license_path, assets_dir / "license.txt")
        logger.info("许可证已移动到assets目录")
    
    logger.info("击剑主题资源创建完成！")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
