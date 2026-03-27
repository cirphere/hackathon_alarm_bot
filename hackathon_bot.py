import requests
from bs4 import BeautifulSoup
import instaloader
from datetime import datetime, timedelta
import os

# === 사용자 설정 ===
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
KEYWORDS = ['오아시스', '호남', '정보보호', '해커톤']
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
        "",
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
        print("새로운 관심 해커톤이 없습니다.")

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

if __name__ == "__main__":
    check_hackathons()
    check_instagram()