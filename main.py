import os, telebot, threading

# 1. Railway에 입력한 영어 이름표(토큰) 로드
tokens = {
    "engine": os.getenv('ENGINE_TOKEN'),
    "watcher": os.getenv('WATCHER_TOKEN'),
    "enforcer": os.getenv('ENFORCER_TOKEN')
}

def run_bot(token, unit_name, msg):
    if not token: return
    try:
        bot = telebot.TeleBot(token)
        @bot.message_handler(commands=['start'])
        def welcome(m):
            bot.reply_to(m, f"✅ [BD_ONE_V3_{unit_name}] Online\n\n{msg}\n📍 Sovereign Address: 0x7cd253043254d97a732b403d54d6366bf9636194")
        bot.infinity_polling()
    except Exception as e:
        print(f"Error starting {unit_name}: {e}")

# 2. 각 유닛별 임무 하사
tasks = {
    "engine": ("Engine", "데이터 정합성 및 92.1% 수율 연산을 시작합니다."),
    "watcher": ("Watcher", "실시간 입금 상태 및 전위 고착을 모니터링합니다."),
    "enforcer": ("Enforcer", "자산 귀속 집행 및 최종 결과물을 사출합니다.")
}

if __name__ == "__main__":
    for key, token in tokens.items():
        if token:
            name, message = tasks[key]
            threading.Thread(target=run_bot, args=(token, name, message)).start()
