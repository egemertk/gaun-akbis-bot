"""
AKBIS Telegram Bot - Telegram Entegrasyon Modülü
"""
import requests
from typing import List, Dict, Optional
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from scraper import Announcement


def send_message(text: str, chat_id: str = None, parse_mode: str = "HTML") -> bool:
    """
    Telegram mesajı gönder.
    
    Args:
        text: Gönderilecek mesaj
        chat_id: Hedef chat ID (varsayılan: config'den)
        parse_mode: Mesaj formatı (HTML veya Markdown)
        
    Returns:
        True eğer başarılı
    """
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set!")
        return False
    
    chat_id = chat_id or TELEGRAM_CHAT_ID
    if not chat_id:
        print("ERROR: TELEGRAM_CHAT_ID not set!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("ok", False)
    except requests.RequestException as e:
        print(f"Error sending message: {e}")
        return False


def format_announcement(announcement: Announcement) -> str:
    """
    Duyuruyu Telegram mesaj formatına dönüştür.
    
    Args:
        announcement: Duyuru objesi
        
    Returns:
        Formatlanmış mesaj metni
    """
    # Emoji ve başlık
    message_parts = [
        "📢 <b>YENİ DUYURU</b>",
        "",
        f"👨‍🏫 <b>{escape_html(announcement.author)}</b>",
        f"📅 {escape_html(announcement.date)}",
        "",
        f"📝 <b>{escape_html(announcement.title)}</b>",
    ]
    
    # İçerik (max 500 karakter)
    if announcement.content:
        content = announcement.content[:500]
        if len(announcement.content) > 500:
            content += "..."
        message_parts.extend(["", escape_html(content)])
    
    # Dosyalar
    if announcement.files:
        message_parts.extend(["", "📎 <b>Dosyalar:</b>"])
        for file in announcement.files[:5]:  # Max 5 dosya
            file_name = escape_html(file.get("name", "Dosya"))
            file_url = file.get("url", "")
            if file_url:
                message_parts.append(f"• <a href=\"{file_url}\">{file_name}</a>")
            else:
                message_parts.append(f"• {file_name}")
    
    # Kaynak linki
    message_parts.extend([
        "",
        f"🔗 <a href=\"{announcement.source_url}\">Kaynağa Git</a>"
    ])
    
    return "\n".join(message_parts)


def escape_html(text: str) -> str:
    """HTML özel karakterlerini escape et"""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def send_announcement(announcement: Announcement, chat_id: str = None) -> bool:
    """
    Duyuruyu Telegram'a gönder.
    
    Args:
        announcement: Duyuru objesi
        chat_id: Hedef chat ID
        
    Returns:
        True eğer başarılı
    """
    message = format_announcement(announcement)
    return send_message(message, chat_id)


def send_status_message(stats: dict, chat_id: str = None) -> bool:
    """
    Bot durum mesajı gönder.
    
    Args:
        stats: İstatistik dictionary
        chat_id: Hedef chat ID
        
    Returns:
        True eğer başarılı
    """
    message = f"""📊 <b>Bot Durumu</b>

🔢 Toplam görülen duyuru: {stats.get('total_seen', 0)}
📅 Son 24 saat: {stats.get('last_24h', 0)}
⏰ Son kontrol: {stats.get('last_check', 'Bilinmiyor')}

✅ Bot aktif çalışıyor"""
    
    return send_message(message, chat_id)


def send_error_message(error: str, chat_id: str = None) -> bool:
    """
    Hata mesajı gönder.
    
    Args:
        error: Hata mesajı
        chat_id: Hedef chat ID
        
    Returns:
        True eğer başarılı
    """
    message = f"""⚠️ <b>Bot Hatası</b>

{escape_html(error)}

Lütfen logları kontrol edin."""
    
    return send_message(message, chat_id)


def test_connection() -> bool:
    """
    Bot bağlantısını test et.
    
    Returns:
        True eğer bot erişilebilir
    """
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        return response.json().get("ok", False)
    except:
        return False


if __name__ == "__main__":
    # Test
    print("Testing Telegram connection...")
    if test_connection():
        print("✅ Bot connection successful!")
        
        # Test mesajı gönder
        from scraper import Announcement
        test_ann = Announcement(
            date="20.01.2026",
            title="Test Duyurusu",
            content="Bu bir test duyurusudur. Bot başarıyla çalışıyor!",
            files=[{"name": "test.pdf", "url": "https://example.com/test.pdf"}],
            source_url="https://akbis.gaziantep.edu.tr",
            author="Test Bot"
        )
        
        if send_announcement(test_ann):
            print("✅ Test message sent!")
        else:
            print("❌ Failed to send test message")
    else:
        print("❌ Bot connection failed! Check your token.")
