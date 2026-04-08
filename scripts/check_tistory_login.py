#!/usr/bin/env python3
"""티스토리 로그인 상태만 확인 — 프로필로 블로그 열기"""

from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR    = Path(__file__).resolve().parent.parent
PROFILE_DIR = BASE_DIR / "config" / "tistory_profile"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        channel="chrome",
        headless=False,
        slow_mo=100,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
        ignore_default_args=["--enable-automation"],
    )

    pages = context.pages
    page = pages[0] if pages else context.new_page()
    page.goto("https://www.tistory.com", wait_until="domcontentloaded")

    input("\n확인 후 Enter를 누르면 브라우저가 닫힙니다...")
    context.close()
