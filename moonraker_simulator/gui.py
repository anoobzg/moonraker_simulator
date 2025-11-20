# -*- coding: utf-8 -*-
"""
Main GUI interface for Moonraker Simulator using DearPyGui.
"""

import logging
import threading
import time
from typing import Optional

import dearpygui.dearpygui as dpg
from moonraker_simulator.gui import (
    load_chinese_font,
    DeviceManager,
    UILayout,
    apply_light_theme
)

logger = logging.getLogger(__name__)


class MoonrakerSimulatorGUI:
    """Main GUI interface for Moonraker Simulator."""
    
    def __init__(self, start_port: int = 7125):
        """
        Initialize GUI.
        
        Args:
            start_port: Starting port for devices
        """
        self.start_port = start_port
        self.device_manager = DeviceManager(start_port=start_port)
        self.ui_layout: Optional[UILayout] = None
        self.chinese_font: Optional[int] = None
        self.update_interval = 1.0  # Update every 1 second
        self.update_thread: Optional[threading.Thread] = None
        self.is_running = False
    
    def _load_fonts(self):
        """Load Chinese fonts."""
        with dpg.font_registry():
            self.chinese_font = load_chinese_font()
        
        # Bind font if loaded
        if self.chinese_font is not None:
            dpg.bind_font(self.chinese_font)
            logger.info("Chinese font loaded and bound")
    
    def create_gui(self):
        """Create and setup the GUI window."""
        dpg.create_context()
        
        # Apply Light theme
        apply_light_theme()
        logger.info("Light theme applied")
        
        # Load fonts first
        self._load_fonts()
        
        # Create UI layout
        self.ui_layout = UILayout(
            device_manager=self.device_manager,
            on_add_device=self._on_add_device,
            on_batch_add=self._on_batch_add
        )
        
        # Create layout
        self.ui_layout.create_layout(width=1200, height=800)
        
        # Ensure font is bound
        if self.chinese_font is not None:
            dpg.bind_font(self.chinese_font)
        
        # Start update thread
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _on_add_device(self):
        """Handle add device button click."""
        self.ui_layout.add_device()
    
    def _on_batch_add(self, count: int):
        """Handle batch add button click."""
        self.ui_layout.batch_add_devices(count)
    
    def _update_loop(self):
        """Background thread to periodically update device info."""
        while self.is_running:
            time.sleep(self.update_interval)
            try:
                if self.ui_layout:
                    self.ui_layout.update_all_devices()
            except Exception as e:
                logger.error(f"Error updating device info: {e}")
    
    def run(self):
        """Run the GUI main loop."""
        self.create_gui()
        
        try:
            dpg.start_dearpygui()
        except KeyboardInterrupt:
            logger.info("GUI interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_running = False
        
        if self.update_thread and self.update_thread.is_alive():
            # Wait for thread to finish (with timeout)
            self.update_thread.join(timeout=2.0)
        
        if self.ui_layout:
            self.ui_layout.cleanup()
        
        dpg.destroy_context()


def main(start_port: int = 7125):
    """
    Main entry point for GUI mode.
    
    Args:
        start_port: Starting port for devices
    """
    gui = MoonrakerSimulatorGUI(start_port=start_port)
    gui.run()


if __name__ == "__main__":
    main()
