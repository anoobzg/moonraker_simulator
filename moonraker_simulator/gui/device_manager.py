# -*- coding: utf-8 -*-
"""
Device management for multiple Moonraker simulator instances.
"""

import logging
from typing import Dict, Optional
from moonraker_simulator.server import MoonrakerSimulator

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages multiple device instances."""
    
    def __init__(self, start_port: int = 7125):
        """
        Initialize device manager.
        
        Args:
            start_port: Starting port number for devices
        """
        self.start_port = start_port
        self.devices: Dict[str, MoonrakerSimulator] = {}
        self.device_names: Dict[str, str] = {}  # device_id -> name
        self.next_port = start_port
        self.device_counter = 0
    
    def add_device(self, name: Optional[str] = None, host: str = "0.0.0.0", port: Optional[int] = None) -> str:
        """
        Add a new device.
        
        Args:
            name: Device name (auto-generated if None)
            host: Host address
            port: Port number (auto-assigned if None)
            
        Returns:
            Device ID
        """
        if port is None:
            port = self.next_port
            self.next_port += 1
        
        if name is None:
            self.device_counter += 1
            name = f"设备 {self.device_counter}"
        
        device_id = f"device_{port}"
        
        try:
            simulator = MoonrakerSimulator(host=host, port=port)
            simulator.start(run_in_thread=True)
            
            self.devices[device_id] = simulator
            self.device_names[device_id] = name
            
            logger.info(f"Added device '{name}' on {host}:{port}")
            return device_id
        except Exception as e:
            logger.error(f"Failed to add device: {e}")
            raise
    
    def remove_device(self, device_id: str) -> bool:
        """
        Remove a device.
        
        Args:
            device_id: Device ID to remove
            
        Returns:
            True if successful, False otherwise
        """
        if device_id not in self.devices:
            logger.warning(f"Device {device_id} not found")
            return False
        
        try:
            simulator = self.devices[device_id]
            simulator.stop()
            del self.devices[device_id]
            if device_id in self.device_names:
                del self.device_names[device_id]
            logger.info(f"Removed device {device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove device {device_id}: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[MoonrakerSimulator]:
        """Get device simulator instance."""
        return self.devices.get(device_id)
    
    def get_device_name(self, device_id: str) -> str:
        """Get device name."""
        return self.device_names.get(device_id, device_id)
    
    def set_device_name(self, device_id: str, name: str):
        """Set device name."""
        if device_id in self.devices:
            self.device_names[device_id] = name
    
    def get_all_devices(self) -> Dict[str, MoonrakerSimulator]:
        """Get all devices."""
        return self.devices.copy()
    
    def get_device_list(self) -> list:
        """Get list of device IDs."""
        return list(self.devices.keys())
    
    def start_device(self, device_id: str) -> bool:
        """Start a device."""
        if device_id not in self.devices:
            return False
        try:
            simulator = self.devices[device_id]
            # Update printer state to printing
            simulator.printer_state['state'] = 'printing'
            simulator.printer_state['state_message'] = '正在打印'
            return True
        except Exception as e:
            logger.error(f"Failed to start device {device_id}: {e}")
            return False
    
    def pause_device(self, device_id: str) -> bool:
        """Pause a device (simulate pause state)."""
        if device_id not in self.devices:
            return False
        try:
            simulator = self.devices[device_id]
            # Update printer state to paused
            simulator.printer_state['state'] = 'paused'
            simulator.printer_state['state_message'] = '打印已暂停'
            return True
        except Exception as e:
            logger.error(f"Failed to pause device {device_id}: {e}")
            return False
    
    def stop_device(self, device_id: str) -> bool:
        """Stop a device."""
        if device_id not in self.devices:
            return False
        try:
            simulator = self.devices[device_id]
            # Update printer state to stopped
            simulator.printer_state['state'] = 'standby'
            simulator.printer_state['state_message'] = '打印机待机'
            return True
        except Exception as e:
            logger.error(f"Failed to stop device {device_id}: {e}")
            return False
    
    def cleanup_all(self):
        """Stop and remove all devices."""
        device_ids = list(self.devices.keys())
        for device_id in device_ids:
            self.remove_device(device_id)

