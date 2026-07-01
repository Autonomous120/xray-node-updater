#!/usr/bin/env python3

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.umask(0o077)

import json
import base64
import urllib.parse
import socket
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_FILE = BASE_DIR / "config.template.json"
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
        raise Exception("curl download failed")

    raw = result.stdout.strip()

    if not raw:
        raise Exception("subscription is empty")

    if raw.startswith("vless://"):
        return raw

    try:
        decoded = base64.b64decode(raw).decode()

        for line in decoded.splitlines():
            line = line.strip()

            if line.startswith("vless://"):
                return line

    except Exception as e:
        print("Base64 decode failed:", e)

    raise Exception("No valid VLESS link found")

def parse_vless(link):
    parsed = urllib.parse.urlparse(link)

    uuid = parsed.username
    address = parsed.hostname
    port = parsed.port

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

    if q("security") == "reality":
        outbound["streamSettings"]["realitySettings"] = {
            "serverName": q("sni"),
            "fingerprint": q("fp", "chrome"),
            "publicKey": q("pbk"),
            "shortId": q("sid"),
            "spiderX": q("spx", "/")
        }

    elif q("security") == "tls":
        outbound["streamSettings"]["tlsSettings"] = {
            "serverName": q("sni"),
            "allowInsecure": False
        }

    return outbound

def update_config(outbound):

    if not OUTPUT_FILE.exists():
        print("config.json not found")
        print("Creating from template...")

        shutil.copy(TEMPLATE_FILE, OUTPUT_FILE)

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
        print(result.stderr)
        raise Exception("Xray config test failed")

    shutil.move(temp_file, OUTPUT_FILE)

    os.chmod(OUTPUT_FILE, 0o600)

    print("Config updated successfully")

def restart_xray():
    subprocess.run(["systemctl", "--user", "restart", "xray"])

def main():
    link = load_subscription()

    print("Subscription loaded")

    outbound = parse_vless(link)

    update_config(outbound)

    restart_xray()

    print("Xray restarted")

if __name__ == "__main__":
    main()
