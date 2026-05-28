# Xray Node Updater

A lightweight Python script for automatically updating Xray VLESS node configurations from a subscription URL while preserving local routing rules and custom settings.

Designed for:

* Home self-hosted Xray clients
* Ubuntu systems
* Cron-based automatic updates
* Minimal and secure deployments

---

# Features

* Automatically fetch subscription URLs
* Parse VLESS links
* Update only outbound node information
* Preserve existing routing rules
* Preserve local SOCKS/HTTP inbound settings
* Support Reality + Vision
* Auto-create `config.json` from template
* Minimal dependency design
* Suitable for cron automation
* IPv4 / IPv6 compatible

---

# Supported Fields

The script updates:

* Server address
* Port
* UUID
* Flow
* Public key
* Short ID
* SNI

The script preserves:

* Routing rules
* DNS settings
* Inbounds
* Logs
* Local policies

---

# Requirements

* Python 3.8+
* Xray-core
* Linux system (Ubuntu / Debian recommended)

---

# Installation

Clone repository:

```bash
git clone https://github.com/yourname/xray-node-updater.git
cd xray-node-updater
```

Create subscription file:

```bash
echo "https://your-subscription-link" > .subscription
chmod 400 .subscription
```

Prepare template:

```bash
cp config.template.json config.json
```

Run manually:

```bash
python3 update_node.py
```

---

# Cron Example

```cron
22 9 * * * cd /home/username/App/Xray && /usr/bin/python3 update_node.py >> cron.log 2>&1
```

For user-level systemd services:

```cron
XDG_RUNTIME_DIR=/run/user/1000
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
```

---

# Security Recommendations

Recommended permissions:

```bash
chmod 700 update_node.py
chmod 600 config.json
chmod 400 .subscription
```

---

# Disclaimer

This project is intended for lawful self-hosted remote access and configuration management purposes only.

Users are responsible for complying with local laws and network policies.

---

# Xray Node Updater

一个轻量级 Python 脚本，用于从订阅链接自动更新 Xray VLESS 节点配置，同时保留本地路由规则和自定义配置。

适用于：

* 家庭自建 Xray 客户端
* Ubuntu Linux
* 基于 cron 的自动更新
* 最小化、低依赖、安全部署

---

# 功能特性

* 自动获取订阅链接
* 解析 VLESS 链接
* 仅更新 outbound 节点信息
* 保留现有路由规则
* 保留本地 SOCKS/HTTP 入站
* 支持 Reality + Vision
* 自动从模板创建 `config.json`
* 极简依赖设计
* 支持 cron 自动化
* 支持 IPv4 / IPv6

---

# 支持更新的字段

脚本会更新：

* 服务器地址
* 端口
* UUID
* Flow
* 公钥
* Short ID
* SNI

脚本会保留：

* 路由规则
* DNS 配置
* 入站配置
* 日志配置
* 本地策略

---

# 运行要求

* Python 3.8+
* Xray-core
* Linux 系统（推荐 Ubuntu / Debian）

---

# 安装方法

克隆仓库：

```bash
git clone https://github.com/yourname/xray-node-updater.git
cd xray-node-updater
```

创建订阅文件：

```bash
echo "https://你的订阅链接" > .subscription
chmod 400 .subscription
```

准备模板：

```bash
cp config.template.json config.json
```

手动运行：

```bash
python3 update_node.py
```

---

# Cron 定时更新示例

```cron
22 9 * * * cd /home/username/App/Xray && /usr/bin/python3 update_node.py >> cron.log 2>&1
```

如果使用用户级 systemd 服务：

```cron
XDG_RUNTIME_DIR=/run/user/1000
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
```

---

# 安全建议

推荐权限：

```bash
chmod 700 update_node.py
chmod 600 config.json
chmod 400 .subscription
```
---

# 免责声明

本项目仅用于合法的自建远程访问与配置管理用途。

请自行遵守当地法律法规及网络管理要求。
