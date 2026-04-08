#!/usr/bin/env python3
"""네이버 로그인 상태 확인 — 사용법: python3 check_naver_login.py [--account 1|2]"""

import json
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--account", type=int, default=1, choices=[1, 2])
args = parser.parse_args()

N = args.account
PROFILE_DIR  = BASE_DIR / "config" / f"naver_profile_{N}"
COOKIES_FILE = BASE_DIR / "config" / f"naver_cookies_{N}.json"

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

    if COOKIES_FILE.exists():
        cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
        context.add_cookies(cookies)
        print(f"쿠키 복원: {len(cookies)}개 (계정 {N})")
    else:
        print(f"쿠키 파일 없음 (계정 {N})")

    pages = context.pages
    page = pages[0] if pages else context.new_page()
    page.goto("https://blog.naver.com", wait_until="domcontentloaded")

    input("\n확인 후 Enter를 누르면 브라우저가 닫힙니다...")
    context.close()
