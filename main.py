"""
AKBIS Telegram Bot - Ana Çalıştırma Scripti
GitHub Actions tarafından periyodik olarak çağrılır.
"""
import sys
import json
import os
from datetime import datetime
from typing import List

from config import AKBIS_PAGES, EEE_PAGE
from scraper import Announcement, scrape_akbis_page_v2, scrape_eee_page
from database import (
    init_db, is_seen, mark_seen, set_status, get_stats,
    init_professor_preferences, get_enabled_professors
)
from telegram_bot import send_announcement, send_error_message


def get_enabled_professor_ids() -> list:
    """
    preferences.json dosyasından aktif profesör ID'lerini al.
    Dosya yoksa tüm profesörler aktif.
    """
    try:
        if os.path.exists("preferences.json"):
            with open("preferences.json", "r") as f:
                prefs = json.load(f)
                return prefs.get("enabled", list(range(len(AKBIS_PAGES))))
    except:
        pass
    
    # Varsayılan: tümü aktif
    return list(range(len(AKBIS_PAGES)))


def check_all_pages() -> List[Announcement]:
    """
    Tüm sayfaları kontrol et ve yeni duyuruları döndür.
    Sadece takip edilen profesörleri kontrol eder.
    
    Returns:
        Yeni duyuru listesi
    """
    new_announcements = []
    
    # preferences.json'dan aktif profesör ID'lerini al
    enabled_ids = get_enabled_professor_ids()
    
    if not enabled_ids:
        print("⚠️ Hiçbir profesör takip edilmiyor!")
        return []
    
    print(f"📋 {len(enabled_ids)} profesör takip ediliyor")
    
    # Aktif AKBIS sayfalarını kontrol et
    for i, page in enumerate(AKBIS_PAGES):
        if i not in enabled_ids:
            continue  # Bu profesör takip edilmiyor
            
        url = page["url"]
        name = page["name"]
        
        print(f"Checking: {name}")
        
        try:
            announcements = scrape_akbis_page_v2(url, name)
            
            for ann in announcements:
                ann_hash = ann.get_hash()
                
                if not is_seen(ann_hash):
                    new_announcements.append(ann)
                    print(f"  ➕ New: {ann.title[:50]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # EEE Bölüm sayfasını kontrol et
    print(f"Checking: {EEE_PAGE['name']}")
    
    try:
        eee_announcements = scrape_eee_page(EEE_PAGE["url"])
        
        for ann in eee_announcements:
            ann_hash = ann.get_hash()
            
            if not is_seen(ann_hash):
                new_announcements.append(ann)
                print(f"  ➕ New: {ann.title[:50]}...")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return new_announcements


def process_announcements(announcements: List[Announcement]) -> int:
    """
    Yeni duyuruları Telegram'a gönder ve veritabanına kaydet.
    
    Args:
        announcements: Duyuru listesi
        
    Returns:
        Başarıyla gönderilen duyuru sayısı
    """
    sent_count = 0
    
    for ann in announcements:
        ann_hash = ann.get_hash()
        
        # Telegram'a gönder
        if send_announcement(ann):
            # Başarılı - veritabanına kaydet
            mark_seen(ann_hash, ann.author, ann.title, ann.date)
            sent_count += 1
            print(f"✅ Sent: {ann.title[:50]}...")
        else:
            print(f"❌ Failed to send: {ann.title[:50]}...")
    
    return sent_count


def main():
    """Ana fonksiyon"""
    print("=" * 50)
    print(f"AKBIS Bot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Veritabanını başlat
    init_db()
    
    # Profesör tercihlerini başlat (ilk çalıştırmada tümü aktif)
    init_professor_preferences(AKBIS_PAGES)
    
    # Sayfaları kontrol et
    print("\n📡 Checking pages for new announcements...")
    new_announcements = check_all_pages()
    
    if new_announcements:
        print(f"\n📢 Found {len(new_announcements)} new announcement(s)")
        
        # Duyuruları gönder
        sent_count = process_announcements(new_announcements)
        print(f"\n✅ Successfully sent {sent_count}/{len(new_announcements)} announcement(s)")
    else:
        print("\n✓ No new announcements found")
    
    # Son kontrol zamanını kaydet
    set_status("last_check", datetime.now().isoformat())
    
    # İstatistikleri göster
    stats = get_stats()
    print(f"\n📊 Stats: {stats['total_seen']} total, {stats['last_24h']} in last 24h")
    
    print("\n" + "=" * 50)
    print("Done!")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        send_error_message(str(e))
        sys.exit(1)
