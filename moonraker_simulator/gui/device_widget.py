# -*- coding: utf-8 -*-
"""
UI widget for displaying and controlling a single device using tkinter.
"""

import logging
from typing import Optional, Callable
import tkinter as tk
from tkinter import ttk
from moonraker_simulator.server import MoonrakerSimulator

logger = logging.getLogger(__name__)


class DeviceWidget:
    """UI widget for a single device."""
    
    def __init__(self, device_id: str, device_name: str, simulator: MoonrakerSimulator,
                 on_remove: Optional[Callable[[str], None]] = None,
                 parent: Optional[tk.Widget] = None):
        """
        Initialize device widget.
        
        Args:
            device_id: Unique device identifier
            device_name: Display name for device
            simulator: MoonrakerSimulator instance
            on_remove: Callback when remove button is clicked
            parent: Parent widget (Frame)
        """
        self.device_id = device_id
        self.device_name = device_name
        self.simulator = simulator
        self.on_remove = on_remove
        self.parent = parent
        
        # UI widgets
        self.frame: Optional[ttk.LabelFrame] = None
        self.name_label: Optional[ttk.Label] = None
        self.remove_btn: Optional[ttk.Button] = None
        self.start_btn: Optional[ttk.Button] = None
        self.pause_btn: Optional[ttk.Button] = None
        self.stop_btn: Optional[ttk.Button] = None
        self.state_label: Optional[ttk.Label] = None
        self.temp_label: Optional[ttk.Label] = None
        self.speed_label: Optional[ttk.Label] = None
        self.task_label: Optional[ttk.Label] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
    
    def create_widget(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        Create the device widget UI.
        
        Args:
            width: Fixed width for grid layout (optional)
            height: Fixed height for grid layout (optional)
        """
        # Create device container frame
        self.frame = ttk.LabelFrame(
            self.parent,
            text=self.device_name,
            width=width if width else 380,
            height=height if height else 200,
            padding="10"
        )
        self.frame.pack_propagate(False)
        
        # Device header with name and remove button
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.name_label = ttk.Label(
            header_frame,
            text=self.device_name,
            font=("", 10, "bold"),
            foreground="#6495ED"
        )
        self.name_label.pack(side=tk.LEFT)
        
        if self.on_remove:
            self.remove_btn = ttk.Button(
                header_frame,
                text="移除设备",
                command=lambda: self.on_remove(self.device_id)
            )
            self.remove_btn.pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="开始",
            command=self._on_start
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(
            button_frame,
            text="暂停",
            command=self._on_pause
        )
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="停止",
            command=self._on_stop
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Status information
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.state_label = ttk.Label(status_frame, text="状态: 未知")
        self.state_label.pack(anchor=tk.W)
        
        self.temp_label = ttk.Label(status_frame, text="温度: --")
        self.temp_label.pack(anchor=tk.W)
        
        self.speed_label = ttk.Label(status_frame, text="速度: --")
        self.speed_label.pack(anchor=tk.W)
        
        # Separator
        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Print task and progress
        task_frame = ttk.Frame(self.frame)
        task_frame.pack(fill=tk.X, pady=5)
        
        self.task_label = ttk.Label(task_frame, text="打印任务: 无")
        self.task_label.pack(anchor=tk.W)
        
        progress_frame = ttk.Frame(task_frame)
        progress_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
    
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
        if not self.simulator or not self.frame:
            return
        
        try:
            state = self.simulator.printer_state
            
            # Update state
            if self.state_label:
                self.state_label.config(text=f"状态: {state.get('state', '未知')}")
            
            # Update temperature
            if self.temp_label:
                temp = state.get('temperature', {})
                extruder_temp = temp.get('extruder', {}).get('actual', 0)
                bed_temp = temp.get('heater_bed', {}).get('actual', 0)
                self.temp_label.config(
                    text=f"温度: 挤出机 {extruder_temp:.1f}°C | 热床 {bed_temp:.1f}°C"
                )
            
            # Update speed (simulate from print stats)
            if self.speed_label:
                print_state = state.get('state', 'standby')
                if print_state == 'printing':
                    speed = 100  # Default printing speed
                elif print_state == 'paused':
                    speed = 0
                else:
                    speed = 0
                self.speed_label.config(text=f"速度: {speed}%")
            
            # Update print task and progress
            if self.task_label:
                print_state = state.get('state', 'standby')
                if print_state == 'printing' or print_state == 'paused':
                    task_name = state.get('print_file', '未知任务')
                    self.task_label.config(text=f"打印任务: {task_name}")
                else:
                    self.task_label.config(text="打印任务: 无")
            
            # Update progress bar
            if self.progress_bar:
                print_state = state.get('state', 'standby')
                if print_state == 'printing':
                    # Simulate progress increment
                    progress = state.get('print_progress', 0.0)
                    # Increment progress if printing (simulate)
                    if progress < 100:
                        progress = min(100, progress + 0.1)  # Increment by 0.1% per update
                        state['print_progress'] = progress
                    self.progress_bar['value'] = progress
                elif print_state == 'paused':
                    # Keep current progress when paused
                    progress = state.get('print_progress', 0.0)
                    self.progress_bar['value'] = progress
                else:
                    # Reset progress when stopped
                    self.progress_bar['value'] = 0.0
        
        except Exception as e:
            logger.error(f"Failed to update device widget {self.device_id}: {e}")
    
    def destroy(self):
        """Destroy the widget."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
