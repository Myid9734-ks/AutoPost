#!/usr/bin/env python3
"""
setup_session.py
- 브라우저를 열어 티스토리에 직접 로그인
- 로그인 완료 후 세션(쿠키)을 파일로 저장
- 이후 upload_tistory.py가 저장된 세션을 재사용
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_FILE = Path(__file__).resolve().parent.parent / "config" / "tistory_session.json"
SESSION_FILE.parent.mkdir(exist_ok=True)

print("=" * 50)
print("티스토리 세션 설정")
print("=" * 50)
print("브라우저가 열리면 티스토리에 로그인하세요.")
print("로그인 완료 후 이 터미널에서 Enter를 누르세요.")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto("https://www.tistory.com/")

    print("1. 카카오계정으로 시작하기 클릭")
    print("2. 카카오계정으로 로그인 클릭")
    print("3. 로그인 완료 후 티스토리 메인이 보이면 Enter")
    input("\n로그인 완료 후 Enter 키를 누르세요... ")

    context.storage_state(path=str(SESSION_FILE))
    browser.close()

print(f"\n세션 저장 완료: {SESSION_FILE}")
print("이제 upload_tistory.py를 실행하세요.")
