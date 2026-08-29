from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ Tekil IP Test Et", callback_data="test_single"),
            InlineKeyboardButton(text="📂 Toplu IP Testi", callback_data="test_bulk")
        ]
    ])

def format_single_result(res: dict) -> str:
    if res["working"]:
        quality = "🚀 Mükemmel" if res["latency"] < 200 else ("🟡 Orta" if res["latency"] < 500 else "🔴 Yavaş")
        return (
            f"<b>🟢 IP Durumu: AKTİF</b>\n\n"
            f"📍 <b>IP:</b> <code>{res['ip']}</code>\n"
            f"⏱ <b>Gecikme Süresi:</b> <code>{res['latency']} ms</code>\n"
            f"📊 <b>Kalite:</b> {quality}\n"
            f"🔗 <b>Test Adresi:</b> <code>google.com/gen_204</code>\n"
        )
    else:
        return (
            f"<b>🔴 IP Durumu: PASİF / ERİŞİLEMEZ</b>\n\n"
            f"📍 <b>IP:</b> <code>{res['ip']}</code>\n"
            f"⚠️ <b>Hata Türü:</b> <code>{res.get('error', 'Yanıt Alınamadı')}</code>\n"
        )
