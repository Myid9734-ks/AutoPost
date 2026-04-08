#!/usr/bin/env python3
"""
upload_tistory.py
- output/tistory/ 파일을 읽어 티스토리에 자동 업로드
- config/tistory_session.json 세션 파일 사용 (setup_session.py로 생성)
- 실패 시 최대 3회 재시도 + 텔레그램 알림
"""

import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
PROFILE_DIR      = BASE_DIR / "config" / "tistory_profile"
TISTORY_DIR      = BASE_DIR / "output" / "tistory"


# ── 텔레그램 알림 ─────────────────────────────────────────────────────────────

def send_telegram(message: str) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10,
        )
    except Exception:
        pass


# ── 파일 읽기 ──────────────────────────────────────────────────────────────────

def read_output_files() -> dict:
    return {
        "title":    (TISTORY_DIR / "title.txt").read_text(encoding="utf-8").strip(),
        "content":  (TISTORY_DIR / "content.html").read_text(encoding="utf-8").strip(),
        "hashtags": (TISTORY_DIR / "hashtags.txt").read_text(encoding="utf-8").strip(),
        "category": (TISTORY_DIR / "category.txt").read_text(encoding="utf-8").strip(),
    }


# ── 업로드 핵심 로직 ───────────────────────────────────────────────────────────

def upload(page, data: dict) -> None:

    # 1. 티스토리 메인 접속 + 로그인 체크
    print("  [1] 티스토리 메인 접속")
    page.goto("https://www.tistory.com/", wait_until="domcontentloaded")
    time.sleep(2)

    # 로그인 여부 확인 — 글쓰기 버튼 없으면 자동 로그인 시도
    if not page.locator("a.link_tab[href*='newpost']").is_visible():
        print("  [1-1] 로그인 필요 — 카카오 로그인 시도")
        page.locator("a.btn_login.link_kakao_id").click()
        time.sleep(2)
        page.locator("span.txt_login", has_text="카카오계정으로 로그인").click()
        time.sleep(4)
        # 로그인 완료 확인
        if not page.locator("a.link_tab[href*='newpost']").is_visible():
            raise Exception("자동 로그인 실패 — setup_session.py를 다시 실행하세요.")
        print("  [1-1] 로그인 완료")

    print("  [2] 글쓰기 버튼 클릭")
    with page.context.expect_page() as new_page_info:
        page.locator("a.link_tab[href*='newpost']").click()
    write_page = new_page_info.value
    write_page.wait_for_load_state("domcontentloaded")
    time.sleep(2)

    # 2. HTML 모드 전환 (확인 dialog 자동 수락)
    print("  [3] HTML 모드 전환")
    write_page.on("dialog", lambda dialog: dialog.accept())
    write_page.locator("div.mce-tistory-mode").click()
    time.sleep(0.8)
    write_page.evaluate("""
        () => {
            const htmlItem = document.querySelector('div.mce-tistory-mode-item.mce-last');
            if (htmlItem) htmlItem.click();
        }
    """)
    time.sleep(1.5)

    # 3. 제목 입력
    print(f"  [4] 제목 입력: {data['title']}")
    title_input = write_page.locator("textarea#post-title-inp")
    title_input.click()
    title_input.fill(data["title"])
    time.sleep(0.5)

    # 4. 본문 입력 (클립보드 → 붙여넣기)
    print("  [5] 본문 입력")
    import subprocess
    subprocess.run(['pbcopy'], input=data["content"].encode('utf-8'), check=True)
    write_page.locator(".cm-s-tistory-html").click()
    time.sleep(0.3)
    write_page.keyboard.press("Meta+a")
    time.sleep(0.2)
    write_page.keyboard.press("Meta+v")
    time.sleep(1)

    # 5. 카테고리 선택
    print(f"  [6] 카테고리 선택: {data['category']}")
    write_page.locator("button#category-btn").click()
    time.sleep(1)
    write_page.locator("#category-list div.mce-menu-item", has_text=data["category"]).first.click()
    time.sleep(0.5)

    # 6. 태그 입력
    print(f"  [7] 태그 입력: {data['hashtags']}")
    tag_input = write_page.locator("input#tagText")
    for tag in data["hashtags"].split(","):
        tag = tag.strip()
        if tag:
            tag_input.fill(tag)
            tag_input.press("Enter")
            time.sleep(0.3)

    # 7. 완료 버튼 → 공개 발행
    print("  [8] 완료 버튼 클릭")
    write_page.locator("button#publish-layer-btn").click()
    time.sleep(1)

    print("  [9] 공개 발행 클릭")
    write_page.locator("button#publish-btn[type='submit']").click()
    time.sleep(3)

    print("  업로드 완료!")


# ── 재시도 래퍼 ───────────────────────────────────────────────────────────────

def run_with_retry(max_retries: int = 3) -> bool:
    if not PROFILE_DIR.exists():
        print("프로필 디렉토리가 없습니다. 먼저 setup_session.py를 실행하세요.")
        return False

    data = read_output_files()
    print(f"업로드 시작: {data['title']}")

    for attempt in range(1, max_retries + 1):
        print(f"\n[시도 {attempt}/{max_retries}]")
        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(PROFILE_DIR),
                    headless=False,
                    slow_mo=200,
                    viewport={"width": 1280, "height": 900},
                )
                pages = context.pages
                page = pages[0] if pages else context.new_page()
                upload(page, data)
                context.close()

            send_telegram(f"✅ 티스토리 업로드 완료\n제목: {data['title']}")
            return True

        except PlaywrightTimeoutError as e:
            print(f"  타임아웃 오류: {e}")
        except Exception as e:
            print(f"  오류: {e}")

        if attempt < max_retries:
            print(f"  {attempt * 10}초 후 재시도...")
            time.sleep(attempt * 10)

    send_telegram(f"❌ 티스토리 업로드 실패 (3회)\n제목: {data['title']}")
    return False


if __name__ == "__main__":
    success = run_with_retry()
    sys.exit(0 if success else 1)
