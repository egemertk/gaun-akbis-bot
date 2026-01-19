"""
AKBIS Telegram Bot - Vercel Serverless Webhook Handler
Telegram komutlarını 7/24 işler.
"""
import os
import json
import sqlite3
import hashlib
import requests
from http.server import BaseHTTPRequestHandler

# Environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

# Hoca listesi (config.py'den)
AKBIS_PAGES = [
    {"id": 0, "name": "Arş. Gör. Veysel TURAN"},
    {"id": 1, "name": "Arş. Gör. Şule ÖZTÜRK"},
    {"id": 2, "name": "Arş. Gör. Muhterem Alper KAPLAN"},
    {"id": 3, "name": "Arş. Gör. Ali HAZAR"},
    {"id": 4, "name": "Arş. Gör. Ahmet Said DEDEOĞLU"},
    {"id": 5, "name": "Arş. Gör. İsa AKKAYA"},
    {"id": 6, "name": "Dr. Öğr. Üyesi Seydi KAÇMAZ"},
    {"id": 7, "name": "Dr. Öğr. Üyesi Mehmet DEMİR"},
    {"id": 8, "name": "Dr. Öğr. Üyesi Musa BUTE"},
    {"id": 9, "name": "Dr. Öğr. Üyesi Mahmut AYKAÇ"},
    {"id": 10, "name": "Dr. Öğr. Üyesi Ali Osman ARSLAN"},
    {"id": 11, "name": "Doç. Dr. Serkan ÖZBAY"},
    {"id": 12, "name": "Doç. Dr. Taner İNCE"},
    {"id": 13, "name": "Prof. Dr. Ahmet Mete VURAL"},
    {"id": 14, "name": "Prof. Dr. Gölge ÖĞÜCÜ YETKİN"},
    {"id": 15, "name": "Prof. Dr. Sema KAYHAN"},
    {"id": 16, "name": "Prof. Dr. Tolgay KARA"},
    {"id": 17, "name": "Prof. Dr. Uğur Cem HASAR"},
    {"id": 18, "name": "Prof. Dr. Ergün ERÇELEBİ"},
    {"id": 19, "name": "Prof. Dr. Nuran DOĞRU"},
]


def send_message(chat_id: str, text: str, parse_mode: str = "HTML"):
    """Telegram mesajı gönder"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


def is_admin(user_id: int) -> bool:
    """Admin kontrolü"""
    return str(user_id) == str(ADMIN_CHAT_ID)


def get_preferences_from_github() -> dict:
    """GitHub repo'dan tercihleri al"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return {}
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/preferences.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            import base64
            content = base64.b64decode(resp.json()["content"]).decode()
            return json.loads(content)
    except:
        pass
    
    # Varsayılan: tümü aktif
    return {"enabled": list(range(20))}


def save_preferences_to_github(prefs: dict) -> bool:
    """Tercihleri GitHub'a kaydet"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/preferences.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Önce mevcut SHA'yı al
    sha = None
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            sha = resp.json().get("sha")
    except:
        pass
    
    # Kaydet
    import base64
    content = base64.b64encode(json.dumps(prefs, indent=2).encode()).decode()
    
    payload = {
        "message": "Update preferences via Telegram",
        "content": content
    }
    if sha:
        payload["sha"] = sha
    
    try:
        resp = requests.put(url, json=payload, headers=headers, timeout=10)
        return resp.status_code in [200, 201]
    except:
        return False


def handle_command(chat_id: str, user_id: int, text: str):
    """Komutu işle"""
    if not text.startswith("/"):
        return
    
    parts = text.split()
    command = parts[0].lower().split("@")[0]  # @botname kısmını kaldır
    args = parts[1:] if len(parts) > 1 else []
    
    if command == "/start":
        send_message(chat_id, 
            "🤖 <b>AKBIS Duyuru Botu</b>\n\n"
            "Komutlar:\n"
            "/list - Hoca listesi\n"
            "/follow <no> - Takip et\n"
            "/unfollow <no> - Takibi bırak\n"
            "/followall - Tümünü takip et\n"
            "/unfollowmall - Takipleri kaldır\n"
            "/status - Durum\n"
            "/help - Yardım"
        )
        return
    
    # Admin gerektiren komutlar
    if not is_admin(user_id):
        send_message(chat_id, "⛔ Bu komut sadece admin için.")
        return
    
    if command == "/list":
        prefs = get_preferences_from_github()
        enabled = prefs.get("enabled", list(range(20)))
        
        lines = ["📋 <b>Hoca Listesi</b>\n"]
        for p in AKBIS_PAGES:
            status = "✅" if p["id"] in enabled else "❌"
            lines.append(f"{status} <b>{p['id']}</b> - {p['name']}")
        
        lines.append("\n<i>/follow 5</i> - 5 numaralı hocayı takip et")
        send_message(chat_id, "\n".join(lines))
    
    elif command == "/follow" and args:
        try:
            prof_id = int(args[0])
            if 0 <= prof_id < 20:
                prefs = get_preferences_from_github()
                enabled = set(prefs.get("enabled", list(range(20))))
                enabled.add(prof_id)
                prefs["enabled"] = list(enabled)
                
                if save_preferences_to_github(prefs):
                    name = AKBIS_PAGES[prof_id]["name"]
                    send_message(chat_id, f"✅ <b>{name}</b> takip ediliyor.")
                else:
                    send_message(chat_id, "❌ Kayıt başarısız. GitHub token kontrol edin.")
            else:
                send_message(chat_id, "❌ Geçersiz numara (0-19).")
        except:
            send_message(chat_id, "❌ Geçersiz numara.")
    
    elif command == "/unfollow" and args:
        try:
            prof_id = int(args[0])
            if 0 <= prof_id < 20:
                prefs = get_preferences_from_github()
                enabled = set(prefs.get("enabled", list(range(20))))
                enabled.discard(prof_id)
                prefs["enabled"] = list(enabled)
                
                if save_preferences_to_github(prefs):
                    name = AKBIS_PAGES[prof_id]["name"]
                    send_message(chat_id, f"❌ <b>{name}</b> takibi bırakıldı.")
                else:
                    send_message(chat_id, "❌ Kayıt başarısız.")
            else:
                send_message(chat_id, "❌ Geçersiz numara (0-19).")
        except:
            send_message(chat_id, "❌ Geçersiz numara.")
    
    elif command == "/followall":
        prefs = {"enabled": list(range(20))}
        if save_preferences_to_github(prefs):
            send_message(chat_id, "✅ Tüm hocalar (20) takip ediliyor.")
        else:
            send_message(chat_id, "❌ Kayıt başarısız.")
    
    elif command == "/unfollowmall":
        prefs = {"enabled": []}
        if save_preferences_to_github(prefs):
            send_message(chat_id, "❌ Tüm takipler kaldırıldı.")
        else:
            send_message(chat_id, "❌ Kayıt başarısız.")
    
    elif command == "/status":
        prefs = get_preferences_from_github()
        enabled = prefs.get("enabled", [])
        send_message(chat_id,
            f"📊 <b>Bot Durumu</b>\n\n"
            f"👥 Takip edilen: {len(enabled)} hoca\n"
            f"✅ Bot aktif (GitHub Actions)"
        )
    
    elif command == "/help":
        send_message(chat_id,
            "📖 <b>Yardım</b>\n\n"
            "/list - Hocaları listele\n"
            "/follow <no> - Takip et\n"
            "/unfollow <no> - Takibi bırak\n"
            "/followall - Tümünü takip\n"
            "/unfollowmall - Takipleri kaldır\n"
            "/status - Durum"
        )


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            update = json.loads(body)
            
            if "message" in update:
                message = update["message"]
                chat_id = str(message["chat"]["id"])
                user_id = message["from"]["id"]
                text = message.get("text", "")
                
                if text:
                    handle_command(chat_id, user_id, text)
        except Exception as e:
            print(f"Error: {e}")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'AKBIS Bot Webhook Active')
