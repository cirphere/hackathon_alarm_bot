# 🔍 hackathon_bot.py 코드 설명

## 개요

해커톤, 공모전, 대학 공지사항을 **5개 소스**에서 자동 크롤링하여, 설정한 키워드에 매칭되는 게시글을 **디스코드 웹훅**으로 알림을 보내는 봇입니다.

---

## 전체 흐름

```
매일 오전 9시 (GitHub Actions)
    │
    ├── seen_posts.json 로드 (이전 알림 기록)
    │
    ├── check_hackathons()    → Wevity 크롤링
    ├── check_sojoong()       → 전남대 SW중심대학 크롤링
    ├── check_aicoss()        → AICOSS 크롤링
    ├── check_cossnet()       → COSS 경진대회 크롤링
    └── check_instagram()     → 인스타그램 게시물 확인
            │
            ▼
    키워드 매칭 + 신규 게시물만 → 디스코드 알림 전송
            │
            ▼
    seen_posts.json 저장 → GitHub에 자동 커밋
```

---

## 설정 변수

| 변수 | 설명 |
|------|------|
| `DISCORD_WEBHOOK_URL` | 환경변수에서 디스코드 웹훅 URL을 가져옴 |
| `KEYWORDS` | 관심 키워드 목록 (아래 참고) |
| `SEEN_POSTS_FILE` | 이미 알림 보낸 게시물 URL을 저장하는 JSON 파일 경로 |

### 키워드별 매칭 대상 예시

| 키워드 | 매칭되는 게시물 예시 |
|--------|---------------------|
| `경진대회` | "에너지신산업 아이디어랩 **경진대회**", "AI 활용 **경진대회**" |
| `챌린지` | "2026 데이터 분석 **챌린지**", "코딩 **챌린지** 참가자 모집" |
| `공모전` | "SW중심대학 에세이 **공모전**", "AI 아이디어 **공모전**" |
| `모집` | "SW봉사동아리 **모집** 안내", "서포터즈 **모집** 공고", "인턴십 참여인원**모집**" |
| `개최` | "전문가 특강 **개최** 안내", "해커톤 대회 **개최**" |
| `오아시스` | "**오아시스** 해커톤 참가 안내" |
| `호남` | "**호남**지역 정보보호 해커톤 대회" |
| `정보보호` | "**정보보호** 해커톤 대회 참가자 모집" |
| `해커톤` | "2026 오아시스 **해커톤**", "호남지역 **해커톤** 대회" |
| `CTF` | "**CTF** 대회 참가자 모집", "보안 **CTF** 챌린지" |

> ⚠️ **`모집`** 키워드는 범위가 넓어서 동아리 모집, 서포터즈 모집, 인턴십 모집 등 다양한 게시물이 매칭됩니다.
| `INSTAGRAM_ACCOUNTS` | 모니터링할 인스타그램 계정 (`oasis_hackathon`) |

---

## 중복 감지 (`seen_posts.json`)

- 실행 시작 시 `seen_posts.json`에서 이전에 알림 보낸 URL 목록을 로드
- 각 `check_*` 함수에서 게시물 URL이 이미 목록에 있으면 **스킵**
- 새 게시물만 디스코드로 알림 후, 해당 URL을 목록에 추가
- 실행 종료 시 업데이트된 목록을 `seen_posts.json`에 저장
- GitHub Actions에서 자동으로 커밋하여 다음 실행에 반영

---

## 함수별 상세 설명

### 1. `send_discord_message(message)` — 디스코드 알림 전송

- 디스코드 웹훅 URL로 POST 요청을 보내 메시지를 전송
- `username`은 `"해커톤 알리미"`로 설정
- 성공 시 `204` 응답 코드 반환

### 2. `check_hackathons()` — Wevity 크롤링

- **대상**: `https://www.wevity.com` (공모전/대회 플랫폼)
- **방식**: HTML 파싱 (BeautifulSoup)
- **셀렉터**: `.tit a` — 게시글 제목 링크를 선택
- **중복 체크**: URL이 `seen_posts`에 있으면 스킵
- **동작**: 키워드 매칭 + 신규 게시물만 디스코드로 알림

### 3. `check_sojoong()` — 전남대 SW중심대학 공지사항

- **대상**: `https://sojoong.kr/notice/notice-board/`
- **방식**: HTML 파싱 (BeautifulSoup)
- **셀렉터**: `a[href*="uid="]` — KBoard 게시판의 게시글 링크
- **URL 생성**: `href`가 상대경로이면 `https://sojoong.kr` + href로 절대경로 생성
- **중복 체크**: URL이 `seen_posts`에 있으면 스킵
- **동작**: 키워드 매칭 + 신규 게시물만 디스코드로 알림

### 4. `check_aicoss()` — AICOSS 인공지능혁신융합대학 공지사항

- **대상**: `https://aicoss.ac.kr/www/notice/`
- **방식**: HTML 파싱 (BeautifulSoup)
- **셀렉터**: `a[href*="movePageView"]` — JavaScript 링크에서 게시글 추출
- **ID 추출**: 정규식 `movePageView\((\d+)\)`으로 게시글 ID를 추출
- **URL 생성**: `https://aicoss.ac.kr/www/notice/view/{ID}`
- **중복 체크**: URL이 `seen_posts`에 있으면 스킵
- **동작**: 키워드 매칭 + 신규 게시물만 디스코드로 알림

### 5. `check_cossnet()` — COSS 경진대회

- **대상**: `https://www.cossnet.com/contest/program/list`
- **방식**: **JSON API 호출** (Next.js SPA라 HTML 파싱 불가)
- **API**: `GET https://www.cossnet.com/api/programs?type=contest&take=12&page=1`
- **응답 구조**: `{ "data": [ { "id": 145, "title": "...", ... }, ... ] }`
- **URL 생성**: `https://www.cossnet.com/contest/program/view?id={id}`
- **중복 체크**: URL이 `seen_posts`에 있으면 스킵
- **동작**: 키워드 매칭 + 신규 게시물만 디스코드로 알림

### 6. `check_instagram()` — 인스타그램 모니터링

- **대상**: `@oasis_hackathon` 계정
- **방식**: `instaloader` 라이브러리로 게시물 조회
- **조건**: 최근 **1일 이내** 게시물만 확인
- **캡션 처리**: 200자 초과 시 잘라서 표시
- **중복 체크**: URL이 `seen_posts`에 있으면 스킵
- **동작**: 새 게시물이 있으면 디스코드로 알림 (키워드 필터 없이 모든 게시물)

---

## 실행 환경

### GitHub Actions 워크플로우 (`hackathon_alert.yml`)

| 항목 | 설정 |
|------|------|
| 실행 주기 | 매일 UTC 00:00 (KST 09:00) |
| 수동 실행 | `workflow_dispatch`로 가능 |
| Python 버전 | 3.10 |
| 환경변수 | `DISCORD_WEBHOOK_URL` (GitHub Secrets에서 주입) |
| 자동 커밋 | 실행 후 `seen_posts.json`을 GitHub에 자동 커밋 |

---

## 의존성 (`requirements.txt`)

| 패키지 | 용도 |
|--------|------|
| `requests` | HTTP 요청 (크롤링, 디스코드 웹훅) |
| `beautifulsoup4` | HTML 파싱 |
| `instaloader` | 인스타그램 게시물 조회 |

---

## 크롤링 방식 요약

| 소스 | 방식 | 셀렉터 / API | 중복 체크 |
|------|------|--------------|----------|
| Wevity | HTML 파싱 | `.tit a` | ✅ URL 기반 |
| 소중 (sojoong.kr) | HTML 파싱 | `a[href*="uid="]` | ✅ URL 기반 |
| AICOSS | HTML 파싱 + 정규식 | `a[href*="movePageView"]` → ID 추출 | ✅ URL 기반 |
| COSS | JSON API | `/api/programs?type=contest&take=12&page=1` | ✅ URL 기반 |
| Instagram | instaloader 라이브러리 | 최근 1일 이내 게시물 전체 | ✅ URL 기반 |
