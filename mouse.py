import pyautogui
from PIL import ImageGrab, ImageDraw

# ==========================================
# PYAUTOGUI GÜVENLİK AYARLARI
# ==========================================
pyautogui.FAILSAFE = True       # Sol üst köşeye gidince durdur
pyautogui.PAUSE = 0.05          # Komutlar arası küçük bekleme

# Son tıklama bilgisi (MOUSE_BAK için)
son_islem = {
    "tur": None,        # "tikla", "sur", "klavye"
    "x": None,
    "y": None,
    "x2": None,
    "y2": None,
    "detay": ""
}

# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def ekran_boyutu():
    """Ekran genişlik ve yüksekliğini döner."""
    g = pyautogui.size()
    return g.width, g.height

def koordinat_gecerli_mi(x, y):
    """Koordinatların ekran sınırları içinde olup olmadığını kontrol eder."""
    w, h = ekran_boyutu()
    if not (0 <= x <= w and 0 <= y <= h):
        return False, f"Koordinat ekran dışı! Ekran boyutu: {w}x{h}, İstenen: ({x},{y})"
    return True, ""

def parametre_parse(deger, tip=int, varsayilan=None):
    """Parametreyi güvenli şekilde parse eder."""
    try:
        return tip(deger.strip()) if isinstance(deger, str) else tip(deger)
    except (ValueError, AttributeError):
        return varsayilan

def tus_parse(tus_str):
    """
    Tuş kombinasyonunu pyautogui formatına çevirir.
    'ctrl+c' → ['ctrl', 'c']
    'enter'  → 'enter'
    """
    tus_str = tus_str.strip().lower()
    if "+" in tus_str:
        return [t.strip() for t in tus_str.split("+")]
    return tus_str

# ==========================================
# MOUSE FONKSİYONLARI
# ==========================================
def mouse_tikla(x, y, buton="LEFT", sure=0.3):
    """
    Belirtilen koordinata mouse tıklaması yapar.
    
    buton: LEFT (sol tık), RIGHT (sağ tık/context menu), DOUBLE (çift tık)
    sure:  Harekete kaç saniyede ulaşılacağı
    """
    global son_islem

    x = parametre_parse(x, int)
    y = parametre_parse(y, int)
    buton = str(buton).strip().upper() if buton else "LEFT"

    if x is None or y is None:
        return "HATA: Geçersiz koordinat değeri."

    gecerli, hata = koordinat_gecerli_mi(x, y)
    if not gecerli:
        return f"HATA: {hata}"

    try:
        pyautogui.moveTo(x, y, duration=sure)

        if buton == "DOUBLE":
            pyautogui.doubleClick(x, y)
            tur_aciklama = "Çift tıklama"
        elif buton == "RIGHT":
            pyautogui.rightClick(x, y)
            tur_aciklama = "Sağ tıklama"
        else:  # LEFT veya bilinmeyen → sol tık
            pyautogui.click(x, y)
            tur_aciklama = "Sol tıklama"

        son_islem.update({
            "tur": "tikla",
            "x": x, "y": y,
            "x2": None, "y2": None,
            "detay": f"{tur_aciklama} → ({x}, {y})"
        })

        return f"{tur_aciklama} tamamlandı. Konum: ({x}, {y})"

    except pyautogui.FailSafeException:
        return "HATA: FailSafe tetiklendi! Mouse sol üst köşeye gitti, işlem iptal edildi."
    except Exception as e:
        return f"HATA (mouse_tikla): {str(e)}"


def mouse_sur(x1, y1, x2, y2, buton="LEFT", sure=1.0):
    """
    Başlangıç noktasından bitiş noktasına sol/sağ tuş basılı tutarak sürükler.
    
    Kullanım: dosya taşıma, slider kaydırma, metin seçme
    sure: Sürükleme animasyon süresi (saniye)
    """
    global son_islem

    x1 = parametre_parse(x1, int)
    y1 = parametre_parse(y1, int)
    x2 = parametre_parse(x2, int)
    y2 = parametre_parse(y2, int)
    buton = str(buton).strip().upper() if buton else "LEFT"
    pbutton = "right" if buton == "RIGHT" else "left"

    if any(v is None for v in [x1, y1, x2, y2]):
        return "HATA: Geçersiz koordinat değeri."

    for (x, y) in [(x1, y1), (x2, y2)]:
        gecerli, hata = koordinat_gecerli_mi(x, y)
        if not gecerli:
            return f"HATA: {hata}"

    try:
        pyautogui.moveTo(x1, y1, duration=0.3)
        pyautogui.dragTo(x2, y2, duration=sure, button=pbutton)

        son_islem.update({
            "tur": "sur",
            "x": x1, "y": y1,
            "x2": x2, "y2": y2,
            "detay": f"Sürükleme ({pbutton}) → ({x1},{y1}) → ({x2},{y2})"
        })

        return f"Sürükleme tamamlandı. ({x1},{y1}) → ({x2},{y2}), Tuş: {buton}"

    except pyautogui.FailSafeException:
        return "HATA: FailSafe tetiklendi! İşlem iptal edildi."
    except Exception as e:
        return f"HATA (mouse_sur): {str(e)}"


def mouse_bak(prompt=""):
    """
    Son mouse işleminin yapıldığı noktayı 7px kırmızı kare ile işaretleyerek
    ekran görüntüsü alır ve base64 olarak döner.
    
    Koordinat farkı ve islem detayları da raporlanır.
    prompt: AI'a ek bağlam vermek için (opsiyonel)
    """
    if son_islem["tur"] is None:
        return None, "Henüz hiç mouse işlemi yapılmadı."

    try:
        ekran = ImageGrab.grab()
        draw  = ImageDraw.Draw(ekran)

        x = son_islem["x"]
        y = son_islem["y"]

        # Ana nokta — 7px kırmızı kare
        draw.rectangle(
            [x - 7, y - 7, x + 7, y + 7],
            outline="red", width=2
        )

        # Sürükleme ise bitiş noktasını da işaretle
        if son_islem["tur"] == "sur" and son_islem["x2"] is not None:
            x2 = son_islem["x2"]
            y2 = son_islem["y2"]
            draw.rectangle(
                [x2 - 7, y2 - 7, x2 + 7, y2 + 7],
                outline="orange", width=2
            )
            # Başlangıç → bitiş çizgisi
            draw.line([x, y, x2, y2], fill="yellow", width=1)

        gecici_yol = "temp_mouse_bak.png"
        ekran.save(gecici_yol)

        rapor = (
            f"SON İŞLEM: {son_islem['detay']}\n"
            f"Başlangıç: ({x}, {y})\n"
        )
        if son_islem["tur"] == "sur":
            rapor += f"Bitiş: ({son_islem['x2']}, {son_islem['y2']})\n"
        if prompt:
            rapor += f"Kullanıcı notu: {prompt}"

        return gecici_yol, rapor

    except Exception as e:
        return None, f"HATA (mouse_bak): {str(e)}"


# ==========================================
# KLAVYE FONKSİYONLARI
# ==========================================
def klavye_yaz(metin, sure=0.03):
    """
    Metni klavyeden yazılıyormuş gibi karakter karakter yazar.
    Türkçe karakter desteği için pyperclip fallback kullanır.
    
    sure: Karakterler arası gecikme (saniye)
    """
    global son_islem

    if not metin:
        return "HATA: Yazılacak metin boş."

    try:
        # Türkçe/özel karakter varsa clipboard üzerinden yaz
        try:
            import pyperclip
            pyperclip.copy(metin)
            pyautogui.hotkey('ctrl', 'v')
        except ImportError:
            # pyperclip yoksa direkt yaz (Türkçe bozulabilir)
            pyautogui.write(metin, interval=sure)

        son_islem.update({
            "tur": "klavye",
            "x": None, "y": None,
            "detay": f"Metin yazıldı: '{metin[:50]}{'...' if len(metin) > 50 else ''}'"
        })

        return f"Metin yazıldı: '{metin[:80]}{'...' if len(metin) > 80 else ''}'"

    except pyautogui.FailSafeException:
        return "HATA: FailSafe tetiklendi!"
    except Exception as e:
        return f"HATA (klavye_yaz): {str(e)}"


def klavye_tus(kombinasyon):
    """
    Tek tuş veya kombinasyon basar.
    
    Örnekler:
      'enter'        → Enter tuşu
      'ctrl+c'       → Kopyala
      'ctrl+shift+t' → Yeni sekme (tarayıcı)
      'alt+f4'       → Pencereyi kapat
      'win+d'        → Masaüstü göster
    """
    global son_islem

    if not kombinasyon:
        return "HATA: Tuş kombinasyonu boş."

    try:
        tuslar = tus_parse(kombinasyon)

        if isinstance(tuslar, list):
            pyautogui.hotkey(*tuslar)
        else:
            pyautogui.press(tuslar)

        son_islem.update({
            "tur": "klavye",
            "x": None, "y": None,
            "detay": f"Tuş basıldı: '{kombinasyon}'"
        })

        return f"Tuş kombinasyonu çalıştırıldı: '{kombinasyon}'"

    except pyautogui.FailSafeException:
        return "HATA: FailSafe tetiklendi!"
    except Exception as e:
        return f"HATA (klavye_tus): {str(e)}"