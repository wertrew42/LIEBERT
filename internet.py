from duckduckgo_search import DDGS

def internette_ara(sorgu):
    """Verilen sorguyu internette arar ve özet sonuçları döner."""
    try:
        print(f"--- 🌐 İnternet Taranıyor: {sorgu} ---")
        results = DDGS().text(keywords=sorgu, region='tr-tr', safesearch='off', max_results=4)
        
        if not results:
            return "İnternette bununla ilgili bir sonuç bulunamadı."
            
        ozet = "İNTERNET ARAMA SONUÇLARI:\n"
        for i, r in enumerate(results, 1):
            ozet += f"{i}. {r['title']}: {r['body']} (Link: {r['href']})\n"
            
        return ozet
    except Exception as e:
        return f"İnternet bağlantı hatası: {str(e)}"