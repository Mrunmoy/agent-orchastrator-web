#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import socket
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "screenshots" / "mockup-latest.png"


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, timeout: float = 8.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port):
            return
        time.sleep(0.1)
    raise RuntimeError(f"Server on port {port} did not start in time")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture screenshot of mock UI")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server_proc = None
    started_here = False

    try:
        if not is_port_open(args.port):
            server_proc = subprocess.Popen(
                ["python3", "-m", "http.server", str(args.port), "--directory", str(ROOT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            started_here = True
            wait_for_port(args.port)

        url = f"http://127.0.0.1:{args.port}/src/mockup.html"
        OUT.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=os.environ.get("CHROMIUM_PATH") or None,
            )
            page = browser.new_page(viewport={"width": 1600, "height": 980})
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=str(OUT), full_page=True)
            browser.close()

        print(f"Saved screenshot: {OUT}")
        return 0
    finally:
        if started_here and server_proc is not None:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server_proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
