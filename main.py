import os
import json
import datetime
import re
import asyncio
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from openai import OpenAI

import hafiza
import internet
import terminal
import gorsel
import web_araci
import mouse as mouse_modulu

# ==========================================
# AYARLAR — PLACEHOLDER'LARI DOLDUR
# ==========================================
TELEGRAM_TOKEN = "86...YDY"
AUTHORIZED_ID  = 888888
API_DOSYASI    = "APIs.json"
BASE_URL       = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL_NAME     = "gemini-flash-latest"

# ==========================================
# API YÖNETİMİ
# ==========================================
def json_yukle():
    if not os.path.exists(API_DOSYASI):
        sablon = {"aktif_api": "", "api_listesi": {"API_1": "BURAYA_API_KEY_YAZIN"}}
        with open(API_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(sablon, f, indent=4)
        return sablon
    with open(API_DOSYASI, "r", encoding="utf-8") as f:
        return json.load(f)

def json_kaydet(veri):
    with open(API_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

def aktif_api_ayarla(api_ismi):
    veri = json_yukle()
    api_key = veri["api_listesi"].get(api_ismi, "")
    veri["aktif_api"] = api_key
    json_kaydet(veri)
    return api_key

# ==========================================
# OTURUM DURUMU
# ==========================================
oturum = {
    "messages": [],
    "api_key": "",
    "terminal_event": None,
    "terminal_approved": False,
    "terminal_komut": "",
    "mesgul": False,
}

# ==========================================
# MESAJ YARDIMCILARI
# ==========================================
async def log_gonder(bot, chat_id, mesaj):
    zaman = datetime.datetime.now().strftime("%H:%M:%S")
    await bot.send_message(
        chat_id=chat_id,
        text=f"📟 `[{zaman}] {mesaj}`",
        parse_mode="Markdown"
    )

async def liebert_mesaj_gonder(bot, chat_id, mesaj):
    # Uzun mesajları böl (Telegram 4096 karakter limiti)
    limit = 4000
    if len(mesaj) <= limit:
        await bot.send_message(chat_id=chat_id, text=f"🤖 LIEBERT:\n{mesaj}")
    else:
        parcalar = [mesaj[i:i+limit] for i in range(0, len(mesaj), limit)]
        for i, parca in enumerate(parcalar):
            baslik = "🤖 LIEBERT:\n" if i == 0 else "🤖 LIEBERT (devam):\n"
            await bot.send_message(chat_id=chat_id, text=f"{baslik}{parca}")

async def sistem_mesaj_gonder(bot, chat_id, mesaj, emoji="⚡"):
    await bot.send_message(chat_id=chat_id, text=f"{emoji} {mesaj}")

# ==========================================
# YETKİ KONTROLÜ
# ==========================================
def yetkili_mi(update: Update) -> bool:
    return update.effective_user.id == AUTHORIZED_ID

# ==========================================
# /start — API SEÇİMİ
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not yetkili_mi(update):
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return

    veri = json_yukle()
    api_listesi = veri.get("api_listesi", {})

    if not api_listesi:
        await update.message.reply_text("❌ APIs.json içinde API anahtarı bulunamadı.")
        return

    butonlar = [
        [InlineKeyboardButton(f"🔑 {isim}", callback_data=f"api_sec:{isim}")]
        for isim in api_listesi.keys()
    ]
    klavye = InlineKeyboardMarkup(butonlar)
    await update.message.reply_text(
        "🤖 LIEBERT başlatılıyor.\nKullanılacak API anahtarını seç:",
        reply_markup=klavye
    )

# ==========================================
# API SEÇİM CALLBACK
# ==========================================
async def api_sec_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != AUTHORIZED_ID:
        await query.edit_message_text("⛔ Yetkisiz erişim.")
        return

    api_ismi = query.data.split(":", 1)[1]
    api_key  = aktif_api_ayarla(api_ismi)

    if not api_key or api_key == "BURAYA_API_KEY_YAZIN":
        await query.edit_message_text("❌ Geçersiz API anahtarı.")
        return

    oturum["api_key"] = api_key
    oturum["mesgul"]  = False
    sistemi_baslat(api_key)

    await query.edit_message_text(
        f"✅ {api_ismi} seçildi.\n🤖 LIEBERT çevrimiçi. Komutlarını bekliyorum."
    )

# ==========================================
# SİSTEM BAŞLATICI & SYSTEM PROMPT
# ==========================================
def sistemi_baslat(api_key: str):
    su_an = datetime.datetime.now().strftime("%d %B %Y, %A")
    kullanici_profili = hafiza.profil_yukle()

    talimat = f"""
KİMLİK VE KİŞİLİK:
Ad: LIEBERT
Tarih: {su_an}
Rol: Üst düzey, otonom, analitik ve aksiyon odaklı dijital operatör.
Amaç: Kullanıcının verdiği görevleri en az adımda, en yüksek doğrulukla tamamlamak.
Arayüz: Telegram üzerinden çalışıyor. Kullanıcı mobil/uzaktan komut veriyor.
İşletim Sistemi: Windows. Terminal komutlarında SADECE Windows cmd/PowerShell kullan.

BİLİNENLER (Profil):
{json.dumps(kullanici_profili, ensure_ascii=False)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPERASYONEL KURALLAR (HAYATİ ÖNEM TAŞIR)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. KOMUT KULLANIMI:
   - İşlem yapacaksan KESİNLİKLE [[[KOMUT_ADI: parametreler]]] formatını kullan.
   - Sadece açıklama yapıyorsan komut formatını KULLANMA.
   - Komutu yazdığın an sistem onu gerçek emir olarak algılar. Deneme yapma.
   - Komut içindeki metinlerde "\\n" veya "/n" KULLANMA. Gerçek alt satır kullan.

2. ÇOKLU ADIM:
   - Karmaşık görevlerde adım adım git. Her adımda SİSTEM RAPORU bekle.
   - Dosya işlemleri için SADECE [[[TERMINAL]]] kullan.

3. HAFIZA:
   - Yeni bilgi öğrenirsen: [[[BILGI_EKLE: {{"anahtar": "değer"}}]]]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KOMUT SÖZLÜĞÜ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A. İNTERNET VE ARAŞTIRMA
───────────────────────
[[[INTERNET_ARA: "sorgu"]]]
  Örnek: [[[INTERNET_ARA: "Python asyncio tutorial"]]]

B. SİSTEM VE DOSYA
──────────────────
[[[TERMINAL: komut]]]
  Örnek: [[[TERMINAL: dir C:\\Users\\Kullanici\\Desktop]]]
  Örnek: [[[TERMINAL: powershell Get-Process]]]

C. GÖRSEL VE KAMERA
───────────────────
[[[MASAUSTU_BAK: "prompt"]]]
  → Ekranın anlık görüntüsünü alır, AI gözüyle analiz eder.
  Örnek: [[[MASAUSTU_BAK: "Ekranda hangi pencereler açık?"]]]
  Örnek: [[[MASAUSTU_BAK: "Kaydet butonu nerede, koordinatını ver"]]]

[[[KAMERA_BAK: "prompt"]]]
  → Kameradan anlık görüntü alır, analiz eder.
  Örnek: [[[KAMERA_BAK: "Masanın üzerinde ne var?"]]]

[[[GORSEL_ANALIZ: "dosya_yolu" ::: "prompt"]]]
  Örnek: [[[GORSEL_ANALIZ: "C:\\ekran.png" ::: "Bu görselde ne yazıyor?"]]]

D. WEB
──────
[[[WEB_PENCERESI: "url"]]]
  Örnek: [[[WEB_PENCERESI: "https://google.com"]]]

E. MOUSE KONTROLÜ
─────────────────
[[[MOUSE_TIKLA: x ::: y ::: BUTON]]]
  BUTON seçenekleri: LEFT (varsayılan), RIGHT (sağ tık), DOUBLE (çift tık)
  
  Örnekler:
    [[[MOUSE_TIKLA: 234 ::: 891 ::: LEFT]]]    → Sol tık
    [[[MOUSE_TIKLA: 234 ::: 891 ::: RIGHT]]]   → Sağ tık (context menu açar)
    [[[MOUSE_TIKLA: 234 ::: 891 ::: DOUBLE]]]  → Çift tık (dosya/klasör açar)
    [[[MOUSE_TIKLA: 234 ::: 891]]]             → BUTON yazılmazsa LEFT varsayılır

[[[MOUSE_SUR: x1 ::: y1 ::: x2 ::: y2 ::: BUTON]]]
  Sol veya sağ tuş BASILI TUTARAK sürükler.
  BUTON: LEFT (varsayılan), RIGHT
  
  Örnekler:
    [[[MOUSE_SUR: 100 ::: 200 ::: 500 ::: 200 ::: LEFT]]]
      → (100,200)'den (500,200)'e sol tuşla sürükle (metin seçme, slider)
    [[[MOUSE_SUR: 300 ::: 400 ::: 600 ::: 400 ::: LEFT]]]
      → Dosyayı (300,400)'den (600,400)'e taşı

[[[MOUSE_BAK: "prompt"]]]
  → Son mouse işleminin yapıldığı noktayı KIRMIZI KARE ile işaretler.
  → Sürüklemede başlangıç (kırmızı) ve bitiş (turuncu) gösterilir.
  → Koordinat raporu + ekran görüntüsü Telegram'a gönderilir.
  → Kalibrasyon ve doğrulama için kullan.
  
  Örnekler:
    [[[MOUSE_BAK: "Kaydet butonunu hedeflemiştim, tam ortasına geldim mi?"]]]
    [[[MOUSE_BAK: "Dosyayı doğru klasöre sürükledim mi?"]]]
    [[[MOUSE_BAK: "İmlecin şu anki pozisyonu ekranın neresinde?"]]]

  MOUSE_BAK KULLANIM STRATEJİSİ:
  - Her tıklamadan sonra otomatik çağırma. Gerek duyduğunda kullan.
  - Hassas işlemlerde (küçük butonlar, menüler) tıklama SONRASI doğrulama yap.
  - Birden fazla ardışık tıklamada sadece kritik adımları doğrula.
  - Görüntüyü alınca şunu değerlendir: "Hedeflediğim yere ne kadar yakın?"

F. KLAVYE KONTROLÜ
──────────────────
[[[KLAVYE_YAZ: "metin"]]]
  → Metni klavyeden yazılıyormuş gibi girer. Türkçe destekler.
  
  Örnekler:
    [[[KLAVYE_YAZ: "Merhaba, bu bir test mesajıdır."]]]
    [[[KLAVYE_YAZ: "print('Hello World')"]]]

[[[KLAVYE_TUS: "kombinasyon"]]]
  → Tek tuş veya kombinasyon basar.
  
  Örnekler:
    [[[KLAVYE_TUS: "enter"]]]           → Enter
    [[[KLAVYE_TUS: "ctrl+c"]]]          → Kopyala
    [[[KLAVYE_TUS: "ctrl+v"]]]          → Yapıştır
    [[[KLAVYE_TUS: "ctrl+z"]]]          → Geri al
    [[[KLAVYE_TUS: "ctrl+s"]]]          → Kaydet
    [[[KLAVYE_TUS: "alt+f4"]]]          → Pencereyi kapat
    [[[KLAVYE_TUS: "win+d"]]]           → Masaüstü göster
    [[[KLAVYE_TUS: "ctrl+shift+t"]]]    → Kapalı sekmeyi aç
    [[[KLAVYE_TUS: "tab"]]]             → Tab
    [[[KLAVYE_TUS: "escape"]]]          → Escape
    [[[KLAVYE_TUS: "delete"]]]          → Delete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TİPİK İŞ AKIŞLARI (ÖRNEKLER)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SENARYO 1 — Ekranda bir butona tıklama:
  1. [[[MASAUSTU_BAK: "Kaydet butonu nerede? Koordinatını ver."]]]
  2. (Rapor gelir: "Kaydet butonu 456,312 koordinatında")
  3. [[[MOUSE_TIKLA: 456 ::: 312 ::: LEFT]]]
  4. [[[MOUSE_BAK: "Kaydet butonuna tam bastım mı?"]]]

SENARYO 2 — Dosya taşıma:
  1. [[[MASAUSTU_BAK: "Taşınacak dosya ve hedef klasör nerede?"]]]
  2. [[[MOUSE_SUR: 200 ::: 300 ::: 500 ::: 300 ::: LEFT]]]
  3. [[[MOUSE_BAK: "Dosya doğru klasöre gitti mi?"]]]

SENARYO 3 — Metin editörüne yazma:
  1. [[[MOUSE_TIKLA: 640 ::: 400 ::: LEFT]]]   (editöre tıkla)
  2. [[[KLAVYE_TUS: "ctrl+a"]]]                (hepsini seç)
  3. [[[KLAVYE_YAZ: "Yeni içerik buraya"]]]    (yaz)
  4. [[[KLAVYE_TUS: "ctrl+s"]]]                (kaydet)

SENARYO 4 — Sağ tık menüsü:
  1. [[[MOUSE_TIKLA: 234 ::: 567 ::: RIGHT]]]  (context menu aç)
  2. [[[MASAUSTU_BAK: "Menüde hangi seçenekler var?"]]]
  3. (Rapor gelir, hedef seçeneğin koordinatı)
  4. [[[MOUSE_TIKLA: x ::: y ::: LEFT]]]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CEVAP FORMATI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Kısa ve sonuç odaklı ol. Gereksiz açıklama yapma.
- Telegram düz metin formatı kullan. Markdown işaretleri kullanma (* _ ` vb.)
- Görev bitti mi? Kısa rapor ver ve sus.
"""

    eski_konusmalar = hafiza.hafiza_yukle()
    if not isinstance(eski_konusmalar, list):
        eski_konusmalar = []

    oturum["messages"] = [{"role": "system", "content": talimat}]
    oturum["messages"].extend(eski_konusmalar)

# ==========================================
# TERMINAL ONAY MEKANİZMASI
# ==========================================
async def terminal_onay_sor(bot, chat_id, komut):
    kisa = komut[:300] + "..." if len(komut) > 300 else komut
    klavye = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Onayla", callback_data="terminal:onayla"),
        InlineKeyboardButton("❌ Reddet", callback_data="terminal:reddet"),
    ]])
    await bot.send_message(
        chat_id=chat_id,
        text=f"⚡ Kritik İşlem Onayı\n\nŞu komut çalıştırılacak:\n{kisa}\n\nOnaylıyor musun?",
        reply_markup=klavye
    )

async def terminal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != AUTHORIZED_ID:
        return

    karar = query.data.split(":")[1]
    oturum["terminal_approved"] = (karar == "onayla")

    if oturum["terminal_approved"]:
        await query.edit_message_text("✅ Terminal komutu onaylandı, çalıştırılıyor...")
    else:
        await query.edit_message_text("❌ Terminal komutu reddedildi.")

    if oturum["terminal_event"]:
        oturum["terminal_event"].set()

# ==========================================
# KOMUT İŞLEYİCİ
# ==========================================
async def komut_isle(bot, chat_id, komut_adi, p1, p2, api_key):
    """
    Tek bir komutu işler, sonucu döner.
    main loop'u temiz tutar.
    """
    sonuc = ""

    # --- TERMINAL ---
    if komut_adi == "TERMINAL":
        oturum["terminal_event"]    = threading.Event()
        oturum["terminal_approved"] = False
        oturum["terminal_event"].clear()

        await terminal_onay_sor(bot, chat_id, p1)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, oturum["terminal_event"].wait)

        if oturum["terminal_approved"]:
            await log_gonder(bot, chat_id, "Terminal çalıştırılıyor...")
            sonuc = terminal.komut_calistir(p1)
            kisa_sonuc = sonuc[:3000] if len(sonuc) > 3000 else sonuc
            await bot.send_message(chat_id=chat_id, text=f"🖥️\n{kisa_sonuc}")
        else:
            sonuc = "KULLANICI REDDETTİ: Terminal işlemi iptal edildi."

    # --- İNTERNET ---
    elif komut_adi == "INTERNET_ARA":
        await log_gonder(bot, chat_id, f"İnternette aranıyor: {p1}")
        sonuc = internet.internette_ara(p1)

    # --- WEB ---
    elif komut_adi == "WEB_PENCERESI":
        await log_gonder(bot, chat_id, f"Web açılıyor: {p1}")
        sonuc = web_araci.web_ac(p1)

    # --- MASAÜSTÜ ---
    elif komut_adi == "MASAUSTU_BAK":
        await log_gonder(bot, chat_id, "Ekran görüntüsü alınıyor...")
        prompt = p1 or "Ekranda neler açık, neler var detaylıca anlat."
        gecici_yol = "temp_masaustu.png"
        try:
            from PIL import ImageGrab
            ekran = ImageGrab.grab()
            ekran.save(gecici_yol)
            with open(gecici_yol, "rb") as f:
                await bot.send_photo(chat_id=chat_id, photo=f, caption="📸 Masaüstü")
            sonuc = gorsel.resim_analiz_et(api_key, BASE_URL, MODEL_NAME, gecici_yol, prompt)
            if os.path.exists(gecici_yol):
                os.remove(gecici_yol)
        except Exception as e:
            sonuc = f"Masaüstü yakalama hatası: {e}"

    # --- KAMERA ---
    elif komut_adi == "KAMERA_BAK":
        await log_gonder(bot, chat_id, "Kameradan görüntü alınıyor...")
        prompt = p1 or "Kameradan anlık görüntü. Gördüklerini detaylıca anlat."
        gecici_yol = "temp_kamera.jpg"
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite(gecici_yol, frame)
                with open(gecici_yol, "rb") as f:
                    await bot.send_photo(chat_id=chat_id, photo=f, caption="📸 Kamera")
                sonuc = gorsel.resim_analiz_et(api_key, BASE_URL, MODEL_NAME, gecici_yol, prompt)
                if os.path.exists(gecici_yol):
                    os.remove(gecici_yol)
            else:
                sonuc = "HATA: Kameradan görüntü alınamadı."
        except Exception as e:
            sonuc = f"Kamera hatası: {e}"

    # --- GÖRSEL ANALİZ ---
    elif komut_adi == "GORSEL_ANALIZ":
        await log_gonder(bot, chat_id, f"Görsel analiz: {p1}")
        prompt = p2 or "Bu görseli analiz et."
        sonuc = gorsel.resim_analiz_et(api_key, BASE_URL, MODEL_NAME, p1, prompt)

    # --- MOUSE TIKLA ---
    elif komut_adi == "MOUSE_TIKLA":
        parcalar = [s.strip() for s in p1.split(":::")]
        x      = parcalar[0] if len(parcalar) > 0 else "0"
        y      = parcalar[1] if len(parcalar) > 1 else "0"
        buton  = parcalar[2] if len(parcalar) > 2 else "LEFT"
        await log_gonder(bot, chat_id, f"Mouse tıklama: ({x},{y}) [{buton}]")
        sonuc = mouse_modulu.mouse_tikla(x, y, buton)

    # --- MOUSE SÜR ---
    elif komut_adi == "MOUSE_SUR":
        parcalar = [s.strip() for s in p1.split(":::")]
        x1     = parcalar[0] if len(parcalar) > 0 else "0"
        y1     = parcalar[1] if len(parcalar) > 1 else "0"
        x2     = parcalar[2] if len(parcalar) > 2 else "0"
        y2     = parcalar[3] if len(parcalar) > 3 else "0"
        buton  = parcalar[4] if len(parcalar) > 4 else "LEFT"
        await log_gonder(bot, chat_id, f"Sürükleme: ({x1},{y1}) → ({x2},{y2}) [{buton}]")
        sonuc = mouse_modulu.mouse_sur(x1, y1, x2, y2, buton)

    # --- MOUSE BAK ---
    elif komut_adi == "MOUSE_BAK":
        await log_gonder(bot, chat_id, "Son mouse işlemi görüntüleniyor...")
        prompt = p1 or ""
        gorsel_yol, rapor = mouse_modulu.mouse_bak(prompt)
        if gorsel_yol and os.path.exists(gorsel_yol):
            with open(gorsel_yol, "rb") as f:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=f"🎯 Mouse Konum Raporu\n{rapor[:900]}"
                )
            os.remove(gorsel_yol)
        sonuc = rapor

    # --- KLAVYE YAZ ---
    elif komut_adi == "KLAVYE_YAZ":
        await log_gonder(bot, chat_id, f"Klavye yazıyor: '{p1[:40]}'")
        sonuc = mouse_modulu.klavye_yaz(p1)

    # --- KLAVYE TUŞ ---
    elif komut_adi == "KLAVYE_TUS":
        await log_gonder(bot, chat_id, f"Tuş kombinasyonu: {p1}")
        sonuc = mouse_modulu.klavye_tus(p1)

    # --- BİLGİ EKLE ---
    elif komut_adi == "BILGI_EKLE":
        sonuc = ""  # Üstte ayrıca işleniyor

    else:
        sonuc = f"HATA: Bilinmeyen komut '{komut_adi}'"

    return sonuc

# ==========================================
# ANA AI İŞLEMCİSİ
# ==========================================
async def ai_isle(bot, chat_id, user_input: str):
    api_key = oturum["api_key"]
    if not api_key:
        await sistem_mesaj_gonder(bot, chat_id, "Önce /start ile API seç.", "⚠️")
        return

    client = OpenAI(api_key=api_key, base_url=BASE_URL)

    await sistem_mesaj_gonder(bot, chat_id, "Düşünüyor...", "⏳")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=oturum["messages"]
        )
        gelen_cevap = response.choices[0].message.content
        oturum["messages"].append({"role": "assistant", "content": gelen_cevap})
    except Exception as e:
        await sistem_mesaj_gonder(bot, chat_id, f"API Hatası: {e}", "❌")
        oturum["mesgul"] = False
        return

    ajan_aktif   = True
    dongu_sayaci = 0
    MAX_DONGU    = 7

    while ajan_aktif and dongu_sayaci < MAX_DONGU:
        islem_yapildi = False
        raporlar      = []

        # BILGI_EKLE — özel parse
        if "[[[BILGI_EKLE:" in gelen_cevap:
            try:
                bas = gelen_cevap.find("[[[BILGI_EKLE:")
                son = gelen_cevap.find("]]]", bas)
                if son != -1:
                    kod      = gelen_cevap[bas:son+3]
                    json_str = kod.replace("[[[BILGI_EKLE:", "").replace("]]]", "").strip()
                    try:
                        veri = json.loads(json_str)
                    except Exception:
                        veri = json.loads(json_str.replace("'", '"'))
                    hafiza.profil_guncelle(veri)
                    gelen_cevap = gelen_cevap.replace(kod, "").strip()
                    await log_gonder(bot, chat_id, "Profil güncellendi.")
            except Exception:
                gelen_cevap = re.sub(
                    r'\[\[\[BILGI_EKLE:.*?\]\]\]', '', gelen_cevap, flags=re.DOTALL
                ).strip()

        # Komutları parse et
        komut_deseni = r'\[\[\[([A-Z_]+)(?::\s*(.*?))?\]\]\]'
        eslesmeler   = list(re.finditer(komut_deseni, gelen_cevap, re.DOTALL))

        for match in eslesmeler:
            islem_yapildi = True
            tam_eslesme  = match.group(0)
            komut_adi    = match.group(1)
            parametreler = match.group(2) or ""

            await log_gonder(bot, chat_id, f"Komut algılandı: {komut_adi}")

            try:
                # p1/p2 split (:::)
                if ":::" in parametreler:
                    parcalar = parametreler.split(":::", 1)
                    p1 = parcalar[0].strip().strip('"').strip("'")
                    p2 = parcalar[1].strip().strip('"').strip("'")
                else:
                    p1 = parametreler.strip().strip('"').strip("'")
                    p2 = ""

                # Mouse komutlarında p1'i olduğu gibi bırak (kendi parse ediyor)
                if komut_adi in ("MOUSE_TIKLA", "MOUSE_SUR", "MOUSE_BAK"):
                    p1 = parametreler  # split'i komut_isle içinde yapıyor

                sonuc = await komut_isle(bot, chat_id, komut_adi, p1, p2, api_key)

                if sonuc:
                    raporlar.append(f"KOMUT: {komut_adi}\nSONUÇ: {sonuc}")

                gelen_cevap = gelen_cevap.replace(tam_eslesme, "").strip()

            except Exception as e:
                hata = f"HATA ({komut_adi}): {str(e)}"
                raporlar.append(hata)
                await log_gonder(bot, chat_id, hata)

        # Temizlenmiş cevabı gönder
        gelen_cevap = gelen_cevap.strip()
        if gelen_cevap:
            await liebert_mesaj_gonder(bot, chat_id, gelen_cevap)

        if islem_yapildi and raporlar:
            sistem_raporu = (
                "SİSTEM RAPORU (Kullanıcı Görmüyor):\n"
                + "\n---\n".join(raporlar)
                + "\n\nBu sonuçlara göre sıradaki adımın ne? "
                  "Görev bittiyse kullanıcıya kısa rapor ver."
            )
            oturum["messages"].append({"role": "user", "content": sistem_raporu})

            await sistem_mesaj_gonder(bot, chat_id, "Sonuçlar işleniyor...", "⏳")
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=oturum["messages"]
                )
                gelen_cevap = response.choices[0].message.content
                oturum["messages"].append({"role": "assistant", "content": gelen_cevap})
                dongu_sayaci += 1
            except Exception as e:
                await sistem_mesaj_gonder(bot, chat_id, f"API Hatası: {e}", "❌")
                break
        else:
            ajan_aktif = False

    # Hafızayı kaydet
    try:
        hafiza.hafiza_kaydet(oturum["messages"][1:])
    except Exception as e:
        await log_gonder(bot, chat_id, f"Hafıza kaydetme hatası: {e}")

    await sistem_mesaj_gonder(bot, chat_id, "Hazır.", "✅")
    oturum["mesgul"] = False

# ==========================================
# MESAJ HANDLER
# ==========================================
async def mesaj_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not yetkili_mi(update):
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return

    if not oturum["api_key"]:
        await update.message.reply_text("⚠️ Önce /start ile API anahtarı seç.")
        return

    if oturum["mesgul"]:
        await update.message.reply_text("⏳ Şu an bir görev işleniyor, bekle...")
        return

    user_input = update.message.text.strip()
    oturum["mesgul"] = True
    oturum["messages"].append({"role": "user", "content": user_input})

    asyncio.create_task(
        ai_isle(context.bot, update.effective_chat.id, user_input)
    )

# ==========================================
# /api — ÇALIŞIRKEN API DEĞİŞTİR
# ==========================================
async def api_degistir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not yetkili_mi(update):
        return
    veri      = json_yukle()
    butonlar  = [
        [InlineKeyboardButton(f"🔑 {isim}", callback_data=f"api_sec:{isim}")]
        for isim in veri.get("api_listesi", {}).keys()
    ]
    await update.message.reply_text(
        "🔑 Yeni API anahtarını seç:",
        reply_markup=InlineKeyboardMarkup(butonlar)
    )

# ==========================================
# /durum
# ==========================================
async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not yetkili_mi(update):
        return

    veri     = json_yukle()
    aktif    = veri.get("aktif_api", "")
    api_ismi = next(
        (isim for isim, key in veri.get("api_listesi", {}).items() if key == aktif),
        "Bilinmiyor"
    )
    w, h = mouse_modulu.ekran_boyutu()

    await update.message.reply_text(
        f"🤖 LIEBERT Durum Raporu\n"
        f"{'─'*24}\n"
        f"🔑 Aktif API: {api_ismi}\n"
        f"💬 Mesaj sayısı: {len(oturum['messages'])}\n"
        f"⚙️ Meşgul: {'Evet' if oturum['mesgul'] else 'Hayır'}\n"
        f"🧠 Model: {MODEL_NAME}\n"
        f"🖥️ Ekran: {w}x{h}\n"
    )

# ==========================================
# /sifirla
# ==========================================
async def sifirla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not yetkili_mi(update):
        return
    api_key = oturum["api_key"]
    if api_key:
        sistemi_baslat(api_key)
    else:
        oturum["messages"] = []
    await update.message.reply_text("🔄 Oturum sıfırlandı.")

# ==========================================
# UYGULAMA BAŞLATMA
# ==========================================
def main():
    print("LIEBERT Telegram Bot başlatılıyor...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("api",     api_degistir))
    app.add_handler(CommandHandler("durum",   durum))
    app.add_handler(CommandHandler("sifirla", sifirla))
    app.add_handler(CallbackQueryHandler(api_sec_callback,  pattern="^api_sec:"))
    app.add_handler(CallbackQueryHandler(terminal_callback, pattern="^terminal:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_al))

    print("Bot çalışıyor. Telegram'dan /start yaz.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()