# 🚨 해커톤 알리미 봇

해커톤, 공모전, 대학 공지사항을 자동으로 크롤링하여 **디스코드**로 알림을 보내주는 봇입니다.

## 📡 크롤링 소스

| 소스 | 사이트 | 설명 |
|------|--------|------|
| 소중 | [sojoong.kr](https://sojoong.kr/notice/notice-board/) | 전남대 SW중심대학 공지사항 |
| AICOSS | [aicoss.ac.kr](https://aicoss.ac.kr/www/notice/) | 전남대 인공지능혁신융합대학사업단 공지사항 |
| COSS | [cossnet.com](https://www.cossnet.com/contest/program/list) | 첨단분야 혁신융합대학 경진대회 |

## 🔑 키워드

다음 키워드가 포함된 게시글을 감지합니다:

`경진대회` `챌린지` `공모전` `모집` `개최` `오아시스` `호남` `정보보호` `해커톤` `CTF`

## ⏰ 실행 주기

- **자동**: GitHub Actions로 매일 **오전 9시 (KST)** 실행
- **수동**: GitHub Actions에서 `workflow_dispatch`로 수동 실행 가능

## 🛠️ 설정

### 1. 환경 변수

| 변수명 | 설명 |
|--------|------|
| `DISCORD_WEBHOOK_URL` | 디스코드 웹훅 URL |

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 로컬 실행

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python hackathon_bot.py
```

## 📁 프로젝트 구조

```
alarm_bot/
├── hackathon_bot.py          # 메인 봇 스크립트
├── requirements.txt          # Python 의존성
├── seen_posts.json           # 중복 알림 방지용 기록
├── .github/
│   └── workflows/
│       └── hackathon_alert.yml  # GitHub Actions 워크플로우
└── README.md
```
