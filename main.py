import os, telebot, threading

# 1. Railway에 설정한 영어 이름표를 그대로 로드
t = {
    "ENGINE": os.getenv('ENGINE_TOKEN'),   # Advisor 유닛
    "WATCHER": os.getenv('WATCHER_TOKEN'), # Watcher 유닛
    "ENFORCER": os.getenv('ENFORCER_TOKEN') # Enforcer 유닛
}

def run_bot(token, name, msg):
    if not token: return
    try:
        bot = telebot.TeleBot(token)
        @bot.message_handler(commands=['start'])
        def s(m):
            bot.reply_to(m, f"✅ [BD_ONE_V3_{name}] Online\n{msg}\n📍 주권 주소: 0x7cd253043254d97a732b403d54d6366bf9636194")
        bot.infinity_polling()
    except Exception as e:
        print(f"Error: {e}")

# 2. 각 유닛별 임무 메시지
m = {
    "ENGINE": ("Advisor", "데이터 정합성 및 수율 연산을 집행합니다."),
    "WATCHER": ("Watcher", "실시간 자산 전위 및 입금을 모니터링합니다."),
    "ENFORCER": ("Enforcer", "자산 귀속 및 결과 사출을 담당합니다.")
}

if __name__ == "__main__":
    # 3. 세 마리 봇 병렬 사출
    for k, v in t.items():
        if v:
            threading.Thread(target=run_bot, args=(v, m[k][0], m[k][1])).start()
