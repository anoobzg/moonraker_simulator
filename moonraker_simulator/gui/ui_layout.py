# -*- coding: utf-8 -*-
"""
UI layout management for the main window using tkinter.
"""

import logging
from typing import Optional, Callable
import tkinter as tk
from tkinter import ttk, simpledialog
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
        
        # Root window
        self.root: Optional[tk.Tk] = None
        self.main_frame: Optional[ttk.Frame] = None
        self.button_frame: Optional[ttk.Frame] = None
        self.device_frame: Optional[ttk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None
        self.device_container: Optional[ttk.Frame] = None
        
        # Device widgets
        self.device_widgets: dict[str, DeviceWidget] = {}
        
        # Grid layout settings
        self.grid_columns = 3  # Number of columns in grid
        self.device_width = 380  # Width of each device widget
        self.device_height = 200  # Height of each device widget
        self.device_spacing = 10  # Spacing between devices
        self.window_padding = 20  # Window padding
        
        # Empty label
        self.empty_label: Optional[ttk.Label] = None
    
    def create_layout(self, width: int = 1200, height: int = 800):
        """
        Create the main UI layout.
        
        Args:
            width: Window width
            height: Window height
        """
        # Create root window
        self.root = tk.Tk()
        self.root.title("Moonraker Simulator")
        self.root.geometry(f"{width}x{height}")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create button bar
        self._create_button_bar()
        
        # Create device list area
        self._create_device_list()
        
        # Bind resize event
        self.root.bind("<Configure>", self._on_window_resize)
        
        # Calculate initial grid columns
        self._calculate_grid_columns()
    
    def _create_button_bar(self):
        """Create the top button bar."""
        self.button_frame = ttk.Frame(self.main_frame, height=50)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        self.button_frame.pack_propagate(False)
        
        # Add device button
        add_btn = ttk.Button(
            self.button_frame,
            text="添加设备",
            command=self._on_add_device_clicked
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Batch add device button
        batch_btn = ttk.Button(
            self.button_frame,
            text="批量添加设备",
            command=self._on_batch_add_clicked
        )
        batch_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_device_list(self):
        """Create the device list area with grid layout."""
        # Create scrollable frame
        scroll_frame = ttk.Frame(self.main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(scroll_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.canvas.yview)
        self.device_container = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.device_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = self.canvas.create_window((0, 0), window=self.device_container, anchor="nw")
        
        # Update scroll region when container size changes
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Keep canvas window width equal to canvas width
            canvas_width = event.width
            self.canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.device_container.bind("<Configure>", configure_scroll_region)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(canvas_window, width=e.width))
        
        # Bind mousewheel
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empty label
        self.empty_label = ttk.Label(
            self.device_container,
            text="暂无设备，点击上方按钮添加设备",
            foreground="gray"
        )
        self.empty_label.pack(pady=20)
    
    def _on_add_device_clicked(self):
        """Handle add device button click."""
        if self.on_add_device:
            self.on_add_device()
        else:
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
        count = simpledialog.askinteger(
            "批量添加设备",
            "请输入要添加的设备数量:",
            parent=self.root,
            minvalue=1,
            maxvalue=10,
            initialvalue=3
        )
        
        if count is not None:
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
                # Hide empty label
                if self.empty_label:
                    self.empty_label.pack_forget()
                
                # Ensure grid columns are up to date
                current_columns = self._calculate_grid_columns()
                if current_columns != self.grid_columns:
                    self.grid_columns = current_columns
                    # Reorganize existing devices if column count changed
                    if len(self.device_widgets) > 0:
                        self._reorganize_grid()
                
                # Create device widget
                widget = DeviceWidget(
                    device_id=device_id,
                    device_name=device_name,
                    simulator=simulator,
                    on_remove=self.remove_device,
                    parent=self.device_container
                )
                
                widget.create_widget(
                    width=self.device_width,
                    height=self.device_height
                )
                
                self.device_widgets[device_id] = widget
                
                # Update grid layout
                self._update_grid_layout()
                
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
            
            # Show empty label if no devices
            if len(self.device_widgets) == 0:
                if self.empty_label:
                    self.empty_label.pack(pady=20)
            else:
                # Reorganize remaining devices in grid
                self._update_grid_layout()
            
            logger.info(f"Removed device {device_id}")
        except Exception as e:
            logger.error(f"Failed to remove device {device_id}: {e}")
    
    def update_all_devices(self):
        """Update all device widgets."""
        for widget in self.device_widgets.values():
            widget.update()
        
        # Check for window size changes
        self._calculate_grid_columns()
    
    def _calculate_grid_columns(self):
        """Calculate number of columns based on window width."""
        try:
            if self.root and self.canvas:
                canvas_width = self.canvas.winfo_width()
                if canvas_width > 1:  # Widget must be visible
                    # Calculate available width (canvas width minus padding)
                    available_width = canvas_width - (self.window_padding * 2)
                    # Calculate how many devices can fit
                    # Each device needs: device_width + spacing
                    columns = max(1, int((available_width + self.device_spacing) / (self.device_width + self.device_spacing)))
                    if columns != self.grid_columns:
                        old_columns = self.grid_columns
                        self.grid_columns = columns
                        # Reorganize if column count changed
                        if len(self.device_widgets) > 0:
                            self._update_grid_layout()
                    return columns
        except Exception as e:
            logger.error(f"Error calculating grid columns: {e}")
        return self.grid_columns
    
    def _on_window_resize(self, event=None):
        """Handle window resize event."""
        if event and event.widget == self.root:
            # Update grid layout after a short delay to allow widget to resize
            self.root.after(100, self._calculate_grid_columns)
    
    def _update_grid_layout(self):
        """Update grid layout for all devices."""
        if not self.device_container:
            return
        
        # Get all widget frames
        widget_list = list(self.device_widgets.values())
        if len(widget_list) == 0:
            return
        
        # Clear current grid
        for widget in widget_list:
            if widget.frame:
                widget.frame.grid_forget()
        
        # Organize into grid rows
        for idx, widget in enumerate(widget_list):
            row = idx // self.grid_columns
            col = idx % self.grid_columns
            
            if widget.frame:
                widget.frame.grid(
                    row=row,
                    column=col,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )
        
        # Update scroll region
        if self.canvas:
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _reorganize_grid(self):
        """Reorganize grid layout after device removal or window resize."""
        self._update_grid_layout()
    
    def run(self):
        """Run the GUI main loop."""
        if self.root:
            self.root.mainloop()
    
    def _on_closing(self):
        """Handle window closing event."""
        self.cleanup()
        if self.root:
            self.root.destroy()
    
    def cleanup(self):
        """Cleanup UI resources."""
        # Cleanup all widgets
        for widget in self.device_widgets.values():
            widget.destroy()
        self.device_widgets.clear()
        
        # Cleanup device manager
        self.device_manager.cleanup_all()
