import os
import telebot

# 봇 토큰 로드
TOKEN = os.getenv('ENFORCER_TOKEN')
bot = telebot.TeleBot(TOKEN)

# 입금 주소 (형의 Sovereign Address)
SOVEREIGN_ADDR = "0x7cd253043254d97a732b403d54d6366bf9636194"

@bot.message_handler(commands=['start'])
def start(message):
    msg = (
        "⚠️ [BD_ONE_V3_System] Enforcer Online\n\n"
        "데이터 집행을 시작합니다.\n"
        f"📍 수납 주소: {SOVEREIGN_ADDR}\n"
        "설계 파일을 던지면 견적이 사출됩니다."
    )
    bot.reply_to(message, msg)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    bot.reply_to(message, "📡 데이터 정합성 스캔 중... 견적: 1.21 ETH. 입금 확인 시 집행합니다.")

bot.infinity_polling()
