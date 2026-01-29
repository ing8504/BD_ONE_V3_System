import os, telebot, threading

# 1. Railway 이름표 로드 (이름표 정합성 강제 집행)
t = {
    "ENGINE": os.getenv('ENGINE_TOKEN'),
    "WATCHER": os.getenv('WATCHER_TOKEN'),
    "ENFORCER": os.getenv('ENFORCER_TOKEN')
}

def run(token, name, msg):
    if not token: return
    try:
        bot = telebot.TeleBot(token)
        @bot.message_handler(commands=['start'])
        def s(m):
            bot.reply_to(m, f"✅ [BD_ONE_V3_{name}] Online\n{msg}\n📍 Sovereign: 0x7cd253043254d97a732b403d54d6366bf9636194")
        bot.infinity_polling()
    except: pass

# 2. 유닛별 메시지 매칭 (Advisor 이름표 수정 완료)
m = {
    "ENGINE": ("Advisor", "데이터 정합성 및 92.1% 수율 연산을 시작합니다."),
    "WATCHER": ("Watcher", "실시간 입금 상태 및 전위 고착을 모니터링합니다."),
    "ENFORCER": ("Enforcer", "자산 귀속 집행 및 최종 결과물을 사출합니다.")
}

if __name__ == "__main__":
    for k, v in t.items():
        if v: threading.Thread(target=run, args=(v, m[k][0], m[k][1])).start()
