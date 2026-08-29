import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from tester import check_ip_gen204, bulk_test_ips
from UI import main_keyboard, format_single_result

# Token çevre değişkeninden okunur, bulunamazsa varsayılan atanır
TOKEN = os.getenv("BOT_TOKEN", "8815090309:AAFzqlBaaiEhfNA1DiFQUjC_B0B5J_7c_kg")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    welcome_text = (
        f"<b>👋 Merhaba {message.from_user.first_name}!</b>\n\n"
        "Global & TM Ağ Analiz ve IP Test Botuna Hoş Geldiniz.\n"
        "Fastly, Cloudflare ve CDN IP'lerinizi <code>google.com/gen_204</code> üzerinden anlık test edebilirsiniz.\n\n"
        "İşlem yapmak için tekil IP veya toplu IP listesi gönderebilirsiniz:"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard())

@dp.message(F.text)
async def handle_ip_input(message: types.Message):
    raw_text = [line.strip() for line in message.text.strip().split("\n") if line.strip()]
    
    if not raw_text:
        return

    if len(raw_text) == 1:
        ip = raw_text[0]
        status_msg = await message.answer(f"🔍 <code>{ip}</code> test ediliyor...")
        result = await check_ip_gen204(ip)
        await status_msg.edit_text(format_single_result(result), parse_mode=ParseMode.HTML)
    else:
        status_msg = await message.answer(f"⏳ <b>{len(raw_text)}</b> adet IP test ediliyor, lütfen bekleyin...")
        results = await bulk_test_ips(raw_text)
        working_ips = [r for r in results if r["working"]]
        
        summary = (
            f"<b>📊 Toplu Test Sonucu</b>\n\n"
            f"✅ <b>Çalışan IP Sayısı:</b> {len(working_ips)} / {len(results)}\n\n"
        )
        
        if working_ips:
            summary += "<b>🟢 Aktif IP'ler (En Düşük Ping):</b>\n"
            working_ips.sort(key=lambda x: x["latency"])
            for item in working_ips[:15]:
                summary += f"• <code>{item['ip']}</code> — {item['latency']} ms\n"
        
        await status_msg.edit_text(summary, parse_mode=ParseMode.HTML)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
