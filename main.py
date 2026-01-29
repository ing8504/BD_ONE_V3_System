import os
import telebot
import threading
import time
import logging
import random
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

# 새 버전: 더 강력한 야한 텍스트 생성기
body_parts = ["가슴", "허벅지", "입술", "엉덩이", "허리", "목선", "발목", "배꼽"]
adjectives = ["부드러운", "촉촉한", "뜨거운", "부드러운", "탄력 있는", "매끄러운", "감각적인"]
actions = ["스며든다", "헐떡인다", "움직인다", "속삭인다", "부딪힌다", "떨린다", "감싼다"]
endings = ["... 상상만 해도 몸이 달아오르네 🔥", "... 이 맛에 못 헤어나와", "... 더 깊이 들어가고 싶지?", "... 입금하면 풀 버전 풀어줄게 ㄱㄱ"]

def generate_erotic_text():
    body = random.choice(body_parts)
    adj = random.choice(adjectives)
    act = random.choice(actions)
    end = random.choice(endings)
    text = f"{adj} {body}가 {act}하는 그 느낌... "
    return text + end

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
                f"[{name.upper()}] 새 버전 오픈! 완전 무료 모드 🔥\n\n"
                f"봇이 3분마다 새 야한 텍스트 생성해서 풀어줌\n"
                f"입금 없이도 계속 즐겨! (더 강한 버전은 0.01 ETH 입금)\n"
                f"주소: {WALLET}\n"
                f"첫 참여자 = 자동 1위 랭킹 업그레이드"
            )
            bot.reply_to(m, welcome)
            bot.reply_to(m, generate_erotic_text())

def auto_new_loop():
    while True:
        time.sleep(180)  # 3분으로 줄여서 더 능동적으로
        try:
            if CHANNEL_ID == 0 or 'WATCHER' not in bots:
                continue

            # 랭킹
            sorted_r = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
            table = "📊 새 랭킹 자동 업데이트\n"
            if not sorted_r:
                table += "첫 입금자 대기 중! 지금 입금하면 영구 1위 🔥\n"
            else:
                for i, (a, am) in enumerate(sorted_r[:3], 1):
                    table += f"{i}위: {a[:6]}...{a[-4:]} | {am:.4f} ETH\n"

            table += f"\n봇이 새 버전으로 업그레이드! 더 강한 텍스트 자동 생성 중\n입금하면 풀버전 무한 루프 사출\n주소: {WALLET}"

            bots['WATCHER'].send_message(CHANNEL_ID, table)
            bots['WATCHER'].send_message(CHANNEL_ID, generate_erotic_text())

            logging.info("새 루프 실행 완료")

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

    threading.Thread(target=auto_new_loop, daemon=True).start()

    PORT = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=PORT)
