import os
import telebot
import threading

# 1. Railway 변수에서 이름표 3개 가져오기
ENGINE_TOKEN = os.getenv('ENGINE_TOKEN')
WATCHER_TOKEN = os.getenv('WATCHER_TOKEN')
ENFORCER_TOKEN = os.getenv('ENFORCER_TOKEN')

# 2. 봇 인스턴스 생성
engine_bot = telebot.TeleBot(ENGINE_TOKEN) if ENGINE_TOKEN else None
watcher_bot = telebot.TeleBot(WATCHER_TOKEN) if WATCHER_TOKEN else None
enforcer_bot = telebot.TeleBot(ENFORCER_TOKEN) if ENFORCER_TOKEN else None

# --- [유닛 1: 연산 엔진] 로직 ---
if engine_bot:
    @engine_bot.message_handler(commands=['start'])
    def start_e(m): engine_bot.reply_to(m, "📊 [BD_ONE_V3_Engine] 가동.\n설계 데이터를 전송하면 정합성 스캔을 시작합니다.")

# --- [유닛 2: 감시 유닛] 로직 ---
if watcher_bot:
    @watcher_bot.message_handler(commands=['start'])
    def start_w(m): watcher_bot.reply_to(m, "🛡 [BD_ONE_V3_Watcher] 가동.\n0x7cd2... 주소의 입금 상태를 모니터링 중입니다.")

# --- [유닛 3: 집행 유닛] 로직 ---
if enforcer_bot:
    @enforcer_bot.message_handler(commands=['start'])
    def start_f(m): enforcer_bot.reply_to(m, "⚠️ [BD_ONE_V3_Enforcer] 가동.\n최종 자산 귀속 및 결과물 사출을 담당합니다.")

# 3. 세 마리 동시에 깨우는 마법 (멀티스레딩)
def run_bot(bot):
    if bot: bot.infinity_polling()

if __name__ == "__main__":
    threads = [
        threading.Thread(target=run_bot, args=(engine_bot,)),
        threading.Thread(target=run_bot, args=(watcher_bot,)),
        threading.Thread(target=run_bot, args=(enforcer_bot,))
    ]
    for t in threads: t.start()
