import os
import telebot
import threading
import time
from web3 import Web3
from flask import Flask, request, abort
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 1. 토큰 안전 로드
tokens = {
    "ENGINE": os.getenv('ENGINE_TOKEN'),
    "WATCHER": os.getenv('WATCHER_TOKEN'),
    "ENFORCER": os.getenv('ENFORCER_TOKEN')
}

bots = {}
for name, token in tokens.items():
    if token and token.strip():  # 빈 문자열/None 체크
        try:
            bots[name] = telebot.TeleBot(token)
            logging.info(f"{name} 봇 초기화 성공")
        except Exception as e:
            logging.error(f"{name} 봇 초기화 실패: {e}")
    else:
        logging.warning(f"{name} 토큰 없음, 스킵")

# 2. 인프라 설정 (Railway Variables에서 읽기)
INFURA_URL = os.getenv('INFURA_URL')
if not INFURA_URL:
    logging.error("INFURA_URL 없음! Railway Variables에 추가하세요")
    raise ValueError("INFURA_URL 필수")

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not w3.is_connected():
    logging.error("Infura 연결 실패")
    raise ConnectionError("Infura 연결 안 됨")

WALLET = '0x7cd253043254d97a732b403d54d6366bf9636194'.lower()
CHANNEL_ID = os.getenv('CHANNEL_ID')  # -100으로 시작하는 숫자 문자열
if not CHANNEL_ID:
    logging.error("CHANNEL_ID 없음! 텔레그램 채널 ID 넣으세요")
    CHANNEL_ID = "0"  # 임시로 0 넣어서 크래시 방지

FILE_PATH = os.getenv('FILE_PATH', 'ai_hentai_pack.zip')  # Railway에 업로드한 파일명

# 3. 랭킹
ranking = {}  # {from_addr: total_eth}

@app.route('/webhook/<name>', methods=['POST'])
def webhook(name):
    name = name.upper()
    if name not in bots:
        abort(404)
    bot = bots[name]
    try:
        json_string = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_string)
        if update:
            bot.process_new_updates([update])
        return ''
    except Exception as e:
        logging.error(f"Webhook 에러 ({name}): {e}")
        abort(500)

def monitor_wallet():
    if not w3.is_connected():
        logging.error("monitor_wallet: Infura 연결 안 됨")
        return

    prev_bal = w3.eth.get_balance(WALLET)
    logging.info(f"시작 잔액: {w3.from_wei(prev_bal, 'ether')} ETH")

    while True:
        try:
            time.sleep(15)
            curr_bal = w3.eth.get_balance(WALLET)
            if curr_bal > prev_bal:
                delta = curr_bal - prev_bal
                logging.info(f"입금 감지! delta: {w3.from_wei(delta, 'ether')} ETH")

                # 최근 블록에서 입금 tx 찾기 (간단히 latest 1블록만)
                block = w3.eth.get_block('latest', full_transactions=True)
                for tx in block['transactions']:
                    if tx['to'] and tx['to'].lower() == WALLET and tx['value'] > 0:
                        from_addr = tx['from'].lower()
                        amount = float(w3.from_wei(tx['value'], 'ether'))
                        ranking[from_addr] = ranking.get(from_addr, 0) + amount
                        logging.info(f"입금자: {from_addr}, amount: {amount}")

                prev_bal = curr_bal

                # 랭킹 표 생성
                sorted_rank = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
                table = "📊 [SOVEREIGN 엑셀 랭킹]\n"
                for i, (addr, amt) in enumerate(sorted_rank[:5], 1):
                    table += f"{i}위: {addr[:6]}...{addr[-4:]} | {amt:.4f} ETH\n"

                if "WATCHER" in bots:
                    try:
                        bots["WATCHER"].send_message(int(CHANNEL_ID), table + "\n👑 1위 보상 준비 중!")
                    except Exception as e:
                        logging.error(f"채널 메시지 전송 실패: {e}")

                # 1위 혜택 (파일 있으면)
                if sorted_rank and "ENFORCER" in bots:
                    try:
                        if os.path.exists(FILE_PATH):
                            with open(FILE_PATH, 'rb') as f:
                                bots["ENFORCER"].send_document(
                                    int(CHANNEL_ID),
                                    f,
                                    caption="🔥 현재 1위 독점 보상: AI 선정적 이미지 팩!"
                                )
                        else:
                            logging.warning(f"파일 없음: {FILE_PATH}")
                    except Exception as e:
                        logging.error(f"파일 전송 실패: {e}")

        except Exception as e:
            logging.error(f"monitor_wallet 에러: {e}")
            time.sleep(60)  # 에러 시 잠시 대기

if __name__ == "__main__":
    # Webhook 세팅
    PORT = int(os.getenv('PORT', 8080))
    DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if not DOMAIN:
        logging.error("RAILWAY_PUBLIC_DOMAIN 없음! Railway에서 자동 제공됨")
    else:
        for name, bot in bots.items():
            webhook_url = f"https://{DOMAIN}/webhook/{name.lower()}"
            try:
                bot.remove_webhook()
                bot.set_webhook(url=webhook_url)
                logging.info(f"{name} webhook 설정: {webhook_url}")
            except Exception as e:
                logging.error(f"{name} webhook 설정 실패: {e}")

    threading.Thread(target=monitor_wallet, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
