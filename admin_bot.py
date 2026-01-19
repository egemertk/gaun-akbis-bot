"""
AKBIS Telegram Bot - Admin Komutları
Telegram üzerinden bot kontrolü sağlar.
"""
import os
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID, GITHUB_TOKEN, GITHUB_REPO
from database import init_db, get_stats, set_status, get_status


# Admin olup olmadığını kontrol et
def is_admin(user_id: int) -> bool:
    """Kullanıcının admin olup olmadığını kontrol et"""
    return str(user_id) == str(ADMIN_CHAT_ID)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start komutu - Bot hakkında bilgi verir
    """
    await update.message.reply_text(
        "🤖 <b>AKBIS Duyuru Botu</b>\n\n"
        "Bu bot, Gaziantep Üniversitesi Elektrik-Elektronik Mühendisliği "
        "bölümü hocalarının AKBIS sayfalarından duyuruları takip eder.\n\n"
        "<b>Admin Komutları:</b>\n"
        "/status - Bot durumu\n"
        "/check - Manuel kontrol\n"
        "/setinterval - Kontrol aralığını ayarla\n"
        "/help - Yardım\n",
        parse_mode="HTML"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /status komutu - Bot durumunu gösterir
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bu komut sadece admin için kullanılabilir.")
        return
    
    stats = get_stats()
    interval = get_status("check_interval") or "5"
    
    await update.message.reply_text(
        f"📊 <b>Bot Durumu</b>\n\n"
        f"🔢 Toplam görülen: {stats['total_seen']}\n"
        f"📅 Son 24 saat: {stats['last_24h']}\n"
        f"⏰ Son kontrol: {stats['last_check']}\n"
        f"⏱️ Kontrol aralığı: {interval} dakika\n\n"
        f"✅ Bot aktif",
        parse_mode="HTML"
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /check komutu - Manuel kontrol tetikler (GitHub Actions workflow)
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bu komut sadece admin için kullanılabilir.")
        return
    
    await update.message.reply_text("🔄 Kontrol başlatılıyor...")
    
    # GitHub Actions workflow'u manuel tetikle
    if GITHUB_TOKEN and GITHUB_REPO:
        success = trigger_workflow()
        if success:
            await update.message.reply_text("✅ Kontrol başlatıldı! Sonuçlar birkaç dakika içinde gelecek.")
        else:
            await update.message.reply_text("❌ Workflow tetiklenemedi. GitHub token/repo ayarlarını kontrol edin.")
    else:
        await update.message.reply_text(
            "⚠️ GitHub ayarları yapılandırılmamış.\n"
            "Manuel kontrol için GITHUB_TOKEN ve GITHUB_REPO environment variable'ları gerekli."
        )


async def setinterval_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setinterval <dakika> komutu - Kontrol aralığını ayarlar
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Bu komut sadece admin için kullanılabilir.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Kullanım: /setinterval <dakika>\n"
            "Örnek: /setinterval 10\n\n"
            "Not: Minimum 5 dakika (GitHub Actions limiti)"
        )
        return
    
    try:
        interval = int(context.args[0])
        
        if interval < 5:
            await update.message.reply_text("⚠️ Minimum aralık 5 dakikadır.")
            return
        
        if interval > 1440:  # 24 saat
            await update.message.reply_text("⚠️ Maksimum aralık 1440 dakikadır (24 saat).")
            return
        
        # Aralığı kaydet
        set_status("check_interval", str(interval))
        
        await update.message.reply_text(
            f"✅ Kontrol aralığı {interval} dakika olarak ayarlandı.\n\n"
            f"⚠️ Not: GitHub Actions workflow'u manuel olarak güncellemeniz gerekebilir."
        )
        
        # GitHub Actions cron'u güncelle (opsiyonel, gelişmiş özellik)
        # Bu özellik için workflow'un dinamik olarak güncellenmesi gerekir
        
    except ValueError:
        await update.message.reply_text("❌ Geçersiz değer. Bir sayı girin.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help komutu - Yardım mesajı
    """
    await update.message.reply_text(
        "📖 <b>AKBIS Bot Yardım</b>\n\n"
        "<b>Genel Komutlar:</b>\n"
        "/start - Bot hakkında bilgi\n"
        "/help - Bu yardım mesajı\n\n"
        "<b>Admin Komutları:</b>\n"
        "/status - Bot durumu ve istatistikler\n"
        "/check - Manuel duyuru kontrolü\n"
        "/setinterval <dk> - Kontrol aralığını ayarla\n\n"
        "<b>Örnek:</b>\n"
        "<code>/setinterval 10</code> - Her 10 dakikada kontrol",
        parse_mode="HTML"
    )


def trigger_workflow() -> bool:
    """
    GitHub Actions workflow'u manuel tetikle.
    
    Returns:
        True eğer başarılı
    """
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/check_announcements.yml/dispatches"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "ref": "main"  # veya "master"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.status_code == 204
    except requests.RequestException as e:
        print(f"Error triggering workflow: {e}")
        return False


def main():
    """Admin bot'u başlat (polling mode)"""
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set!")
        return
    
    print("🤖 Starting admin bot...")
    
    # Veritabanını başlat
    init_db()
    
    # Application oluştur
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Komut handler'ları ekle
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("setinterval", setinterval_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Bot'u başlat
    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
