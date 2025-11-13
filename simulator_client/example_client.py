"""
Example client for testing Moonraker Simulator

This script demonstrates how to interact with the Moonraker Simulator
using both REST API and WebSocket connections.
"""

import requests
import websocket
import threading
import time
import json
from zeroconf import ServiceBrowser, Zeroconf, ServiceListener


def test_rest_api(base_url: str = "http://localhost:7125"):
    """Test REST API endpoints."""
    print("=" * 50)
    print("Testing REST API")
    print("=" * 50)
    
    # Test server info
    print("\n1. Getting server info...")
    try:
        response = requests.get(f"{base_url}/server/info")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test printer info
    print("\n2. Getting printer info...")
    try:
        response = requests.get(f"{base_url}/printer/info")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test printer objects query
    print("\n3. Querying printer objects...")
    try:
        response = requests.get(
            f"{base_url}/printer/objects/query",
            params={"objects": "temperature_sensor,heater_bed,print_stats"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test start print
    print("\n4. Starting a print job...")
    try:
        response = requests.post(
            f"{base_url}/printer/print/start",
            json={"filename": "test.gcode"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test cancel print
    print("\n5. Cancelling print job...")
    try:
        response = requests.post(f"{base_url}/printer/print/cancel")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


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


class MoonrakerServiceListener(ServiceListener):
    """Listener for Moonraker service discovery."""
    
    def __init__(self):
        self.services = []
        self.lock = threading.Lock()
    
    def add_service(self, zeroconf, service_type, name):
        """Called when a service is discovered."""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            with self.lock:
                # Convert addresses from bytes to IP strings
                addresses = []
                for addr in info.addresses:
                    if isinstance(addr, bytes):
                        # IPv4 address is 4 bytes
                        if len(addr) == 4:
                            addresses.append('.'.join(str(b) for b in addr))
                        elif len(addr) == 16:
                            # IPv6 address (16 bytes) - convert to hex format
                            ipv6_parts = [f'{addr[i]:02x}{addr[i+1]:02x}' for i in range(0, 16, 2)]
                            addresses.append(':'.join(ipv6_parts))
                        else:
                            addresses.append(addr.hex())
                    else:
                        addresses.append(str(addr))
                
                # Convert properties from bytes to strings
                properties = {}
                if info.properties:
                    for key, value in info.properties.items():
                        if isinstance(key, bytes):
                            key = key.decode('utf-8')
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except UnicodeDecodeError:
                                value = value.hex()
                        properties[key] = value
                
                service_data = {
                    "name": name,
                    "type": service_type,
                    "addresses": addresses,
                    "port": info.port,
                    "properties": properties,
                    "server": info.server
                }
                self.services.append(service_data)
                print(f"\n✓ Discovered service: {name}")
                print(f"  Address: {', '.join(service_data['addresses'])}")
                print(f"  Port: {service_data['port']}")
                if service_data['properties']:
                    print(f"  Properties: {service_data['properties']}")
    
    def remove_service(self, zeroconf, service_type, name):
        """Called when a service is removed."""
        with self.lock:
            self.services = [s for s in self.services if s['name'] != name]
            print(f"\n✗ Service removed: {name}")
    
    def update_service(self, zeroconf, service_type, name):
        """Called when a service is updated."""
        # Re-add to get updated info
        self.add_service(zeroconf, service_type, name)
    
    def get_services(self):
        """Get list of discovered services."""
        with self.lock:
            return self.services.copy()


def test_service_discovery(timeout: int = 5):
    """Test Zeroconf service discovery on local network."""
    print("\n" + "=" * 50)
    print("Testing Service Discovery (Zeroconf/mDNS)")
    print("=" * 50)
    
    print(f"\nSearching for Moonraker services on local network (timeout: {timeout}s)...")
    print("Make sure the Moonraker Simulator is running on the same network!")
    print("\nNote: This uses mDNS/Bonjour for local network discovery.")
    print("      Services on the same LAN should be discoverable automatically.")
    
    zeroconf = Zeroconf()
    listener = MoonrakerServiceListener()
    
    # Browse for Moonraker services
    service_type = "_moonraker._tcp.local."
    browser = ServiceBrowser(zeroconf, service_type, listener)
    
    try:
        # Wait for services to be discovered
        print("\nWaiting for services to be discovered...")
        print("(Services will appear as they are found)")
        time.sleep(timeout)
        
        # Get discovered services
        services = listener.get_services()
        
        if services:
            print(f"\n✓ Found {len(services)} service(s):")
            print("\n" + "-" * 50)
            for i, service in enumerate(services, 1):
                print(f"\nService {i}:")
                print(f"  Name: {service['name']}")
                print(f"  Type: {service['type']}")
                print(f"  Addresses: {', '.join(service['addresses'])}")
                print(f"  Port: {service['port']}")
                print(f"  Server: {service['server']}")
                if service['properties']:
                    print(f"  Properties:")
                    for key, value in service['properties'].items():
                        if isinstance(value, bytes):
                            value = value.decode('utf-8')
                        print(f"    {key}: {value}")
                
                # Try to connect to the discovered service
                if service['addresses']:
                    address = service['addresses'][0]
                    port = service['port']
                    base_url = f"http://{address}:{port}"
                    print(f"\n  Testing connection to {base_url}...")
                    try:
                        response = requests.get(f"{base_url}/server/info", timeout=2)
                        if response.status_code == 200:
                            print(f"  ✓ Successfully connected!")
                            info = response.json()
                            if 'result' in info:
                                print(f"  Moonraker Version: {info['result'].get('moonraker_version', 'unknown')}")
                        else:
                            print(f"  ✗ Connection failed: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"  ✗ Connection failed: {e}")
                print("-" * 50)
        else:
            print("\n✗ No Moonraker services found")
            print("  Make sure:")
            print("  1. Moonraker Simulator is running")
            print("  2. Zeroconf service is properly registered")
            print("  3. Firewall allows mDNS/Bonjour traffic")
        
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
    finally:
        browser.cancel()
        zeroconf.close()
        print("\nService discovery stopped")


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
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Moonraker Simulator Test Client")
    parser.add_argument("--url", default="http://localhost:7125", help="Base URL of the simulator")
    parser.add_argument("--rest-only", action="store_true", help="Test REST API only")
    parser.add_argument("--ws-only", action="store_true", help="Test WebSocket only")
    parser.add_argument("--discovery-only", action="store_true", help="Test service discovery only")
    parser.add_argument("--discovery-timeout", type=int, default=5, help="Service discovery timeout in seconds")
    
    args = parser.parse_args()
    
    if args.discovery_only:
        test_service_discovery(args.discovery_timeout)
    else:
        if not args.ws_only:
            test_rest_api(args.url)
        
        if not args.rest_only:
            test_websocket(args.url)
        
        # Also test service discovery if not restricted
        if not args.rest_only and not args.ws_only:
            test_service_discovery(args.discovery_timeout)


if __name__ == "__main__":
    main()
