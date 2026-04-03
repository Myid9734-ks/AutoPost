#!/bin/bash
cd /Users/mypc/blog_auto

echo "=== [1/5] 이미지 생성 (티스토리) ===" | tee -a /tmp/autopost.log
python3 scripts/generate_image.py \
  --platform tistory \
  --slug "mac-ai-routine-repeat-work" \
  --prompts '["A Korean office worker using a MacBook with AI assistant for daily work automation, clean desk, realistic productivity scene, no text, no watermark", "Close-up of a MacBook screen with organized work tasks and AI workflow, neat office lighting, realistic productivity image, no text, no watermark"]' \
  >> /tmp/autopost.log 2>&1

echo "=== [2/5] 이미지 생성 (네이버) ===" | tee -a /tmp/autopost.log
python3 scripts/generate_image.py \
  --platform naver \
  --slug "relationship-tiredness-health-check" \
  --prompts '["A Korean couple sitting together but looking emotionally tired, calm home setting, soft natural light, realistic relationship mood, no text, no watermark", "A Korean couple having a quiet heartfelt conversation in a cozy room, emotional healing atmosphere, realistic lifestyle photo, no text, no watermark"]' \
  >> /tmp/autopost.log 2>&1

echo "=== [3/5] 티스토리 업로드 ===" | tee -a /tmp/autopost.log
python3 scripts/upload_tistory.py >> /tmp/autopost.log 2>&1

echo "=== [4/5] 네이버 업로드 ===" | tee -a /tmp/autopost.log
python3 scripts/upload_naver.py >> /tmp/autopost.log 2>&1

echo "=== [5/5] 정리 ===" | tee -a /tmp/autopost.log
python3 scripts/cleanup.py >> /tmp/autopost.log 2>&1

echo "=== 전체 완료 ===" | tee -a /tmp/autopost.log
