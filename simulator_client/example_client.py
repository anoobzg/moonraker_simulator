"""
Example client for testing Moonraker Simulator

This script provides a unified entry point to test all Moonraker Simulator features:
- REST API endpoints
- WebSocket connections
- Zeroconf service discovery

It imports and orchestrates tests from separate modules.
"""

import argparse

# Import test modules
from test_rest_api import test_rest_api
from test_websocket import test_websocket
from test_zeroconf import test_service_discovery


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Moonraker Simulator Test Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all features
  python example_client.py

  # Test only REST API
  python example_client.py --rest-only

  # Test only WebSocket
  python example_client.py --ws-only

  # Test only service discovery
  python example_client.py --discovery-only

  # Test with custom URL
  python example_client.py --url http://192.168.1.100:7125

  # Test with custom discovery timeout
  python example_client.py --discovery-only --discovery-timeout 10
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:7125",
        help="Base URL of the simulator (default: http://localhost:7125)"
    )
    parser.add_argument(
        "--rest-only",
        action="store_true",
        help="Test REST API only"
    )
    parser.add_argument(
        "--ws-only",
        action="store_true",
        help="Test WebSocket only"
    )
    parser.add_argument(
        "--discovery-only",
        action="store_true",
        help="Test service discovery only"
    )
    parser.add_argument(
        "--discovery-timeout",
        type=int,
        default=5,
        help="Service discovery timeout in seconds (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Run tests based on arguments
    if args.discovery_only:
        # Only test service discovery
        test_service_discovery(args.discovery_timeout)
    else:
        # Run REST API test if not WebSocket-only
        if not args.ws_only:
            test_rest_api(args.url)
        
        # Run WebSocket test if not REST-only
        if not args.rest_only:
            test_websocket(args.url)
        
        # Also test service discovery if not restricted
        if not args.rest_only and not args.ws_only:
            test_service_discovery(args.discovery_timeout)


if __name__ == "__main__":
    main()
