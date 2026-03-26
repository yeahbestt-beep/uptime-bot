import asyncio
import requests
import logging
import json
import os
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- AYARLAR ---
TOKEN = "8791752339:AAHtoym5XBUFCsn5_qV0FFGONy5jJ6mFIEs" # LÜTFEN YENİ TOKEN ALIP BURAYA YAPIŞTIR
CHECK_INTERVAL = 60 
TIMEOUT = 10
DATA_FILE = "sites.json"

# --- VERİ YÖNETİMİ (JSON) ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(monitored_sites, f)

monitored_sites = load_data()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- MENÜ TASARIMI ---
def main_menu_keyboard():
    keyboard = [
        ['📊 Liste', '🔄 Monitörü Başlat'],
        ['➕ Site Ekle', 'ℹ️ Yardım']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **Uptime Monitör PRO v2.0**\n\n"
        "Sitelerini 7/24 izliyorum. Bir sorun olursa anında haber vereceğim.",
        reply_markup=main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '📊 Liste':
        if not monitored_sites:
            await update.message.reply_text("📭 İzleme listesi boş.")
        else:
            msg = "🔍 **Güncel İzleme Listesi:**\n\n"
            for url, data in monitored_sites.items():
                status = data.get("status", True)
                icon = "🟢 Online" if status else "🔴 Offline"
                msg += f"{icon} -> `{url}`\n"
            await update.message.reply_text(msg, parse_mode='Markdown')

    elif text == '➕ Site Ekle':
        await update.message.reply_text("Format: `/ekle https://site.com`", parse_mode='Markdown')

    elif text == '🔄 Monitörü Başlat':
        chat_id = update.effective_message.chat_id
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        if not current_jobs:
            context.job_queue.run_repeating(monitor_task, interval=CHECK_INTERVAL, first=1, chat_id=chat_id, name=str(chat_id))
            await update.message.reply_text(f"✅ Sistem Aktif! Kontrol periyodu: {CHECK_INTERVAL}sn.")
        else:
            await update.message.reply_text("ℹ️ Monitör zaten çalışıyor.")

    elif text == 'ℹ️ Yardım':
        await update.message.reply_text(
            "📖 **Kullanım Kılavuzu:**\n\n"
            "1. `/ekle URL` -> Listeye yeni site ekler.\n"
            "2. `/sil URL` -> Siteyi listeden çıkarır.\n"
            "3. **Monitörü Başlat** -> Arka plan kontrolünü açar."
        )

async def add_site_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Kullanım: `/ekle https://site.com`")
        return
    
    url = context.args[0]
    if not url.startswith("http"): url = "https://" + url
        
    monitored_sites[url] = {"status": True, "last_check": time.time()}
    save_data()
    await update.message.reply_text(f"✅ `{url}` eklendi.", parse_mode='Markdown')

async def remove_site_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Kullanım: `/sil https://site.com`")
        return
    
    url = context.args[0]
    if url in monitored_sites:
        del monitored_sites[url]
        save_data()
        await update.message.reply_text(f"🗑 `{url}` listeden silindi.", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Bu URL listede bulunamadı.")

# --- ARKA PLAN GÖREVİ ---

async def monitor_task(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id

    for url, data in monitored_sites.items():
        last_status = data.get("status", True)
        try:
            start_time = time.time()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) UptimeBot/1.0'}
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
            end_time = time.time()
            
            response_ms = round((end_time - start_time) * 1000)
            current_status = (response.status_code == 200)
            status_info = f"Kod: {response.status_code}"
        except Exception as e:
            current_status = False
            status_info = "Erişim Engellendi/Zaman Aşımı"
            response_ms = 0

        if current_status != last_status:
            monitored_sites[url]["status"] = current_status
            save_data()
            
            if current_status:
                await context.bot.send_message(chat_id, f"✅ **SİTE GERİ GELDİ!**\n🌐 {url}\n⚡ Hız: {response_ms}ms\n✨ Durum: Online", parse_mode='Markdown')
            else:
                await context.bot.send_message(chat_id, f"🚨 **SİTE ÇÖKTÜ!**\n🌐 {url}\n⚠️ Hata: {status_info}\n❌ Durum: Offline", parse_mode='Markdown')

# --- ANA ÇALIŞTIRICI ---

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ekle", add_site_cmd))
    app.add_handler(CommandHandler("sil", remove_site_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 PRO Bot Başarıyla Başlatıldı!")
    app.run_polling()

if __name__ == '__main__':
    main()