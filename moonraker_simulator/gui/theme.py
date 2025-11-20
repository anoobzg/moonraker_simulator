# -*- coding: utf-8 -*-
"""
Theme configuration for DearPyGui.
"""

import dearpygui.dearpygui as dpg


def create_light_theme() -> int:
    """
    Create and return a Light theme for DearPyGui.
    
    Returns:
        Theme ID
    """
    with dpg.theme() as theme_id:
        with dpg.theme_component(dpg.mvAll):
            # Window colors
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [255, 255, 255], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [250, 250, 250], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, [255, 255, 255], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Border, [220, 220, 220], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [240, 240, 240], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, [230, 230, 230], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, [220, 220, 220], category=dpg.mvThemeCat_Core)
            
            # Text colors
            dpg.add_theme_color(dpg.mvThemeCol_Text, [0, 0, 0], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, [150, 150, 150], category=dpg.mvThemeCat_Core)
            
            # Button colors
            dpg.add_theme_color(dpg.mvThemeCol_Button, [240, 240, 240], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [220, 220, 220], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [200, 200, 200], category=dpg.mvThemeCat_Core)
            
            # Header colors
            dpg.add_theme_color(dpg.mvThemeCol_Header, [230, 230, 230], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, [210, 210, 210], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, [190, 190, 190], category=dpg.mvThemeCat_Core)
            
            # Scrollbar colors
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, [250, 250, 250], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, [200, 200, 200], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, [180, 180, 180], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, [160, 160, 160], category=dpg.mvThemeCat_Core)
            
            # Separator color
            dpg.add_theme_color(dpg.mvThemeCol_Separator, [220, 220, 220], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, [200, 200, 200], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, [180, 180, 180], category=dpg.mvThemeCat_Core)
            
            # Title bar colors
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, [240, 240, 240], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, [230, 230, 230], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, [250, 250, 250], category=dpg.mvThemeCat_Core)
            
            # Menu bar colors
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, [240, 240, 240], category=dpg.mvThemeCat_Core)
            
            # Progress bar colors
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, [100, 150, 255], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogramHovered, [80, 130, 235], category=dpg.mvThemeCat_Core)
            
            # Resize grip
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, [200, 200, 200], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGripHovered, [180, 180, 180], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive, [160, 160, 160], category=dpg.mvThemeCat_Core)
            
            # Tab colors
            dpg.add_theme_color(dpg.mvThemeCol_Tab, [230, 230, 230], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, [210, 210, 210], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, [240, 240, 240], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, [240, 240, 240], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, [230, 230, 230], category=dpg.mvThemeCat_Core)
            
            # Table colors
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, [240, 240, 240], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, [200, 200, 200], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, [230, 230, 230], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, [255, 255, 255], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, [250, 250, 250], category=dpg.mvThemeCat_Core)
        
        # Style settings
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 5.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 3.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 3.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 1.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8.0, 8.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4.0, 3.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8.0, 4.0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 4.0, 4.0, category=dpg.mvThemeCat_Core)
    
    return theme_id


def apply_light_theme():
    """Apply Light theme to the entire application."""
    theme_id = create_light_theme()
    dpg.bind_theme(theme_id)
    return theme_id

