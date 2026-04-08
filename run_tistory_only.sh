#!/bin/bash
cd /Users/mypc/blog_auto

echo "=== [1/2] 이미지 생성 (티스토리) ===" | tee -a /tmp/autopost_tistory.log
python3 scripts/generate_image.py \
  --platform tistory \
  --slug "macbook-work-memo-ai" \
  --prompts '["A Korean office worker organizing work notes on a MacBook with AI assistance, clean desk, realistic productivity scene, no text, no watermark", "Close-up of a MacBook with structured memo workflow and AI note organization, practical office atmosphere, realistic image, no text, no watermark"]' \
  >> /tmp/autopost_tistory.log 2>&1

echo "=== [2/2] 티스토리 업로드 ===" | tee -a /tmp/autopost_tistory.log
python3 scripts/upload_tistory.py >> /tmp/autopost_tistory.log 2>&1

echo "=== 전체 완료 (cleanup 미실행) ===" | tee -a /tmp/autopost_tistory.log
