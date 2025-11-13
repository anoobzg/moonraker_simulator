"""
WebSocket Test Module

This module provides functions and classes to test Moonraker Simulator WebSocket connections.
"""

import websocket
import threading
import time
import json


class WebSocketClient:
    """WebSocket client for testing."""
    
    def __init__(self, url: str):
        self.url = url.replace("http://", "ws://").replace("https://", "wss://") + "/websocket"
        self.ws = None
        self.connected = False
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            method = data.get("method", "")
            params = data.get("params", {})
            
            if method == "connected":
                print(f"\n✓ Server confirmed connection: {params}")
            elif method == "printer.objects.status":
                print(f"\n✓ Received status update:")
                print(json.dumps(params, indent=2))
            elif method == "server.info":
                print(f"\n✓ Received server info:")
                print(json.dumps(params, indent=2))
            elif method == "notify_status_update":
                print(f"\n✓ Received notification:")
                print(json.dumps(params, indent=2))
            else:
                print(f"\n? Unknown message: {data}")
        except json.JSONDecodeError:
            print(f"\n? Invalid JSON message: {message}")
        except Exception as e:
            print(f"\n✗ Error handling message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket error."""
        print(f"\n✗ WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        print("\n✗ Disconnected from WebSocket server")
        self.connected = False
    
    def on_open(self, ws):
        """Handle WebSocket open."""
        print("\n✓ Connected to WebSocket server")
        self.connected = True
    
    def connect(self):
        """Connect to WebSocket server."""
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Run in a separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for connection
        timeout = 5
        elapsed = 0
        while not self.connected and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1
        
        if not self.connected:
            raise Exception("Failed to connect to WebSocket server")
    
    def send(self, method: str, params: dict = None, msg_id: int = None):
        """Send a JSON-RPC message."""
        if not self.connected or not self.ws:
            raise Exception("WebSocket not connected")
        
        message = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params:
            message["params"] = params
        if msg_id is not None:
            message["id"] = msg_id
        
        self.ws.send(json.dumps(message))
    
    def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.ws:
            self.ws.close()
        self.connected = False


def test_websocket(base_url: str = "http://localhost:7125"):
    """Test WebSocket connection."""
    print("\n" + "=" * 50)
    print("Testing WebSocket")
    print("=" * 50)
    
    client = WebSocketClient(base_url)
    
    try:
        # Connect to server
        print("\nConnecting to WebSocket server...")
        client.connect()
        
        # Wait a bit for connection
        time.sleep(0.5)
        
        # Subscribe to printer objects
        print("\nSubscribing to printer objects...")
        client.send("printer.objects.subscribe", {
            "objects": {
                "temperature_sensor": None,
                "heater_bed": None,
                "print_stats": None
            }
        }, msg_id=1)
        
        # Request server info
        print("\nRequesting server info...")
        client.send("server.info", msg_id=2)
        
        # Wait for responses
        time.sleep(2)
        
        # Disconnect
        print("\nDisconnecting...")
        client.disconnect()
        time.sleep(0.5)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if client.connected:
            client.disconnect()


def main():
    """Main entry point for WebSocket testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Moonraker Simulator WebSocket")
    parser.add_argument("--url", default="http://localhost:7125", help="Base URL of the simulator")
    
    args = parser.parse_args()
    test_websocket(args.url)


if __name__ == "__main__":
    main()

