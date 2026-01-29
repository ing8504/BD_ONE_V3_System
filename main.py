import os, telebot, threading, time, json
from web3 import Web3
from flask import Flask, request, abort

app = Flask(__name__)

# 1. 시스템 정합성 로드 (Railway 변수와 일치)
tokens = {
    "ENGINE": os.getenv('ENGINE_TOKEN'),
    "WATCHER": os.getenv('WATCHER_TOKEN'),
    "ENFORCER": os.getenv('ENFORCER_TOKEN')
}
bots = {name: telebot.TeleBot(token) for name, token in tokens.items() if token}

# 2. 인프라 설정
INFURA_URL = os.getenv('INFURA_URL') # Railway에 반드시 입력
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
WALLET = '0x7cd253043254d97a732b403d54d6366bf9636194'
CHANNEL_ID = os.getenv('CHANNEL_ID') # 엑셀 표를 뿌릴 공지 채널 ID
FILE_PATH = 'ai_hentai_pack.zip' # Railway 서버 내 실제 파일 경로

# 3. 랭킹 데이터 관리 (메모리)
ranking = {} # {지갑주소: 누적금액}
addr_to_chat = {} # {지갑주소: 텔레그램ID} - 입금 시 매핑 필요

@app.route('/webhook/<name>', methods=['POST'])
def webhook(name):
    if name.upper() not in bots: abort(404)
    bot = bots[name.upper()]
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return ''

# 4. 엑셀방 전용 입금 감시 및 랭킹 사출
def monitor_wallet():
    prev_bal = w3.eth.get_balance(WALLET)
    while True:
        try:
            time.sleep(15) # 과도한 요청 방지
            curr_bal = w3.eth.get_balance(WALLET)
            if curr_bal > prev_bal:
                # 최근 트랜잭션에서 입금자 추출
                block = w3.eth.get_block('latest', full_transactions=True)
                for tx in block.transactions:
                    if tx['to'] == WALLET:
                        from_addr = tx['from']
                        amount = float(w3.from_wei(tx['value'], 'ether'))
                        ranking[from_addr] = ranking.get(from_addr, 0) + amount
                        
                        # 실시간 엑셀 랭킹 생성
                        sorted_rank = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
                        table = "📊 [SOVEREIGN 엑셀 랭킹]\n"
                        for i, (addr, amt) in enumerate(sorted_rank[:5], 1):
                            table += f"{i}위: {addr[:6]}...{addr[-4:]} | {amt:.3f} ETH\n"
                        
                        # WATCHER가 채널에 엑셀 표 사출
                        if "WATCHER" in bots:
                            bots["WATCHER"].send_message(CHANNEL_ID, table + "\n👑 1위에게는 독점 AI 사진팩 전송!")
                        
                        # 1위 혜택 사출 (ENFORCER)
                        if from_addr == sorted_rank[0][0] and "ENFORCER" in bots:
                            with open(FILE_PATH, 'rb') as f:
                                bots["ENFORCER"].send_document(CHANNEL_ID, f, caption="🔥 현재 1위 독점 보상 사출!")
                prev_bal = curr_bal
        except Exception as e: print(f"ERR: {e}")

if __name__ == "__main__":
    threading.Thread(target=monitor_wallet, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
