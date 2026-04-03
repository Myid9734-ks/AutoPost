#!/usr/bin/env python3
"""
setup_session.py
- 고정 프로필 디렉토리로 브라우저를 열어 티스토리에 로그인
- 로그인 정보가 config/tistory_profile/ 에 영구 저장
- 이후 upload_tistory.py가 같은 프로필로 자동 재사용
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path(__file__).resolve().parent.parent / "config" / "tistory_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 50)
print("티스토리 로그인 프로필 설정")
print("=" * 50)
print("브라우저가 열리면 티스토리에 로그인하세요.")
print("로그인 완료 후 이 터미널에서 Enter를 누르세요.")
print("=" * 50)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        slow_mo=100,
        viewport={"width": 1280, "height": 900},
    )
    page = context.new_page()
    page.goto("https://www.tistory.com/")

    print("1. 카카오계정으로 시작하기 클릭")
    print("2. 카카오계정으로 로그인 클릭")
    print("3. 로그인 완료 후 티스토리 메인이 보이면 Enter")
    input("\n로그인 완료 후 Enter 키를 누르세요... ")

    context.close()

print(f"\n프로필 저장 완료: {PROFILE_DIR}")
print("이제 upload_tistory.py를 실행하세요.")
