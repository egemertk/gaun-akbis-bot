"""
AKBIS Telegram Bot - Web Scraping Modülü
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class Announcement:
    """Duyuru veri yapısı"""
    date: str
    title: str
    content: str
    files: List[Dict[str, str]]  # [{"name": "dosya.pdf", "url": "..."}]
    source_url: str
    author: str
    
    def get_hash(self) -> str:
        """Duyuru için benzersiz hash oluştur"""
        unique_str = f"{self.author}|{self.date}|{self.title}"
        return hashlib.md5(unique_str.encode()).hexdigest()


def scrape_akbis_page(url: str, author_name: str) -> List[Announcement]:
    """
    AKBIS akademisyen sayfasından duyuruları çeker.
    
    Args:
        url: AKBIS sayfa URL'i
        author_name: Akademisyen adı
        
    Returns:
        Duyuru listesi
    """
    announcements = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # "Duyuru / Döküman" bölümünü bul
        # AKBIS sayfalarında duyurular genellikle h5 tagları ile tarihleniyor
        announcement_section = soup.find('h4', string=re.compile(r'Duyuru.*Döküman', re.IGNORECASE))
        
        if not announcement_section:
            # Alternatif: tüm sayfadaki h5 tarih başlıklarını bul
            date_headers = soup.find_all('h5')
        else:
            # Duyuru bölümünden sonraki h5 tagları
            date_headers = announcement_section.find_all_next('h5')
        
        current_date = ""
        current_title = ""
        current_content = []
        current_files = []
        
        for element in soup.find_all(['h5', 'p', 'a']):
            # Tarih başlığı (format: 05.01.2026)
            if element.name == 'h5':
                text = element.get_text(strip=True)
                # Tarih formatını kontrol et
                date_match = re.match(r'(\d{2}\.\d{2}\.\d{4})(.*)', text)
                if date_match:
                    # Önceki duyuruyu kaydet
                    if current_date and current_title:
                        announcements.append(Announcement(
                            date=current_date,
                            title=current_title,
                            content="\n".join(current_content).strip(),
                            files=current_files.copy(),
                            source_url=url,
                            author=author_name
                        ))
                    
                    # Yeni duyuru başlat
                    current_date = date_match.group(1)
                    current_title = date_match.group(2).strip() if date_match.group(2) else ""
                    current_content = []
                    current_files = []
            
            # İçerik paragrafları
            elif element.name == 'p' and current_date:
                text = element.get_text(strip=True)
                if text:
                    current_content.append(text)
            
            # Dosya linkleri
            elif element.name == 'a' and current_date:
                href = element.get('href', '')
                if href and ('upload/files' in href or href.endswith('.pdf') or href.endswith('.doc') or href.endswith('.docx') or href.endswith('.pptx')):
                    file_name = element.get_text(strip=True) or href.split('/')[-1]
                    # URL'yi tam yap
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = 'https://akbis.gaziantep.edu.tr' + href
                        else:
                            href = 'https://akbis.gaziantep.edu.tr/' + href
                    current_files.append({"name": file_name, "url": href})
        
        # Son duyuruyu da ekle
        if current_date and current_title:
            announcements.append(Announcement(
                date=current_date,
                title=current_title,
                content="\n".join(current_content).strip(),
                files=current_files.copy(),
                source_url=url,
                author=author_name
            ))
                    
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    
    return announcements


def scrape_akbis_page_v2(url: str, author_name: str) -> List[Announcement]:
    """
    AKBIS akademisyen sayfasından duyuruları çeker.
    HTML yapısı:
    - button.btn-link.text-left: Başlık (tarih + title)
    - span.badge: Tarih (DD.MM.YYYY)
    - data-target: Collapse div ID'si (#collapse2One1 gibi)
    - div.collapse > div.card-body: İçerik ve dosyalar
    """
    announcements = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Duyuru başlık butonlarını bul
        title_buttons = soup.find_all('button', class_=lambda c: c and 'btn-link' in c and 'text-left' in c)
        
        for button in title_buttons:
            try:
                # Tarih: span.badge içinde
                date_span = button.find('span', class_=lambda c: c and 'badge' in c)
                date = date_span.get_text(strip=True) if date_span else ""
                
                # Başlık: button text'inden tarihi çıkar
                full_text = button.get_text(strip=True)
                title = full_text.replace(date, '').strip() if date else full_text
                
                # İçerik: data-target ile ilişkili collapse div
                target_id = button.get('data-target', '')
                content = ""
                files = []
                
                if target_id:
                    # #collapse2One1 -> collapse2One1
                    target_id = target_id.lstrip('#')
                    content_div = soup.find('div', id=target_id)
                    
                    if content_div:
                        # Card-body içindeki text
                        card_body = content_div.find('div', class_=lambda c: c and 'card-body' in c)
                        if card_body:
                            # Tüm text'i al
                            content = card_body.get_text(separator="\n", strip=True)
                            
                            # Dosya linklerini bul
                            for a in card_body.find_all('a', href=True):
                                href = a.get('href', '')
                                # PDF, DOC, DOCX, PPTX, XLSX dosyalarını veya upload/files içindeki linkleri al
                                if href and ('upload/files' in href or any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.pptx', '.xlsx'])):
                                    file_name = a.get_text(strip=True) or href.split('/')[-1]
                                    # URL'yi tam yap
                                    if not href.startswith('http'):
                                        if href.startswith('/'):
                                            href = 'https://akbis.gaziantep.edu.tr' + href
                                        else:
                                            href = 'https://akbis.gaziantep.edu.tr/' + href
                                    files.append({"name": file_name, "url": href})
                
                if date and title:
                    announcements.append(Announcement(
                        date=date,
                        title=title,
                        content=content[:1000],  # Max 1000 karakter
                        files=files,
                        source_url=url,
                        author=author_name
                    ))
                    
            except Exception as e:
                print(f"Error parsing announcement: {e}")
                continue
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    
    return announcements


def scrape_eee_page(base_url: str = "https://eee.gaziantep.edu.tr") -> List[Announcement]:
    """
    EEE Bölüm sayfasından duyuruları çeker.
    
    Returns:
        Duyuru listesi
    """
    announcements = []
    announcements_url = f"{base_url}/duyurular.php"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(announcements_url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Duyuru listesi sayfasındaki her duyuru linkini bul
        # Format: [Tarih Başlık](duyuru.php?id=XXX)
        announcement_links = soup.find_all('a', href=re.compile(r'duyuru\.php\?id=\d+'))
        
        for link in announcement_links[:20]:  # Son 20 duyuru
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Tarih ve başlığı ayır
            date_match = re.match(r'(\d{1,2}\s+\w+\s+\d{4})(.*)', text)
            if date_match:
                date = date_match.group(1).strip()
                title = date_match.group(2).strip()
            else:
                # Alternatif format: tarihi parent elementten al
                parent = link.find_parent()
                date_elem = parent.find(class_=re.compile(r'date|tarih', re.I)) if parent else None
                date = date_elem.get_text(strip=True) if date_elem else ""
                title = text
            
            # Detay sayfasını çek
            detail_url = f"{base_url}/{href}" if not href.startswith('http') else href
            
            try:
                detail_response = requests.get(detail_url, headers=headers, timeout=30)
                detail_response.encoding = 'utf-8'
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                
                # İçeriği bul
                content_div = detail_soup.find('div', class_=re.compile(r'content|icerik|duyuru', re.I))
                content = content_div.get_text(separator="\n", strip=True) if content_div else ""
                
                # Dosyaları bul
                files = []
                for a in detail_soup.find_all('a', href=True):
                    ahref = a.get('href', '')
                    if any(ahref.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.pptx', '.xlsx']):
                        file_name = a.get_text(strip=True) or ahref.split('/')[-1]
                        if not ahref.startswith('http'):
                            ahref = f"{base_url}/{ahref}"
                        files.append({"name": file_name, "url": ahref})
                
                announcements.append(Announcement(
                    date=date,
                    title=title,
                    content=content[:500],  # İlk 500 karakter
                    files=files,
                    source_url=detail_url,
                    author="EEE Bölümü"
                ))
                
            except Exception as e:
                print(f"Error fetching detail page {detail_url}: {e}")
                # Detay sayfası çekilemese bile ana bilgiyi ekle
                announcements.append(Announcement(
                    date=date,
                    title=title,
                    content="",
                    files=[],
                    source_url=detail_url,
                    author="EEE Bölümü"
                ))
    
    except requests.RequestException as e:
        print(f"Error fetching EEE announcements: {e}")
    except Exception as e:
        print(f"Error parsing EEE page: {e}")
    
    return announcements


if __name__ == "__main__":
    # Test
    print("Testing AKBIS scraper...")
    test_url = "https://akbis.gaziantep.edu.tr/detay/?A_ID=9132_profesor_ergun-ercelebi"
    announcements = scrape_akbis_page_v2(test_url, "Prof. Dr. Ergün ERÇELEBİ")
    
    print(f"Found {len(announcements)} announcements")
    for ann in announcements[:3]:
        print(f"\n--- {ann.date} ---")
        print(f"Title: {ann.title}")
        print(f"Content: {ann.content[:100]}...")
        print(f"Files: {ann.files}")
        print(f"Hash: {ann.get_hash()}")
