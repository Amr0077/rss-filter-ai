import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, date
import xml.etree.ElementTree as ET
import time
import json
import os
import threading
from urllib.parse import urlparse, parse_qs, unquote
from flask import Flask, Response
from googlenewsdecoder import gnewsdecoder

app = Flask(__name__)

# ============================================================
# ⚙️ الإعدادات
# ============================================================

RSS_FEEDS = [
    # 🇩🇪 ألمانية
    {
        "url": "https://news.google.com/rss/search?q=%22FC+Bayern%22+when:1h&hl=de&gl=DE&ceid=DE:de",
        "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt", "-Informationen"],
    },
    {
        "url": "https://news.google.com/rss/search?q=%22FC+Bayern%22+when:1h&hl=de&gl=AT&ceid=AT:de",
        "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"],
    },
    {
        "url": "https://news.google.com/rss/search?q=%22FC+Bayern%22+when:1h&hl=de&gl=CH&ceid=CH:de",
        "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"],
    },
    # 🇬🇧🇺🇸 إنجليزية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=en-GB&gl=GB&ceid=GB:en",
        "keywords": ["exclusive", "EXCLUSIVE", "sources", "according to sources", "confirmed", "told", "interview", "reveals", "claims", "understands"],
    },
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=en-US&gl=US&ceid=US:en",
        "keywords": ["exclusive", "EXCLUSIVE", "sources", "according to sources", "confirmed", "told", "interview", "reveals", "claims", "understands"],
    },
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=en-AU&gl=AU&ceid=AU:en",
        "keywords": ["exclusive", "sources", "confirmed", "interview", "reveals"],
    },
    # 🇪🇸 إسبانية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnich%22+when:1h&hl=es&gl=ES&ceid=ES:es",
        "keywords": ["exclusiva", "EXCLUSIVA", "entrevista", "fuentes", "según fuentes", "confirma", "asegura", "revela", "desvela"],
    },
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnich%22+when:1h&hl=es-419&gl=MX&ceid=MX:es-419",
        "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "revela"],
    },
    # 🇫🇷 فرنسية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=fr&gl=FR&ceid=FR:fr",
        "keywords": ["exclusif", "EXCLUSIF", "interview", "selon nos informations", "nos sources", "confirme", "révèle", "apprend"],
    },
    # 🇮🇹 إيطالية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Monaco%22+when:1h&hl=it&gl=IT&ceid=IT:it",
        "keywords": ["esclusiva", "ESCLUSIVA", "intervista", "secondo fonti", "fonti", "conferma", "rivela", "apprende"],
    },
    # 🇦🇷 إسبانية - الأرجنتين
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnich%22+when:1h&hl=es-419&gl=AR&ceid=AR:es-419",
        "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "revela", "desvela", "asegura"],
    },
    # 🇵🇹🇧🇷 برتغالية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+de+Munique%22+when:1h&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "keywords": ["exclusivo", "EXCLUSIVO", "entrevista", "fontes", "segundo fontes", "confirma", "revela", "apurou"],
    },
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Munich%22+when:1h&hl=pt-PT&gl=PT&ceid=PT:pt-150",
        "keywords": ["exclusivo", "entrevista", "fontes", "confirma", "revela"],
    },
    # 🇳🇱 هولندية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnchen%22+when:1h&hl=nl&gl=NL&ceid=NL:nl",
        "keywords": ["exclusief", "interview", "bronnen", "meldt", "bevestigt", "onthult"],
    },
    # 🇵🇱 بولندية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+Monachium%22+when:1h&hl=pl&gl=PL&ceid=PL:pl",
        "keywords": ["ekskluzywnie", "wywiad", "źródła", "potwierdza", "ujawnia", "donosi"],
    },
    # 🇹🇷 تركية
    {
        "url": "https://news.google.com/rss/search?q=%22Bayern+M%C3%BCnih%22+when:1h&hl=tr&gl=TR&ceid=TR:tr",
        "keywords": ["özel", "röportaj", "kaynaklar", "iddia", "açıkladı", "doğruladı"],
    },
    # 🇷🇺 روسية
    {
        "url": "https://news.google.com/rss/search?q=%22%D0%91%D0%B0%D0%B2%D0%B0%D1%80%D0%B8%D1%8F%22+when:1h&hl=ru&gl=RU&ceid=RU:ru",
        "keywords": ["эксклюзив", "интервью", "источники", "сообщает", "подтвердил", "раскрыл"],
    },
    # 🇯🇵 يابانية
    {
        "url": "https://news.google.com/rss/search?q=%22%E3%83%90%E3%82%A4%E3%82%A8%E3%83%AB%E3%83%B3%22+when:1h&hl=ja&gl=JP&ceid=JP:ja",
        "keywords": ["独占", "インタビュー", "情報", "明らかに", "確認"],
    },
    # 🇰🇷 كورية
    {
        "url": "https://news.google.com/rss/search?q=%22%EB%B0%94%EC%9D%B4%EC%97%90%EB%A5%B8%22+when:1h&hl=ko&gl=KR&ceid=KR:ko",
        "keywords": ["단독", "인터뷰", "소식통", "확인", "공개"],
    },
    # 🇸🇦 عربية
    {
        "url": "https://news.google.com/rss/search?q=%22%D8%A8%D8%A7%D9%8A%D8%B1%D9%86+%D9%85%D9%8A%D9%88%D9%86%D8%AE%22+when:1h&hl=ar&gl=SA&ceid=SA:ar",
        "keywords": ["حصري", "مصادر", "كشف", "أكد", "مقابلة", "وفقاً لمصادر"],
    },
]

BAYERN_TERMS = [
    "bayern", "münchen", "munich", "munchen", "munique",
    "monachium", "バイエルン", "바이에른", "бавари",
    "ميونخ", "بايرن", "münih", "monaco"
]

MAX_ARTICLES_TO_CHECK = 20
UPDATE_INTERVAL = 300  # كل 5 دقائق
CACHE_TTL_HOURS = 24

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PROXY_URL = os.environ.get("PROXY_URL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # مثال: amr7812/rss-filter-ai

# ============================================================

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
PAYWALL_SIGNALS = ["subscribe", "abonnieren", "premium", "paywall", "sign in to read", "register to read", "nur für abonnenten"]

# الـ state في الذاكرة
state = {
    "feed_xml": "",
    "cache": {},
    "sent_today": [],
    "sent_date": "",
    "last_update": None,
    "lock": threading.Lock(),
}


# ══════════════════════════════════════════════
# GitHub Persistence
# ══════════════════════════════════════════════

def github_get_file(filename: str) -> dict | None:
    """يجلب ملف من GitHub"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None
    try:
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
            timeout=10,
        )
        if r.status_code == 200:
            import base64
            data = r.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return {"content": content, "sha": data["sha"]}
    except Exception as e:
        print(f"GitHub get {filename}: {e}")
    return None


def github_save_file(filename: str, content: str, sha: str = None):
    """يحفظ ملف على GitHub"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    try:
        import base64
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        body = {
            "message": f"Update {filename}",
            "content": encoded,
        }
        if sha:
            body["sha"] = sha

        requests.put(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
            json=body,
            timeout=15,
        )
        print(f"✅ GitHub saved: {filename}")
    except Exception as e:
        print(f"GitHub save {filename}: {e}")


def load_state_from_github():
    """يحمّل الـ cache وسجل اليوم من GitHub"""
    # cache
    result = github_get_file("cache.json")
    if result:
        try:
            data = json.loads(result["content"])
            now = datetime.now(timezone.utc).timestamp()
            cleaned = {k: v for k, v in data.items()
                       if now - v.get("ts", 0) < CACHE_TTL_HOURS * 3600}
            state["cache"] = cleaned
            print(f"💾 Cache loaded: {len(cleaned)} روابط")
        except:
            pass

    # sent_today
    result = github_get_file("sent_today.json")
    if result:
        try:
            data = json.loads(result["content"])
            today = str(date.today())
            if data.get("date") == today:
                state["sent_today"] = data.get("summaries", [])
                state["sent_date"] = today
                print(f"📋 Sent today loaded: {len(state['sent_today'])}")
        except:
            pass


def save_state_to_github():
    """يحفظ الـ cache وسجل اليوم على GitHub"""
    # cache
    result = github_get_file("cache.json")
    sha = result["sha"] if result else None
    github_save_file("cache.json", json.dumps(state["cache"], ensure_ascii=False), sha)

    # sent_today
    result = github_get_file("sent_today.json")
    sha = result["sha"] if result else None
    today = str(date.today())
    data = {"date": today, "summaries": state["sent_today"]}
    github_save_file("sent_today.json", json.dumps(data, ensure_ascii=False), sha)


# ══════════════════════════════════════════════
# Core Functions
# ══════════════════════════════════════════════

def decode_google_news_url(url: str) -> str:
    try:
        proxy = PROXY_URL if PROXY_URL else None
        result = gnewsdecoder(url, interval=1, proxy=proxy)
        if result.get("status"):
            return result["decoded_url"]
    except Exception as e:
        print(f"    ⚠️ decoder: {e}")
    return url


def fetch_article(url: str) -> tuple:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text_lower = text.lower()
        is_short = len(text) < 500
        has_paywall = any(s in text_lower for s in PAYWALL_SIGNALS)
        if len(text) < 200 or (is_short and has_paywall):
            return text, "paywall"
        return text.lower(), "ok"
    except Exception as e:
        print(f"    ❌ {e}")
        return "", "failed"


def matches(text: str, keywords: list) -> tuple:
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True, kw
    return False, ""


def is_about_bayern(text: str) -> bool:
    text_lower = text.lower()
    return any(t in text_lower for t in BAYERN_TERMS)


def call_groq(prompt: str, retries: int = 2) -> dict | None:
    for attempt in range(retries):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 150},
                timeout=15,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if "429" in str(e):
                wait = 10 * (attempt + 1)
                print(f"    ⏳ Groq 429 — انتظار {wait}s...")
                time.sleep(wait)
            else:
                return None
    return None


def call_gemini(prompt: str, retries: int = 2) -> dict | None:
    for attempt in range(retries):
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=15,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if "429" in str(e):
                wait = 15 * (attempt + 1)
                print(f"    ⏳ Gemini 429 — انتظار {wait}s...")
                time.sleep(wait)
            else:
                return None
    return None


def ask_ai(title: str, content: str) -> tuple:
    sent_context = ""
    if state["sent_today"]:
        sent_context = "المقالات المرسلة اليوم:\n" + "\n".join(f"- {s}" for s in state["sent_today"][-10:])

    prompt = f"""أنت محلل أخبار متخصص في نادي بايرن ميونخ.

{sent_context}

المقال:
العنوان: {title}
المحتوى: {content[:2000]}

قيّم:
1. هل يحتوي معلومة حصرية أو مصدر موثوق؟
2. هل يحتوي معلومة جديدة لم تُذكر اليوم؟
3. هل يتعلق بانتقال، إصابة، أو تصريح رسمي مهم؟
4. إذا كان تصريحاً، هل هو مختلف عن تصريحات اليوم؟

JSON فقط:
{{"important": true/false, "reason": "سبب قصير", "summary": "ملخص 10 كلمات"}}"""

    def parse(text: str):
        text = text.strip().replace("```json", "").replace("```", "").strip()
        r = json.loads(text)
        return r.get("important", False), r.get("reason", ""), r.get("summary", title[:50])

    if GROQ_API_KEY:
        data = call_groq(prompt)
        if data:
            try:
                important, reason, summary = parse(data["choices"][0]["message"]["content"])
                print(f"    🤖 Groq: {'✅' if important else '❌'} — {reason}")
                time.sleep(2)
                return important, summary
            except:
                pass

    if GEMINI_API_KEY:
        data = call_gemini(prompt)
        if data:
            try:
                important, reason, summary = parse(data["candidates"][0]["content"]["parts"][0]["text"])
                print(f"    🤖 Gemini: {'✅' if important else '❌'} — {reason}")
                time.sleep(4)
                return important, summary
            except:
                pass

    return False, ""


def cache_set(link: str, result: str, real_url: str = ""):
    state["cache"][link] = {
        "result": result,
        "real_url": real_url,
        "ts": datetime.now(timezone.utc).timestamp(),
    }


def build_rss_xml(articles: list) -> str:
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Bayern Filtered Feed - AI Powered"
    ET.SubElement(channel, "link").text = "https://news.google.com"
    ET.SubElement(channel, "description").text = "FC Bayern - Keywords + AI"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    for article in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article["title"]
        ET.SubElement(item, "link").text = article["link"]
        ET.SubElement(item, "description").text = article.get("summary", "")
        ET.SubElement(item, "pubDate").text = article.get("published", "")
        ET.SubElement(item, "guid").text = article["link"]
    return ET.tostring(rss, encoding="unicode", xml_declaration=True)


def run_filter():
    """الدالة الرئيسية — تُشغَّل كل 5 دقائق"""
    print(f"\n{'='*50}")
    print(f"🔄 تحديث جديد: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
    print(f"💾 Cache: {len(state['cache'])} | 📋 اليوم: {len(state['sent_today'])}")

    # نظّف sent_today إذا تغيّر اليوم
    today = str(date.today())
    if state["sent_date"] != today:
        state["sent_today"] = []
        state["sent_date"] = today

    all_matched = []
    new_summaries = []
    seen_links = set()

    for feed_config in RSS_FEEDS:
        feed_url = feed_config["url"]
        keywords = feed_config["keywords"]
        print(f"\n🔍 {feed_url[50:95]}...")

        try:
            feed = feedparser.parse(feed_url)
        except:
            continue

        if not feed.entries:
            continue

        entries = feed.entries[:MAX_ARTICLES_TO_CHECK]

        for i, entry in enumerate(entries):
            title = entry.get("title", "")
            link = entry.get("link", "")
            rss_summary = entry.get("summary", "")

            if link in seen_links:
                continue
            seen_links.add(link)

            # cache hit
            if link in state["cache"]:
                cached = state["cache"][link]
                if cached["result"] in ("matched", "paywall"):
                    all_matched.append({
                        "title": title,
                        "link": cached.get("real_url", link),
                        "summary": rss_summary,
                        "published": entry.get("published", ""),
                    })
                continue

            print(f"  [{i+1}] {title[:70]}...")

            # الخطوة 1: عنوان/وصف
            quick_match, kw = matches(f"{title} {rss_summary}", keywords)
            if quick_match:
                print(f"    ✅ عنوان: '{kw}'")
                real_url = decode_google_news_url(link)
                cache_set(link, "matched", real_url)
                all_matched.append({"title": title, "link": real_url, "summary": rss_summary, "published": entry.get("published", "")})
                new_summaries.append(title[:60])
                time.sleep(0.5)
                continue

            # الخطوة 2: فك الرابط واقرأ
            real_url = decode_google_news_url(link)
            article_text, status = fetch_article(real_url)

            if status == "paywall":
                if is_about_bayern(title):
                    cache_set(link, "paywall", real_url)
                    all_matched.append({"title": title, "link": real_url, "summary": rss_summary, "published": entry.get("published", "")})
                    new_summaries.append(title[:60])
                else:
                    cache_set(link, "no_match", real_url)
                time.sleep(0.5)
                continue

            if status == "failed" or not article_text:
                cache_set(link, "failed", real_url)
                time.sleep(0.5)
                continue

            # الخطوة 3: كلمات في المحتوى
            content_match, kw = matches(article_text, keywords)
            if content_match and is_about_bayern(article_text):
                print(f"    ✅ محتوى: '{kw}'")
                cache_set(link, "matched", real_url)
                all_matched.append({"title": title, "link": real_url, "summary": rss_summary, "published": entry.get("published", "")})
                new_summaries.append(title[:60])
                time.sleep(0.5)
                continue
            elif content_match:
                cache_set(link, "no_match", real_url)
                time.sleep(0.5)
                continue

            # الخطوة 4: AI
            if is_about_bayern(title):
                print(f"    🤖 AI يقيّم...")
                important, summary = ask_ai(title, article_text)
                if important:
                    cache_set(link, "matched", real_url)
                    all_matched.append({"title": title, "link": real_url, "summary": rss_summary, "published": entry.get("published", "")})
                    new_summaries.append(summary or title[:60])
                else:
                    cache_set(link, "no_match", real_url)
            else:
                cache_set(link, "no_match", real_url)

            time.sleep(1)

    # تحديث sent_today
    state["sent_today"].extend(new_summaries)

    # بناء الـ feed
    xml = build_rss_xml(all_matched)
    with state["lock"]:
        state["feed_xml"] = xml
        state["last_update"] = datetime.now(timezone.utc)

    print(f"\n📊 {len(all_matched)} مقال | آخر تحديث: {state['last_update'].strftime('%H:%M:%S')}")

    # حفظ على GitHub
    save_state_to_github()


def background_loop():
    """يشغّل run_filter كل 5 دقائق"""
    # تحميل الـ state من GitHub أولاً
    load_state_from_github()

    while True:
        try:
            run_filter()
        except Exception as e:
            print(f"❌ خطأ في run_filter: {e}")
        time.sleep(UPDATE_INTERVAL)


# ══════════════════════════════════════════════
# Flask Routes
# ══════════════════════════════════════════════

@app.route("/feed")
def serve_feed():
    with state["lock"]:
        xml = state["feed_xml"]
    if not xml:
        # إذا الـ feed فارغ، شغّل الفلترة مباشرة
        print("⚡ طلب feed والـ cache فارغ — تشغيل فوري...")
        try:
            run_filter()
        except Exception as e:
            print(f"❌ {e}")
        with state["lock"]:
            xml = state["feed_xml"]
    if not xml:
        return Response("Feed is loading, try again in a minute.", status=503)
    return Response(xml, mimetype="application/rss+xml; charset=utf-8")


@app.route("/")
def index():
    last = state["last_update"]
    last_str = last.strftime("%Y-%m-%d %H:%M:%S UTC") if last else "جاري التحميل..."
    cache_size = len(state["cache"])
    return f"""
    <h2>✅ Bayern RSS Filter - Running</h2>
    <p>📡 آخر تحديث: {last_str}</p>
    <p>💾 Cache: {cache_size} رابط</p>
    <p>🔗 <a href="/feed">Feed RSS</a></p>
    """


# ══════════════════════════════════════════════
# Start
# ══════════════════════════════════════════════

thread = threading.Thread(target=background_loop, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
