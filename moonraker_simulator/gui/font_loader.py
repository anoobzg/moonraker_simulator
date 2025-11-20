# -*- coding: utf-8 -*-
"""
Font loading utilities for Chinese character support.
"""

import logging
import os
import platform
from typing import Optional

import dearpygui.dearpygui as dpg

logger = logging.getLogger(__name__)


def load_chinese_font() -> Optional[int]:
    """
    Load a Chinese font if available with proper character range hints.
    
    Returns:
        Font ID if successful, None otherwise
    """
    system = platform.system()
    font_path = None
    
    # Try to find a Chinese font based on OS
    # Prefer TTF files over TTC for better compatibility
    if system == "Windows":
        # Windows font paths - prioritize TTF files
        font_paths = [
            # SimHei (黑体) - TTF format, better compatibility
            r"C:\Windows\Fonts\simhei.ttf",
            # SimSun (宋体) - TTC but widely supported
            r"C:\Windows\Fonts\simsun.ttc",
            # Microsoft YaHei (微软雅黑) - TTC format
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\msyhbd.ttc",
            # Microsoft YaHei UI - TTF format
            r"C:\Windows\Fonts\msyh.ttf",
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            # PingFang SC (苹果系统默认中文字体)
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
    else:  # Linux
        font_paths = [
            # Common Linux Chinese fonts
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    
    # Try to find an available font
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            logger.info(f"Found Chinese font: {font_path}")
            break
    
    if font_path:
        try:
            # Use a slightly larger size for better readability
            font_size = 18
            # Load font with Chinese character range hints using context manager
            # This ensures proper rendering of Chinese characters
            # The font range hints must be added within the font context
            with dpg.font(font_path, font_size) as default_font:
                # Add font range hints for proper Chinese character support
                # This is the key to fixing Chinese character display issues
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            
            logger.info(f"Successfully loaded Chinese font: {font_path} (size={font_size}) with character range hints")
            return default_font
        except Exception as e:
            logger.warning(f"Failed to load font {font_path}: {e}")
            import traceback
            logger.warning(traceback.format_exc())
    else:
        logger.warning("No Chinese font file found in system")
        # Log available font paths for debugging
        if system == "Windows":
            fonts_dir = r"C:\Windows\Fonts"
            if os.path.exists(fonts_dir):
                logger.info(f"Fonts directory exists: {fonts_dir}")
    
    logger.warning("Chinese characters may display incorrectly")
    return None

