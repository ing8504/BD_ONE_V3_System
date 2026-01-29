import os
import telebot
import threading
import time
from web3 import Web3

# Env 토큰들
tokens = {
    "ENGINE": os.getenv('ENGINE_TOKEN'),
    "WATCHER": os.getenv('WATCHER_TOKEN'),
    "ENFORCER": os.getenv('ENFORCER_TOKEN')
}

messages = {
    "ENGINE": ("Advisor", "데이터 정합성 및 92.1% 수율 연산을 시작합니다."),
    "WATCHER": ("Watcher", "실시간 입금 상태 및 결과를 감시합니다."),
    "ENFORCER": ("Enforcer", "자산 귀속 및 최종 결과를 집행합니다.")
}

# Ethereum 연결 (Infura 등 무료 노드 URL 넣으세요)
INFURA_URL = 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID'  # ← 여기 본인 키
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
WALLET = '0x7cd253043254d97a732b403d54d6366bf9636194'

def monitor_wallet():
    """WATCHER용: 지갑 잔액 모니터링 (별도 스레드)"""
    prev_balance = w3.eth.get_balance(WALLET)
    print(f"초기 잔액: {w3.from_wei(prev_balance, 'ether')} ETH")
    while True:
        time.sleep(30)  # 30초마다 체크 (rate limit 피함)
        current = w3.eth.get_balance(WALLET)
        if current > prev_balance:
            delta = current - prev_balance
            msg = f"입금 감지! +{w3.from_wei(delta, 'ether')} ETH\n현재: {w3.from_wei(current, 'ether')} ETH\nSovereign Address: {WALLET}"
            # Enforcer 봇으로 칭송 사출 (Enforcer 토큰 필요시)
            print("Enforcer 사출:", msg)  # 실제론 Enforcer bot.send_message(chat_id, msg)
            prev_balance = current

def run_bot(token, name, init_msg):
    if not token:
        print(f"{name} 토큰 없음, 스킵")
        return
    try:
        bot = telebot.TeleBot(token)
        
        @bot.message_handler(commands=['start'])
        def start(m):
            bot.reply_to(m, f"[{name.upper()}] Online\n{init_msg}\nSovereign: {WALLET} 💰")
        
        # 추가: /balance 명령으로 잔액 확인 (테스트용)
        @bot.message_handler(commands=['balance'])
        def balance(m):
            bal = w3.eth.get_balance(WALLET)
            bot.reply_to(m, f"현재 Sovereign 잔액: {w3.from_wei(bal, 'ether')} ETH")
        
        print(f"{name} 봇 시작")
        bot.infinity_polling()
    except Exception as e:
        print(f"{name} 에러: {e}")

if __name__ == "__main__":
    # 지갑 모니터링 스레드 별도 실행 (WATCHER 역할 강화)
    threading.Thread(target=monitor_wallet, daemon=True).start()
    
    # 각 봇 스레드
    threads = []
    for name, token in tokens.items():
        msg = messages[name][1]
        t = threading.Thread(target=run_bot, args=(token, name, msg))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()  # 메인 스레드 대기
