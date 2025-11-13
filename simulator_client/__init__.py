"""
Simulator Client Package

This package provides test clients for Moonraker Simulator:
- test_rest_api: REST API testing
- test_websocket: WebSocket testing
- test_zeroconf: Service discovery testing
- example_client: Unified test entry point
"""

from .test_rest_api import test_rest_api
from .test_websocket import test_websocket, WebSocketClient
from .test_zeroconf import test_service_discovery, MoonrakerServiceListener

__all__ = [
    'test_rest_api',
    'test_websocket',
    'test_service_discovery',
    'WebSocketClient',
    'MoonrakerServiceListener',
]

