"""
Minimal Moonraker API Server Simulator

This module implements a basic Moonraker API server that simulates
common endpoints and WebSocket connections using Tornado framework.
"""

import json
import logging
import time
from typing import Dict, Any, Set

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpserver import HTTPServer
from zeroconf import ServiceInfo, Zeroconf, IPVersion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAPIHandler(tornado.web.RequestHandler):
    """Base handler for API endpoints."""
    
    def set_default_headers(self):
        """Set CORS headers."""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    
    def options(self):
        """Handle OPTIONS request for CORS."""
        self.set_status(204)
        self.finish()
    
    def write_json(self, data: Dict[str, Any]):
        """Write JSON response."""
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))
        self.finish()
    
    def write_error(self, status_code, **kwargs):
        """Handle errors and return JSON response."""
        self.set_header("Content-Type", "application/json")
        error_info = {
            "error": {
                "message": kwargs.get("reason", "Internal server error"),
                "code": status_code
            }
        }
        if "exc_info" in kwargs:
            exception = kwargs["exc_info"][1]
            logger.error(f"Handler error: {exception}", exc_info=kwargs["exc_info"])
            error_info["error"]["message"] = str(exception)
        
        self.set_status(status_code)
        self.write(json.dumps(error_info))
        self.finish()
    
    @property
    def simulator(self):
        """Get simulator instance."""
        try:
            # Get from application attribute (set directly)
            return self.application.simulator
        except AttributeError:
            logger.error("Simulator not found in application")
            raise tornado.web.HTTPError(500, reason="Server configuration error")


class ServerInfoHandler(BaseAPIHandler):
    """Handle /server/info endpoint."""
    
    def get(self):
        """Return server information."""
        self.write_json({
            "result": {
                "klippy_connected": True,
                "klippy_state": "ready",
                "components": ["server", "database", "file_manager", "machine"],
                "failed_components": [],
                "registered_directories": ["config", "logs", "gcodes"],
                "warnings": [],
                "websocket_count": len(self.simulator.websocket_clients),
                "moonraker_version": "0.1.0"
            }
        })


class PrinterInfoHandler(BaseAPIHandler):
    """Handle /printer/info endpoint."""
    
    def get(self):
        """Return printer information."""
        state = self.simulator.printer_state
        self.write_json({
            "result": {
                "state": state["state"],
                "state_message": state["state_message"],
                "hostname": "moonraker-simulator",
                "software_version": "Moonraker Simulator v0.1.0",
                "cpu_info": "Simulated CPU",
                "klipper_path": "/fake/path/klippy",
                "python_path": "/fake/path/python",
                "log_file": "/fake/path/klippy.log",
                "config_file": "/fake/path/printer.cfg"
            }
        })


class PrinterObjectsQueryHandler(BaseAPIHandler):
    """Handle /printer/objects/query endpoint."""
    
    def get(self):
        """Query printer objects."""
        objects_str = self.get_argument("objects", "temperature_sensor,heater_bed,extruder")
        obj_list = [obj.strip() for obj in objects_str.split(",")]
        
        result = {}
        state = self.simulator.printer_state
        
        for obj in obj_list:
            if obj == "temperature_sensor" or obj == "extruder":
                result[obj] = {
                    "temperature": state["temperature"]["extruder"]["actual"],
                    "target": state["temperature"]["extruder"]["target"],
                    "power": 0.0
                }
            elif obj == "heater_bed":
                result[obj] = {
                    "temperature": state["temperature"]["heater_bed"]["actual"],
                    "target": state["temperature"]["heater_bed"]["target"],
                    "power": 0.0
                }
            elif obj == "print_stats":
                result[obj] = state["print_stats"]
        
        self.write_json({"result": {"status": result}})


class PrinterObjectsListHandler(BaseAPIHandler):
    """Handle /printer/objects/list endpoint."""
    
    def get(self):
        """List available printer objects."""
        self.write_json({
            "result": {
                "objects": [
                    "temperature_sensor",
                    "heater_bed",
                    "extruder",
                    "print_stats",
                    "virtual_sdcard",
                    "display_status"
                ]
            }
        })


class FilesListHandler(BaseAPIHandler):
    """Handle /server/files/list endpoint."""
    
    def get(self):
        """List files in the gcode directory."""
        root = self.get_argument("root", "gcodes")
        self.write_json({
            "result": {
                "files": [
                    {
                        "filename": "test.gcode",
                        "modified": time.time(),
                        "size": 1024
                    }
                ],
                "dirs": []
            }
        })


class ServerRestartHandler(BaseAPIHandler):
    """Handle /server/restart endpoint."""
    
    def post(self):
        """Simulate server restart."""
        self.write_json({"result": "ok"})


class PrintStartHandler(BaseAPIHandler):
    """Handle /printer/print/start endpoint."""
    
    def post(self):
        """Start a print job."""
        try:
            data = json.loads(self.request.body) if self.request.body else {}
            filename = data.get("filename", "")
        except (json.JSONDecodeError, ValueError):
            filename = ""
        
        simulator = self.simulator
        simulator.printer_state["state"] = "printing"
        simulator.printer_state["state_message"] = f"Printing {filename}"
        simulator.printer_state["print_stats"]["filename"] = filename
        simulator.printer_state["print_stats"]["state"] = "printing"
        
        # Broadcast state change to WebSocket clients
        simulator.broadcast_status_update({
            "printer.state": simulator.printer_state["state"],
            "printer.state_message": simulator.printer_state["state_message"]
        })
        
        self.write_json({"result": "ok"})


class PrintCancelHandler(BaseAPIHandler):
    """Handle /printer/print/cancel endpoint."""
    
    def post(self):
        """Cancel current print job."""
        simulator = self.simulator
        simulator.printer_state["state"] = "standby"
        simulator.printer_state["state_message"] = "Print cancelled"
        simulator.printer_state["print_stats"]["state"] = "standby"
        
        # Broadcast state change to WebSocket clients
        simulator.broadcast_status_update({
            "printer.state": simulator.printer_state["state"],
            "printer.state_message": simulator.printer_state["state_message"]
        })
        
        self.write_json({"result": "ok"})


class GcodeScriptHandler(BaseAPIHandler):
    """Handle /printer/gcode/script endpoint."""
    
    def post(self):
        """Execute G-code script."""
        try:
            data = json.loads(self.request.body) if self.request.body else {}
            script = data.get("script", "")
        except (json.JSONDecodeError, ValueError):
            script = ""
        
        logger.info(f"Received G-code: {script}")
        self.write_json({"result": "ok"})


class MoonrakerWebSocketHandler(tornado.websocket.WebSocketHandler):
    """WebSocket handler for Moonraker API."""
    
    def set_default_headers(self):
        """Set CORS headers."""
        self.set_header("Access-Control-Allow-Origin", "*")
    
    def check_origin(self, origin):
        """Allow all origins for development."""
        return True
    
    def open(self):
        """Handle WebSocket connection."""
        logger.info("Client connected via WebSocket")
        self.simulator.websocket_clients.add(self)
        
        # Send connection confirmation
        self.write_message(json.dumps({
            "jsonrpc": "2.0",
            "method": "connected",
            "params": {"connection_id": id(self)}
        }))
    
    def on_message(self, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            method = data.get("method", "")
            params = data.get("params", {})
            msg_id = data.get("id")
            
            if method == "printer.objects.subscribe":
                self._handle_subscribe(params, msg_id)
            elif method == "server.info":
                self._handle_server_info(msg_id)
            else:
                logger.warning(f"Unknown method: {method}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _handle_subscribe(self, params: Dict, msg_id: Any):
        """Handle subscription request."""
        objects = params.get("objects", {})
        logger.info(f"Subscription request: {objects}")
        
        # Build status response
        status = {}
        state = self.simulator.printer_state
        
        for obj_name, obj_params in objects.items():
            if obj_name in ["temperature_sensor", "extruder"]:
                status[obj_name] = {
                    "temperature": state["temperature"]["extruder"]["actual"],
                    "target": state["temperature"]["extruder"]["target"]
                }
            elif obj_name == "heater_bed":
                status[obj_name] = {
                    "temperature": state["temperature"]["heater_bed"]["actual"],
                    "target": state["temperature"]["heater_bed"]["target"]
                }
            elif obj_name == "print_stats":
                status[obj_name] = state["print_stats"]
        
        # Send response
        response = {
            "jsonrpc": "2.0",
            "method": "printer.objects.status",
            "params": {"status": status}
        }
        if msg_id is not None:
            response["id"] = msg_id
        
        self.write_message(json.dumps(response))
    
    def _handle_server_info(self, msg_id: Any):
        """Handle server info request."""
        response = {
            "jsonrpc": "2.0",
            "method": "server.info",
            "params": {
                "klippy_connected": True,
                "klippy_state": "ready",
                "moonraker_version": "0.1.0"
            }
        }
        if msg_id is not None:
            response["id"] = msg_id
        
        self.write_message(json.dumps(response))
    
    def on_close(self):
        """Handle WebSocket disconnection."""
        logger.info("Client disconnected")
        self.simulator.websocket_clients.discard(self)
    
    @property
    def simulator(self):
        """Get simulator instance."""
        return self.application.simulator


class MoonrakerSimulator:
    """Minimal Moonraker API server simulator."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 7125):
        self.host = host
        self.port = port
        self.zeroconf = None
        self.service_info = None
        self.websocket_clients: Set[MoonrakerWebSocketHandler] = set()
        self.http_server = None
        self._thread = None
        self._ioloop = None
        
        # Simulated printer state
        self.printer_state = {
            "state": "ready",
            "state_message": "Printer is ready",
            "temperature": {
                "extruder": {"actual": 25.0, "target": 0.0},
                "heater_bed": {"actual": 25.0, "target": 0.0}
            },
            "print_stats": {
                "filename": "",
                "total_duration": 0.0,
                "print_duration": 0.0,
                "filament_used": 0.0,
                "state": "standby"
            }
        }
        
        # Setup Tornado application
        # Store simulator reference directly on application
        self.app = tornado.web.Application(
            [
                (r"/server/info", ServerInfoHandler),
                (r"/printer/info", PrinterInfoHandler),
                (r"/printer/objects/query", PrinterObjectsQueryHandler),
                (r"/printer/objects/list", PrinterObjectsListHandler),
                (r"/server/files/list", FilesListHandler),
                (r"/server/restart", ServerRestartHandler),
                (r"/printer/print/start", PrintStartHandler),
                (r"/printer/print/cancel", PrintCancelHandler),
                (r"/printer/gcode/script", GcodeScriptHandler),
                (r"/websocket", MoonrakerWebSocketHandler),
            ],
            simulator=self
        )
        # Also store as attribute for direct access
        self.app.simulator = self
    
    def broadcast_status_update(self, data: Dict[str, Any]):
        """Broadcast status update to all WebSocket clients."""
        message = json.dumps({
            "jsonrpc": "2.0",
            "method": "notify_status_update",
            "params": data
        })
        
        disconnected = []
        for client in self.websocket_clients:
            try:
                client.write_message(message)
            except Exception as e:
                logger.warning(f"Failed to send message to client: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.websocket_clients.discard(client)
    
    def _register_zeroconf(self):
        """Register service with Zeroconf for service discovery."""
        # Skip if already registered
        if self.zeroconf is not None:
            return
        
        try:
            import socket
            
            service_type = "_moonraker._tcp.local."
            
            # Get local IP address for service registration
            local_ip = self._get_local_ip()
            
            # Generate a unique service name (use hostname if available)
            # Format: hostname._moonraker._tcp.local. (replace spaces with hyphens)
            # For multiple instances, add port to make it unique
            try:
                hostname = socket.gethostname()
                # Clean hostname: replace spaces and special chars with hyphens
                clean_hostname = hostname.replace(' ', '-').replace('_', '-')
                # Add port to service name for uniqueness when running multiple instances
                service_name = f"{clean_hostname}-{self.port}.{service_type}"
            except Exception:
                service_name = f"Moonraker-Simulator-{self.port}.{service_type}"
            
            # Convert IP string to bytes for ServiceInfo
            ip_bytes = socket.inet_aton(local_ip)
            
            # Get server hostname for mDNS (format: hostname.local.)
            try:
                clean_hostname = socket.gethostname().replace(' ', '-').replace('_', '-')
                server_hostname = f"{clean_hostname}.local."
            except Exception:
                server_hostname = f"{local_ip.replace('.', '-')}.local."
            
            # Create ServiceInfo with proper format (matching reference implementation)
            self.service_info = ServiceInfo(
                type_=service_type,
                name=service_name,
                addresses=[ip_bytes],
                port=self.port,
                properties={
                    b"version": b"0.1.0",
                    b"hostname": socket.gethostname().encode('utf-8')
                },
                server=server_hostname
            )
            
            # Create Zeroconf instance with IPv4 only for better compatibility
            # This is critical for reliable service discovery
            self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
            
            # Register service - this should be done after server is ready
            self.zeroconf.register_service(self.service_info)
            
            logger.info("=" * 60)
            logger.info("📡 mDNS Service Registered")
            logger.info("=" * 60)
            logger.info(f"📍 Service Name: {service_name}")
            logger.info(f"🌐 Service Type: {service_type}")
            logger.info(f"🔗 Host IP: {local_ip}")
            logger.info(f"🔌 Port: {self.port}")
            logger.info(f"📋 Server: {server_hostname}")
            logger.info(f"🌍 Service URL: http://{local_ip}:{self.port}")
            logger.info("=" * 60)
        except Exception as e:
            logger.warning(f"Failed to register Zeroconf service: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            logger.warning("  Service discovery may not work, but server will still run")
    
    def _get_local_ip(self):
        """Get local IP address."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def _unregister_zeroconf(self):
        """Unregister Zeroconf service."""
        if self.zeroconf and self.service_info:
            try:
                self.zeroconf.unregister_service(self.service_info)
                self.zeroconf.close()
                logger.info("Unregistered Zeroconf service")
            except Exception as e:
                logger.warning(f"Failed to unregister Zeroconf service: {e}")
    
    def start(self, run_in_thread: bool = False):
        """
        Start the simulator server.
        
        Args:
            run_in_thread: If True, run the server in a separate thread.
                          If False, run in the current thread (blocking).
        """
        logger.info(f"Starting Moonraker Simulator on {self.host}:{self.port}")
        
        if run_in_thread:
            # Run in a separate thread
            # Create IOLoop first, then start HTTP server in that IOLoop
            import threading
            import time
            import socket
            
            self._thread = threading.Thread(target=self._run_ioloop, daemon=True)
            self._thread.start()
            
            # Wait for server to be ready by checking if port is listening
            max_retries = 10
            retry_count = 0
            while retry_count < max_retries:
                time.sleep(0.1)
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex((self.host if self.host != "0.0.0.0" else "127.0.0.1", self.port))
                    sock.close()
                    if result == 0:
                        # Port is listening, server is ready
                        break
                except Exception:
                    pass
                retry_count += 1
            
            # Register Zeroconf after server is ready
            self._register_zeroconf()
            logger.info(f"Moonraker Simulator started in background thread on port {self.port}")
        else:
            # Run in current thread (blocking)
            # Create HTTP server and start IOLoop in current thread
            self.http_server = HTTPServer(self.app)
            self.http_server.listen(self.port, address=self.host)
            # Register Zeroconf after server is listening
            self._register_zeroconf()
            try:
                # Start IOLoop
                tornado.ioloop.IOLoop.current().start()
            except KeyboardInterrupt:
                logger.info("Shutting down...")
            finally:
                self.stop()
    
    def _run_ioloop(self):
        """Run the IOLoop in a separate thread."""
        try:
            # Create a new IOLoop for this thread
            self._ioloop = tornado.ioloop.IOLoop()
            self._ioloop.make_current()
            
            # Start HTTP server in this IOLoop's thread
            def start_server():
                self.http_server = HTTPServer(self.app)
                self.http_server.listen(self.port, address=self.host)
                logger.info(f"HTTP server listening on {self.host}:{self.port}")
            
            # Schedule server start in the IOLoop
            self._ioloop.add_callback(start_server)
            
            logger.info(f"IOLoop started for port {self.port}")
            self._ioloop.start()
        except Exception as e:
            logger.error(f"Error in IOLoop for port {self.port}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self.stop()
    
    def stop(self):
        """Stop the simulator server."""
        logger.info(f"Stopping Moonraker Simulator on port {self.port}...")
        self._unregister_zeroconf()
        
        # Stop IOLoop if running in thread
        if self._ioloop:
            try:
                self._ioloop.stop()
            except Exception as e:
                logger.warning(f"Error stopping IOLoop: {e}")
        
        if self.http_server:
            self.http_server.stop()
        
        # Close all WebSocket connections
        for client in list(self.websocket_clients):
            try:
                client.close()
            except Exception:
                pass
        self.websocket_clients.clear()
        
        logger.info(f"Moonraker Simulator stopped on port {self.port}")


def main():
    """Main entry point."""
    import argparse
    import signal
    import sys
    
    parser = argparse.ArgumentParser(
        description="Moonraker Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start a single instance on default port 7125
  python -m moonraker_simulator

  # Start a single instance on custom port
  python -m moonraker_simulator --port 7126

  # Start multiple instances with auto-incrementing ports
  python -m moonraker_simulator --count 3

  # Start multiple instances with custom start port
  python -m moonraker_simulator --count 3 --start-port 8000

  # Start multiple instances with custom host
  python -m moonraker_simulator --host 0.0.0.0 --count 5

  # Legacy: manually specify ports (still supported)
  python -m moonraker_simulator --ports 7125 7126 7127
        """
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to (single instance, default: 7125)")
    parser.add_argument("--ports", type=int, nargs="+", help="Ports to bind to (multiple instances, legacy option)")
    parser.add_argument("--count", type=int, default=1, help="Number of instances to start (default: 1)")
    parser.add_argument("--start-port", type=int, default=7125, help="Starting port for auto-increment (default: 7125)")
    
    args = parser.parse_args()
    
    # Determine which ports to use
    if args.ports:
        # Legacy: manually specified ports (takes precedence)
        ports = args.ports
        logger.info(f"Starting {len(ports)} Moonraker Simulator instances on ports: {ports}")
    elif args.count > 1:
        # Multiple instances with auto-incrementing ports
        # Use --port if specified, otherwise use --start-port (default: 7125)
        if args.port is not None:
            start_port = args.port
        else:
            start_port = args.start_port
        ports = [start_port + i for i in range(args.count)]
        logger.info(f"Starting {args.count} Moonraker Simulator instances on ports: {ports}")
    elif args.port:
        # Single instance with custom port
        ports = [args.port]
    else:
        # Single instance with default port
        ports = [7125]
    
    # Create and start simulators
    simulators = []
    for port in ports:
        simulator = MoonrakerSimulator(host=args.host, port=port)
        if len(ports) > 1:
            # Run in thread for multiple instances
            simulator.start(run_in_thread=True)
        else:
            # Run in main thread for single instance
            simulator.start(run_in_thread=False)
            return  # Single instance blocks here
        
        simulators.append(simulator)
    
    # For multiple instances, wait for interrupt signal
    if len(simulators) > 1:
        def signal_handler(sig, frame):
            logger.info("\nShutting down all simulators...")
            for simulator in simulators:
                simulator.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info(f"All {len(simulators)} simulators are running. Press Ctrl+C to stop.")
        try:
            # Keep main thread alive
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(None, None)


if __name__ == "__main__":
    main()
