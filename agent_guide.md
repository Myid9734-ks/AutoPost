# AutoPost — AI 에이전트 가이드

이 파일 하나면 충분합니다. 블로그 글을 작성하고 아래 경로에 저장하면 나머지는 자동으로 처리됩니다.

---

## 저장 경로

### 티스토리
| 파일 | 내용 |
|------|------|
| `output/tistory/title.txt` | 포스팅 제목 (1줄) |
| `output/tistory/content.html` | HTML 본문 |
| `output/tistory/hashtags.txt` | 태그 (쉼표 구분, 10개 내외) |
| `output/tistory/category.txt` | 카테고리명 (아래 목록에서 정확히 선택) |

### 네이버
| 파일 | 내용 |
|------|------|
| `output/naver/title.txt` | 포스팅 제목 (1줄) |
| `output/naver/content.html` | HTML 본문 |
| `output/naver/hashtags.txt` | 태그 (쉼표 구분, 10개 내외) |
| `output/naver/category.txt` | 카테고리명 (아래 목록에서 정확히 선택) |

---

## 카테고리 목록

### 티스토리
```
주식 브리핑
경매_공매
일상
리뷰
재테크_투자
IT_테크
노하우_팁
방문_체험
```

### 네이버
```
생활정보
경제 정책
금융정보
ETF 산업
저축,투자
주식 투자
부동산 투자
비트코인
스포츠
건강
여행
```

---

## content.html 작성 규칙

**규칙은 단 하나** — 이미지를 넣고 싶은 위치에 `{{IMAGE_N}}` 플레이스홀더를 삽입하세요.

```
{{IMAGE_1}}   ← 첫 번째 이미지 자리
{{IMAGE_2}}   ← 두 번째 이미지 자리
{{IMAGE_3}}   ← 세 번째 이미지 자리 (개수 제한 없음)
```

- 이미지 수량, 위치, HTML 구조, 글 길이 모두 자유
- 이미지 없이 글만 써도 됨
- `{{IMAGE_N}}`은 단독 줄로 작성 권장

### 예시

```html
<p>도입부 텍스트...</p>

{{IMAGE_1}}

<h2>소제목</h2>
<p>본문 내용...</p>
<ul>
  <li>항목 1</li>
  <li>항목 2</li>
</ul>

{{IMAGE_2}}

<h2>마무리</h2>
<p>결론...</p>
```

---

## 이미지 프롬프트

글 작성 후 아래 명령어를 실행할 때 이미지 프롬프트가 필요합니다.

```bash
python3 scripts/generate_image.py \
  --slug "슬러그-영문-소문자" \
  --prompts '["이미지1 영문 프롬프트", "이미지2 영문 프롬프트"]'
```

- 프롬프트는 **영문**으로 작성
- 슬러그는 포스팅 주제를 영문 소문자+하이픈으로 (예: `ai-coding-tools`)
- 이미지 수량은 `{{IMAGE_N}}`의 수와 일치

---

## 전체 실행 순서

```bash
# 1. 이미지 생성 + NAS 업로드 ({{IMAGE_N}} → 실제 URL 교체)
python3 scripts/generate_image.py --slug "슬러그" --prompts '["프롬프트1", "프롬프트2"]'

# 2. 티스토리 업로드
python3 scripts/upload_tistory.py

# 3. 네이버 업로드
python3 scripts/upload_naver.py

# 4. 정리 (output/, images/ 삭제 + 로그 기록)
python3 scripts/cleanup.py
```

---

## 글 작성 방향

- **티스토리**: IT, 재테크, 노하우 등 정보성 글 위주. 검색 유입을 고려한 키워드 포함
- **네이버**: 생활 밀착형, 정책/지원금/금융 정보 위주. 구어체 자연스러운 문체
- 티스토리와 네이버는 **같은 주제라도 제목과 내용을 다르게** 작성 권장
- 중복 방지: `logs/used_titles.json` 에 기발행 제목이 누적되어 있으니 참고

---

## 주의사항

- `category.txt` 에는 위 목록의 카테고리명을 **정확히** 입력 (띄어쓰기, 특수문자 포함)
- `hashtags.txt` 는 쉼표로 구분, 공백 없이 (예: `AI부업,블로그자동화,ChatGPT`)
- `title.txt` 는 개행 없이 1줄
