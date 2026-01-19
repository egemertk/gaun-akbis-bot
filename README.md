# AKBIS Duyuru Takip Botu 📢

Gaziantep Üniversitesi Elektrik-Elektronik Mühendisliği bölümü hocalarının AKBIS sayfalarından duyuruları takip edip Telegram üzerinden bildirim gönderen bot.

## Özellikler

- 🔍 20 AKBIS hoca sayfası + EEE bölüm sayfası takibi
- 📱 Yeni duyurularda anlık Telegram bildirimi
- 📎 Dosya ekleri ve kaynak linkleri
- ⏰ GitHub Actions ile 5 dakikada bir otomatik kontrol
- 🎛️ Telegram üzerinden admin kontrolü

## Hızlı Kurulum

### 1. GitHub Repository Oluştur

1. GitHub'da yeni bir **public** repository oluşturun
2. Bu dosyaları repository'ye yükleyin

### 2. Telegram Chat ID'nizi Öğrenin

1. Telegram'da [@userinfobot](https://t.me/userinfobot)'a mesaj gönderin
2. Bot size chat ID'nizi söyleyecek

### 3. GitHub Secrets Ayarla

Repository Settings → Secrets and variables → Actions → New repository secret:

| Secret Adı | Değer |
|------------|-------|
| `TELEGRAM_BOT_TOKEN` | Bot token'ınız |
| `TELEGRAM_CHAT_ID` | Chat ID'niz |

### 4. Workflow'u Aktifleştir

1. Repository'de Actions sekmesine gidin
2. "I understand my workflows, go ahead and enable them" butonuna tıklayın
3. "Check Announcements" workflow'unu seçin
4. "Run workflow" ile test edin

## Dosya Yapısı

```
gaun/
├── .github/
│   └── workflows/
│       └── check_announcements.yml  # GitHub Actions workflow
├── config.py          # Konfigürasyon ve URL listesi
├── scraper.py         # Web scraping modülü
├── database.py        # SQLite veritabanı
├── telegram_bot.py    # Telegram API entegrasyonu
├── main.py            # Ana çalıştırma scripti
├── admin_bot.py       # Admin komutları (opsiyonel)
├── requirements.txt   # Python bağımlılıkları
└── README.md          # Bu dosya
```

## Admin Komutları (Opsiyonel)

Admin bot'u lokal olarak çalıştırarak Telegram üzerinden kontrol edebilirsiniz:

```bash
# Environment variable'ları ayarla
set TELEGRAM_BOT_TOKEN=your_token_here
set TELEGRAM_CHAT_ID=your_chat_id

# Admin bot'u başlat
python admin_bot.py
```

### Komutlar

| Komut | Açıklama |
|-------|----------|
| `/status` | Bot durumu ve istatistikler |
| `/check` | Manuel kontrol tetikle |
| `/setinterval <dk>` | Kontrol aralığını ayarla |
| `/help` | Yardım |

## Lokal Test

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment variable'ları ayarla (PowerShell)
$env:TELEGRAM_BOT_TOKEN="your_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"

# Test et
python main.py
```

## SSS

### Bot duyuru göndermiyor?

1. GitHub Actions'ın aktif olduğunu kontrol edin
2. Secrets'ların doğru ayarlandığını kontrol edin
3. Actions sekmesinden son çalıştırma loglarını inceleyin

### 60 gün sonra bot durdu?

GitHub, 60 gün inaktif repository'lerde scheduled workflow'ları otomatik devre dışı bırakır. Herhangi bir commit atarak tekrar aktifleştirebilirsiniz.

### Daha sık/seyrek kontrol yapmak istiyorum?

`.github/workflows/check_announcements.yml` dosyasındaki cron değerini değiştirin:

```yaml
# Her 5 dakikada bir (minimum)
- cron: '*/5 * * * *'

# Her 15 dakikada bir
- cron: '*/15 * * * *'

# Her saat başı
- cron: '0 * * * *'

# Günde bir kez (sabah 9:00 UTC)
- cron: '0 9 * * *'
```

## Lisans

MIT
