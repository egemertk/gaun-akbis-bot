"""
AKBIS Telegram Bot - Veritabanı Modülü
Görülen duyuruları SQLite ile takip eder.
"""
import sqlite3
from datetime import datetime
from typing import Optional
import os

from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Veritabanı bağlantısı al"""
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    """Veritabanı tablolarını oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_announcements (
            hash TEXT PRIMARY KEY,
            author TEXT,
            title TEXT,
            date TEXT,
            seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_status (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def is_seen(announcement_hash: str) -> bool:
    """
    Duyuru daha önce görüldü mü kontrol et.
    
    Args:
        announcement_hash: Duyurunun benzersiz hash değeri
        
    Returns:
        True eğer daha önce görüldüyse
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT 1 FROM seen_announcements WHERE hash = ?",
        (announcement_hash,)
    )
    result = cursor.fetchone()
    
    conn.close()
    return result is not None


def mark_seen(announcement_hash: str, author: str = "", title: str = "", date: str = ""):
    """
    Duyuruyu görüldü olarak işaretle.
    
    Args:
        announcement_hash: Duyurunun benzersiz hash değeri
        author: Duyuru sahibi
        title: Duyuru başlığı
        date: Duyuru tarihi
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO seen_announcements (hash, author, title, date, seen_at)
        VALUES (?, ?, ?, ?, ?)
    """, (announcement_hash, author, title, date, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_status(key: str) -> Optional[str]:
    """Bot durum bilgisi al"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT value FROM bot_status WHERE key = ?",
        (key,)
    )
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None


def set_status(key: str, value: str):
    """Bot durum bilgisi kaydet"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO bot_status (key, value, updated_at)
        VALUES (?, ?, ?)
    """, (key, value, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Bot istatistiklerini al"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Toplam görülen duyuru sayısı
    cursor.execute("SELECT COUNT(*) FROM seen_announcements")
    total_seen = cursor.fetchone()[0]
    
    # Son 24 saatte görülen
    cursor.execute("""
        SELECT COUNT(*) FROM seen_announcements 
        WHERE seen_at > datetime('now', '-1 day')
    """)
    last_24h = cursor.fetchone()[0]
    
    # Son kontrol zamanı
    cursor.execute("SELECT value FROM bot_status WHERE key = 'last_check'")
    last_check = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_seen": total_seen,
        "last_24h": last_24h,
        "last_check": last_check[0] if last_check else "Henüz kontrol yapılmadı"
    }


def cleanup_old_records(days: int = 90):
    """Eski kayıtları temizle"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"""
        DELETE FROM seen_announcements 
        WHERE seen_at < datetime('now', '-{days} days')
    """)
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted


if __name__ == "__main__":
    # Test
    print("Initializing database...")
    init_db()
    
    print("Testing mark_seen...")
    mark_seen("test_hash_123", "Test Author", "Test Title", "20.01.2026")
    
    print(f"Is seen: {is_seen('test_hash_123')}")  # True
    print(f"Is seen (new): {is_seen('new_hash')}")  # False
    
    print(f"Stats: {get_stats()}")
