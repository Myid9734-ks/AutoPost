#!/usr/bin/env python3
"""
upload_naver.py
- output/naver/ 파일을 읽어 네이버 블로그에 자동 업로드
- content.html을 새 탭에서 열어 전체 복사 → 스마트에디터 붙여넣기
- 실패 시 최대 3회 재시도 + 텔레그램 알림
"""

import os
import sys
import time
import random
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
SESSION_FILE     = BASE_DIR / "config" / "naver_session.json"
NAVER_DIR        = BASE_DIR / "output" / "naver"
CONTENT_FILE     = NAVER_DIR / "content.html"


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
        "title":    (NAVER_DIR / "title.txt").read_text(encoding="utf-8").strip(),
        "content":  CONTENT_FILE.read_text(encoding="utf-8").strip(),
        "hashtags": (NAVER_DIR / "hashtags.txt").read_text(encoding="utf-8").strip(),
        "category": (NAVER_DIR / "category.txt").read_text(encoding="utf-8").strip(),
    }


# ── 업로드 핵심 로직 ───────────────────────────────────────────────────────────

def upload(context, data: dict) -> None:

    # 1. 네이버 블로그 접속
    print("  [1] 네이버 블로그 접속")
    page = context.new_page()
    page.goto("https://blog.naver.com/myid9734", wait_until="domcontentloaded")
    time.sleep(2)

    # 2. 글쓰기 버튼 클릭 (iframe 안에 있음)
    print("  [2] 글쓰기 클릭")
    for frame in page.frames:
        btn = frame.query_selector("a._checkBlock._rosRestrict")
        if btn:
            btn.click()
            break
    time.sleep(3)

    # 스마트에디터 iframe 진입
    editor_frame = page.frame_locator("iframe#mainFrame")

    # 2-1. 이전 글 이어쓰기 팝업 처리 — "취소" = 새 글 쓰기
    try:
        popup = editor_frame.locator("div.se-popup-alert-confirm")
        if popup.is_visible(timeout=4000):
            popup.locator("button").first.click()  # 취소(새 글)
            time.sleep(1)
    except Exception:
        pass

    # 3. 제목 입력
    print(f"  [3] 제목 입력: {data['title']}")
    title_area = editor_frame.locator("p.se-text-paragraph").first
    title_area.click()
    time.sleep(0.5)
    page.keyboard.press("Meta+a")
    time.sleep(0.2)
    page.keyboard.type(data["title"], delay=30)
    time.sleep(0.5)

    # 4. 본문 붙여넣기 (content.html → 클립보드 → 붙여넣기)
    print("  [4] 본문 입력 (클립보드 붙여넣기)")

    # content.html을 새 탭에서 열고 전체 복사
    html_page = context.new_page()
    html_page.goto(f"file://{CONTENT_FILE}")
    time.sleep(1)
    html_page.keyboard.press("Meta+a")
    time.sleep(0.3)
    html_page.keyboard.press("Meta+c")
    time.sleep(0.5)
    html_page.close()

    # 본문 영역 클릭 후 붙여넣기
    # 1순위: placeholder has_text
    body_area = editor_frame.locator("span.se-placeholder").filter(has_text="글감과 함께")
    if body_area.count() > 0 and body_area.first.is_visible():
        body_area.first.click()
    else:
        # draft 로드된 경우 — Tab으로 본문 이동 후 전체선택
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("Meta+a")
        time.sleep(0.3)
    time.sleep(0.5)
    page.keyboard.press("Meta+v")
    time.sleep(random.uniform(1.5, 2.5))

    # 5. 발행 버튼 클릭 (1차) - 도움말 패널 먼저 닫기
    print("  [5] 발행 버튼 클릭")
    close_btn = editor_frame.locator("button.se-help-panel-close-button")
    if close_btn.count() > 0 and close_btn.first.is_visible():
        close_btn.first.click()
        time.sleep(0.5)
    editor_frame.locator("button.publish_btn__m9KHH").click()
    time.sleep(2)

    # 6. 카테고리 선택 — 드롭다운 열고 li에서 선택
    print(f"  [6] 카테고리 선택: {data['category']}")
    time.sleep(1)
    editor_frame.locator("span.text__sraQE").first.click()  # 드롭다운 열기
    time.sleep(1)
    editor_frame.locator("[class*='option_category'] li").filter(has_text=data["category"]).first.click(timeout=10000)
    time.sleep(0.5)

    # 7. 태그 입력
    print(f"  [7] 태그 입력: {data['hashtags']}")
    tag_input = editor_frame.locator("input#tag-input")
    for tag in data["hashtags"].split(","):
        tag = tag.strip()
        if tag:
            tag_input.fill(tag)
            tag_input.press("Enter")
            time.sleep(random.uniform(0.3, 0.6))

    # 8. 최종 발행
    print("  [8] 최종 발행")
    editor_frame.locator("button.confirm_btn__WEaBq").click()
    time.sleep(3)

    print("  업로드 완료!")
    page.close()


# ── 재시도 래퍼 ───────────────────────────────────────────────────────────────

def run_with_retry(max_retries: int = 3) -> bool:
    if not SESSION_FILE.exists():
        print("세션 파일이 없습니다. 먼저 setup_naver_session.py를 실행하세요.")
        return False

    data = read_output_files()
    print(f"업로드 시작: {data['title']}")

    for attempt in range(1, max_retries + 1):
        print(f"\n[시도 {attempt}/{max_retries}]")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, slow_mo=200)
                context = browser.new_context(
                    storage_state=str(SESSION_FILE),
                    viewport={"width": 1280, "height": 900},
                )
                upload(context, data)
                browser.close()

            send_telegram(f"✅ 네이버 업로드 완료\n제목: {data['title']}")
            return True

        except PlaywrightTimeoutError as e:
            print(f"  타임아웃 오류: {e}")
        except Exception as e:
            print(f"  오류: {e}")

        if attempt < max_retries:
            delay = attempt * 10 + random.randint(1, 5)
            print(f"  {delay}초 후 재시도...")
            time.sleep(delay)

    send_telegram(f"❌ 네이버 업로드 실패 (3회)\n제목: {data['title']}")
    return False


if __name__ == "__main__":
    success = run_with_retry()
    sys.exit(0 if success else 1)
