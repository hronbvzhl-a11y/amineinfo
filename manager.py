#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
import time

# ==============================================================================
# الإعدادات الأساسية
# ==============================================================================
PORT = int(os.environ.get("PORT", "8080"))
FIXED_UUID = os.environ.get(
    "XRAY_UUID", "2418a096-7b44-42b7-8db1-e289bfad04c2"
)
WS_PATH = os.environ.get("XRAY_WS_PATH", "/@pycorav1")

XRAY_BIN = "/usr/local/bin/xray"
CONFIG_PATH = "/usr/local/etc/xray/config.json"


def log(msg):
    print(f"[XRAY] {msg}", flush=True)


def build_and_save_config():
    """إنشاء ملف إعدادات Xray النظيف مع VLESS عبر WebSocket"""
    config = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": PORT,
                "listen": "0.0.0.0",
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": FIXED_UUID,
                            "level": 0
                        }
                    ],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {
                        "path": WS_PATH
                    }
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "freedom",
                "tag": "direct"
            },
            {
                "protocol": "blackhole",
                "tag": "block"
            }
        ]
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    log(f"Config generated for UUID: {FIXED_UUID} on port {PORT}")


def main():
    build_and_save_config()

    # تشغيل Xray مباشرة ومراقبة عمله
    cmd = [XRAY_BIN, "run", "-config", CONFIG_PATH]
    log(f"Starting Xray core...")

    while True:
        try:
            process = subprocess.Popen(cmd)
            process.wait()
            log("Xray stopped unexpectedly. Restarting in 2 seconds...")
            time.sleep(2)
        except KeyboardInterrupt:
            log("Shutting down...")
            if process:
                process.terminate()
            sys.exit(0)


if name == "main":
    main()
