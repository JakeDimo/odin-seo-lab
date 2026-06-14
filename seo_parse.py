"""SHARED ON-PAGE FIELD EXTRACTOR — one source of truth for both scrapers:
  - scrape_page.py    (fast path: requests, no JS)
  - scrape_render.py  (render path: Playwright, rendered DOM + screenshot)
Pass HTML (raw or rendered) + the final URL; get the parsed signal dict back.
"""
import re
import json
import datetime
from bs4 import BeautifulSoup

CTA_WORDS = ["call", "book", "quote", "contact", "get started", "free", "enquire",
             "appointment", "request", "buy", "shop", "sign up", "schedule"]

# Within-page-1 differentiator signals (correlational leads, not rules — see
# wiki/seo-lab/page-one-differentiators.md). All derived from HTML + the label's
# keyword, so they cost nothing extra to capture.
POWER_WORDS = ["best", "top", "free", "guide", "how", "why", "new", "cheap", "fast",
               "easy", "ultimate", "proven", "expert", "trusted", "local", "affordable",
               "review", "compare", "official", "near me", "cost", "price", "vs",
               "2024", "2025", "2026"]
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _iso_date(s):
    if not isinstance(s, str):
        return None
    m = DATE_RE.search(s)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except Exception:
        return None


def _kw_tokens(kw):
    return [w for w in re.findall(r"[a-z0-9]+", (kw or "").lower()) if len(w) > 2]


def _all_in(toks, s):
    s = (s or "").lower()
    return bool(toks) and all(w in s for w in toks)


def classify_page_type(final_url, types, cta_count, form_count, word_count):
    """Coarse page-type for query-intent match (H3): home / blog-article /
    product / service / category / other. Schema first, then URL, then a
    conversion-vs-content fallback."""
    url = (final_url or "").lower()
    path = re.sub(r"^https?://[^/]+", "", url).split("?")[0].split("#")[0].strip("/")
    ts = set(types or [])
    if path in ("", "index", "index.html", "home"):
        return "home"
    if {"BlogPosting", "Article", "NewsArticle", "TechArticle"} & ts or \
            re.search(r"/(blog|news|article|post|guide|resources|insights)/", url):
        return "blog/article"
    if {"Product", "ProductGroup", "Offer"} & ts or re.search(r"/(product|shop|store|buy|cart)/", url):
        return "product"
    if {"Service", "ProfessionalService"} & ts or re.search(r"/(service|services)/", url):
        return "service"
    if {"ItemList", "CollectionPage"} & ts or re.search(r"/(category|categories|collection|collections)/", url):
        return "category"
    if (cta_count or 0) >= 2 or (form_count or 0) >= 1:
        return "service"           # conversion-oriented landing page
    if (word_count or 0) >= 800:
        return "blog/article"
    return "other"


def title_attractiveness(title, query):
    """Click-attractiveness proxy for the NavBoost input (H1): number, bracket/
    separator, power word, 40-60 char (truncation-safe), query front-loaded."""
    t = title or ""
    tl = t.lower()
    toks = _kw_tokens(query)
    has_number = bool(re.search(r"\d", t))
    has_bracket = bool(re.search(r"[\[\(\|:]", t))
    has_power = any(w in tl for w in POWER_WORDS)
    len_ok = 40 <= len(t) <= 60
    first5 = " ".join(tl.split()[:5])
    early = bool(toks) and all(w in first5 for w in toks)
    return {"score": int(has_number) + int(has_bracket) + int(has_power) + int(len_ok) + int(early),
            "has_number": has_number, "has_bracket": has_bracket,
            "has_power": has_power, "len_ok": len_ok, "query_early": early}


def _syllables(word):
    word = word.lower()
    n = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e"):
        n -= 1
    return max(1, n)


def flesch(text):
    words = re.findall(r"[a-zA-Z]+", text)
    if not words:
        return None
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    syl = sum(_syllables(w) for w in words)
    return round(206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syl / len(words)), 1)


def parse_jsonld(soup):
    """Return (types, aggregateRating, sameAs, telephone, has_address, meta)
    where meta = {date_published, date_modified, has_author, has_reviewed}."""
    types, same_as = set(), set()
    agg, tel, addr = None, None, False
    meta = {"date_published": None, "date_modified": None,
            "has_author": False, "has_reviewed": False}

    def walk(node):
        nonlocal agg, tel, addr
        if isinstance(node, list):
            for x in node:
                walk(x)
        elif isinstance(node, dict):
            t = node.get("@type")
            if isinstance(t, list):
                types.update(t)
            elif isinstance(t, str):
                types.add(t)
            ar = node.get("aggregateRating")
            if isinstance(ar, dict):
                agg = {"ratingValue": ar.get("ratingValue"),
                       "reviewCount": ar.get("reviewCount") or ar.get("ratingCount")}
            if node.get("telephone"):
                tel = node["telephone"]
            if node.get("address"):
                addr = True
            if not meta["date_published"] and node.get("datePublished"):
                meta["date_published"] = node["datePublished"]
            if node.get("dateModified"):
                meta["date_modified"] = node["dateModified"]
            if node.get("author"):
                meta["has_author"] = True
            if node.get("reviewedBy") or node.get("lastReviewed"):
                meta["has_reviewed"] = True
            sa = node.get("sameAs")
            if isinstance(sa, str):
                same_as.add(sa)
            elif isinstance(sa, list):
                same_as.update(x for x in sa if isinstance(x, str))
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)

    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = s.string or s.get_text()
        if not raw:
            continue
        try:
            walk(json.loads(raw))
        except Exception:
            continue
    return sorted(types), agg, sorted(same_as), tel, addr, meta


def extract_fields(html, final_url, label=""):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    md = soup.find("meta", attrs={"name": "description"})
    metadesc = (md.get("content") or "").strip() if md else ""
    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]

    host = re.sub(r"^https?://([^/]+).*", r"\1", final_url or "")

    def _is_internal(href):
        if href.startswith(("#", "mailto:", "tel:")):
            return None
        if href.startswith("/") or (host and host in href):
            return True
        return False if href.startswith("http") else None

    internal = external = 0
    for a in soup.find_all("a", href=True):
        v = _is_internal(a["href"])
        if v is True:
            internal += 1
        elif v is False:
            external += 1

    # In-content vs navigation links: the confirmed internal-links lead may really be a
    # contextual-linking lead — nav/footer links are sitewide boilerplate, links inside
    # the content are editorial choices. Semantic <main>/<article> when present; most
    # local-service sites have neither, so fall back to internal-minus-nav.
    nav_link_count = sum(1 for nv in soup.find_all(["nav", "header", "footer"])
                         for a in nv.find_all("a", href=True) if _is_internal(a["href"]) is True)
    main_node = soup.find("main") or soup.find("article")
    if main_node:
        main_internal_links = sum(1 for a in main_node.find_all("a", href=True)
                                  if _is_internal(a["href"]) is True)
    else:
        main_internal_links = max(0, internal - nav_link_count)

    imgs = soup.find_all("img")
    with_alt = sum(1 for i in imgs if (i.get("alt") or "").strip())

    body = BeautifulSoup(html, "html.parser")
    for t in body(["script", "style", "noscript"]):
        t.extract()
    text = body.get_text(separator=" ")
    words = len(text.split())

    types, agg, same_as, tel_schema, has_addr, jm = parse_jsonld(soup)
    gen = soup.find("meta", attrs={"name": "generator"})
    robots = soup.find("meta", attrs={"name": "robots"})
    hreflangs = sorted({l.get("hreflang") for l in soup.find_all("link", attrs={"rel": "alternate"}) if l.get("hreflang")})
    clickable = soup.find_all(["a", "button"])
    cta_count = sum(1 for c in clickable if any(w in c.get_text(" ", strip=True).lower() for w in CTA_WORDS))
    interstitial = bool(soup.select('[class*="modal"], [class*="popup"], [id*="popup"], [class*="overlay"]'))
    visible_review_hint = bool(re.search(r"\b(reviews?|ratings?|stars?|testimonials?)\b", text, re.I))
    html_tag = soup.find("html")

    # --- within-page-1 differentiator signals (leads, not rules) ---
    cta_count_v = cta_count
    form_count_v = len(soup.find_all("form"))
    page_type = classify_page_type(final_url, types, cta_count_v, form_count_v, words)

    # Freshness (H6): schema dates, then OG article times, then <time datetime>.
    def _meta_time(prop):
        m = soup.find("meta", attrs={"property": prop})
        return m.get("content") if m else None
    time_tag = soup.find("time")
    time_dt = time_tag.get("datetime") if (time_tag and time_tag.get("datetime")) else None
    d_mod = next((d for d in (_iso_date(jm["date_modified"]), _iso_date(_meta_time("article:modified_time")),
                              _iso_date(time_dt)) if d), None)
    d_pub = next((d for d in (_iso_date(jm["date_published"]), _iso_date(_meta_time("article:published_time"))) if d), None)
    best_date = d_mod or d_pub
    page_age_days = (datetime.date.today() - best_date).days if best_date else None
    if page_age_days is not None and page_age_days < 0:
        page_age_days = None

    # Title click-attractiveness (H1) + exact-query position (H3).
    kw = label.split("|")[2] if len(label.split("|")) >= 3 else ""
    toks = _kw_tokens(kw)
    tattr = title_attractiveness(title, kw)
    lead_text = " ".join(text.split()[:120])
    # Keyword frequency / density on the page (does repeating the term help?)
    text_l = text.lower()
    kw_exact = kw.lower().strip()
    kw_exact_count = text_l.count(kw_exact) if kw_exact else 0
    kw_token_hits = sum(text_l.count(t) for t in toks)
    kw_in_h2 = any(_all_in(toks, h) for h in h2s)

    # E-E-A-T completeness (H-EEAT): schema author + visible byline + review date.
    byline = bool(soup.find_all(class_=re.compile(r"author|byline", re.I))) or \
        bool(soup.find_all(attrs={"rel": "author"}))
    has_author = jm["has_author"] or byline
    first_p = soup.find("p")

    # Question-style H2/H3s (PAA alignment): does structuring content as the questions
    # people actually ask correlate with winning?
    QUESTION_RE = re.compile(r"^\s*(how|what|why|when|where|who|which|can|do|does|is|are|should)\b", re.I)
    subheads = h2s + [h.get_text(strip=True) for h in soup.find_all("h3")]
    h2_question_count = sum(1 for h in subheads if h.endswith("?") or QUESTION_RE.match(h))

    # Rich-content + local-trust markers (AU local-service SERPs)
    has_video = bool(soup.find("video")) or any(
        re.search(r"youtube\.com|youtu\.be|vimeo\.com|wistia", i.get("src") or "", re.I)
        for i in soup.find_all("iframe"))
    has_map_embed = any(re.search(r"google\.[^/]*/maps|maps\.google", i.get("src") or "", re.I)
                        for i in soup.find_all("iframe"))
    has_breadcrumb = "BreadcrumbList" in types or \
        bool(soup.select('[class*="breadcrumb"], nav[aria-label*="readcrumb"]'))
    trust_mentions = len(re.findall(
        r"\b(licen[cs]ed|fully insured|insured|accredited|certified|qualified|abn\s*[:#]?\s*\d|"
        r"master plumber|guaranteed?|warranty|police check)\b", text, re.I))
    has_service_area = bool(re.search(
        r"(areas? we (service|serve|cover)|service areas?|suburbs we|servicing (the )?[A-Z])", text))

    return {
        "label": label,
        "title": title, "title_len": len(title),
        "meta_description": metadesc, "metadesc_len": len(metadesc),
        "h1": h1s, "h1_count": len(h1s),
        "h2_sample": h2s[:12], "h2_count": len(h2s),
        "h3_count": len(soup.find_all("h3")),
        "word_count": words,
        "readability_flesch": flesch(text[:20000]),
        "internal_links": internal, "external_links": external,
        "img_count": len(imgs), "img_with_alt": with_alt,
        "alt_coverage": round(with_alt / len(imgs), 2) if imgs else None,
        "cta_count": cta_count, "form_count": len(soup.find_all("form")),
        "tel_links": len(soup.select('a[href^="tel:"]')),
        "schema_types": types,
        "has_canonical": bool(soup.find("link", attrs={"rel": "canonical"})),
        "robots_meta": (robots.get("content") if robots else "") or "",
        "og_present": bool(soup.find("meta", attrs={"property": "og:title"})),
        "hreflang": hreflangs,
        "viewport": bool(soup.find("meta", attrs={"name": "viewport"})),
        "html_lang": (html_tag.get("lang") if html_tag else "") or "",
        "platform": (gen.get("content") if gen else "") or "",
        "same_as": same_as,
        "schema_aggregate_rating": agg,
        "schema_telephone": tel_schema,
        "schema_has_address": has_addr,
        "flag_fake_rating": bool(agg) and words > 200 and not visible_review_hint,
        "interstitial_hint": interstitial,
        # --- within-page-1 differentiators (correlational leads) ---
        "page_type": page_type,
        "date_published": d_pub.isoformat() if d_pub else None,
        "date_modified": d_mod.isoformat() if d_mod else None,
        "page_age_days": page_age_days,
        "has_freshness_date": bool(best_date),
        "title_ctr_score": tattr["score"],
        "title_has_number": tattr["has_number"],
        "title_has_bracket": tattr["has_bracket"],
        "title_has_power": tattr["has_power"],
        "title_len_ok": tattr["len_ok"],
        "query_in_title": _all_in(toks, title),
        "query_in_h1": any(_all_in(toks, h) for h in h1s),
        "query_in_lead": _all_in(toks, lead_text),
        "query_early_title": tattr["query_early"],
        "has_author": has_author,
        "has_review_date": jm["has_reviewed"],
        "eeat_score": int(has_author) + int(jm["has_reviewed"]) + int(bool(best_date)),
        "list_count": len(soup.find_all(["ul", "ol"])),
        "table_count": len(soup.find_all("table")),
        "has_faq": bool({"FAQPage", "Question"} & set(types)),
        "stat_count": len(re.findall(r"\d+\s?%|\$\s?\d", text)),
        "lead_para_words": len(first_p.get_text(" ", strip=True).split()) if first_p else 0,
        "kw_exact_count": kw_exact_count,
        "kw_density_per_1k": round(kw_exact_count / words * 1000, 2) if words else 0,
        "kw_token_hits": kw_token_hits,
        "kw_in_h2": kw_in_h2,
        # --- link-context + rich-content + local-trust signals (added 2026-06-12) ---
        "main_internal_links": main_internal_links,
        "nav_link_count": nav_link_count,
        "h2_question_count": h2_question_count,
        "has_video": has_video,
        "has_map_embed": has_map_embed,
        "has_breadcrumb": has_breadcrumb,
        "trust_mentions": trust_mentions,
        "has_service_area": has_service_area,
    }
