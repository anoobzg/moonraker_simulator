# -*- coding: utf-8 -*-
"""
GUI interface for Moonraker Simulator using DearPyGui.
"""

import logging
import os
import platform
import threading
import time
from typing import Optional

import dearpygui.dearpygui as dpg
from moonraker_simulator.server import MoonrakerSimulator

logger = logging.getLogger(__name__)


class MoonrakerSimulatorGUI:
    """GUI interface for Moonraker Simulator."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 7125):
        self.host = host
        self.port = port
        self.simulator: Optional[MoonrakerSimulator] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.update_interval = 1.0  # Update every 1 second
        self.update_thread: Optional[threading.Thread] = None
        self.chinese_font = None
        
    def start_server(self):
        """Start the simulator server in a background thread."""
        if self.is_running:
            logger.warning("Server is already running")
            return
        
        try:
            self.simulator = MoonrakerSimulator(host=self.host, port=self.port)
            self.simulator.start(run_in_thread=True)
            self.is_running = True
            logger.info(f"Server started on {self.host}:{self.port}")
            self.update_status("运行中", f"服务器运行在 http://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.update_status("错误", f"启动失败: {str(e)}")
            self.is_running = False
    
    def stop_server(self):
        """Stop the simulator server."""
        if not self.is_running or not self.simulator:
            return
        
        try:
            self.simulator.stop()
            self.is_running = False
            logger.info("Server stopped")
            self.update_status("已停止", "服务器已停止")
        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            self.update_status("错误", f"停止失败: {str(e)}")
    
    def update_status(self, status: str, message: str):
        """Update status display in GUI."""
        if dpg.does_item_exist("status_text"):
            dpg.set_value("status_text", f"状态: {status}\n{message}")
    
    def update_server_info(self):
        """Update server information display."""
        if not self.simulator or not self.is_running:
            return
        
        try:
            # Update WebSocket client count
            ws_count = len(self.simulator.websocket_clients)
            if dpg.does_item_exist("ws_count_text"):
                dpg.set_value("ws_count_text", f"WebSocket 连接数: {ws_count}")
            
            # Update printer state
            state = self.simulator.printer_state
            if dpg.does_item_exist("printer_state_text"):
                dpg.set_value("printer_state_text", f"打印机状态: {state['state']}")
            
            # Update temperature info
            temp = state['temperature']
            if dpg.does_item_exist("temp_text"):
                extruder_temp = temp['extruder']['actual']
                bed_temp = temp['heater_bed']['actual']
                dpg.set_value("temp_text", 
                             f"挤出机温度: {extruder_temp:.1f}°C\n"
                             f"热床温度: {bed_temp:.1f}°C")
        except Exception as e:
            logger.error(f"Failed to update server info: {e}")
    
    def _load_chinese_font(self):
        """Load a Chinese font if available with proper character range hints."""
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
                
                self.chinese_font = default_font
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
    
    def create_gui(self):
        """Create and setup the GUI window."""
        dpg.create_context()
        
        # Load Chinese font registry FIRST, before any UI elements
        with dpg.font_registry():
            # Load Chinese font if available
            self._load_chinese_font()
        
        # Bind font BEFORE creating viewport and UI elements
        if self.chinese_font is not None:
            dpg.bind_font(self.chinese_font)
            logger.info("Font bound before creating UI")
        
        dpg.create_viewport(title="Moonraker Simulator", width=600, height=500)
        
        with dpg.window(label="Moonraker Simulator", tag="main_window"):
            dpg.add_text("Moonraker Simulator", color=[100, 200, 255])
            dpg.add_separator()
            
            # Server configuration
            with dpg.group(horizontal=True):
                dpg.add_text("服务器配置:")
                dpg.add_text(f"主机: {self.host}")
                dpg.add_text(f"端口: {self.port}")
            
            dpg.add_separator()
            
            # Status display
            dpg.add_text("状态: 未启动", tag="status_text", color=[200, 200, 200])
            
            dpg.add_separator()
            
            # Server info display
            with dpg.group():
                dpg.add_text("服务器信息:", color=[150, 200, 255])
                dpg.add_text("WebSocket 连接数: 0", tag="ws_count_text")
                dpg.add_text("打印机状态: 未知", tag="printer_state_text")
                dpg.add_text("", tag="temp_text")
            
            dpg.add_separator()
            
            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="启动服务器", callback=self.on_start_clicked, tag="start_button")
                dpg.add_button(label="停止服务器", callback=self.on_stop_clicked, tag="stop_button", enabled=False)
            
            dpg.add_separator()
            
            # Info text
            dpg.add_text("提示: 服务器启动后，可以通过以下地址访问:", color=[150, 150, 150])
            dpg.add_text(f"http://localhost:{self.port}", color=[100, 200, 100])
        
        dpg.setup_dearpygui()
        
        # Ensure font is bound (should already be bound, but double-check)
        if self.chinese_font is not None:
            dpg.bind_font(self.chinese_font)
            logger.info("Chinese font bound to GUI (confirmed)")
        
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        
        # Force font binding one more time after viewport is shown
        # Sometimes dearpygui needs this to properly apply fonts
        if self.chinese_font is not None:
            dpg.bind_font(self.chinese_font)
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self):
        """Background thread to periodically update server info."""
        while True:
            time.sleep(self.update_interval)
            if self.is_running:
                try:
                    self.update_server_info()
                except Exception as e:
                    logger.error(f"Error updating server info: {e}")
    
    def on_start_clicked(self):
        """Handle start button click."""
        self.start_server()
        if dpg.does_item_exist("start_button"):
            dpg.configure_item("start_button", enabled=False)
        if dpg.does_item_exist("stop_button"):
            dpg.configure_item("stop_button", enabled=True)
    
    def on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_server()
        if dpg.does_item_exist("start_button"):
            dpg.configure_item("start_button", enabled=True)
        if dpg.does_item_exist("stop_button"):
            dpg.configure_item("stop_button", enabled=False)
    
    def run(self):
        """Run the GUI main loop."""
        self.create_gui()
        
        # Auto-start server
        self.start_server()
        if dpg.does_item_exist("start_button"):
            dpg.configure_item("start_button", enabled=False)
        if dpg.does_item_exist("stop_button"):
            dpg.configure_item("stop_button", enabled=True)
        
        try:
            dpg.start_dearpygui()
        except KeyboardInterrupt:
            logger.info("GUI interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_server()
        dpg.destroy_context()


def main(host: str = "0.0.0.0", port: int = 7125):
    """Main entry point for GUI mode."""
    gui = MoonrakerSimulatorGUI(host=host, port=port)
    gui.run()


if __name__ == "__main__":
    main()

