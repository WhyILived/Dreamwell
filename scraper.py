#!/usr/bin/env python3
"""
Company Keyword Scraper — Lightweight & Fast

- Minimal deps: requests, beautifulsoup4
- Uses html.parser (no lxml needed)
- Parses only contentful tags via SoupStrainer for speed
- Weighted scoring (title/meta/headings > body)
- Produces top unigrams & bigrams without heavy NLP

Install:
  pip install requests beautifulsoup4

Usage:
  python scraper_fast.py https://example.com 20
"""

from __future__ import annotations
import re
import sys
import time
import html
import math
import urllib.parse as urlparse
from collections import Counter
from typing import List, Tuple, Iterable, Dict

import requests
from bs4 import BeautifulSoup, SoupStrainer

# ---------------- Config ----------------
HEADERS = {"User-Agent": "KeywordScraper-Fast/1.0 (+https://example.com)"}
REQUEST_TIMEOUT = 10
MAX_CHARS = 150_000
TOP_N_DEFAULT = 20

# Minimal stopword list; add more if needed
STOPWORDS = set("""
a an and are as at be but by for from has have in is it its of on or that the their them there these they this to was were will with your you we us our about into over
""".split())

# Generic junk to drop
GENERIC = {
    "home","about","contact","services","solutions","learn","more","read","policy","privacy",
    "terms","careers","login","signup","sign","up","get","started","request","demo"
}

TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]+")

# Weights (headings/meta matter more)
WEIGHTS = {
    "title": 3.0,
    "meta": 2.5,
    "h1": 3.0,
    "h2": 2.25,
    "h3": 1.75,
    "p": 1.0,
    "li": 1.0,
}

# ---------------- Utils ----------------
def normalize_url(url: str) -> str:
    return url if re.match(r"^https?://", url, re.I) else "https://" + url.lstrip("/")

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or r.encoding
    return (r.text or "")[:MAX_CHARS]

def clean(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN.findall(text)]

def ngrams(tokens: List[str], n: int) -> Iterable[str]:
    for i in range(len(tokens) - n + 1):
        yield " ".join(tokens[i:i+n])

def good_word(w: str) -> bool:
    if len(w) < 3: return False
    if w in STOPWORDS or w in GENERIC: return False
    if re.fullmatch(r"\d+[\w\-]*", w): return False
    return True

def good_phrase(ph: str) -> bool:
    if ph in GENERIC: return False
    words = ph.split()
    if any((w in STOPWORDS or w in GENERIC) for w in words):  # e.g., “of the”
        return False
    return True

# ---------------- Core ----------------
def extract_weighted_text(html_text: str) -> Dict[str, List[str]]:
    # Parse only content-carrying tags for speed
    strainer = SoupStrainer(["title", "meta", "h1", "h2", "h3", "p", "li"])
    soup = BeautifulSoup(html_text, "html.parser", parse_only=strainer)

    buckets: Dict[str, List[str]] = {k: [] for k in ["title", "meta", "h1", "h2", "h3", "p", "li"]}

    # Title
    if soup.title and soup.title.string:
        buckets["title"].append(clean(soup.title.get_text(" ", strip=True)))

    # Meta descriptions (description, og:description, twitter:description, keywords)
    for name in ("description", "og:description", "twitter:description", "keywords"):
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            buckets["meta"].append(clean(tag["content"]))

    # Headings & body text
    for tag_name in ("h1", "h2", "h3", "p", "li"):
        for t in soup.find_all(tag_name):
            txt = clean(t.get_text(" ", strip=True))
            if txt and any(c.isalpha() for c in txt):
                buckets[tag_name].append(txt)

    return buckets

def score_keywords(buckets: Dict[str, List[str]], top_n: int) -> List[Tuple[str, float]]:
    uni = Counter()
    bi = Counter()

    # Count with weights
    for tag_name, texts in buckets.items():
        w = WEIGHTS.get(tag_name, 1.0)
        for text in texts:
            toks = [t for t in tokenize(text) if good_word(t)]
            if not toks: 
                continue
            uni.update({t: w for t in toks})
            for bg in ngrams(toks, 2):
                if good_phrase(bg):
                    bi.update({bg: w * 1.5})  # bump bigrams slightly

    # Prefer bigrams, then complement with strong unigrams not covered by bigrams
    ranked: List[Tuple[str, float]] = []

    bigrams_ranked = bi.most_common(top_n)
    ranked.extend([(ph, float(score)) for ph, score in bigrams_ranked])

    covered_unigrams = set()
    for ph, _ in bigrams_ranked:
        covered_unigrams.update(ph.split())

    # Title/meta presence bonus (quick heuristic)
    title_meta_text = " ".join((buckets.get("title") or []) + (buckets.get("meta") or []))
    title_meta_tokens = set(tokenize(title_meta_text))

    unigram_candidates = [
        (w, s * (1.15 if w in title_meta_tokens else 1.0))
        for w, s in uni.items()
        if w not in covered_unigrams and good_word(w)
    ]
    unigram_candidates.sort(key=lambda x: x[1], reverse=True)

    need = max(0, top_n - len(ranked))
    ranked.extend(unigram_candidates[:need])

    # Final light dedupe and return
    seen = set()
    final = []
    for ph, sc in ranked:
        canon = " ".join(ph.split())
        if canon in seen: 
            continue
        seen.add(canon)
        final.append((canon, round(sc, 3)))
    return final[:top_n]

def scrape_company_keywords(url: str, top_n: int = TOP_N_DEFAULT) -> List[Tuple[str, float]]:
    url = normalize_url(url)
    html_text = fetch(url)
    buckets = extract_weighted_text(html_text)
    return score_keywords(buckets, top_n)

# ---------------- CLI ----------------
def scrape(url = "https://www.dreamwell.ai", top_n=5):
    t0 = time.time()
    res = []
    try:
        results = scrape_company_keywords(url, top_n=top_n)
        dt = time.time() - t0
        print(f"\nTop {len(results)} lightweight keywords for: {url}")
        print(f"(processed in {dt:.2f}s)\n")
        for i, (k, s) in enumerate(results, 1):
            print(f"{i:2d}. {k}  [{s}]")
            res.append(k)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
        sys.exit(2)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(3)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(4)
    return res
#if __name__ == "__main__":
    #scrape()
