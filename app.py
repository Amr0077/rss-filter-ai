import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, date
import xml.etree.ElementTree as ET
import time
import json
import os
import threading
from flask import Flask, Response
from googlenewsdecoder import gnewsdecoder

app = Flask(__name__)

# ============================================================
RSS_FEEDS = [
    {"url": "https://news.google.com/rss/search?q=%22FC+Bayern%22+when:1h&hl=de&gl=DE&ceid=DE:de", "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"]},
    {"url": "https://news.google.com/rss/search?q=%22FC+Bayern%22+when:1h&hl=de&gl=AT&ceid=AT:de", "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"]},
    {"url": "https://news.google.com/rss/search?q=%22FC+Bayern%22+when:1h&hl=de&gl=CH&ceid=CH:de", "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=en-GB&gl=GB&ceid=GB:en", "keywords": ["exclusive", "EXCLUSIVE", "sources", "according to sources", "confirmed", "told", "interview", "reveals", "claims", "understands"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=en-US&gl=US&ceid=US:en", "keywords": ["exclusive", "EXCLUSIVE", "sources", "confirmed", "told", "interview", "reveals", "claims", "understands"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=en-AU&gl=AU&ceid=AU:en", "keywords": ["exclusive", "sources", "confirmed", "interview", "reveals"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnich%22+when:1h&hl=es&gl=ES&ceid=ES:es", "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "asegura", "revela", "desvela"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnich%22+when:1h&hl=es-419&gl=MX&ceid=MX:es-419", "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "revela"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=fr&gl=FR&ceid=FR:fr", "keywords": ["exclusif", "interview", "nos sources", "confirme", "révèle", "apprend"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Monaco%22+when:1h&hl=it&gl=IT&ceid=IT:it", "keywords": ["esclusiva", "intervista", "fonti", "conferma", "rivela", "apprende"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnich%22+when:1h&hl=es-419&gl=AR&ceid=AR:es-419", "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "revela"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+de+Munique%22+when:1h&hl=pt-BR&gl=BR&ceid=BR:pt-419", "keywords": ["exclusivo", "entrevista", "fontes", "confirma", "revela", "apurou"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=pt-PT&gl=PT&ceid=PT:pt-150", "keywords": ["exclusivo", "entrevista", "fontes", "confirma", "revela"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnchen%22+when:1h&hl=nl&gl=NL&ceid=NL:nl", "keywords": ["exclusief", "interview", "bronnen", "meldt", "bevestigt", "onthult"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+Monachium%22+when:1h&hl=pl&gl=PL&ceid=PL:pl", "keywords": ["ekskluzywnie", "wywiad", "źródła", "potwierdza", "ujawnia", "donosi"]},
    {"url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnih%22+when:1h&hl=tr&gl=TR&ceid=TR:tr", "keywords": ["özel", "röportaj", "kaynaklar", "iddia", "açıkladı", "doğruladı"]},
    {"url": "https://news.google.com/rss/search?q=%22%D0%91%D0%B0%D0%B2%D0%B0%D1%80%D0%B8%D1%8F%22+when:1h&hl=ru&gl=RU&ceid=RU:ru", "keywords": ["эксклюзив", "интервью", "источники", "сообщает", "подтвердил"]},
    {"url": "https://news.google.com/rss/search?q=%22%E3%83%90%E3%82%A4%E3%82%A8%E3%83%AB%E3%83%B3%22+when:1h&hl=ja&gl=JP&ceid=JP:ja", "keywords": ["独占", "インタビュー", "情報", "明らかに", "確認"]},
    {"url": "https://news.google.com/rss/search?q=%22%EB%B0%94%EC%9D%B4%EC%97%90%EB%A5%B8%22+when:1h&hl=ko&gl=KR&ceid=KR:ko", "keywords": ["단독", "인터뷰", "소식통", "확인", "공개"]},
    {"url": "https://news.google.com/rss/search?q=%22%D8%A8%D8%A7%D9%8A%D8%B1%D9%86+%D9%85%D9%8A%D9%88%D9%86%D8%AE%22+when:1h&hl=ar&gl=SA&ceid=SA:ar", "keywords": ["حصري", "مصادر", "كشف", "أكد", "مقابلة"]},
]

BAYERN_TERMS = ["bayern", "münchen", "munich", "munchen", "munique", "monachium", "バイエルン", "바이에른", "бавари", "ميونخ", "بايرن", "münih", "monaco"]
PAYWALL_SIGNALS = ["subscribe", "abonnieren", "premium", "paywall", "sign in to read", "nur für abonnenten"]
MAX_ARTICLES = 20
UPDATE_INTERVAL = 300
CACHE_TTL_HOURS = 24

PROXY_URL = os.environ.get("PROXY_URL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

state = {
    "feed_xml": "",
    "cache": {},
    "lock": threading.Lock(),
    "running": False,
}


# ══════════════════════════════════════════════
# GitHub
# ══════════════════════════════════════════════

def github_get(filename):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None
    try:
        import base64
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            return {"content": base64.b64decode(data["content"]).decode("utf-8"), "sha": data["sha"]}
    except:
        pass
    return None


def github_save(filename, content):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    try:
        import base64
        existing = github_get(filename)
        body = {"message": f"Update {filename}", "content": base64.b64encode(content.encode()).decode()}
        if existing:
            body["sha"] = existing["sha"]
        requests.put(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            json=body, timeout=15,
        )
    except Exception as e:
        print(f"GitHub save error: {e}")


def load_cache():
    result = github_get("cache.json")
    if result:
        try:
            data = json.loads(result["content"])
            now = datetime.now(timezone.utc).timestamp()
            state["cache"] = {k: v for k, v in data.items() if now - v.get("ts", 0) < CACHE_TTL_HOURS * 3600}
            print(f"💾 Cache: {len(state['cache'])} روابط")
        except:
            pass


def save_cache():
    github_save("cache.json", json.dumps(state["cache"], ensure_ascii=False))


# ══════════════════════════════════════════════
# Core
# ══════════════════════════════════════════════

def decode_url(url):
    try:
        proxy = PROXY_URL if PROXY_URL else None
        result = gnewsdecoder(url, interval=1, proxy=proxy)
        if result.get("status"):
            return result["decoded_url"]
    except:
        pass
    return url


def fetch_article(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        is_short = len(text) < 500
        has_paywall = any(s in text.lower() for s in PAYWALL_SIGNALS)
        if len(text) < 200 or (is_short and has_paywall):
            return text, "paywall"
        return text.lower(), "ok"
    except Exception as e:
        return "", "failed"


def matches(text, keywords):
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True, kw
    return False, ""


def is_about_bayern(text):
    return any(t in text.lower() for t in BAYERN_TERMS)


def build_xml(articles):
    rss = ET.Element("rss", version="2.0")
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = "Bayern Filtered Feed"
    ET.SubElement(ch, "link").text = "https://news.google.com"
    ET.SubElement(ch, "description").text = "FC Bayern filtered news"
    ET.SubElement(ch, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    for a in articles:
        item = ET.SubElement(ch, "item")
        ET.SubElement(item, "title").text = a["title"]
        ET.SubElement(item, "link").text = a["link"]
        ET.SubElement(item, "description").text = a.get("summary", "")
        ET.SubElement(item, "pubDate").text = a.get("published", "")
        ET.SubElement(item, "guid").text = a["link"]
    return ET.tostring(rss, encoding="unicode", xml_declaration=True)


def run_filter():
    if state["running"]:
        return
    state["running"] = True
    try:
        print(f"\n{'='*50}")
        print(f"🔄 {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')} | Cache: {len(state['cache'])}")

        all_matched = []
        seen = set()

        for feed_config in RSS_FEEDS:
            feed_url = feed_config["url"]
            keywords = feed_config["keywords"]
            print(f"🔍 {feed_url[50:90]}...")

            try:
                feed = feedparser.parse(feed_url)
            except:
                continue

            for i, entry in enumerate(feed.entries[:MAX_ARTICLES]):
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")

                if link in seen:
                    continue
                seen.add(link)

                # Cache hit
                if link in state["cache"]:
                    cached = state["cache"][link]
                    if cached["result"] in ("matched", "paywall"):
                        all_matched.append({"title": title, "link": cached.get("real_url", link), "summary": summary, "published": entry.get("published", "")})
                    continue

                # الخطوة 1: عنوان/وصف
                quick_match, kw = matches(f"{title} {summary}", keywords)
                if quick_match:
                    print(f"  ✅ عنوان '{kw}': {title[:60]}...")
                    real_url = decode_url(link)
                    state["cache"][link] = {"result": "matched", "real_url": real_url, "ts": datetime.now(timezone.utc).timestamp()}
                    all_matched.append({"title": title, "link": real_url, "summary": summary, "published": entry.get("published", "")})
                    time.sleep(0.5)
                    continue

                # الخطوة 2: افتح المقال
                real_url = decode_url(link)
                article_text, status = fetch_article(real_url)

                if status == "paywall":
                    if is_about_bayern(title):
                        state["cache"][link] = {"result": "paywall", "real_url": real_url, "ts": datetime.now(timezone.utc).timestamp()}
                        all_matched.append({"title": title, "link": real_url, "summary": summary, "published": entry.get("published", "")})
                    else:
                        state["cache"][link] = {"result": "no_match", "real_url": real_url, "ts": datetime.now(timezone.utc).timestamp()}
                    time.sleep(0.5)
                    continue

                if status == "failed" or not article_text:
                    state["cache"][link] = {"result": "failed", "real_url": real_url, "ts": datetime.now(timezone.utc).timestamp()}
                    time.sleep(0.5)
                    continue

                # الخطوة 3: كلمات في المحتوى
                content_match, kw = matches(article_text, keywords)
                if content_match and is_about_bayern(article_text):
                    print(f"  ✅ محتوى '{kw}': {title[:60]}...")
                    state["cache"][link] = {"result": "matched", "real_url": real_url, "ts": datetime.now(timezone.utc).timestamp()}
                    all_matched.append({"title": title, "link": real_url, "summary": summary, "published": entry.get("published", "")})
                else:
                    state["cache"][link] = {"result": "no_match", "real_url": real_url, "ts": datetime.now(timezone.utc).timestamp()}

                time.sleep(0.5)

        xml = build_xml(all_matched)
        with state["lock"]:
            state["feed_xml"] = xml

        print(f"📊 {len(all_matched)} مقال مطابق")
        save_cache()

    finally:
        state["running"] = False


def background_loop():
    load_cache()
    while True:
        try:
            run_filter()
        except Exception as e:
            print(f"❌ {e}")
        time.sleep(UPDATE_INTERVAL)


# ══════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════

@app.route("/feed")
def serve_feed():
    with state["lock"]:
        xml = state["feed_xml"]
    if not xml:
        run_filter()
        with state["lock"]:
            xml = state["feed_xml"]
    if not xml:
        return Response("Loading...", status=503)
    return Response(xml, mimetype="application/rss+xml; charset=utf-8")


@app.route("/")
def index():
    cache_size = len(state["cache"])
    return f"<h2>✅ Bayern RSS Filter</h2><p>💾 Cache: {cache_size}</p><p><a href='/feed'>Feed</a></p>"


thread = threading.Thread(target=background_loop, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
