"""
Zeroconf Service Discovery Test Module

This module provides functions and classes to test Moonraker Simulator service discovery
using Zeroconf (mDNS/Bonjour) on local networks.
"""

import threading
import time
import json
import requests
from zeroconf import ServiceBrowser, Zeroconf, ServiceListener


class MoonrakerServiceListener(ServiceListener):
    """Listener for Moonraker service discovery."""
    
    def __init__(self):
        self.services = []
        self.services_by_key = {}  # Track services by (IP, port) to avoid duplicates
        self.lock = threading.Lock()
    
    def _get_service_key(self, address, port):
        """Generate a unique key for a service (IP address + port)."""
        return f"{address}:{port}"
    
    def _convert_addresses(self, info):
        """Convert addresses from bytes to IP strings."""
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
        return addresses
    
    def add_service(self, zeroconf, service_type, name):
        """Called when a service is discovered."""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            with self.lock:
                # Convert addresses first
                addresses = self._convert_addresses(info)
                if not addresses:
                    return  # No valid address
                
                # Use first address + port as unique key
                primary_address = addresses[0]
                port = info.port
                service_key = self._get_service_key(primary_address, port)
                
                # Check if service already exists (by IP + port)
                if service_key in self.services_by_key:
                    # Service already exists, update it silently (no duplicate)
                    existing_service = self.services_by_key[service_key]
                    # Update existing service data
                    self._update_service_data(existing_service, info, service_type, name, addresses)
                    return
                
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
                    "port": port,
                    "properties": properties,
                    "server": info.server
                }
                self.services.append(service_data)
                self.services_by_key[service_key] = service_data
                print(f"\n✓ Discovered service: {name}")
                print(f"  Address: {', '.join(service_data['addresses'])}")
                print(f"  Port: {service_data['port']}")
                if service_data['properties']:
                    print(f"  Properties: {service_data['properties']}")
    
    def _update_service_data(self, service_data, info, service_type, name, addresses=None):
        """Update existing service data with new information."""
        if addresses is None:
            addresses = self._convert_addresses(info)
        
        old_address = service_data.get("addresses", [""])[0] if service_data.get("addresses") else ""
        old_port = service_data.get("port")
        new_address = addresses[0] if addresses else ""
        new_port = info.port
        
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
        
        # Check if address or port changed (shouldn't happen, but log if it does)
        if old_address != new_address or old_port != new_port:
            print(f"\n⚠ Service {name} changed: {old_address}:{old_port} -> {new_address}:{new_port}")
            # Remove old service key and add new one
            old_key = self._get_service_key(old_address, old_port)
            new_key = self._get_service_key(new_address, new_port)
            if old_key in self.services_by_key:
                del self.services_by_key[old_key]
            self.services_by_key[new_key] = service_data
        
        # Update service data
        service_data["addresses"] = addresses
        service_data["port"] = new_port
        service_data["properties"] = properties
        service_data["server"] = info.server
        service_data["name"] = name  # Update name in case it changed
    
    def remove_service(self, zeroconf, service_type, name):
        """Called when a service is removed."""
        with self.lock:
            # Find and remove all services with this name (could be multiple IP:port combinations)
            services_to_remove = [s for s in self.services if s['name'] == name]
            for service in services_to_remove:
                address = service['addresses'][0] if service.get('addresses') else 'unknown'
                port = service['port']
                service_key = self._get_service_key(address, port)
                if service_key in self.services_by_key:
                    del self.services_by_key[service_key]
                self.services.remove(service)
                print(f"\n✗ Service removed: {name} ({address}:{port})")
    
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
                    
                    # Try connection with retries
                    max_retries = 3
                    connected = False
                    for attempt in range(1, max_retries + 1):
                        try:
                            # Use longer timeout for connection test
                            response = requests.get(
                                f"{base_url}/server/info",
                                timeout=(3, 5)  # (connect timeout, read timeout)
                            )
                            if response.status_code == 200:
                                print(f"  ✓ Successfully connected!")
                                info = response.json()
                                if 'result' in info:
                                    version = info['result'].get('moonraker_version', 'unknown')
                                    state = info['result'].get('klippy_state', 'unknown')
                                    print(f"  Moonraker Version: {version}")
                                    print(f"  Klippy State: {state}")
                                connected = True
                                break
                            else:
                                print(f"  ✗ Connection failed: HTTP {response.status_code}")
                                if attempt < max_retries:
                                    print(f"    Retrying... ({attempt}/{max_retries})")
                        except requests.exceptions.Timeout as e:
                            if attempt < max_retries:
                                print(f"  ⚠ Connection timeout (attempt {attempt}/{max_retries}), retrying...")
                            else:
                                print(f"  ✗ Connection failed: Timeout after {max_retries} attempts")
                                print(f"    This may indicate:")
                                print(f"    - Server is not responding")
                                print(f"    - Firewall blocking the connection")
                                print(f"    - Network connectivity issues")
                        except requests.exceptions.ConnectionError as e:
                            if attempt < max_retries:
                                print(f"  ⚠ Connection error (attempt {attempt}/{max_retries}), retrying...")
                            else:
                                print(f"  ✗ Connection failed: {e}")
                                print(f"    This may indicate:")
                                print(f"    - Server is not running on this port")
                                print(f"    - Port is blocked by firewall")
                                print(f"    - Network routing issues")
                        except Exception as e:
                            print(f"  ✗ Connection failed: {e}")
                            break
                    
                    if not connected:
                        print(f"  💡 Tip: Verify the server is running with:")
                        print(f"     python -m moonraker_simulator --port {port}")
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


def main():
    """Main entry point for Zeroconf service discovery testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Moonraker Simulator Service Discovery")
    parser.add_argument("--timeout", type=int, default=5, help="Service discovery timeout in seconds")
    
    args = parser.parse_args()
    test_service_discovery(args.timeout)


if __name__ == "__main__":
    main()

