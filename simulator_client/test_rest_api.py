"""
REST API Test Module

This module provides functions to test Moonraker Simulator REST API endpoints.
"""

import requests
import json


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


def main():
    """Main entry point for REST API testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Moonraker Simulator REST API")
    parser.add_argument("--url", default="http://localhost:7125", help="Base URL of the simulator")
    
    args = parser.parse_args()
    test_rest_api(args.url)


if __name__ == "__main__":
    main()

