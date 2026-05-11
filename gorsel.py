import os
import base64
import cv2
from PIL import ImageGrab
from openai import OpenAI

def resim_analiz_et(api_key, base_url, model, dosya_yolu, prompt="Bu görseli detaylıca analiz et."):
    if not os.path.exists(dosya_yolu):
        return f"HATA: Görsel dosyası bulunamadı: {dosya_yolu}"
    
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        with open(dosya_yolu, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content":[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024
        )
        return f"GÖRSEL ANALİZ RAPORU:\n{response.choices[0].message.content}"
    except Exception as e:
        return f"Görsel analiz hatası: {str(e)}"

def masaustu_cek_ve_analiz_et(api_key, base_url, model, prompt=""):
    """Masaüstünün anlık görüntüsünü alır ve analiz eder."""
    if not prompt:
        prompt = "Bu kullanıcının masaüstü ekran görüntüsü. Ekranda neler açık, neler var detaylıca anlat."
        
    gecici_yol = "temp_masaustu.png"
    try:
        ekran = ImageGrab.grab()
        ekran.save(gecici_yol)
        sonuc = resim_analiz_et(api_key, base_url, model, gecici_yol, prompt)
        if os.path.exists(gecici_yol):
            os.remove(gecici_yol) # İzi sil
        return sonuc
    except Exception as e:
        return f"Masaüstü yakalama hatası: {e}"

def kamera_cek_ve_analiz_et(api_key, base_url, model, prompt=""):
    """Kameradan anlık görüntü alır ve analiz eder."""
    if not prompt:
        prompt = "Bu kullanıcının kamerasından anlık bir görüntü. Gördüklerini detaylıca anlat."
        
    gecici_yol = "temp_kamera.jpg"
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite(gecici_yol, frame)
            sonuc = resim_analiz_et(api_key, base_url, model, gecici_yol, prompt)
            if os.path.exists(gecici_yol):
                os.remove(gecici_yol) # İzi sil
            return sonuc
        else:
            return "HATA: Kameradan görüntü alınamadı. Kamera kapalı veya başka bir uygulama tarafından kullanılıyor olabilir."
    except Exception as e:
        return f"Kamera yakalama hatası: {e}"