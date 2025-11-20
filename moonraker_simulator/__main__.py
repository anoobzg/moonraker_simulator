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
        from moonraker_simulator.gui import main as gui_main
        gui_main(host=args.host, port=args.port)
    else:
        # Launch CLI mode (pass remaining args to server main)
        from moonraker_simulator.server import main as server_main
        # Reconstruct sys.argv for server main
        sys.argv = [sys.argv[0]] + remaining_args
        server_main()

