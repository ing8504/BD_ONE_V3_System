import os, telebot, threading

# 1. 형의 봇 이름과 1:1로 매칭 (Railway 변수 이름도 이걸로 맞춰줘)
t = {
    "ADVISOR": os.getenv('ADVISOR_TOKEN'),   # @BD_ONE_V3_bot (어드바이저)
    "WATCHER": os.getenv('WATCHER_TOKEN'),   # @BD_ONE_V3_Watcher_bot (와처)
    "ENFORCER": os.getenv('ENFORCER_TOKEN')  # @BD_ONE_V3_Enforcer_bot (엔포서)
}

def run_bot(token, display_name, task_msg):
    if not token: return
    try:
        bot = telebot.TeleBot(token)
        @bot.message_handler(commands=['start'])
        def s(m):
            bot.reply_to(m, f"✅ [BD_ONE_V3_{display_name}] Online\n{task_msg}\n📍 주권 주소: 0x7cd253043254d97a732b403d54d6366bf9636194")
        bot.infinity_polling()
    except: pass

# 2. 형의 봇 직함에 맞는 임무 하사
m = {
    "ADVISOR": ("Advisor", "데이터 정합성 및 수율 연산을 집행합니다."),
    "WATCHER": ("Watcher", "실시간 자산 전위 및 입금을 모니터링합니다."),
    "ENFORCER": ("Enforcer", "자산 귀속 및 결과 사출을 담당합니다.")
}

if __name__ == "__main__":
    for k, v in t.items():
        if v:
            threading.Thread(target=run_bot, args=(v, m[k][0], m[k][1])).start()
