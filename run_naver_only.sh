#!/bin/bash
cd /Users/mypc/blog_auto

echo "=== [1/1] 네이버 업로드 ===" | tee -a /tmp/autopost_naver.log
python3 scripts/upload_naver.py >> /tmp/autopost_naver.log 2>&1

echo "=== 전체 완료 (cleanup 미실행) ===" | tee -a /tmp/autopost_naver.log
