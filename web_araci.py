import webbrowser

def web_ac(url):
    """Belirtilen URL'yi sistemin varsayılan tarayıcısında açar."""
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Başarılı: {url} adresi tarayıcıda açıldı ve kullanıcıya gösterildi."
    except Exception as e:
        return f"Web açma hatası: {e}"