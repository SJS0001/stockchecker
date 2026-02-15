Nejedná se o funkční verzi.

---

# Sneaker Stock Checker (Discord Bot)

Tento nástroj sloužil k automatickému monitorování skladových zásob na dvou populárních českých resellingových (komisních) portálech: **SneakerGallery** a **Section Prague**.

Hlavním účelem bylo rychle zjistit aktuální dostupnost konkrétních velikostí, aby prodejce věděl, zda má smysl posílat do komise další kusy.

## 🚀 Hlavní funkce

* **Sledování zásob v reálném čase:** * U platformy Shoptet (SneakerGallery) bot využívá metodu zjišťování limitu košíku pro určení přesného počtu kusů (až do 20 ks).
* U platformy WooCommerce (Section Prague) bot čte data přímo z JSON metadat produktu.


* **Vyhledávání:** Bot přijímá buď přímý **URL odkaz**, nebo **klíčová slova** (v tom případě provede automatické vyhledání na webu a vybere první výsledek).
* **Ekonomické výpočty:**
* Výpočet odhadované výplaty pro prodejce (payout) po odečtení provize (standardně 15 %).
* Automatický převod CZK/EUR u SneakerGallery pomocí externího API pro směnné kurzy.


* **Vizuální přehled:** Barevné indikátory (emoji) pro rychlé vyhodnocení stavu zásob (např. červená při vysokém počtu kusů).
* **Paralelní zpracování:** Využití `ThreadPoolExecutor` pro bleskové zjištění všech velikostí najednou.

## 🛠 Použité technologie

* **Python 3.x**
* **discord.py** (komunikace s Discord API)
* **BeautifulSoup4** (web scraping a parsing HTML)
* **Requests** (HTTP komunikace)
* **Concurrent Futures** (multi-threading pro vyšší rychlost)

## ⌨️ Příkazy

Bot reaguje na prefix `.` (tečka):

| Příkaz | Popis | Příklad |
| --- | --- | --- |
| `.sg [odkaz/název]` | Zkontroluje sklad na **SneakerGallery.cz** | `.sg Dunk Low Panda` |
| `.sc [odkaz/název]` | Zkontroluje sklad na **SectionStore.cz** | `.sc https://sectionstore.cz/produkt/...` |
 
