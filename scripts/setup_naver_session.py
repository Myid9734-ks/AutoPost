#!/usr/bin/env python3
"""
setup_naver_session.py
- 고정 프로필 디렉토리로 브라우저를 열어 네이버에 로그인
- 로그인 쿠키를 naver_cookies_{N}.json에 만료일 강제 설정하여 저장
- 사용법: python3 setup_naver_session.py [--account 1|2]
"""

import json
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--account", type=int, default=1, choices=[1, 2], help="네이버 계정 번호 (1 또는 2)")
args = parser.parse_args()

N = args.account
PROFILE_DIR  = BASE_DIR / "config" / f"naver_profile_{N}"
COOKIES_FILE = BASE_DIR / "config" / f"naver_cookies_{N}.json"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 50)
print(f"네이버 로그인 프로필 설정 (계정 {N})")
print("=" * 50)
print("브라우저가 열리면 네이버에 로그인하세요.")
print("로그인 완료 후 이 터미널에서 Enter를 누르세요.")
print("=" * 50)

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
    page.goto("https://nid.naver.com/nidlogin.login")

    print(f"  → 계정 {N} 아이디/비밀번호로 로그인하세요.")
    print("  → 로그인 완료 후 Enter를 누르세요.")
    input("\n로그인 완료 후 Enter 키를 누르세요... ")

    # 쿠키 저장 — 세션 쿠키에 만료일 30일 강제 부여
    cookies = context.cookies()
    for c in cookies:
        if c.get("expires", -1) == -1:
            c["expires"] = time.time() + 86400 * 30
    json.dump(cookies, open(str(COOKIES_FILE), "w"), ensure_ascii=False, indent=2)
    print(f"  쿠키 저장 완료: {COOKIES_FILE} ({len(cookies)}개)")

    context.close()

print(f"\n프로필 저장 완료: {PROFILE_DIR}")
print(f"쿠키 저장 완료: {COOKIES_FILE}")
print(f"이제 upload_naver.py --account {N} 을 실행하세요.")
