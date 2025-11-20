# -*- coding: utf-8 -*-
"""
UI layout management for the main window.
"""

import logging
from typing import Optional, Callable
import dearpygui.dearpygui as dpg
from .device_manager import DeviceManager
from .device_widget import DeviceWidget

logger = logging.getLogger(__name__)


class UILayout:
    """Manages the main UI layout."""
    
    def __init__(self, device_manager: DeviceManager,
                 on_add_device: Optional[Callable[[], None]] = None,
                 on_batch_add: Optional[Callable[[int], None]] = None):
        """
        Initialize UI layout.
        
        Args:
            device_manager: DeviceManager instance
            on_add_device: Callback for add device button
            on_batch_add: Callback for batch add button
        """
        self.device_manager = device_manager
        self.on_add_device = on_add_device
        self.on_batch_add = on_batch_add
        
        # UI tags
        self.main_window_tag = "main_window"
        self.button_bar_tag = "button_bar"
        self.device_list_tag = "device_list"
        
        # Device widgets
        self.device_widgets: dict[str, DeviceWidget] = {}
    
    def create_layout(self, width: int = 1200, height: int = 800):
        """
        Create the main UI layout.
        
        Args:
            width: Window width
            height: Window height
        """
        # Create viewport
        dpg.create_viewport(title="Moonraker Simulator", width=width, height=height)
        
        # Create main window
        with dpg.window(label="Moonraker Simulator", tag=self.main_window_tag):
            # Top button bar (height 50)
            self._create_button_bar()
            
            # Device list area (remaining space)
            self._create_device_list()
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window_tag, True)
    
    def _create_button_bar(self):
        """Create the top button bar (height 50)."""
        # Use child_window to control height precisely
        with dpg.child_window(
            tag=self.button_bar_tag,
            height=50,
            border=True,
            autosize_x=True
        ):
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="添加设备",
                    callback=self._on_add_device_clicked,
                    tag="add_device_btn",
                    height=40
                )
                dpg.add_button(
                    label="批量添加设备",
                    callback=self._on_batch_add_clicked,
                    tag="batch_add_btn",
                    height=40
                )
    
    def _create_device_list(self):
        """Create the device list area."""
        # Create scrollable area for device list
        with dpg.child_window(
            tag=self.device_list_tag,
            height=-1,  # Fill remaining space
            border=False,
            autosize_x=True
        ):
            dpg.add_text("暂无设备，点击上方按钮添加设备", color=[150, 150, 150], tag="empty_list_text")
    
    def _on_add_device_clicked(self):
        """Handle add device button click."""
        if self.on_add_device:
            self.on_add_device()
        else:
            # Default behavior
            self.add_device()
    
    def _on_batch_add_clicked(self):
        """Handle batch add button click."""
        if self.on_batch_add:
            # Show input dialog for count
            self._show_batch_add_dialog()
        else:
            # Default: add 3 devices
            self.batch_add_devices(3)
    
    def _show_batch_add_dialog(self):
        """Show dialog for batch add count."""
        # Simple input using DearPyGui modal
        with dpg.window(
            label="批量添加设备",
            modal=True,
            tag="batch_add_dialog",
            width=300,
            height=150
        ):
            dpg.add_text("请输入要添加的设备数量:")
            count_input = dpg.add_input_int(
                tag="batch_count_input",
                default_value=3,
                min_value=1,
                max_value=10,
                width=200
            )
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="确定",
                    callback=lambda: self._confirm_batch_add()
                )
                dpg.add_button(
                    label="取消",
                    callback=lambda: dpg.delete_item("batch_add_dialog")
                )
    
    def _confirm_batch_add(self):
        """Confirm batch add."""
        if dpg.does_item_exist("batch_count_input"):
            count = dpg.get_value("batch_count_input")
            dpg.delete_item("batch_add_dialog")
            
            if self.on_batch_add:
                self.on_batch_add(count)
            else:
                self.batch_add_devices(count)
    
    def add_device(self, name: Optional[str] = None) -> Optional[str]:
        """
        Add a device to the UI.
        
        Args:
            name: Device name (optional)
            
        Returns:
            Device ID if successful
        """
        try:
            device_id = self.device_manager.add_device(name=name)
            device_name = self.device_manager.get_device_name(device_id)
            simulator = self.device_manager.get_device(device_id)
            
            if simulator:
                # Hide empty list text
                if dpg.does_item_exist("empty_list_text"):
                    dpg.hide_item("empty_list_text")
                
                # Create device widget
                widget = DeviceWidget(
                    device_id=device_id,
                    device_name=device_name,
                    simulator=simulator,
                    on_remove=self.remove_device
                )
                widget.create_widget(parent=self.device_list_tag)
                
                self.device_widgets[device_id] = widget
                
                logger.info(f"Added device widget for {device_id}")
                return device_id
        except Exception as e:
            logger.error(f"Failed to add device to UI: {e}")
            return None
    
    def batch_add_devices(self, count: int):
        """
        Add multiple devices at once.
        
        Args:
            count: Number of devices to add
        """
        for i in range(count):
            name = f"设备 {i + 1}"
            self.add_device(name=name)
    
    def remove_device(self, device_id: str):
        """
        Remove a device from the UI.
        
        Args:
            device_id: Device ID to remove
        """
        try:
            # Remove widget
            if device_id in self.device_widgets:
                widget = self.device_widgets[device_id]
                widget.destroy()
                del self.device_widgets[device_id]
            
            # Remove from device manager
            self.device_manager.remove_device(device_id)
            
            # Show empty list text if no devices
            if len(self.device_widgets) == 0:
                if dpg.does_item_exist("empty_list_text"):
                    dpg.show_item("empty_list_text")
            
            logger.info(f"Removed device {device_id}")
        except Exception as e:
            logger.error(f"Failed to remove device {device_id}: {e}")
    
    def update_all_devices(self):
        """Update all device widgets."""
        for widget in self.device_widgets.values():
            widget.update()
    
    def cleanup(self):
        """Cleanup UI resources."""
        # Cleanup all widgets
        for widget in self.device_widgets.values():
            widget.destroy()
        self.device_widgets.clear()
        
        # Cleanup device manager
        self.device_manager.cleanup_all()

