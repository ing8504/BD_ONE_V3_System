import os
import telebot
import threading
import time
import logging
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 토큰 & 채널 로드
tokens = {
    'WATCHER': os.getenv('WATCHER_TOKEN'),
    'ADVISOR': os.getenv('ENGINE_TOKEN'),
    'ENFORCER': os.getenv('ENFORCER_TOKEN')
}

bots = {}
for name, token in tokens.items():
    if token:
        bots[name] = teleBot = telebot.TeleBot(token)
        logging.info(f"{name} 연결 OK")

CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))

# 무료 풀 콘텐츠 파일 (Railway에 업로드 필수)
GOOD_FREE_IMAGES = ['good_sample1.jpg', 'good_sample2.jpg', 'good_sample3.jpg']  # 고퀄 3장
FREE_PACK_ZIP = 'good_free_pack.zip'  # 첫판용 풀팩 ZIP (10장 이상, 크기 50MB 이하)

# 랭킹 (초기 빈 상태)
ranking = {}

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

# /start 시 첫판 풀어주기 + 유료 유도
def add_handlers():
    for name, bot in bots.items():
        @bot.message_handler(commands=['start'])
        def start(m):
            msg = (
                "BD_ONE 역설방 첫판 풀 오픈!\n\n"
                "지금부터 진짜 좋은 거 무료로 풀어줄게 🔥\n"
                "고퀄 AI 선정적 이미지 팩 첫 세트 도착\n"
                "계속 보려면? 0.01 ETH 입금 → 풀버전 + 매일 신규 업데이트 독점\n"
                "입금 주소: 0x7cd253043254d97a732b403d54d6366bf9636194\n"
                "첫 입금자 = 영구 1위 + 보너스 팩 증정!"
            )
            bot.reply_to(m, msg)

            # 첫판 무료 풀 사출 (사진 여러 장)
            for img in GOOD_FREE_IMAGES:
                if os.path.exists(img):
                    with open(img, 'rb') as f:
                        bot.send_photo(m.chat.id, f, caption="첫판 무료 풀: 고퀄 AI 샘플")

            # 무료 팩 ZIP도 바로 보내기
            if os.path.exists(FREE_PACK_ZIP):
                with open(FREE_PACK_ZIP, 'rb') as f:
                    bot.send_document(m.chat.id, f, caption="첫판 풀팩 다운로드 (10장+)")

# 자동 풀 루프 (5분마다 채널에 좋은 거 풀기)
def auto_free_full():
    count = 0
    while True:
        time.sleep(300)  # 5분
        count += 1
        try:
            if CHANNEL_ID == 0 or 'WATCHER' not in bots:
                continue

            # 랭킹 표 + 유료 유도 문구
            sorted_r = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
            table = f"📊 BD_ONE 랭킹 (무료 체험 중 {count}회차)\n"
            if not sorted_r:
                table += "아직 입금자 없음! 첫 입금자가 영구 1위 + 보너스 🔥\n"
            else:
                for i, (a, am) in enumerate(sorted_r[:3], 1):
                    table += f"{i}위: {a[:6]}...{a[-4:]} | {am:.4f} ETH\n"
            
            table += "\n첫판부터 좋은 거 풀었지? 계속 보려면 0.01 ETH 입금 ㄱㄱ\n매일 신규 고퀄 업데이트 + 독점 풀버전 자동 사출!\n주소: 0x7cd253043254d97a732b403d54d6366bf9636194"

            bots['WATCHER'].send_message(CHANNEL_ID, table)

            # 좋은 거 무료 풀 (사진 + ZIP 번갈아)
            if count % 2 == 0 and os.path.exists(FREE_PACK_ZIP):
                with open(FREE_PACK_ZIP, 'rb') as f:
                    bots['WATCHER'].send_document(CHANNEL_ID, f, caption=f"{count}회차 무료 풀팩 (고퀄 업데이트)")
            else:
                for img in GOOD_FREE_IMAGES[:2]:  # 2장만
                    if os.path.exists(img):
                        with open(img, 'rb') as f:
                            bots['WATCHER'].send_photo(CHANNEL_ID, f, caption=f"{count}회차 무료 고퀄 샘플")

            logging.info(f"무료 풀 {count}회 완료")

        except Exception as e:
            logging.error(f"Auto free error: {e}")

if __name__ == '__main__':
    add_handlers()

    DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if DOMAIN:
        for name in bots:
            url = f"https://{DOMAIN}/webhook/{name.lower()}"
            try:
                bots[name].remove_webhook()
                bots[name].set_webhook(url=url)
                logging.info(f"{name} webhook OK")
            except Exception as e:
                logging.error(f"{name} webhook 실패: {e}")

    threading.Thread(target=auto_free_full, daemon=True).start()

    PORT = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=PORT)
