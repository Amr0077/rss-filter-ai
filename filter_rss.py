import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, date
import xml.etree.ElementTree as ET
import time
import json
import os
from urllib.parse import urlparse, parse_qs, unquote

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
SENT_TODAY_FILE = "sent_today.json"  # يحفظ ملخصات ما أُرسل اليوم

# Gemini API Key - يُقرأ من GitHub Secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ============================================================

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
JINA_PREFIX = "https://r.jina.ai/"
PAYWALL_SIGNALS = ["subscribe", "abonnieren", "premium", "paywall", "sign in to read", "register to read", "nur für abonnenten"]


def load_sent_today() -> list:
    """يحمّل ملخصات المقالات المرسلة اليوم"""
    try:
        if os.path.exists(SENT_TODAY_FILE):
            data = json.load(open(SENT_TODAY_FILE))
            # إذا كان من يوم آخر نبدأ من جديد
            if data.get("date") == str(date.today()):
                return data.get("summaries", [])
    except:
        pass
    return []


def save_sent_today(summaries: list):
    """يحفظ ملخصات المقالات المرسلة اليوم"""
    try:
        json.dump({"date": str(date.today()), "summaries": summaries}, open(SENT_TODAY_FILE, "w"), ensure_ascii=False)
    except:
        pass


def extract_real_url(url: str) -> str:
    try:
        params = parse_qs(urlparse(url).query)
        if "url" in params:
            return unquote(params["url"][0])
    except:
        pass
    return url


def fetch_article_jina(google_url: str) -> tuple:
    """
    يستخدم Jina AI لفك رابط Google News وقراءة المحتوى
    يرجع: (النص, الرابط الحقيقي, نوع المحتوى)
    نوع المحتوى: 'ok' | 'paywall' | 'failed'
    """
    try:
        jina_url = JINA_PREFIX + google_url
        r = requests.get(jina_url, headers=HEADERS, timeout=20)
        r.raise_for_status()

        text = r.text
        real_url = google_url

        # Jina يضع الرابط الحقيقي في أول سطر
        lines = text.strip().split("\n")
        for line in lines[:5]:
            if line.startswith("URL:"):
                real_url = line.replace("URL:", "").strip()
                break

        # تحقق من Paywall
        text_lower = text.lower()
        if len(text) < 500 or any(signal in text_lower for signal in PAYWALL_SIGNALS):
            print(f"    🔒 Paywall مكتشف")
            return text, real_url, "paywall"

        print(f"    ✅ قراءة ناجحة: {len(text)} حرف | {real_url[:60]}...")
        return text.lower(), real_url, "ok"

    except Exception as e:
        print(f"    ⚠️ فشل Jina: {e}")
        # fallback: حاول مباشرة
        try:
            real_url = extract_real_url(google_url)
            r = requests.get(real_url, headers=HEADERS, timeout=10, allow_redirects=True)
            r.raise_for_status()
            real_url = r.url
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            print(f"    ✅ fallback ناجح: {len(text)} حرف")
            return text.lower(), real_url, "ok"
        except Exception as e2:
            print(f"    ❌ فشل كلي: {e2}")
            return "", google_url, "failed"


def matches(text: str, keywords: list) -> tuple:
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True, kw
    return False, ""


def ask_gemini(title: str, content: str, sent_today: list) -> tuple:
    """
    يسأل Gemini إذا كان المقال يستحق الإرسال
    يرجع: (True/False, السبب)
    """
    if not GEMINI_API_KEY:
        return False, "لا يوجد API key"

    try:
        # ملخص ما أُرسل اليوم
        sent_context = ""
        if sent_today:
            sent_context = f"""
المقالات التي أُرسلت بالفعل اليوم (لتجنب التكرار):
{chr(10).join(f'- {s}' for s in sent_today[-10:])}
"""

        prompt = f"""أنت محلل أخبار متخصص في نادي بايرن ميونخ.

{sent_context}

المقال الجديد:
العنوان: {title}
المحتوى: {content[:2000]}

قيّم هذا المقال بناءً على المعايير التالية:
1. هل يحتوي على معلومة حصرية أو مصدر موثوق؟
2. هل يحتوي على معلومة جديدة لم تُذكر في المقالات السابقة اليوم؟
3. هل يتعلق بموضوع مهم: انتقال، إصابة، تصريح رسمي، قرار إداري؟
4. إذا كان تصريحاً، هل هو مختلف عن التصريحات السابقة اليوم؟

أجب بـ JSON فقط بهذا الشكل بدون أي نص إضافي:
{{"important": true/false, "reason": "سبب قصير بجملة واحدة", "summary": "ملخص قصير جداً للمقال بـ 10 كلمات"}}"""

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # تنظيف الرد
        text = text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)

        important = result.get("important", False)
        reason = result.get("reason", "")
        summary = result.get("summary", title[:50])

        print(f"    🤖 Gemini: {'✅ مهم' if important else '❌ غير مهم'} — {reason}")
        return important, summary

    except Exception as e:
        print(f"    ⚠️ Gemini error: {e}")
        return False, ""


def build_rss_feed(articles: list) -> str:
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Bayern Filtered Feed - AI Powered"
    ET.SubElement(channel, "link").text = "https://news.google.com"
    ET.SubElement(channel, "description").text = "FC Bayern filtered news - Keywords + Gemini AI"
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

        # ── الخطوة 1: تحقق من العنوان والوصف (بدون فتح الرابط)
        quick_match, kw = matches(f"{title} {rss_summary}", keywords)
        if quick_match:
            print(f"    ✅ كلمة مفتاح: '{kw}' — جاري فتح الرابط...")
            _, real_url, status = fetch_article_jina(link)
            if status == "failed":
                real_url = link
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(f"{title[:60]}")
            time.sleep(0.5)
            continue

        # ── الخطوة 2: افتح المقال واقرأ المحتوى
        article_text, real_url, status = fetch_article_jina(link)

        # إذا Paywall → أرسل مباشرة
        if status == "paywall":
            print(f"    🔒 Paywall → يُرسل مباشرة")
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(f"{title[:60]}")
            time.sleep(0.5)
            continue

        # إذا فشل القراءة → تخطي
        if status == "failed" or not article_text:
            print(f"    ⚠️ فشل القراءة — تخطي")
            time.sleep(0.5)
            continue

        # ── الخطوة 3: تحقق من الكلمات في المحتوى
        content_match, kw = matches(article_text, keywords)
        if content_match:
            print(f"    ✅ كلمة في المحتوى: '{kw}'")
            matched.append({
                "title": title, "link": real_url,
                "summary": rss_summary, "published": entry.get("published", ""),
            })
            new_summaries.append(f"{title[:60]}")
            time.sleep(0.5)
            continue

        # ── الخطوة 4: Gemini يقرر
        print(f"    🤖 لا كلمة مفتاح — Gemini يقيّم...")
        important, summary = ask_gemini(title, article_text, sent_today + new_summaries)
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
    print(f"🤖 Gemini: {'مفعّل ✅' if GEMINI_API_KEY else 'غير مفعّل ❌'}")

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

    # حفظ الـ feed
    xml_content = build_rss_feed(all_matched)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # تحديث ملخصات اليوم
    save_sent_today(sent_today + all_new_summaries)

    if all_matched:
        print(f"✅ تم الحفظ في: {OUTPUT_FILE}")
    else:
        print("⚠️ لا مقالات مطابقة")


if __name__ == "__main__":
    main()
