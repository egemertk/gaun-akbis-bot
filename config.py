"""
AKBIS Telegram Bot - Konfigürasyon Dosyası
"""
import os

# Telegram Bot Ayarları
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Admin Chat ID (aynı olabilir)
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", TELEGRAM_CHAT_ID)

# GitHub API (admin komutları için)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # format: "username/repo"

# Takip Edilecek Sayfalar
AKBIS_PAGES = [
    # Araştırma Görevlileri
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=423728_arastirma-gorevlisi_veysel-turan",
        "name": "Araştırma Görevlisi Veysel TURAN"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=365257_arastirma-gorevlisi_sule-ozturk",
        "name": "Araştırma Görevlisi Şule ÖZTÜRK"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=424279_arastirma-gorevlisi_muhterem-alper-kaplan",
        "name": "Araştırma Görevlisi Muhterem Alper KAPLAN"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=424280_arastirma-gorevlisi_ali-hazar",
        "name": "Araştırma Görevlisi Ali HAZAR"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=317884_arastirma-gorevlisi_ahmet-said-dedeoglu",
        "name": "Araştırma Görevlisi Ahmet Said DEDEOĞLU"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=382968_arastirma-gorevlisi_isa-akkaya",
        "name": "Araştırma Görevlisi İsa AKKAYA"
    },
    # Doktor Öğretim Üyeleri
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=149283_doktor-ogretim-uyesi_seydi-kacmaz",
        "name": "Dr. Öğr. Üyesi Seydi KAÇMAZ"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=107423_doktor-ogretim-uyesi_mehmet-demir",
        "name": "Dr. Öğr. Üyesi Mehmet DEMİR"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=183330_doktor-ogretim-uyesi_musa-bute",
        "name": "Dr. Öğr. Üyesi Musa BUTE"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=148024_doktor-ogretim-uyesi_mahmut-aykac",
        "name": "Dr. Öğr. Üyesi Mahmut AYKAÇ"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=51709_doktor-ogretim-uyesi_ali-osman-arslan",
        "name": "Dr. Öğr. Üyesi Ali Osman ARSLAN"
    },
    # Doçentler
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=149310_docent_serkan-ozbay",
        "name": "Doç. Dr. Serkan ÖZBAY"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=149286_docent_taner-ince",
        "name": "Doç. Dr. Taner İNCE"
    },
    # Profesörler
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=160452_profesor_ahmet-mete-vural",
        "name": "Prof. Dr. Ahmet Mete VURAL"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=148038_profesor_golge-ogucu-yetkin",
        "name": "Prof. Dr. Gölge ÖĞÜCÜ YETKİN"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=191951_profesor_sema-kayhan",
        "name": "Prof. Dr. Sema KAYHAN"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=19932_profesor_tolgay-kara",
        "name": "Prof. Dr. Tolgay KARA"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=182085_profesor_ugur-cem-hasar",
        "name": "Prof. Dr. Uğur Cem HASAR"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=9132_profesor_ergun-ercelebi",
        "name": "Prof. Dr. Ergün ERÇELEBİ"
    },
    {
        "url": "https://akbis.gaziantep.edu.tr/detay/?A_ID=148036_profesor_nuran-dogru",
        "name": "Prof. Dr. Nuran DOĞRU"
    },
]

# EEE Bölüm Sayfası
EEE_PAGE = {
    "url": "https://eee.gaziantep.edu.tr",
    "announcements_url": "https://eee.gaziantep.edu.tr/duyurular.php",
    "name": "EEE Bölümü"
}

# Veritabanı
DATABASE_PATH = "seen_announcements.db"

# Varsayılan kontrol aralığı (dakika)
DEFAULT_CHECK_INTERVAL = 5
