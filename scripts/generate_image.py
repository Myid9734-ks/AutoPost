#!/usr/bin/env python3
"""
generate_image.py
- AI가 결정한 프롬프트 목록을 받아 DALL-E 3로 이미지 생성
- images/ 에 임시 저장 후 NAS blog_images/ 에 복사
- 외부 접근 가능한 URL 목록을 출력
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

# 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NAS_IMAGE_URL  = os.getenv("NAS_IMAGE_URL", "").rstrip("/")
NAS_MOUNT_PATH = os.getenv("NAS_MOUNT_PATH", "")

IMAGES_DIR = BASE_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)


def download_and_compress(url: str, dest_path: Path, jpeg_quality: int = 85) -> None:
    """DALL-E 3 임시 URL에서 다운로드 후 JPEG 압축 저장"""
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    tmp_png = dest_path.with_suffix(".tmp.png")
    tmp_png.write_bytes(response.content)

    img = Image.open(tmp_png).convert("RGB")
    img.save(dest_path, format="JPEG", quality=jpeg_quality, optimize=True)
    tmp_png.unlink()


def copy_to_nas(src_path: Path, filename: str) -> str:
    """NAS 마운트 경로에 파일 복사 후 외부 URL 반환"""
    nas_path = Path(NAS_MOUNT_PATH)

    if not nas_path.exists():
        raise RuntimeError(
            f"NAS 마운트 경로를 찾을 수 없습니다: {NAS_MOUNT_PATH}\n"
            "Finder에서 NAS가 연결되어 있는지 확인하세요."
        )

    dest = nas_path / filename
    shutil.copy2(src_path, dest)
    return f"{NAS_IMAGE_URL}/{filename}"


def generate_images(slug: str, prompts: list[str]) -> list[str]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    today  = datetime.now().strftime("%Y%m%d")
    urls   = []

    for i, prompt in enumerate(prompts):
        seq      = str(i + 1).zfill(3)
        filename = f"{today}_{slug}_{seq}.jpg"
        tmp_path = IMAGES_DIR / filename

        print(f"[{i+1}/{len(prompts)}] 이미지 생성 중: {filename}")
        print(f"  프롬프트: {prompt[:80]}...")

        # DALL-E 3 생성 (1024x1024 고정, standard 퀄리티)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        dalle_url = response.data[0].url

        # 다운로드 + JPEG 압축
        download_and_compress(dalle_url, tmp_path)
        print(f"  임시 저장: {tmp_path}")

        # NAS 복사
        public_url = copy_to_nas(tmp_path, filename)
        print(f"  NAS 업로드 완료: {public_url}")

        urls.append(public_url)

    return urls


def main():
    parser = argparse.ArgumentParser(description="DALL-E 3 이미지 생성 + NAS 업로드")
    parser.add_argument("--slug",    required=True, help="주제 슬러그 (예: ai-trend)")
    parser.add_argument("--prompts", required=True, help="이미지 프롬프트 목록 (JSON 배열)")
    args = parser.parse_args()

    try:
        prompts = json.loads(args.prompts)
    except json.JSONDecodeError:
        print("오류: --prompts 값이 올바른 JSON 배열이 아닙니다.", file=sys.stderr)
        sys.exit(1)

    if not prompts:
        print("오류: 프롬프트 목록이 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    if not OPENAI_API_KEY:
        print("오류: .env에 OPENAI_API_KEY가 없습니다.", file=sys.stderr)
        sys.exit(1)

    if not NAS_MOUNT_PATH:
        print("오류: .env에 NAS_MOUNT_PATH가 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"총 {len(prompts)}장 생성 시작 (슬러그: {args.slug})\n")

    urls = generate_images(args.slug, prompts)

    print("\n생성 완료 — URL 목록:")
    for url in urls:
        print(f"  {url}")

    # content.html 플레이스홀더 교체 ({{IMAGE_1}}, {{IMAGE_2}}, ...)
    for platform in ["tistory", "naver"]:
        content_path = BASE_DIR / "output" / platform / "content.html"
        if content_path.exists():
            html = content_path.read_text(encoding="utf-8")
            for i, url in enumerate(urls):
                html = html.replace(f"{{{{IMAGE_{i+1}}}}}", f'<img src="{url}" style="max-width:100%;" alt="이미지{i+1}">')
            content_path.write_text(html, encoding="utf-8")
            print(f"  {platform}/content.html 이미지 URL 삽입 완료")

    print("\n[JSON]")
    print(json.dumps(urls, ensure_ascii=False))


if __name__ == "__main__":
    main()
