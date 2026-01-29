import os
import telebot
import threading
import time
import logging
from web3 import Web3
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Env 로드
INFURA_URL = os.getenv('INFURA_URL')
if not INFURA_URL:
    raise ValueError("INFURA_URL 없음")

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
WALLET = '0x7cd253043254d97a732b403d54d6366bf9636194'.lower()

tokens = {
    'WATCHER': os.getenv('WATCHER_TOKEN'),
    'ADVISOR': os.getenv('ENGINE_TOKEN'),
    'ENFORCER': os.getenv('ENFORCER_TOKEN')
}

bots = {}
for name, token in tokens.items():
    if token:
        bots[name] = telebot.TeleBot(token)

CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))  # -100xxxxxx 형태
FILE_PATH = 'ai_hentai_pack.zip'  # Railway에 업로드한 파일명

ranking = {}  # {addr: total_eth}

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
        logging.error(f"Webhook error {name}: {e}")
        return '', 500

def monitor_wallet():
    prev_bal = w3.eth.get_balance(WALLET)
    logging.info(f"Start balance: {w3.from_wei(prev_bal, 'ether')} ETH")

    while True:
        try:
            time.sleep(30)  # 30초로 늘려 rate limit 피함
            curr_bal = w3.eth.get_balance(WALLET)
            if curr_bal <= prev_bal:
                continue

            delta = curr_bal - prev_bal
            logging.info(f"Deposit detected: +{w3.from_wei(delta, 'ether')} ETH")

            # 최근 tx에서 입금자 찾기 (최적화: 전체 블록 안 돌림)
            block = w3.eth.get_block('latest', full_transactions=True)
            updated = False
            for tx in block.transactions:
                if tx.get('to') and tx['to'].lower() == WALLET and tx['value'] > 0:
                    addr = tx['from'].lower()
                    amt = float(w3.from_wei(tx['value'], 'ether'))
                    ranking[addr] = ranking.get(addr, 0) + amt
                    updated = True

            if updated:
                prev_bal = curr_bal
                # 랭킹 표
                sorted_r = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
                table = "📊 SOVEREIGN 엑셀 랭킹 (최신)\n" + "\n".join(
                    f"{i+1}위: {a[:6]}...{a[-4:]} | {am:.4f} ETH"
                    for i, (a, am) in enumerate(sorted_r[:5])
                )

                if 'WATCHER' in bots and CHANNEL_ID != 0:
                    bots['WATCHER'].send_message(CHANNEL_ID, table)

                # 현재 1위한테 매번 혜택 사출 (중복 OK, 형님이 원하는 대로)
                if sorted_r and 'ENFORCER' in bots and CHANNEL_ID != 0:
                    top_addr = sorted_r[0][0]
                    if os.path.exists(FILE_PATH):
                        with open(FILE_PATH, 'rb') as f:
                            bots['ENFORCER'].send_document(
                                CHANNEL_ID,
                                f,
                                caption=f"현재 1위 ({top_addr[:6]}...) 보상 재사출 🔥 AI 팩 도착!"
                            )
                    else:
                        logging.warning("파일 없음: 혜택 스킵")

        except Exception as e:
            logging.error(f"Monitor error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 8080))
    DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')

    if DOMAIN:
        for name in bots:
            url = f"https://{DOMAIN}/webhook/{name.lower()}"
            try:
                bots[name].remove_webhook()
                bots[name].set_webhook(url=url)
                logging.info(f"{name} webhook set: {url}")
            except Exception as e:
                logging.error(f"{name} webhook fail: {e}")

    threading.Thread(target=monitor_wallet, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT, debug=False)
