from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
PORT = 8081


def _wait_for_port(port: int, timeout: float = 8.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.25)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"Server on {port} not ready")


def test_mockup_renders_key_sections() -> None:
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT), "--directory", str(ROOT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_port(PORT)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=os.environ.get("CHROMIUM_PATH") or None,
            )
            page = browser.new_page(viewport={"width": 1500, "height": 900})
            page.goto(f"http://127.0.0.1:{PORT}/src/mockup.html", wait_until="networkidle")

            assert page.get_by_text("Conversations").first.is_visible()
            assert page.get_by_text("Group Debate").first.is_visible()
            assert page.get_by_text("Batch Intelligence").first.is_visible()
            assert page.get_by_text("Run New Batch (20)").first.is_visible()
            assert page.get_by_text("Continue Batch (20) With Notes").first.is_visible()

            out = ROOT / "artifacts" / "screenshots" / "mockup-test.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(out), full_page=True)
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
