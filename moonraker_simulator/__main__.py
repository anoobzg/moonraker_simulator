"""Entry point for running the simulator as a module."""

import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moonraker Simulator")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7125, help="Port to bind to (default: 7125)")
    
    args, remaining_args = parser.parse_known_args()
    
    if args.gui:
        # Launch GUI mode
        # Import from gui.py module using importlib to avoid package/module conflict
        import importlib.util
        from pathlib import Path
        
        # Get the gui.py file path
        gui_file = Path(__file__).parent / "gui.py"
        spec = importlib.util.spec_from_file_location("moonraker_simulator.gui_main", gui_file)
        gui_main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gui_main_module)
        
        # Use start_port instead of port for new GUI
        gui_main_module.main(start_port=args.port)
    else:
        # Launch CLI mode (pass remaining args to server main)
        from moonraker_simulator.server import main as server_main
        # Reconstruct sys.argv for server main
        sys.argv = [sys.argv[0]] + remaining_args
        server_main()

