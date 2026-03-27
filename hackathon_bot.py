import requests
from bs4 import BeautifulSoup
import os

# === 사용자 설정 ===
# 로컬에서 테스트할 때는 아래 '여기에_복사한_웹훅_URL_입력' 부분에 1단계의 URL을 직접 넣어도 됩니다.
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def send_discord_message(events_text):
    """디스코드로 알림을 전송하는 함수"""
    if not DISCORD_WEBHOOK_URL:
        print("웹훅 URL이 설정되지 않았습니다.")
        return

    # 디스코드로 보낼 메시지 구성
    data = {
        "content": f"🚨 **관심 해커톤 발견!** 🚨\n\n{events_text}",
        "username": "해커톤 알리미"
    }
    
    # 디스코드 웹훅으로 POST 요청 보내기
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("디스코드 알림 전송 성공!")
    else:
        print(f"전송 실패: {response.status_code}")

def check_hackathons():
    """웹사이트 크롤링 및 키워드 확인"""
    urls = [
        "https://www.wevity.com/?c=find&s=1&gbn=viewok&jnp=1&cidx=21",  # 여기에 크롤링할 URL들을 추가하세요
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
        send_discord_message(events_text)
    else:
        print("새로운 관심 해커톤이 없습니다.")

if __name__ == "__main__":
    check_hackathons()