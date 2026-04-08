#!/bin/bash
cd /Users/mypc/blog_auto

echo "=== [1/4] 이미지 생성 (티스토리) ===" | tee -a /tmp/autopost.log
python3 scripts/generate_image.py \
  --platform tistory \
  --slug "mac-ai-repeat-work-routine" \
  --prompts '["A Korean office worker using a MacBook to manage repetitive tasks with AI help, clean desk, realistic productivity scene, no text, no watermark", "Close-up of a MacBook with organized work notes and AI assistant workflow, practical office atmosphere, realistic image, no text, no watermark"]' \
  >> /tmp/autopost.log 2>&1

echo "=== [2/4] 이미지 생성 (네이버) ===" | tee -a /tmp/autopost.log
python3 scripts/generate_image.py \
  --platform naver \
  --slug "fatigue-rhythm-motivation-health" \
  --prompts '["A Korean person feeling tired at home in the morning, soft natural light, realistic wellness mood, no text, no watermark", "A Korean person rebuilding a healthy daily routine with calm bedroom and morning light, realistic lifestyle photo, no text, no watermark"]' \
  >> /tmp/autopost.log 2>&1

echo "=== [3/4] 티스토리 업로드 ===" | tee -a /tmp/autopost.log
python3 scripts/upload_tistory.py >> /tmp/autopost.log 2>&1

echo "=== [4/4] 네이버 업로드 ===" | tee -a /tmp/autopost.log
python3 scripts/upload_naver.py >> /tmp/autopost.log 2>&1

echo "=== 전체 완료 (cleanup 미실행) ===" | tee -a /tmp/autopost.log
