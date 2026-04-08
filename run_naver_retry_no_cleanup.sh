#!/bin/bash
cd /Users/mypc/blog_auto

echo "=== [1/2] 이미지 생성 (네이버) ===" | tee -a /tmp/autopost_naver_retry.log
python3 scripts/generate_image.py \
  --platform naver \
  --slug "relationship-conversation-health-check" \
  --prompts '["A Korean couple sitting together in emotional tension, quiet relationship mood, soft indoor light, realistic lifestyle photo, no text, no watermark", "A Korean couple having a sincere but slightly difficult conversation in a cozy room, emotional realism, no text, no watermark"]' \
  >> /tmp/autopost_naver_retry.log 2>&1

echo "=== [2/2] 네이버 업로드 ===" | tee -a /tmp/autopost_naver_retry.log
python3 scripts/upload_naver.py >> /tmp/autopost_naver_retry.log 2>&1

echo "=== 전체 완료 ===" | tee -a /tmp/autopost_naver_retry.log
