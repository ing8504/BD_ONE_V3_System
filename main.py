import os
import telebot
import threading
import time
import logging
import random
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 토큰 & 채널
tokens = {
    'WATCHER': os.getenv('WATCHER_TOKEN'),
    'ADVISOR': os.getenv('ENGINE_TOKEN'),
    'ENFORCER': os.getenv('ENFORCER_TOKEN')
}

bots = {}
for name, token in tokens.items():
    if token:
        bots[name] = telebot.TeleBot(token)

CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))
WALLET = '0x7cd253043254d97a732b403d54d6366bf9636194'

ranking = {}

# 야한 텍스트 베이스 (봇이 조합해서 변형)
base_parts = [
    "그녀의", "부드러운", "촉촉한", "헐떡이는", "숨결이", "피부가", "빛나는", "가슴골이", "깊게", "패인", "허벅지 사이로", "스며드는", "손길", "신음소리가", "새어나오는", "입술이", "살짝", "벌어지며", "속삭이는", "더 해줘", "S라인", "몸매가", "천천히", "움직일 때마다", "시선이", "집중되는", "그 순간", "야한 포즈로", "누워서", "카메라를", "바라보는", "눈빛", "위험한", "수준이야", "온몸이", "달아오르는", "느낌", "끝없이", "이어지는", "쾌감"
]

def generate_erotic_text():
    # 랜덤으로 8~12개 조각 골라서 연결
    parts = random.sample(base_parts, random.randint(8, 12))
    text = ' '.join(parts)
    # 자연스럽게 마무리
    endings = ["... 상상만 해도 미치겠네 🔥", "... 이 맛에 사는 거지", "... 계속 보고 싶지?", "... 더 강한 거 원하면 입금 ㄱㄱ"]
    return text + random.choice(endings)

@app.route('/webhook/<name>', methods=['POST'])
def webhook(name):
    name = name.upper()
    if name not in bots:
        return '', 404
    bot = bots[name]
    try:
        update = telebot.types.Update.de_json(request.get_data(as_text=True))
        if update:
            bot.process_new_updates([update])
        return '', 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return '', 500

def add_handlers():
    for name, bot in bots.items():
        @bot.message_handler(commands=['start'])
        def start(m):
            welcome = (
                f"BD_ONE 역설방 완전 무료 오픈!\n\n"
                f"봇이 5분마다 알아서 야한 텍스트 풀어줌\n"
                f"지금부터 계속 즐겨도 됨 🔥\n"
                f"더 강렬하고 상세한 버전 + 매일 신규 콘텐츠 원하면 0.01 ETH 입금\n"
                f"주소: {WALLET}\n"
                f"첫 입금자 = 영구 1위 + 무제한 풀버전"
            )
            bot.reply_to(m, welcome)
            # 첫 콘텐츠 바로 풀기
            bot.reply_to(m, generate_erotic_text())

def auto_erotic_loop():
    while True:
        time.sleep(300)  # 5분
        try:
            if CHANNEL_ID == 0 or 'WATCHER' not in bots:
                continue

            # 랭킹
            sorted_r = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
            table = "📊 BD_ONE 랭킹 (자동 업데이트)\n"
            if not sorted_r:
                table += "아직 입금자 없음! 첫 번째가 영구 1위 🔥\n"
            else:
                for i, (a, am) in enumerate(sorted_r[:3], 1):
                    table += f"{i}위: {a[:6]}...{a[-4:]} | {am:.4f} ETH\n"

            table += f"\n봇이 알아서 야한 텍스트 풀 중! 더 강한 버전 보려면 0.01 ETH 입금 ㄱㄱ\n주소: {WALLET}"

            bots['WATCHER'].send_message(CHANNEL_ID, table)
            bots['WATCHER'].send_message(CHANNEL_ID, generate_erotic_text())

            logging.info("야한 텍스트 자동 사출 완료")

        except Exception as e:
            logging.error(f"Loop error: {e}")

if __name__ == '__main__':
    add_handlers()

    DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if DOMAIN:
        for name in bots:
            url = f"https://{DOMAIN}/webhook/{name.lower()}"
            try:
                bots[name].remove_webhook()
                bots[name].set_webhook(url=url)
                logging.info(f"{name} webhook 설정")
            except Exception as e:
                logging.error(f"{name} webhook 실패: {e}")

    threading.Thread(target=auto_erotic_loop, daemon=True).start()

    PORT = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=PORT)
