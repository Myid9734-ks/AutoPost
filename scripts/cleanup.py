#!/usr/bin/env python3
"""
cleanup.py
- 업로드 완료 후 정리 작업
  1. output/tistory/, output/naver/ 파일 삭제
  2. images/ 로컬 캐시 이미지 삭제
  3. logs/run_log.txt 에 실행 기록 추가
  4. logs/used_titles.json 에 제목 기록 (중복 방지용)
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_TISTORY = BASE_DIR / "output" / "tistory"
OUTPUT_NAVER   = BASE_DIR / "output" / "naver"
IMAGES_DIR     = BASE_DIR / "images"
LOGS_DIR       = BASE_DIR / "logs"
RUN_LOG        = LOGS_DIR / "run_log.txt"
USED_TITLES    = LOGS_DIR / "used_titles.json"


def load_used_titles() -> list:
    if USED_TITLES.exists():
        try:
            return json.loads(USED_TITLES.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_used_titles(titles: list) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    USED_TITLES.write_text(json.dumps(titles, ensure_ascii=False, indent=2), encoding="utf-8")


def read_title_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def delete_output_files() -> dict:
    """output/ 하위 txt, html 파일 삭제"""
    deleted = []
    for folder in [OUTPUT_TISTORY, OUTPUT_NAVER]:
        if folder.exists():
            for f in folder.iterdir():
                if f.suffix in (".txt", ".html"):
                    f.unlink()
                    deleted.append(str(f.relative_to(BASE_DIR)))
    return {"deleted_output": deleted}


def delete_local_images() -> dict:
    """images/ 로컬 캐시 이미지 삭제"""
    deleted = []
    if IMAGES_DIR.exists():
        for f in IMAGES_DIR.iterdir():
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                f.unlink()
                deleted.append(f.name)
    return {"deleted_images": deleted}


def write_run_log(title_tistory: str, title_naver: str, results: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"\n{'='*60}",
        f"[{now}] 실행 완료",
        f"  Tistory 제목 : {title_tistory or '(없음)'}",
        f"  Naver 제목   : {title_naver or '(없음)'}",
        f"  삭제 output  : {len(results.get('deleted_output', []))}개",
        f"  삭제 images  : {len(results.get('deleted_images', []))}개",
    ]
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  로그 기록: {RUN_LOG}")


def record_titles(title_tistory: str, title_naver: str) -> None:
    titles = load_used_titles()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if title_tistory:
        titles.append({"title": title_tistory, "platform": "tistory", "date": now})
    if title_naver:
        titles.append({"title": title_naver, "platform": "naver", "date": now})
    save_used_titles(titles)
    print(f"  사용 제목 기록: {USED_TITLES} ({len(titles)}개 누적)")


def main() -> None:
    print("=== cleanup.py 시작 ===")

    # 제목 먼저 읽기 (파일 삭제 전)
    title_tistory = read_title_safe(OUTPUT_TISTORY / "title.txt")
    title_naver   = read_title_safe(OUTPUT_NAVER   / "title.txt")

    print(f"\n[1] output 파일 삭제")
    r1 = delete_output_files()
    for f in r1["deleted_output"]:
        print(f"  - {f}")

    print(f"\n[2] 로컬 이미지 캐시 삭제")
    r2 = delete_local_images()
    for f in r2["deleted_images"]:
        print(f"  - {f}")

    print(f"\n[3] 실행 로그 기록")
    results = {**r1, **r2}
    write_run_log(title_tistory, title_naver, results)

    print(f"\n[4] 사용 제목 기록")
    record_titles(title_tistory, title_naver)

    print("\n=== cleanup 완료 ===")


if __name__ == "__main__":
    main()
