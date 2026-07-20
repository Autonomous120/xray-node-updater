#!/usr/bin/env python3

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.umask(0o077)

import json
import base64
import urllib.parse
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

HYSTERIA_TEMPLATE = BASE_DIR / "config.template.hysteria.json"
VLESS_TLS_TEMPLATE = BASE_DIR / "config.template.vless.tls.json"
VLESS_REALITY_TEMPLATE = BASE_DIR / "config.template.vless.reality.json"
OUTPUT_FILE = BASE_DIR / "config.json"
SUB_FILE = BASE_DIR / ".subscription"
XRAY_BIN = BASE_DIR / "xray"

def load_subscription():

    sub_url = SUB_FILE.read_text().strip()

    print("Downloading subscription...")

    result = subprocess.run(
        [
            "curl",
            "-4",
            "-L",
            "--connect-timeout", "5",
            "--max-time", "15",
            sub_url
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr.strip())

    raw = result.stdout.strip()

    if not raw:
        raise Exception("subscription is empty")

    protocols = (
        "hysteria2://",
        "hy2://",
        "vless://"
    )

    for p in protocols:
        if raw.startswith(p):
            return raw


    try:
        decoded = base64.b64decode(raw).decode()

        for line in decoded.splitlines():

            line = line.strip()

            for p in protocols:
                if line.startswith(p):
                    return line

    except Exception as e:
        print("Base64 decode failed:", e)


    raise Exception("No supported node found")

def detect_protocol(link):

    if link.startswith(("hysteria2://", "hy2://")):
        return "hysteria"

    if link.startswith("vless://"):
        qs = urllib.parse.parse_qs(
            urllib.parse.urlparse(link).query
        )

        security = qs.get(
            "security",
            [""]
        )[0]

        if security == "tls":
            return "vless_tls"

        elif security == "reality":
            return "vless_reality"

    raise Exception("Unsupported protocol")

def parse_hysteria(link):

    parsed = urllib.parse.urlparse(link)

    qs = urllib.parse.parse_qs(parsed.query)

    def q(name, default=""):
        return qs.get(name, [default])[0]

    address = parsed.hostname
    port = parsed.port

    if not address or not port:
        raise Exception(
            "Missing hysteria server address or port"
        )


    print("Server:", f"{address}:{port}")
    
    password = parsed.username
    
    if not password:
        raise Exception(
            "Missing hysteria password"
        )
    
    salamander = q("obfs-password")

    if not salamander:
        raise Exception(
            "Missing salamander password"
        )

    outbound = {
        "protocol": "hysteria",
        "tag": "proxy",
        "settings": {
            "version": 2,
            "address": address,
            "port": port
        },
        "streamSettings": {
            "network": "hysteria",
            "hysteriaSettings": {
                "version": 2,
                "auth": password
            },
            "security": "tls",
            "tlsSettings": {
                "serverName": q("sni", address)
            },
            "finalmask": {
                "udp": [
                    {
                        "type": "salamander",
                        "settings": {
                            "password": salamander
                        }
                    }
                ]
            }
        }
    }

    return outbound

def parse_vless(link):
    parsed = urllib.parse.urlparse(link)

    uuid = parsed.username
    address = parsed.hostname
    port = parsed.port
    
    if not address or not port:
        raise Exception(
            "Missing vless server address or port"
        )


    print("Server:", f"{address}:{port}")

    qs = urllib.parse.parse_qs(parsed.query)

    def q(name, default=""):
        return qs.get(name, [default])[0]

    outbound = {
        "protocol": "vless",
        "tag": "proxy",
        "settings": {
            "vnext": [
                {
                    "address": address,
                    "port": port,
                    "users": [
                        {
                            "id": uuid,
                            "encryption": "none",
                            "flow": q("flow")
                        }
                    ]
                }
            ]
        },
        "streamSettings": {
            "network": q("type", "tcp"),
            "security": q("security"),
        }
    }
    
    if q("security") == "tls":
        outbound["streamSettings"]["tlsSettings"] = {
            "serverName": q("sni")
        }

    elif q("security") == "reality":
        outbound["streamSettings"]["realitySettings"] = {
            "serverName": q("sni"),
            "fingerprint": q("fp", "chrome"),
            "publicKey": q("pbk"),
            "shortId": q("sid"),
            "spiderX": q("spx", "/")
        }

    return outbound

def ensure_template(protocol):

    if protocol == "hysteria":
        template = HYSTERIA_TEMPLATE

    elif protocol == "vless_tls":
        template = VLESS_TLS_TEMPLATE

    elif protocol == "vless_reality":
        template = VLESS_REALITY_TEMPLATE

    else:
        raise Exception(
            f"Unsupported protocol: {protocol}"
        )


    print("Creating config from template:", template)

    shutil.copy(template, OUTPUT_FILE)

def update_config(outbound):

    config = json.loads(OUTPUT_FILE.read_text())

    found = False

    for i, ob in enumerate(config["outbounds"]):
        if ob.get("tag") == "proxy":
            config["outbounds"][i] = outbound
            found = True
            break

    if not found:
        raise Exception("proxy outbound not found")

    temp_file = BASE_DIR / "config.test.json"

    temp_file.write_text(
        json.dumps(config, indent=2, ensure_ascii=False)
    )

    print("Testing config...")

    result = subprocess.run(
        [XRAY_BIN, "run", "-test", "-config", str(temp_file)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        raise Exception("Xray config test failed")

    shutil.move(temp_file, OUTPUT_FILE)

    os.chmod(OUTPUT_FILE, 0o600)

    print("Config updated successfully")

def restart_xray():
    result = subprocess.run(
        ["systemctl", "--user", "restart", "xray"]
    )

    if result.returncode != 0:
        raise Exception("Failed to restart xray")

def main():

    link = load_subscription()

    print("Subscription loaded")


    protocol = detect_protocol(link)


    print(
        "Detected protocol:",
        protocol
    )


    if protocol == "hysteria":
        outbound = parse_hysteria(link)
    else:
        outbound = parse_vless(link)


    ensure_template(protocol)

    update_config(outbound)

    restart_xray()

    print("Xray restarted")

if __name__ == "__main__":
    main()
