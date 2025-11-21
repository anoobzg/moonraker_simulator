# -*- coding: utf-8 -*-
"""
Font loading utilities for Chinese character support in tkinter.
"""

import logging
import os
import platform
from typing import Optional
import tkinter as tk
from tkinter import font

logger = logging.getLogger(__name__)


def load_chinese_font(root: Optional[tk.Tk] = None, size: int = 10) -> Optional[font.Font]:
    """
    Load a Chinese font if available for tkinter.
    
    Args:
        root: Tk root window (optional)
        size: Font size (default: 10)
    
    Returns:
        Font object if successful, None otherwise
    """
    system = platform.system()
    font_family = None
    
    # Try to find a Chinese font based on OS
    if system == "Windows":
        # Windows font families - try common Chinese fonts
        font_families = [
            "Microsoft YaHei UI",
            "Microsoft YaHei",
            "SimHei",
            "SimSun",
            "KaiTi",
        ]
    elif system == "Darwin":  # macOS
        font_families = [
            "PingFang SC",
            "STHeiti",
            "STSong",
            "Arial Unicode MS",
        ]
    else:  # Linux
        font_families = [
            "WenQuanYi Micro Hei",
            "WenQuanYi Zen Hei",
            "Noto Sans CJK SC",
            "DejaVu Sans",
        ]
    
    # Check which fonts are available
    # font.families() may require a Tk instance depending on Python version
    try:
        # Try without root first (some versions support this)
        available_fonts = set(font.families())
    except TypeError:
        # If that fails, create a temporary root window
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the window
        try:
            if root is None:
                available_fonts = set(font.families(root=temp_root))
            else:
                available_fonts = set(font.families(root=root))
        finally:
            temp_root.destroy()
    except Exception:
        # Fallback: just use the font families list without checking
        available_fonts = set(font_families)
    
    # Try to find an available Chinese font
    for family in font_families:
        if family in available_fonts:
            font_family = family
            logger.info(f"Found Chinese font: {font_family}")
            break
    
    if font_family:
        try:
            chinese_font = font.Font(family=font_family, size=size)
            logger.info(f"Successfully loaded Chinese font: {font_family} (size={size})")
            return chinese_font
        except Exception as e:
            logger.warning(f"Failed to load font {font_family}: {e}")
            import traceback
            logger.warning(traceback.format_exc())
    else:
        logger.warning("No Chinese font found in system")
        # Log available fonts for debugging (first 20)
        available_list = list(available_fonts)[:20]
        logger.debug(f"Available fonts (first 20): {available_list}")
    
    # Return default font if Chinese font not found
    logger.warning("Using default font - Chinese characters may display incorrectly")
    return None


def apply_chinese_font_to_widget(widget: tk.Widget, font_obj: Optional[font.Font] = None, size: int = 10):
    """
    Apply Chinese font to a widget.
    
    Args:
        widget: Tkinter widget to apply font to
        font_obj: Font object (if None, will try to load one)
        size: Font size (default: 10)
    """
    if font_obj is None:
        font_obj = load_chinese_font(widget.winfo_toplevel(), size=size)
    
    if font_obj:
        try:
            widget.config(font=font_obj)
        except Exception as e:
            logger.warning(f"Failed to apply font to widget: {e}")
