# -*- coding: utf-8 -*-
"""
Simple test to verify Chinese font display in dearpygui.
"""

import os
import dearpygui.dearpygui as dpg

def test_simple():
    dpg.create_context()
    
    # Try different fonts
    fonts_to_try = [
        r"C:\Windows\Fonts\simhei.ttf",  # SimHei (黑体)
        r"C:\Windows\Fonts\simsun.ttc",   # SimSun (宋体)
        r"C:\Windows\Fonts\msyh.ttc",     # Microsoft YaHei
    ]
    
    font = None
    font_path = None
    
    with dpg.font_registry():
        for path in fonts_to_try:
            if os.path.exists(path):
                try:
                    font = dpg.add_font(path, 20)
                    font_path = path
                    print(f"Loaded font: {path}")
                    break
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
                    continue
    
    if font is None:
        print("No font loaded!")
        return
    
    # Bind font
    dpg.bind_font(font)
    print(f"Font bound: {font_path}")
    
    # Create viewport
    dpg.create_viewport(title="Font Test", width=500, height=400)
    
    # Create window
    with dpg.window(label="Test", tag="main"):
        dpg.add_text("测试中文字体显示")
        dpg.add_text("服务器配置:")
        dpg.add_text("主机: 0.0.0.0")
        dpg.add_text("端口: 7125")
        dpg.add_text("状态: 运行中")
        dpg.add_button(label="启动服务器")
        dpg.add_button(label="停止服务器")
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main", True)
    
    print("Window created. Check if Chinese displays correctly.")
    print(f"Using font: {font_path}")
    
    try:
        dpg.start_dearpygui()
    except KeyboardInterrupt:
        pass
    finally:
        dpg.destroy_context()

if __name__ == "__main__":
    test_simple()

