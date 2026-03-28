import requests
from bs4 import BeautifulSoup
import os
import re
import json

# === 사용자 설정 ===
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
KEYWORDS = ['경진대회', '챌린지', '공모전', '모집', '개최', '오아시스', '호남', '정보보호', '해커톤', 'CTF']

SEEN_POSTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seen_posts.json')

# === 중복 감지 ===
def load_seen_posts():
    """이전에 알림 보낸 게시물 URL 목록 로드"""
    if os.path.exists(SEEN_POSTS_FILE):
        try:
            with open(SEEN_POSTS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except (json.JSONDecodeError, Exception):
            return set()
    return set()

def save_seen_posts(seen_posts):
    """알림 보낸 게시물 URL 목록 저장"""
    with open(SEEN_POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(seen_posts)), f, ensure_ascii=False, indent=2)

# 전역 변수로 관리
seen_posts = load_seen_posts()

def send_discord_message(message):
    """디스코드로 알림을 전송하는 함수"""
    if not DISCORD_WEBHOOK_URL:
        print("웹훅 URL이 설정되지 않았습니다.")
        return

    data = {
        "content": message,
        "username": "해커톤 알리미"
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("디스코드 알림 전송 성공!")
    else:
        print(f"전송 실패: {response.status_code}")


def check_sojoong():
    """전남대 SW중심대학 공지사항 크롤링"""
    url = "https://sojoong.kr/notice/notice-board/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    found_events = []
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # KBoard 게시판의 게시글 링크 선택
        links = soup.select('a[href*="uid="]')
        
        for link in links:
            text = link.get_text().strip()
            href = link.get('href', '')
            
            if not text or not href:
                continue
            
            # 전체 URL 생성
            if href.startswith('/'):
                full_url = "https://sojoong.kr" + href
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = "https://sojoong.kr/notice/notice-board/" + href
            
            if full_url in seen_posts:
                continue
            
            if any(keyword in text for keyword in KEYWORDS):
                found_events.append(f"📌 **{text}**\n🔗 [자세히 보기]({full_url})")
                seen_posts.add(full_url)
        
        if found_events:
            events_text = "\n\n".join(found_events)
            send_discord_message(f"🚨 **[전남대 SW중심대학] 관심 공지 발견!** 🚨\n\n{events_text}")
        else:
            print("[소중] 새로운 관심 공지가 없습니다.")
    
    except Exception as e:
        print(f"소중 크롤링 중 오류 발생: {e}")

def check_aicoss():
    """전남대 인공지능혁신융합대학사업단 공지사항 크롤링"""
    url = "https://aicoss.ac.kr/www/notice/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    found_events = []
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # javascript:movePageView(ID) 형태의 링크에서 게시글 추출
        links = soup.select('a[href*="movePageView"]')
        
        for link in links:
            text = link.get_text().strip()
            # 줄바꿈/탭 정리
            text = re.sub(r'\s+', ' ', text).strip()
            href = link.get('href', '')
            
            if not text or not href:
                continue
            
            # movePageView(ID)에서 ID 추출
            match = re.search(r'movePageView\((\d+)\)', href)
            if not match:
                continue
            
            post_id = match.group(1)
            full_url = f"https://aicoss.ac.kr/www/notice/view/{post_id}"
            
            if full_url in seen_posts:
                continue
            
            if any(keyword in text for keyword in KEYWORDS):
                found_events.append(f"📌 **{text}**\n🔗 [자세히 보기]({full_url})")
                seen_posts.add(full_url)
        
        if found_events:
            events_text = "\n\n".join(found_events)
            send_discord_message(f"🚨 **[AICOSS 인공지능혁신융합대학] 관심 공지 발견!** 🚨\n\n{events_text}")
        else:
            print("[AICOSS] 새로운 관심 공지가 없습니다.")
    
    except Exception as e:
        print(f"AICOSS 크롤링 중 오류 발생: {e}")

def check_cossnet():
    """COSS 경진대회 목록 크롤링 (API 사용)"""
    api_url = "https://www.cossnet.com/api/programs?type=contest&take=12&page=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    found_events = []
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        programs = data.get('data', [])
        
        for program in programs:
            title = program.get('title', '').strip()
            program_id = program.get('id', '')
            
            if not title or not program_id:
                continue
            
            full_url = f"https://www.cossnet.com/contest/program/view?id={program_id}"
            
            if full_url in seen_posts:
                continue
            
            if any(keyword in title for keyword in KEYWORDS):
                found_events.append(f"📌 **{title}**\n🔗 [자세히 보기]({full_url})")
                seen_posts.add(full_url)
        
        if found_events:
            events_text = "\n\n".join(found_events)
            send_discord_message(f"🚨 **[COSS 경진대회] 관심 대회 발견!** 🚨\n\n{events_text}")
        else:
            print("[COSS] 새로운 관심 경진대회가 없습니다.")
    
    except Exception as e:
        print(f"COSS 크롤링 중 오류 발생: {e}")

if __name__ == "__main__":
    check_sojoong()
    check_aicoss()
    check_cossnet()

    
    # 확인한 게시물 목록 저장
    save_seen_posts(seen_posts)
    print(f"\n총 {len(seen_posts)}개의 게시물이 기록되었습니다.")