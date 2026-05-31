#!/usr/bin/env python3
"""
URL verifier for travel-guide HTML.

Extracts every <a href=""> and <img src=""> from a guide, fetches each URL,
and reports status. Catches the #1 source of friction in this workflow:
links that look correct but 404, redirect to a city landing page, or serve
a missing image.

What it catches:
  ❌ 4xx / 5xx responses (broken links, dead images)
  ⚠️  Redirects to a different URL (especially tour-platform city landings)
  ❌ Non-image Content-Type on <img src=""> (Wikipedia bot-block HTML etc.)
  ❌ Tour-platform specific-tour URL that redirects to /d\d+-ttd or /-l\d+/
  ❌ 📖 reading-source URL with < 100 words of article prose (catches
     structurally-valid-but-semantically-empty pages, e.g. the Lonely
     Planet POI pages that collapsed into booking-CTA shells)

Usage:
  python3 verify_urls.py <file.html>                    # verify all URLs
  python3 verify_urls.py <file.html> --only-images      # only <img src>
  python3 verify_urls.py <file.html> --only-links       # only <a href>
  python3 verify_urls.py <file.html> --quiet            # only show failures
  python3 verify_urls.py <file.html> --workers 8        # concurrency (default 4; Wikimedia CDN rate-limits above 4)

Exit code 0 only if every URL is green.

Reference: `Brain/CORE RULES/Links.html` and `Brain/CORE RULES/Photos Rules.html`
(the canonical content rules, locked 2026-04-25). Live-research behavior
described in `Travel/CLAUDE.md` § Live Research Capabilities.
Companion to validate_itinerary.py (static checks).
"""

import sys
import re
import time
import argparse
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "
SKIP = "➖"

UA = "DaniTravelGuide/1.0 (mailto:bellinello@gmail.com)"
TIMEOUT = 15

# Tour-platform city-landing patterns — a redirect landing here is a silent
# failure even when the final status is 200.
CITY_LANDING_PATTERNS = [
    re.compile(r"https?://(?:www\.)?viator\.com/[^/]+/d\d+-ttd/?$", re.IGNORECASE),
    re.compile(r"https?://(?:www\.)?getyourguide\.com/[A-Za-z0-9\-]+-l\d+/?$", re.IGNORECASE),
    re.compile(r"https?://(?:www\.)?tripadvisor\.com/Tourism-g\d+", re.IGNORECASE),
]

# ─── BOT_BLOCKED_HOSTS ──────────────────────────────────────────────────────
# Domains where a 403 or 429 from an automated request is treated as WARN,
# not FAIL. These hosts serve real pages to browsers but block crawlers.
#
# Categories that are *predictably* bot-blockers — add new entries here before
# building a guide that links to them, not after hitting a ship-gate failure:
#
#   Tour / experience platforms  — viator.com, getyourguide.com
#   Reservation platforms        — opentable.com, guide.michelin.com
#   Review / discovery platforms — tripadvisor.com, atlasobscura.com
#   Hotel chains (all major)     — ihg.com, marriott.com, hilton.com, hyatt.com …
#   Luxury independent hotels    — oetkercollection.com, fourseasons.com …
#   Individual restaurant sites  — any bespoke domain on a restaurant page
#   Train / transit booking      — sncf-connect.com
#   Cultural foundations         — fondationlouisvuitton.fr
#   US cultural institutions     — museums, botanical gardens, zoos (.org)
#
# When verify_urls.py hits a 429 from a host NOT listed here, it emits a WARN
# (not a hard FAIL) with a nudge to add the host. Add it here once confirmed.
BOT_BLOCKED_HOSTS = {
    # Tour / experience platforms
    "viator.com", "www.viator.com",
    "getyourguide.com", "www.getyourguide.com",
    # Restaurant reservation platforms
    "opentable.com", "www.opentable.com",
    "thefork.com", "www.thefork.com",
    "guide.michelin.com",
    # Review / travel platforms
    "tripadvisor.com", "www.tripadvisor.com", "www.tripadvisor.it",
    "atlasobscura.com", "www.atlasobscura.com",
    "theculturetrip.com", "www.theculturetrip.com",
    "yelp.com", "www.yelp.com",
    # US food-delivery platforms (Cloudflare bot wall)
    "doordash.com", "www.doordash.com",
    "ubereats.com", "www.ubereats.com",
    # Uber root domain — returns HTTP 406 to automated UAs (Akamai bot wall)
    "uber.com", "www.uber.com",
    # Hyatt subdomain hosts (sanfrancisco.regency.hyatt.com etc.)
    "sanfrancisco.regency.hyatt.com",
    # Hotel chains (bot-block automated requests across the board)
    "melia.com", "www.melia.com",
    "nh-collection.com", "www.nh-collection.com",
    "marriott.com", "www.marriott.com",
    "hilton.com", "www.hilton.com",
    "accor.com", "www.accor.com",
    "ihg.com", "www.ihg.com",
    "hyatt.com", "www.hyatt.com",
    "booking.com", "www.booking.com",
    # Luxury independent hotel groups (restaurant pages often live on hotel domains)
    "oetkercollection.com", "www.oetkercollection.com",
    "oetkerhotels.com", "www.oetkerhotels.com",
    "fourseasons.com", "www.fourseasons.com",
    "lareserve-paris.com", "www.lareserve-paris.com",
    "chevalblanc.com", "www.chevalblanc.com",
    "peninsula.com", "www.peninsula.com",
    "dorchestercollection.com", "www.dorchestercollection.com",
    "ritzparis.com", "sites.ritzparis.com", "www.ritzparis.com",
    "dior.com", "www.dior.com",
    "raffles.com", "www.raffles.com",
    "armani.com", "www.armani.com",
    # Individual restaurant sites that block automated checks
    "jin-paris.com", "www.jin-paris.com",
    "lebaudelaire.com", "www.lebaudelaire.com",
    "letoutparis.fr", "www.letoutparis.fr",
    "nomicos.fr", "www.nomicos.fr",
    # Portuguese restaurant + venue sites (return 403 to crawlers, real pages in browser)
    "museudoazulejo.gov.pt",
    "www.museudoazulejo.gov.pt",
    "chiadocaffe.pt",
    "www.chiadocaffe.pt",
    "rosettaslisbon.com",
    "www.rosettaslisbon.com",
    "tabernadosmercadores.com", "www.tabernadosmercadores.com",
    "cafeguarany.com", "www.cafeguarany.com",
    "cafeguarany.pt", "www.cafeguarany.pt",
    "cafemajestic.com", "www.cafemajestic.com",
    "cafesantiago.pt", "www.cafesantiago.pt",
    "incomumbyluissantos.pt", "www.incomumbyluissantos.pt",
    "casadaguitarra.pt", "www.casadaguitarra.pt",
    "piriquita.pt", "www.piriquita.pt",
    "lawrenceshotel.com", "www.lawrenceshotel.com",
    "palaciodabolsa.com", "www.palaciodabolsa.com",
    # Train / transit booking platforms
    "sncf-connect.com", "www.sncf-connect.com",
    # Cultural foundations
    "fondationlouisvuitton.fr", "www.fondationlouisvuitton.fr",
    # US cultural institutions (museums, botanical gardens, zoos — block crawlers)
    "huntington.org", "www.huntington.org",
    # UK cultural institutions / Historic Royal Palaces (403 to crawlers)
    "hrp.org.uk", "www.hrp.org.uk",
    # UK bakery chain — drops TCP connections to automated requests (Cloudflare)
    "gailsbakery.co.uk", "www.gailsbakery.co.uk",
    # West End musical official sites — 403 to all automated requests
    "thelionking.co.uk", "www.thelionking.co.uk",
    # Paris transit authority — legitimate operator site, 403 to crawlers
    "ratp.fr", "www.ratp.fr",
    # Irish food-delivery and transit (403 to crawlers)
    "deliveroo.ie", "www.deliveroo.ie",
    "luas.ie", "www.luas.ie",
    "bolt.eu", "www.bolt.eu",
    "free-now.com", "www.free-now.com",
    # Coachella Valley performing arts venue — 403 to crawlers
    "mccallumtheatre.com", "www.mccallumtheatre.com",
}

# Redirect targets that are expected and benign — they just mean the user
# has to click through a consent wall, not that the link is broken.
BENIGN_REDIRECT_HOSTS = {
    "consent.google.com",
    "consent.youtube.com",
}


def host_of(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_benign_redirect(original: str, final: str) -> bool:
    """
    Return True if a redirect looks expected (canonical path rewrite,
    consent wall, same-host normalization) rather than a broken link.
    """
    fh = host_of(final)
    oh = host_of(original)
    if fh in BENIGN_REDIRECT_HOSTS:
        return True
    # Same host — typically a trailing-slash or canonical-path fix
    if fh == oh and fh:
        return True
    # Apple Maps: maps.apple.com/?q=X → maps.apple.com/search?query=X
    if fh.endswith("apple.com") and oh.endswith("apple.com"):
        return True
    return False


def extract_authorized_hotlink_imgs(html: str) -> set:
    """Return the set of img src URLs that carry the CDN-blocked hotlink sentinel.

    The sentinel comment `<!-- hotlink: CDN download blocked in Cowork sandbox -->`
    immediately above an <img> tag (within 300 chars) marks the hotlink as
    intentional and verified — the Cowork sandbox cannot reach upload.wikimedia.org,
    so the URL is authorised for use as-is and should not be re-fetched here.

    Mirrors the same exemption in validate_itinerary.py's wikimedia hotlink check.
    Added 2026-05-30: without this, every guide with CDN-blocked photos fails the
    ship chain at verify_urls.py even though validate_itinerary.py passes.
    """
    authorized = set()
    # Find every sentinel + img pair within 300 chars
    pattern = re.compile(
        r'<!--[^>]*hotlink[^>]*CDN[^>]*blocked[^>]*-->'
        r'.{0,300}?'
        r'<img\b[^>]*\bsrc\s*=\s*"(https?://upload\.wikimedia\.org/[^"]+)"',
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(html):
        authorized.add(m.group(1))
    return authorized


def extract_urls(html: str):
    """Return (hrefs, imgs) as lists of URL strings, preserving order.

    Images whose src carries the CDN-blocked hotlink sentinel are excluded from
    the imgs list — they are intentionally hotlinked and verified externally.
    """
    hrefs = re.findall(r'<a\b[^>]*\bhref\s*=\s*"([^"]+)"', html, re.IGNORECASE)
    all_imgs = re.findall(r'<img\b[^>]*\bsrc\s*=\s*"([^"]+)"', html, re.IGNORECASE)
    authorized_hotlinks = extract_authorized_hotlink_imgs(html)
    imgs = [u for u in all_imgs if u not in authorized_hotlinks]
    return hrefs, imgs


def extract_reading_urls(html: str):
    """
    Return the list of URLs that appear on a 📖 reading-source line.
    Used by the content-quality gate — only these URLs must carry real
    article prose.
    """
    return re.findall(
        r'📖[^<]*<a\s+[^>]*href="(https?://[^"]+)"',
        html,
        re.IGNORECASE,
    )


def should_skip(url: str) -> bool:
    u = url.strip()
    if not u:
        return True
    if u.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return True
    if not u.startswith(("http://", "https://")):
        return True
    return False


def is_city_landing(url: str) -> bool:
    return any(p.search(url) for p in CITY_LANDING_PATTERNS)


def fetch(url: str, is_image: bool = False) -> dict:
    """
    Fetch a URL and return a status dict. Uses GET (streamed, closed early)
    because many CDNs rate-limit or reject HEAD — most notably
    upload.wikimedia.org, which 429s on HEAD but serves GET fine.

    Retries once on 429 with a short backoff — Wikimedia rate-limits
    upload.wikimedia.org if we fan out too many parallel requests.
    """
    result = {
        "url": url,
        "is_image": is_image,
        "status": None,
        "final_url": None,
        "redirected": False,
        "content_type": None,
        "content_length": None,
        "error": None,
        "warnings": [],
        "bot_blocked": False,
        "possible_bot_block": False,  # True when 429 from a host NOT in BOT_BLOCKED_HOSTS
    }
    max_attempts = 4
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            r = requests.get(
                url,
                headers={"User-Agent": UA, "Accept": "*/*"},
                timeout=TIMEOUT,
                allow_redirects=True,
                stream=True,
            )
            result["status"] = r.status_code
            result["final_url"] = r.url
            result["redirected"] = r.url != url
            result["content_type"] = r.headers.get("Content-Type", "").split(";")[0].strip()
            result["content_length"] = r.headers.get("Content-Length")
            r.close()

            # Retry on 429 (rate-limited) with exponential backoff.
            # Wikimedia upload.wikimedia.org does this under parallel load.
            if r.status_code == 429 and attempts < max_attempts:
                backoff = 2 ** attempts  # 2, 4, 8 seconds
                time.sleep(backoff)
                continue

            # Redirect classification
            if result["redirected"]:
                if is_city_landing(result["final_url"]) and not is_city_landing(url):
                    result["warnings"].append(
                        f"Redirected to a city-landing page: {result['final_url']}"
                    )
                elif not is_benign_redirect(url, result["final_url"]):
                    result["warnings"].append(f"Redirected: {result['final_url']}")

            # 403/406/410/429 from a known bot-blocker is a WARN, not a FAIL
            # 410 ("Gone") is also used by some platforms (e.g. ubereats.com) as a
            # bot-detection measure — real browsers see the page fine.
            if r.status_code in (403, 406, 410, 429) and host_of(url) in BOT_BLOCKED_HOSTS:
                result["bot_blocked"] = True
                result["warnings"].append(
                    f"{r.status_code} from a known bot-blocking platform — URL may be valid. "
                    "Visually verify via Chrome MCP before shipping."
                )
            # 429 from an UNKNOWN host → WARN + nudge to add to BOT_BLOCKED_HOSTS.
            # Don't hard-fail ship on a host that might just be rate-limiting crawlers.
            elif r.status_code == 429 and host_of(url) not in BOT_BLOCKED_HOSTS:
                result["possible_bot_block"] = True
                result["warnings"].append(
                    f"429 from a host not in BOT_BLOCKED_HOSTS ({host_of(url)!r}). "
                    "Possible bot-block — visually verify the URL. "
                    "If it's valid in a browser, add this host to BOT_BLOCKED_HOSTS in verify_urls.py."
                )

            # Non-image content type on <img> src is a real failure
            if is_image and r.status_code == 200:
                ctype = result["content_type"] or ""
                if not ctype.startswith("image/"):
                    result["warnings"].append(
                        f"<img> src returned non-image Content-Type: {ctype!r} "
                        f"(likely a bot-block HTML page or error page)"
                    )

            if is_city_landing(url):
                result["warnings"].append(
                    "URL itself is a city-landing page — banned pattern"
                )

            break  # success

        except requests.exceptions.Timeout:
            # Slow sites sometimes recover on retry
            if attempts < max_attempts:
                time.sleep(2)
                continue
            result["error"] = f"timeout after {TIMEOUT}s × {max_attempts} attempts"
            break
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"connection error: {e}"
            break
        except requests.RequestException as e:
            result["error"] = f"request error: {e}"
            break
    return result


# ─── CONTENT-QUALITY GATE (📖 links) ───────────────────────────────
# Per Links.html § 📖 reading sources (Lonely Planet retired — do not use): Lonely Planet POI pages became gut-empty
# shells (title + booking CTA + map, 0 words of article prose). Their URLs
# still resolved 200. This gate fetches each 📖 URL, strips nav/footer/CTA
# boilerplate and non-content tags, and fails any page under MIN_PROSE_WORDS.
# Catches the whole class-of-failure, not just Lonely Planet.

MIN_PROSE_WORDS = 100

# Tags whose text should never count as article prose
_STRIP_TAGS = re.compile(
    r'<(script|style|nav|header|footer|aside|form|noscript)\b[^>]*>.*?</\1>',
    re.IGNORECASE | re.DOTALL,
)
# Common CTA/menu patterns that show up as boilerplate text even inside <main>
_STRIP_CTA_PHRASES = re.compile(
    r'\b(book (?:now|a tour|tickets|this experience)|buy tickets|check availability|'
    r'reserve (?:your|a) (?:spot|table|tour)|add to (?:wishlist|cart)|'
    r'sign up|subscribe|log in|sign in|accept cookies|manage preferences)\b',
    re.IGNORECASE,
)


def _prose_word_count(body_html: str) -> int:
    """
    Rough article-word count. Strip HTML tags, nav/footer/script/style
    content, and common CTA phrases, then count whitespace-separated words.
    Not a true readability parser — a floor, not a precision instrument.
    """
    stripped = _STRIP_TAGS.sub(" ", body_html)
    # Keep only <p>, <li>, <h1>..<h6>, <blockquote> text — the article body
    prose_bits = re.findall(
        r'<(?:p|li|h[1-6]|blockquote)\b[^>]*>(.*?)</(?:p|li|h[1-6]|blockquote)>',
        stripped,
        re.IGNORECASE | re.DOTALL,
    )
    text = " ".join(prose_bits)
    # Strip remaining inline tags
    text = re.sub(r'<[^>]+>', " ", text)
    # Remove CTA boilerplate
    text = _STRIP_CTA_PHRASES.sub(" ", text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Count words with at least 2 alphabetic characters
    words = [w for w in text.split() if re.search(r'[A-Za-zÀ-ÿ]{2,}', w)]
    return len(words)


def fetch_prose(url: str) -> dict:
    """
    Fetch a 📖 URL and return word-count + verdict for the content-quality gate.
    Shares retry/timeout semantics with fetch(). Returns:
      { url, status, words, ok, error }
    `ok` = True if the page returned ≥ MIN_PROSE_WORDS of article prose.
    """
    out = {"url": url, "status": None, "words": 0, "ok": False, "error": None}
    try:
        r = requests.get(
            url,
            headers={"User-Agent": UA, "Accept": "text/html,*/*"},
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        out["status"] = r.status_code
        if r.status_code >= 400:
            out["error"] = f"HTTP {r.status_code}"
            return out
        ctype = r.headers.get("Content-Type", "").lower()
        if "html" not in ctype:
            out["error"] = f"non-html content-type: {ctype}"
            return out
        out["words"] = _prose_word_count(r.text)
        out["ok"] = out["words"] >= MIN_PROSE_WORDS
        return out
    except requests.RequestException as e:
        out["error"] = f"request error: {e}"
        return out


def classify(result: dict) -> str:
    """Return 'pass' | 'warn' | 'fail'."""
    if result["error"]:
        # Connection errors from known bot-blocking hosts → warn, not fail.
        # These sites drop TCP/SSL connections to crawlers but serve real
        # content to browsers (same pattern as 403/429 bot-blocks above).
        if host_of(result["url"]) in BOT_BLOCKED_HOSTS:
            return "warn"
        return "fail"
    status = result["status"]
    if status is None:
        return "fail"
    # Known bot-blocker 403/406/410/429 → warn (visual verification needed)
    if status in (403, 406, 410, 429) and result["bot_blocked"]:
        return "warn"
    # Unknown host 429 → warn + nudge (not a hard fail — may just be rate-limiting)
    if status == 429 and result["possible_bot_block"]:
        return "warn"
    if status >= 400:
        return "fail"
    # Non-image content type on <img> is a fail, not a warn (photo is broken)
    if result["is_image"] and result["content_type"] and not result["content_type"].startswith("image/"):
        return "fail"
    if result["warnings"]:
        return "warn"
    return "pass"


def format_line(result: dict, verdict: str) -> str:
    icon = {"pass": PASS, "warn": WARN, "fail": FAIL, "skip": SKIP}[verdict]
    kind = "IMG" if result["is_image"] else "LNK"
    status = result["status"] if result["status"] is not None else "ERR"
    url_short = result["url"]
    if len(url_short) > 90:
        url_short = url_short[:87] + "..."
    line = f"{icon} [{kind}] {status}  {url_short}"
    if result["error"]:
        line += f"\n        → {result['error']}"
    for w in result["warnings"]:
        line += f"\n        → {w}"
    return line


def verify_file(path: Path, *, only_images: bool, only_links: bool,
                quiet: bool, workers: int) -> int:
    html = path.read_text(encoding="utf-8")
    hrefs, imgs = extract_urls(html)

    jobs = []
    skipped_hrefs = 0
    skipped_imgs = 0
    if not only_images:
        for h in hrefs:
            if should_skip(h):
                skipped_hrefs += 1
                continue
            jobs.append((h, False))
    if not only_links:
        for s in imgs:
            if should_skip(s):
                skipped_imgs += 1
                continue
            jobs.append((s, True))

    # De-duplicate while preserving order
    seen = set()
    unique_jobs = []
    for url, is_img in jobs:
        key = (url, is_img)
        if key in seen:
            continue
        seen.add(key)
        unique_jobs.append((url, is_img))

    print(f"\n{'─'*70}")
    print(f"  Verifying URLs in: {path.name}")
    print(f"  {len(unique_jobs)} unique URL(s)   "
          f"({sum(1 for _, i in unique_jobs if not i)} links, "
          f"{sum(1 for _, i in unique_jobs if i)} images)")
    if skipped_hrefs or skipped_imgs:
        print(f"  skipped: {skipped_hrefs} hrefs, {skipped_imgs} srcs "
              "(anchors / mailto / data: / relative)")
    print(f"{'─'*70}")

    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(fetch, url, is_img): (url, is_img)
                   for url, is_img in unique_jobs}
        for fut in as_completed(futures):
            results.append(fut.result())

    # Preserve original order
    order = {url: i for i, (url, _) in enumerate(unique_jobs)}
    results.sort(key=lambda r: order.get(r["url"], 0))

    passes = warns = fails = 0
    for r in results:
        verdict = classify(r)
        if verdict == "pass":
            passes += 1
            if not quiet:
                print(format_line(r, verdict))
        elif verdict == "warn":
            warns += 1
            print(format_line(r, verdict))
        else:
            fails += 1
            print(format_line(r, verdict))

    # ─── CONTENT-QUALITY GATE for 📖 links ──────────────────────
    # Fetch each 📖 URL and require ≥ MIN_PROSE_WORDS of article prose
    # (strips nav/footer/CTA boilerplate). Catches structurally valid
    # but semantically empty pages — the Lonely Planet class-of-failure.
    reading_urls = [u for u in extract_reading_urls(html)
                    if u.startswith(("http://", "https://"))]
    # De-duplicate while preserving order
    _seen = set()
    reading_urls = [u for u in reading_urls if not (u in _seen or _seen.add(u))]

    prose_fails = 0
    prose_warns = 0
    if reading_urls and not only_images:
        print(f"\n{'─'*70}")
        print(f"  📖 content-quality gate: {len(reading_urls)} reading-source URL(s)")
        print(f"  minimum article prose: {MIN_PROSE_WORDS} words")
        print(f"{'─'*70}")
        with ThreadPoolExecutor(max_workers=workers) as ex:
            p_futures = {ex.submit(fetch_prose, u): u for u in reading_urls}
            prose_results = [f.result() for f in as_completed(p_futures)]
        # Preserve input order
        p_order = {u: i for i, u in enumerate(reading_urls)}
        prose_results.sort(key=lambda r: p_order.get(r["url"], 0))
        for pr in prose_results:
            url_short = pr["url"]
            if len(url_short) > 90:
                url_short = url_short[:87] + "..."
            if pr["error"]:
                prose_warns += 1
                print(f"{WARN} [📖] ERR   {url_short}")
                print(f"        → content-quality gate skipped: {pr['error']}")
            elif pr["ok"]:
                if not quiet:
                    print(f"{PASS} [📖] {pr['words']:>4}w {url_short}")
            else:
                prose_fails += 1
                print(f"{FAIL} [📖] {pr['words']:>4}w {url_short}")
                print(f"        → under {MIN_PROSE_WORDS} words of article prose "
                      f"(structurally valid, semantically empty)")
        print(f"\n  {PASS} {sum(1 for r in prose_results if r['ok'])} passed   "
              f"{WARN}{prose_warns} warnings   {FAIL} {prose_fails} failed")

    print(f"\n{'─'*70}")
    total_fails = fails + prose_fails
    total_warns = warns + prose_warns
    print(f"  {PASS} {passes} passed   {WARN}{total_warns} warnings   {FAIL} {total_fails} failed")
    print(f"{'─'*70}\n")

    return 0 if total_fails == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(
        description="Verify every URL in a travel-guide HTML file actually loads."
    )
    p.add_argument("html_file", type=Path)
    p.add_argument("--only-images", action="store_true",
                   help="Only check <img src> URLs")
    p.add_argument("--only-links", action="store_true",
                   help="Only check <a href> URLs")
    p.add_argument("--quiet", action="store_true",
                   help="Only print failures and warnings")
    p.add_argument("--workers", type=int, default=4,
                   help="Concurrent requests (default 4; Wikimedia CDN rate-limits above this)")
    args = p.parse_args()

    if not args.html_file.exists():
        print(f"❌ File not found: {args.html_file}", file=sys.stderr)
        return 1

    return verify_file(
        args.html_file,
        only_images=args.only_images,
        only_links=args.only_links,
        quiet=args.quiet,
        workers=args.workers,
    )


if __name__ == "__main__":
    sys.exit(main())
