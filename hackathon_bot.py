import requests
from bs4 import BeautifulSoup
import instaloader
from datetime import datetime, timedelta
import os
import re

# === 사용자 설정 ===
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
KEYWORDS = ['경진대회', '챌린지', '공모전', '모집', '개최', '오아시스', '호남', '정보보호', '해커톤', 'CTF']
INSTAGRAM_ACCOUNTS = ['oasis_hackathon']

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

def check_hackathons():
    """웹사이트 크롤링 및 키워드 확인"""
    urls = [
        "https://www.wevity.com/?c=find&s=1&gbn=viewok&jnp=1&cidx=21",
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    found_events = []
    
    for url in urls:
        if not url:
            continue
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            titles = soup.select('.tit a')
            
            for title in titles:
                text = title.get_text().strip()
                link = "https://www.wevity.com/" + title['href']
                
                if any(keyword in text for keyword in KEYWORDS):
                    found_events.append(f"📌 **{text}**\n🔗 [자세히 보기]({link})")
            
        except Exception as e:
            print(f"크롤링 중 오류 발생 ({url}): {e}")
    
    if found_events:
        events_text = "\n\n".join(found_events)
        send_discord_message(f"🚨 **관심 해커톤 발견!** 🚨\n\n{events_text}")
    else:
        print("[위비티] 새로운 관심 해커톤이 없습니다.")

def check_instagram():
    """인스타그램 계정의 최신 게시물 확인"""
    L = instaloader.Instaloader()
    yesterday = datetime.now() - timedelta(days=1)
    
    for account in INSTAGRAM_ACCOUNTS:
        try:
            profile = instaloader.Profile.from_username(L.context, account)
            new_posts = []
            
            for post in profile.get_posts():
                # 최근 1일 이내 게시물만 확인
                if post.date_utc.replace(tzinfo=None) < yesterday:
                    break
                
                caption = post.caption or "(캡션 없음)"
                # 캡션이 너무 길면 200자로 자르기
                if len(caption) > 200:
                    caption = caption[:200] + "..."
                
                post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                new_posts.append(f"📸 **@{account}** 새 게시물\n💬 {caption}\n🔗 [게시물 보기]({post_url})")
            
            if new_posts:
                posts_text = "\n\n".join(new_posts)
                send_discord_message(f"📢 **인스타그램 새 소식!** 📢\n\n{posts_text}")
            else:
                print(f"@{account}: 최근 새 게시물 없음")
                
        except Exception as e:
            print(f"인스타그램 확인 중 오류 ({account}): {e}")

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
            
            if any(keyword in text for keyword in KEYWORDS):
                found_events.append(f"📌 **{text}**\n🔗 [자세히 보기]({full_url})")
        
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
            
            # 대학명/New 뱃지 등 제거하고 제목만 추출
            # text에는 "전남대학교 New 실제제목 2026.03.26" 형태
            # 제목 부분만 키워드 매칭
            if any(keyword in text for keyword in KEYWORDS):
                found_events.append(f"📌 **{text}**\n🔗 [자세히 보기]({full_url})")
        
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
            
            if any(keyword in title for keyword in KEYWORDS):
                found_events.append(f"📌 **{title}**\n🔗 [자세히 보기]({full_url})")
        
        if found_events:
            events_text = "\n\n".join(found_events)
            send_discord_message(f"🚨 **[COSS 경진대회] 관심 대회 발견!** 🚨\n\n{events_text}")
        else:
            print("[COSS] 새로운 관심 경진대회가 없습니다.")
    
    except Exception as e:
        print(f"COSS 크롤링 중 오류 발생: {e}")

if __name__ == "__main__":
    check_hackathons()
    check_sojoong()
    check_aicoss()
    check_cossnet()
    check_instagram()