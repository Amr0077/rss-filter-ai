import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, date
import xml.etree.ElementTree as ET
import time
import json
import os
from urllib.parse import urlparse, parse_qs, unquote
from googlenewsdecoder import gnewsdecoder

# ============================================================
# ⚙️ الإعدادات - عدّل هنا فقط
# ============================================================

RSS_FEEDS = [
    # 🇩🇪 ألمانية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=de&gl=DE&ceid=DE:de",
        "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt", "-Informationen"],
    },
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=de&gl=AT&ceid=AT:de",
        "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"],
    },
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=de&gl=CH&ceid=CH:de",
        "keywords": ["EXKLUSIV", "Interview", "Fakt ist", "Fest steht", "weiß", "Informationen", "klärt"],
    },
    # 🇬🇧🇺🇸 إنجليزية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=en-GB&gl=GB&ceid=GB:en",
        "keywords": ["exclusive", "EXCLUSIVE", "sources", "according to sources", "confirmed", "told", "interview", "reveals", "claims", "understands"],
    },
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=en-US&gl=US&ceid=US:en",
        "keywords": ["exclusive", "EXCLUSIVE", "sources", "according to sources", "confirmed", "told", "interview", "reveals", "claims", "understands"],
    },
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=en-AU&gl=AU&ceid=AU:en",
        "keywords": ["exclusive", "sources", "confirmed", "interview", "reveals"],
    },
    # 🇪🇸 إسبانية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=es&gl=ES&ceid=ES:es",
        "keywords": ["exclusiva", "EXCLUSIVA", "entrevista", "fuentes", "según fuentes", "confirma", "asegura", "revela", "desvela"],
    },
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=es-419&gl=MX&ceid=MX:es-419",
        "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "revela"],
    },
    # 🇫🇷 فرنسية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=fr&gl=FR&ceid=FR:fr",
        "keywords": ["exclusif", "EXCLUSIF", "interview", "selon nos informations", "nos sources", "confirme", "révèle", "apprend"],
    },
    # 🇮🇹 إيطالية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=it&gl=IT&ceid=IT:it",
        "keywords": ["esclusiva", "ESCLUSIVA", "intervista", "secondo fonti", "fonti", "conferma", "rivela", "apprende"],
    },
    # 🇦🇷 إسبانية - الأرجنتين
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=es-419&gl=AR&ceid=AR:es-419",
        "keywords": ["exclusiva", "entrevista", "fuentes", "confirma", "revela", "desvela", "asegura"],
    },
    # 🇵🇹🇧🇷 برتغالية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "keywords": ["exclusivo", "EXCLUSIVO", "entrevista", "fontes", "segundo fontes", "confirma", "revela", "apurou"],
    },
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=pt-PT&gl=PT&ceid=PT:pt-150",
        "keywords": ["exclusivo", "entrevista", "fontes", "confirma", "revela"],
    },
    # 🇳🇱 هولندية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=nl&gl=NL&ceid=NL:nl",
        "keywords": ["exclusief", "interview", "bronnen", "meldt", "bevestigt", "onthult"],
    },
    # 🇵🇱 بولندية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=pl&gl=PL&ceid=PL:pl",
        "keywords": ["ekskluzywnie", "wywiad", "źródła", "potwierdza", "ujawnia", "donosi"],
    },
    # 🇹🇷 تركية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=tr&gl=TR&ceid=TR:tr",
        "keywords": ["özel", "röportaj", "kaynaklar", "iddia", "açıkladı", "doğruladı"],
    },
    # 🇷🇺 روسية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=ru&gl=RU&ceid=RU:ru",
        "keywords": ["эксклюзив", "интервью", "источники", "сообщает", "подтвердил", "раскрыл"],
    },
    # 🇯🇵 يابانية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=ja&gl=JP&ceid=JP:ja",
        "keywords": ["独占", "インタビュー", "情報", "明らかに", "確認"],
    },
    # 🇰🇷 كورية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=ko&gl=KR&ceid=KR:ko",
        "keywords": ["단독", "인터뷰", "소식통", "확인", "공개"],
    },
    # 🇸🇦 عربية
    {
        "url": "https://news.google.com/rss/search?q=Bayern+when:1h&hl=ar&gl=SA&ceid=SA:ar",
        "keywords": ["حصري", "مصادر", "كشف", "أكد", "مقابلة", "وفقاً لمصادر"],
    },
]

MAX_ARTICLES_TO_CHECK = 20
OUTPUT_FILE = "filtered_feed.xml"
SENT_TODAY_FILE = "sent_today.json"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PROXY_URL = os.environ.get("PROXY_URL", "")

# ============================================================

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
PAYWALL_SIGNALS = ["subscribe", "abonnieren", "premium", "paywall", "sign in to read", "register to read", "nur für abonnenten"]


def load_sent_today() -> list:
    try:
        if os.path.exists(SENT_TODAY_FILE):
            data = json.load(open(SENT_TODAY_FILE))
            if data.get("date") == str(date.today()):
                return data.get("summaries", [])
    except:
        pass
    return []


def save_sent_today(summaries: list):
    try:
        json.dump({"date": str(date.today()), "summaries": summaries},
                  open(SENT_TODAY_FILE, "w"), ensure_ascii=False)
    except:
        pass


def decode_google_news_url(url: str) -> str:
    """يفك تشفير رابط Google News باستخدام googlenewsdecoder"""
    try:
        proxy = PROXY_URL if PROXY_URL else None
        result = gnewsdecoder(url, interval=1, proxy=proxy)
        if result.get("status"):
            decoded = result["decoded_url"]
            print(f"    🔓 decoded: {decoded[:80]}...")
            return decoded
        else:
            print(f"    ⚠️ decoder: {result.get('message', '')[:80]}")
    except Exception as e:
        print(f"    ⚠️ decoder error: {e}")
    return url


def fetch_article(url: str, timeout: int = 15) -> tuple:
    """يفتح الرابط الحقيقي ويرجع (النص, نوع المحتوى)"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)

        # تحقق من Paywall
        text_lower = text.lower()
        if len(text) < 500 or any(s in text_lower for s in PAYWALL_SIGNALS):
            print(f"    🔒 Paywall ({len(text)} حرف)")
            return text, "paywall"

        print(f"    ✅ {len(text)} حرف")
        return text.lower(), "ok"
    except Exception as e:
        print(f"    ❌ فشل fetch: {e}")
        return "", "failed"


def matches(text: str, keywords: list) -> tuple:
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True, kw
    return False, ""


def ask_ai(title: str, content: str, sent_today: list) -> tuple:
    """يسأل Groq أولاً، وإذا فشل يجرب Gemini كـ fallback"""

    sent_context = ""
    if sent_today:
        sent_context = "المقالات المرسلة اليوم:\n" + "\n".join(f"- {s}" for s in sent_today[-10:])

    prompt = f"""أنت محلل أخبار متخصص في نادي بايرن ميونخ.

{sent_context}

المقال الجديد:
العنوان: {title}
المحتوى: {content[:2000]}

قيّم هذا المقال:
1. هل يحتوي معلومة حصرية أو مصدر موثوق؟
2. هل يحتوي معلومة جديدة لم تُذكر اليوم؟
3. هل يتعلق بانتقال، إصابة، أو تصريح رسمي مهم؟
4. إذا كان تصريحاً، هل هو مختلف عن التصريحات السابقة اليوم؟

أجب بـ JSON فقط بدون أي نص إضافي:
{{"important": true/false, "reason": "سبب قصير", "summary": "ملخص 10 كلمات"}}"""

    # ── Groq أولاً
    if GROQ_API_KEY:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 150,
                },
                timeout=15,
            )
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            text = text.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            important = result.get("important", False)
            reason = result.get("reason", "")
            summary = result.get("summary", title[:50])
            print(f"    🤖 Groq: {'✅ مهم' if important else '❌ غير مهم'} — {reason}")
            time.sleep(2)
            return important, summary
        except Exception as e:
            print(f"    ⚠️ Groq error: {e} — جاري تجربة Gemini...")

    # ── Gemini كـ fallback
    if GEMINI_API_KEY:
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=15,
            )
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            important = result.get("important", False)
            reason = result.get("reason", "")
            summary = result.get("summary", title[:50])
            print(f"    🤖 Gemini: {'✅ مهم' if important else '❌ غير مهم'} — {reason}")
            time.sleep(4)
            return important, summary
        except Exception as e:
            print(f"    ⚠️ Gemini error: {e}")

    return False, ""


def build_rss_feed(articles: list) -> str:
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Bayern Filtered Feed - AI Powered"
    ET.SubElement(channel, "link").text = "https://news.google.com"
    ET.SubElement(channel, "description").text = "FC Bayern - Keywords + Gemini AI"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )
    for article in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article["title"]
        ET.SubElement(item, "link").text = article["link"]
        ET.SubElement(item, "description").text = article.get("summary", "")
        ET.SubElement(item, "pubDate").text = article.get("published", "")
        ET.SubElement(item, "guid").text = article["link"]
    return ET.tostring(rss, encoding="unicode", xml_declaration=True)


def process_feed(feed_config: dict, seen_links: set, sent_today: list) -> tuple:
    feed_url = feed_config["url"]
    keywords = feed_config["keywords"]

    print(f"\n🔍 {feed_url[50:90]}...")
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        print("  ❌ لا مقالات")
        return [], []

    entries = feed.entries[:MAX_ARTICLES_TO_CHECK]
    print(f"  📰 {len(entries)} مقال")
    matched = []
    new_summaries = []

    for i, entry in enumerate(entries):
        title = entry.get("title", "")
        link = entry.get("link", "")
        rss_summary = entry.get("summary", "")

        if link in seen_links:
            continue
        seen_links.add(link)

        print(f"  [{i+1}] {title[:70]}...")

        # ── الخطوة 1: تحقق من العنوان والوصف
        quick_match, kw = matches(f"{title} {rss_summary}", keywords)
        if quick_match:
            print(f"    ✅ كلمة مفتاح في العنوان: '{kw}'")
            real_url = decode_google_news_url(link)
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(title[:60])
            time.sleep(1)
            continue

        # ── الخطوة 2: فك الرابط ثم افتح المقال
        real_url = decode_google_news_url(link)
        article_text, status = fetch_article(real_url)

        # Paywall → أرسل مباشرة
        if status == "paywall":
            print(f"    🔒 Paywall → يُرسل مباشرة")
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(title[:60])
            time.sleep(1)
            continue

        # فشل → تخطي
        if status == "failed" or not article_text:
            print(f"    ⚠️ فشل القراءة — تخطي")
            time.sleep(1)
            continue

        # ── الخطوة 3: تحقق من الكلمات في المحتوى
        content_match, kw = matches(article_text, keywords)
        if content_match:
            print(f"    ✅ كلمة في المحتوى: '{kw}'")
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(title[:60])
            time.sleep(1)
            continue

        # ── الخطوة 4: Gemini يقرر
        print(f"    🤖 لا كلمة — Gemini يقيّم...")
        important, summary = ask_ai(title, article_text, sent_today + new_summaries)
        if important:
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(summary or title[:60])

        time.sleep(1)

    return matched, new_summaries


def main():
    print(f"📡 عدد الـ Feeds: {len(RSS_FEEDS)}")
    print(f"🤖 Groq: {'مفعّل ✅' if GROQ_API_KEY else 'غير مفعّل ❌'} | Gemini fallback: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"🔀 Proxy: {'مفعّل ✅' if PROXY_URL else 'غير مفعّل ❌'}")

    sent_today = load_sent_today()
    print(f"📋 مقالات اليوم السابقة: {len(sent_today)}")

    all_matched = []
    all_new_summaries = []
    seen_links = set()

    for feed_config in RSS_FEEDS:
        matched, new_summaries = process_feed(feed_config, seen_links, sent_today + all_new_summaries)
        all_matched.extend(matched)
        all_new_summaries.extend(new_summaries)

    print(f"\n📊 النتيجة: {len(all_matched)} مقال مطابق")

    xml_content = build_rss_feed(all_matched)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml_content)

    save_sent_today(sent_today + all_new_summaries)

    if all_matched:
        print(f"✅ تم الحفظ في: {OUTPUT_FILE}")
    else:
        print("⚠️ لا مقالات مطابقة")


if __name__ == "__main__":
    main()
