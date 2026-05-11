import subprocess
import json
import os
import datetime

def komut_kaydet(komut):
    """
    Kullanılan komutları kalıcı olarak komutlar.json dosyasına ekler.
    Asla silinmez, AI'a gönderilmez. Sadece yerel log tutar.
    """
    log_dosyasi = "komutlar.json"
    yeni_kayit = {
        "zaman": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "komut": komut
    }
    
    veriler =[]
    # Dosya varsa mevcut verileri oku
    if os.path.exists(log_dosyasi):
        try:
            with open(log_dosyasi, "r", encoding="utf-8") as f:
                veriler = json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass # Eğer dosya bozuksa veya boşsa, listeyi boş bırakır ve üstüne yazar
            
    veriler.append(yeni_kayit)
    
    # JSON'a kaydet
    with open(log_dosyasi, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

def komut_calistir(komut):
    """
    Verilen shell komutunu çalıştırır ve çıktısını döner.
    Güvenlik kısıtlaması yoktur, onay mekanizması main.py içindedir.
    """
    # Komutu arka planda log dosyasına kaydet
    komut_kaydet(komut)

    try:
        # Shell=True ile sistemin kendi terminali gibi davranır
        # capture_output ile çıktıyı yakalarız
        process = subprocess.run(
            komut, 
            shell=True, 
            text=True, 
            capture_output=True,
            encoding='utf-8', 
            errors='replace' # Türkçe karakter sorunlarını önler
        )
        
        cikti = ""
        if process.stdout:
            cikti += f"[STDOUT]:\n{process.stdout}\n"
        if process.stderr:
            cikti += f"[STDERR/HATA]:\n{process.stderr}\n"
            
        if not cikti:
            return "Komut çalıştırıldı ancak boş çıktı döndü."
            
        # --- KOTA / SINIRLAMA SİSTEMİ ---
        MAX_KARAKTER = 4000
        if len(cikti) > MAX_KARAKTER:
            uyari = f"\n\n...[SİSTEM UYARISI: Çıktı çok uzun ({len(cikti)} karakter). API sınırlarını korumak için {MAX_KARAKTER} karakterde kesildi. Devamını görmek için çıktıyı bir dosyaya yazdırın (örn: komut > cikti.txt) veya daha spesifik bir komut kullanın.]"
            cikti = cikti[:MAX_KARAKTER] + uyari
            
        return cikti

    except Exception as e:
        return f"Terminal Kritik Hata: {str(e)}"