#!/bin/bash
cd /Users/mypc/blog_auto

echo "=== [1/3] 이미지 생성 (네이버) ===" | tee -a /tmp/autopost_naver.log
python3 scripts/generate_image.py \
  --platform naver \
  --slug "korea-stock-market-close-briefing" \
  --prompts '["Korean stock market closing scene with financial charts on monitors, professional trading desk, blue and red market mood, realistic finance atmosphere, no text, no watermark", "A Korean investor reviewing market charts and notes after market close, calm analytical mood, realistic office scene, no text, no watermark"]' \
  >> /tmp/autopost_naver.log 2>&1

echo "=== [2/3] 네이버 업로드 ===" | tee -a /tmp/autopost_naver.log
python3 scripts/upload_naver.py >> /tmp/autopost_naver.log 2>&1

echo "=== [3/3] 정리 ===" | tee -a /tmp/autopost_naver.log
python3 scripts/cleanup.py >> /tmp/autopost_naver.log 2>&1

echo "=== 전체 완료 ===" | tee -a /tmp/autopost_naver.log
