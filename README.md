# AutoPost

AI 기반 블로그 자동화 시스템 — **티스토리**와 **네이버 블로그**에 동시 자동 업로드

## 주요 기능

- **DALL-E 3** 이미지 자동 생성 및 Synology NAS 업로드
- **Playwright** 기반 티스토리 / 네이버 블로그 자동 업로드
- 업로드 성공/실패 시 **텔레그램** 알림
- 사용된 제목 누적 기록으로 중복 방지
- 실행 로그 자동 저장

---

## 폴더 구조

```
blog_auto/
├── .env                    ← API 키 및 계정 정보 (직접 작성)
├── .env.example            ← 환경변수 샘플
├── config/
│   ├── tistory_session.json  ← 세션 저장 (자동 생성)
│   └── naver_session.json    ← 세션 저장 (자동 생성)
├── output/
│   ├── tistory/            ← 티스토리 업로드 콘텐츠
│   └── naver/              ← 네이버 업로드 콘텐츠
├── images/                 ← 생성 이미지 임시 저장
├── logs/
│   ├── run_log.txt         ← 실행 로그
│   └── used_titles.json    ← 발행된 제목 누적
└── scripts/
    ├── generate_image.py   ← DALL-E 이미지 생성 + NAS 업로드
    ├── upload_tistory.py   ← 티스토리 자동 업로드
    ├── upload_naver.py     ← 네이버 자동 업로드
    ├── cleanup.py          ← 업로드 후 정리
    ├── setup_session.py    ← 티스토리 세션 초기 설정
    └── setup_naver_session.py  ← 네이버 세션 초기 설정
```

---

## 설치

```bash
# 의존성 설치
pip install playwright openai pillow python-dotenv requests

# Playwright Chromium 설치
playwright install chromium
```

---

## 초기 설정

### 1. 환경변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 각 값 입력
```

### 2. output 디렉토리 생성
```bash
mkdir -p output/tistory output/naver images logs config
```

### 3. 세션 저장 (최초 1회)
```bash
# 티스토리 로그인 세션 저장
python3 scripts/setup_session.py

# 네이버 로그인 세션 저장
python3 scripts/setup_naver_session.py
```

---

## 실행 순서

### 1. AI가 콘텐츠 작성
아래 파일들을 AI(Claude, ChatGPT 등)로 직접 작성하여 저장:

**`output/tistory/`**
- `title.txt` — 포스팅 제목
- `content.html` — HTML 본문 (이미지 위치에 `{{IMAGE_1}}`, `{{IMAGE_2}}` 삽입)
- `hashtags.txt` — 태그 (쉼표 구분)
- `category.txt` — 카테고리명

**`output/naver/`** (동일 구조)

### 2. 이미지 생성 및 NAS 업로드
```bash
python3 scripts/generate_image.py \
  --slug "포스팅-슬러그" \
  --prompts '["이미지1 프롬프트", "이미지2 프롬프트"]'
```
→ `{{IMAGE_1}}`, `{{IMAGE_2}}` 가 실제 NAS URL로 자동 교체됩니다.

### 3. 티스토리 업로드
```bash
python3 scripts/upload_tistory.py
```

### 4. 네이버 업로드
```bash
python3 scripts/upload_naver.py
```

### 5. 정리
```bash
python3 scripts/cleanup.py
```

---

## 환경 요구사항

- macOS (pbcopy 사용)
- Python 3.10+
- Synology NAS (WebDAV 마운트)
- OpenAI API 키 (DALL-E 3)
- 텔레그램 봇 토큰 (선택)

---

## 주의사항

- `.env` 파일과 `*_session.json` 파일은 절대 커밋하지 마세요.
- 세션이 만료되면 `setup_session.py` / `setup_naver_session.py` 재실행 필요
- NAS가 마운트되어 있어야 이미지 업로드 가능
