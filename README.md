# Moonraker Simulator

一个最小化的 Moonraker API 服务器模拟器，用于开发和测试目的。

## 功能特性

- ✅ 基本的 REST API 端点
- ✅ WebSocket 支持用于实时状态更新
- ✅ Zeroconf 服务发现
- ✅ 模拟打印机状态和温度
- ✅ 支持打印作业控制

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 作为模块运行

```bash
python -m moonraker_simulator
```

### 直接运行

```bash
python moonraker_simulator/server.py
```

### 自定义端口和主机

```bash
python -m moonraker_simulator --host 0.0.0.0 --port 7125
```

## API 端点

模拟器实现了以下主要 API 端点：

- `GET /server/info` - 服务器信息
- `GET /printer/info` - 打印机信息
- `GET /printer/objects/query` - 查询打印机对象状态
- `GET /printer/objects/list` - 列出可用的打印机对象
- `GET /server/files/list` - 列出文件
- `POST /printer/print/start` - 开始打印
- `POST /printer/print/cancel` - 取消打印
- `POST /printer/gcode/script` - 执行 G-code 脚本
- `POST /server/restart` - 重启服务器（模拟）

## WebSocket 连接

WebSocket 端点位于 `/websocket`，使用 JSON-RPC 2.0 协议进行通信。

### WebSocket 事件

- `printer.objects.subscribe` - 订阅打印机对象状态更新
- `server.info` - 获取服务器信息
- `notify_status_update` - 服务器推送的状态更新通知

### WebSocket 消息格式

所有消息使用 JSON-RPC 2.0 格式：

```json
{
  "jsonrpc": "2.0",
  "method": "method_name",
  "params": {...},
  "id": 1
}
```

## 示例

### 使用 curl 测试 API

```bash
# 获取服务器信息
curl http://localhost:7125/server/info

# 获取打印机信息
curl http://localhost:7125/printer/info

# 查询温度传感器
curl "http://localhost:7125/printer/objects/query?objects=temperature_sensor,heater_bed"
```

### 使用 Python 客户端

```python
import requests

# 获取服务器信息
response = requests.get("http://localhost:7125/server/info")
print(response.json())

# 开始打印
response = requests.post(
    "http://localhost:7125/printer/print/start",
    json={"filename": "test.gcode"}
)
print(response.json())
```

### 使用测试客户端脚本

项目包含一个测试客户端示例，可以测试 REST API、WebSocket 和服务发现功能：

```bash
# 测试所有功能
python simulator_client/example_client.py

# 只测试 REST API
python simulator_client/example_client.py --rest-only

# 只测试 WebSocket
python simulator_client/example_client.py --ws-only

# 只测试服务发现
python simulator_client/example_client.py --discovery-only

# 指定服务器地址
python simulator_client/example_client.py --url http://192.168.1.100:7125

# 自定义服务发现超时时间
python simulator_client/example_client.py --discovery-only --discovery-timeout 10
```

### 服务发现测试

测试客户端支持通过 Zeroconf (mDNS/Bonjour) 在**局域网内**自动发现 Moonraker 服务：

```bash
# 搜索并测试发现的 Moonraker 服务
python simulator_client/example_client.py --discovery-only
```

服务发现功能会：
- **在局域网内自动搜索** Moonraker 服务（使用 mDNS/Bonjour 协议）
- 显示服务的地址、端口和属性
- 自动测试与发现服务的连接
- 验证服务的可用性

#### 局域网服务发现说明

- ✅ **支持局域网搜索**：服务发现使用 mDNS/Bonjour 协议，可以在同一局域网内自动发现服务
- ✅ **无需配置**：只要服务器和客户端在同一局域网，服务会自动被发现
- ⚠️ **防火墙要求**：确保防火墙允许 mDNS/Bonjour 流量（UDP 端口 5353）
- ⚠️ **网络要求**：服务器和客户端必须在同一局域网（同一子网）内

#### 使用场景

1. **本地开发**：在同一台机器上运行服务器和客户端
2. **局域网测试**：在不同设备上运行，但连接到同一 WiFi/以太网
3. **多设备部署**：在局域网内部署多个 Moonraker 模拟器实例

## 技术栈

- **Tornado** - 异步 Web 框架和 WebSocket 支持
- **Zeroconf** - 服务发现
- **JSON-RPC 2.0** - WebSocket 通信协议

## 注意事项

这是一个最小化的模拟器，主要用于开发和测试。它不包含完整的 Moonraker 功能，也不连接到真实的 Klipper 固件。

模拟器使用 Tornado 框架实现，提供高性能的异步 I/O 和原生 WebSocket 支持。

## 许可证

MIT License

