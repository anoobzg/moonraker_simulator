# -*- coding: utf-8 -*-
"""
Test script to diagnose Chinese font display issues in DearPyGui.
"""

import os
import platform
import dearpygui.dearpygui as dpg

def test_chinese_font():
    """Test Chinese font loading."""
    system = platform.system()
    print(f"Operating System: {system}")
    
    # Find Chinese font
    font_path = None
    if system == "Windows":
        font_paths = [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
        ]
    else:
        print("This test is for Windows. Please check font paths for your OS.")
        return
    
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            print(f"Found font: {font_path}")
            break
    
    if not font_path:
        print("No Chinese font found!")
        return
    
    # Create GUI
    dpg.create_context()
    
    # Try to load font
    try:
        with dpg.font_registry():
            # Load font directly (dearpygui 2.1.1 doesn't support glyph_ranges)
            # Prefer TTF over TTC for better compatibility
            font_paths_priority = [
                r"C:\Windows\Fonts\simhei.ttf",  # TTF format, better compatibility
                r"C:\Windows\Fonts\simsun.ttc",
                r"C:\Windows\Fonts\msyh.ttc",
            ]
            
            loaded_font = None
            for test_path in font_paths_priority:
                if os.path.exists(test_path):
                    try:
                        font = dpg.add_font(test_path, 20)
                        dpg.bind_font(font)
                        loaded_font = font
                        print(f"Successfully loaded font: {test_path}")
                        break
                    except Exception as e:
                        print(f"Failed to load {test_path}: {e}")
                        continue
            
            if loaded_font is None:
                # Fallback to original font_path
                font = dpg.add_font(font_path, 20)
                dpg.bind_font(font)
                print(f"Loaded fallback font: {font_path}")
    except Exception as e:
        print(f"Failed to load font: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create viewport
    dpg.create_viewport(title="Chinese Font Test", width=400, height=300)
    
    # Create window with Chinese text
    with dpg.window(label="Font Test", tag="main_window"):
        dpg.add_text("Chinese Font Test / 中文字体测试", color=[255, 255, 255])
        dpg.add_separator()
        dpg.add_text("服务器配置:")
        dpg.add_text("主机: 0.0.0.0")
        dpg.add_text("端口: 7125")
        dpg.add_separator()
        dpg.add_text("状态: 运行中")
        dpg.add_text("WebSocket 连接数: 0")
        dpg.add_text("打印机状态: 就绪")
        dpg.add_separator()
        dpg.add_button(label="启动服务器")
        dpg.add_button(label="停止服务器")
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    
    print("GUI created. Check if Chinese characters display correctly.")
    print("Press Ctrl+C to exit.")
    
    try:
        dpg.start_dearpygui()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        dpg.destroy_context()

if __name__ == "__main__":
    test_chinese_font()

