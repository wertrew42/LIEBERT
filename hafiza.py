import json
import os

DOSYA_ADI = "hafiza.json"
PROFIL_DOSYASI = "profil.json"

def hafiza_yukle():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            try:
                eski_hafiza = json.load(f)
                temiz_hafiza =[]
                
                # Google formatından OpenAI formatına dönüşüm köprüsü
                for mesaj in eski_hafiza:
                    role = mesaj.get("role", "user")
                    if role == "model": role = "assistant" # Groq 'model' rolünü sevmez
                    
                    # Eğer eski veri 'parts' içeriyorsa 'content'e çek
                    if "parts" in mesaj:
                        content = mesaj["parts"][0].get("text", "")
                    else:
                        content = mesaj.get("content", "")
                        
                    temiz_hafiza.append({"role": role, "content": content})
                return temiz_hafiza
            except json.JSONDecodeError:
                return[]
    return[]

def hafiza_kaydet(gecmis, limit=20): # LİMİT 20 OLARAK GÜNCELLENDİ
    serilestirilmis_gecmis =[]
    budanmis_gecmis = gecmis[-limit:] if len(gecmis) > limit else gecmis
    
    for mesaj in budanmis_gecmis:
        try:
            # OpenAI/Groq kütüphanesi mesajları dict veya obje olarak dönebilir, ikisini de yakalıyoruz
            if isinstance(mesaj, dict):
                r = mesaj.get("role")
                c = mesaj.get("content")
            else:
                r = getattr(mesaj, "role", "user")
                c = getattr(mesaj, "content", "")

            # ARTIK 'parts' YOK, SADECE 'content' VAR (Evrensel Yapı)
            serilestirilmis_gecmis.append({
                "role": r,
                "content": c
            })
        except Exception:
            continue
    
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(serilestirilmis_gecmis, f, ensure_ascii=False, indent=4)

def profil_yukle():
    if os.path.exists(PROFIL_DOSYASI):
        with open(PROFIL_DOSYASI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def profil_guncelle(yeni_veri_sozlugu):
    mevcut_profil = profil_yukle()
    mevcut_profil.update(yeni_veri_sozlugu)
    
    with open(PROFIL_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut_profil, f, ensure_ascii=False, indent=4)