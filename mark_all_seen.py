"""
Tüm mevcut duyuruları 'görüldü' olarak işaretle.
Bu script bir kez çalıştırılarak mevcut duyuruların tekrar gönderilmesini engeller.
"""
from config import AKBIS_PAGES
from scraper import scrape_akbis_page_v2
from database import init_db, mark_seen

def main():
    init_db()
    total = 0
    
    print("Tüm mevcut duyurular 'görüldü' olarak işaretleniyor...")
    
    for page in AKBIS_PAGES:
        try:
            anns = scrape_akbis_page_v2(page['url'], page['name'])
            for ann in anns:
                mark_seen(ann.get_hash(), ann.author, ann.title, ann.date)
                total += 1
            print(f"✅ {page['name']}: {len(anns)} duyuru")
        except Exception as e:
            print(f"❌ {page['name']}: Hata - {e}")
    
    print(f"\n✅ Toplam {total} duyuru 'görüldü' olarak işaretlendi.")
    print("Artık sadece YENİ duyurular gönderilecek.")

if __name__ == "__main__":
    main()
