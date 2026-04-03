#!/bin/bash
cd /Users/mypc/blog_auto

python3 scripts/generate_image.py \
  --slug "ai-prompt-health-0402" \
  --prompts '["A professional person working on a laptop with AI assistant interface on screen, clean modern office, soft lighting, flat illustration style", "Colorful healthy foods rich in zinc magnesium and omega3 including oysters salmon spinach and nuts arranged on white background, food photography style", "Top view of nutritious meal prep with various vegetables seafood and nuts, vibrant colors, clean minimal style"]'

python3 scripts/upload_tistory.py

python3 scripts/upload_naver.py

python3 scripts/cleanup.py
