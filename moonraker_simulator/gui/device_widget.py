# -*- coding: utf-8 -*-
"""
UI widget for displaying and controlling a single device.
"""

import logging
from typing import Optional, Callable
import dearpygui.dearpygui as dpg
from moonraker_simulator.server import MoonrakerSimulator

logger = logging.getLogger(__name__)


class DeviceWidget:
    """UI widget for a single device."""
    
    def __init__(self, device_id: str, device_name: str, simulator: MoonrakerSimulator,
                 on_remove: Optional[Callable[[str], None]] = None):
        """
        Initialize device widget.
        
        Args:
            device_id: Unique device identifier
            device_name: Display name for device
            simulator: MoonrakerSimulator instance
            on_remove: Callback when remove button is clicked
        """
        self.device_id = device_id
        self.device_name = device_name
        self.simulator = simulator
        self.on_remove = on_remove
        
        # UI tags
        self.container_tag = f"device_{device_id}"
        self.name_tag = f"device_name_{device_id}"
        self.state_tag = f"device_state_{device_id}"
        self.temp_tag = f"device_temp_{device_id}"
        self.speed_tag = f"device_speed_{device_id}"
        self.task_tag = f"device_task_{device_id}"
        self.progress_tag = f"device_progress_{device_id}"
        self.progress_bar_tag = f"device_progress_bar_{device_id}"
    
    def create_widget(self, parent: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None):
        """
        Create the device widget UI.
        
        Args:
            parent: Parent window/group tag
            width: Fixed width for grid layout (optional)
            height: Fixed height for grid layout (optional)
        """
        # Create device container (child window or group)
        with dpg.child_window(
            tag=self.container_tag,
            parent=parent,
            width=width if width else -1,
            height=height if height else 200,
            border=True,
            autosize_x=width is None
        ):
            # Device header with name and remove button
            with dpg.group(horizontal=True):
                dpg.add_text(self.device_name, tag=self.name_tag, color=[100, 200, 255])
                if self.on_remove:
                    dpg.add_button(
                        label="移除设备",
                        callback=lambda: self.on_remove(self.device_id),
                        tag=f"remove_btn_{self.device_id}"
                    )
            
            dpg.add_separator()
            
            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="开始",
                    callback=lambda: self._on_start(),
                    tag=f"start_btn_{self.device_id}"
                )
                dpg.add_button(
                    label="暂停",
                    callback=lambda: self._on_pause(),
                    tag=f"pause_btn_{self.device_id}"
                )
                dpg.add_button(
                    label="停止",
                    callback=lambda: self._on_stop(),
                    tag=f"stop_btn_{self.device_id}"
                )
            
            dpg.add_separator()
            
            # Status information
            with dpg.group():
                # Device state
                dpg.add_text("状态: 未知", tag=self.state_tag)
                
                # Temperature info
                dpg.add_text("温度: --", tag=self.temp_tag)
                
                # Speed info
                dpg.add_text("速度: --", tag=self.speed_tag)
            
            dpg.add_separator()
            
            # Print task and progress
            with dpg.group():
                dpg.add_text("打印任务: 无", tag=self.task_tag)
                dpg.add_progress_bar(
                    tag=self.progress_bar_tag,
                    default_value=0.0,
                    overlay=self.progress_tag,
                    width=-1
                )
    
    def _on_start(self):
        """Handle start button click."""
        try:
            if self.simulator:
                self.simulator.printer_state['state'] = 'printing'
                self.simulator.printer_state['state_message'] = '正在打印'
                # Set default print file if not set
                if 'print_file' not in self.simulator.printer_state:
                    self.simulator.printer_state['print_file'] = '示例任务.gcode'
                # Initialize progress
                if 'print_progress' not in self.simulator.printer_state:
                    self.simulator.printer_state['print_progress'] = 0.0
                logger.info(f"Started device {self.device_id}")
        except Exception as e:
            logger.error(f"Failed to start device {self.device_id}: {e}")
    
    def _on_pause(self):
        """Handle pause button click."""
        try:
            if self.simulator:
                self.simulator.printer_state['state'] = 'paused'
                self.simulator.printer_state['state_message'] = '打印已暂停'
                logger.info(f"Paused device {self.device_id}")
        except Exception as e:
            logger.error(f"Failed to pause device {self.device_id}: {e}")
    
    def _on_stop(self):
        """Handle stop button click."""
        try:
            if self.simulator:
                self.simulator.printer_state['state'] = 'standby'
                self.simulator.printer_state['state_message'] = '打印机待机'
                # Reset progress when stopped
                self.simulator.printer_state['print_progress'] = 0.0
                if 'print_file' in self.simulator.printer_state:
                    del self.simulator.printer_state['print_file']
                logger.info(f"Stopped device {self.device_id}")
        except Exception as e:
            logger.error(f"Failed to stop device {self.device_id}: {e}")
    
    def update(self):
        """Update device widget with current state."""
        if not self.simulator:
            return
        
        try:
            state = self.simulator.printer_state
            
            # Update state
            if dpg.does_item_exist(self.state_tag):
                dpg.set_value(self.state_tag, f"状态: {state.get('state', '未知')}")
            
            # Update temperature
            if dpg.does_item_exist(self.temp_tag):
                temp = state.get('temperature', {})
                extruder_temp = temp.get('extruder', {}).get('actual', 0)
                bed_temp = temp.get('heater_bed', {}).get('actual', 0)
                dpg.set_value(
                    self.temp_tag,
                    f"温度: 挤出机 {extruder_temp:.1f}°C | 热床 {bed_temp:.1f}°C"
                )
            
            # Update speed (simulate from print stats)
            if dpg.does_item_exist(self.speed_tag):
                # Simulate speed based on state
                print_state = state.get('state', 'standby')
                if print_state == 'printing':
                    speed = 100  # Default printing speed
                elif print_state == 'paused':
                    speed = 0
                else:
                    speed = 0
                dpg.set_value(self.speed_tag, f"速度: {speed}%")
            
            # Update print task and progress
            if dpg.does_item_exist(self.task_tag):
                print_state = state.get('state', 'standby')
                if print_state == 'printing' or print_state == 'paused':
                    task_name = state.get('print_file', '未知任务')
                    dpg.set_value(self.task_tag, f"打印任务: {task_name}")
                else:
                    dpg.set_value(self.task_tag, "打印任务: 无")
            
            # Update progress bar
            if dpg.does_item_exist(self.progress_bar_tag):
                print_state = state.get('state', 'standby')
                if print_state == 'printing':
                    # Simulate progress increment
                    progress = state.get('print_progress', 0.0)
                    # Increment progress if printing (simulate)
                    if progress < 100:
                        progress = min(100, progress + 0.1)  # Increment by 0.1% per update
                        state['print_progress'] = progress
                    dpg.set_value(self.progress_bar_tag, progress / 100.0)
                    if dpg.does_item_exist(self.progress_tag):
                        dpg.set_value(self.progress_tag, f"{progress:.1f}%")
                elif print_state == 'paused':
                    # Keep current progress when paused
                    progress = state.get('print_progress', 0.0)
                    dpg.set_value(self.progress_bar_tag, progress / 100.0)
                    if dpg.does_item_exist(self.progress_tag):
                        dpg.set_value(self.progress_tag, f"{progress:.1f}% (已暂停)")
                else:
                    # Reset progress when stopped
                    dpg.set_value(self.progress_bar_tag, 0.0)
                    if dpg.does_item_exist(self.progress_tag):
                        dpg.set_value(self.progress_tag, "0.0%")
        
        except Exception as e:
            logger.error(f"Failed to update device widget {self.device_id}: {e}")
    
    def destroy(self):
        """Destroy the widget."""
        if dpg.does_item_exist(self.container_tag):
            dpg.delete_item(self.container_tag)

