#!/usr/bin/env python3
"""Scrape a JavaScript-rendered site with a real browser into a CSV.

Target: quotes.toscrape.com/js/ — content is injected by JS, so requests/BeautifulSoup
return an empty shell. Uses the locally installed Chrome (no bundled download).

Usage: python scrape_js.py [--pages N] [--out quotes.csv]
"""
import argparse
import csv
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "https://quotes.toscrape.com/js/page/{}/"
FIELDS = ["quote", "author", "tags"]


def scrape(page, max_pages: int):
    rows, seen = [], set()
    for n in range(1, max_pages + 1):
        page.goto(BASE.format(n), wait_until="networkidle")
        page.wait_for_selector("div.quote", timeout=15000)
        cards = page.query_selector_all("div.quote")
        fresh = 0
        for card in cards:
            text = card.query_selector("span.text").inner_text().strip()
            author = card.query_selector("small.author").inner_text().strip()
            tags = [t.inner_text().strip() for t in card.query_selector_all("a.tag")]
            if text in seen:
                continue
            seen.add(text)
            rows.append({"quote": text, "author": author, "tags": ";".join(tags)})
            fresh += 1
        print(f"page {n}: {len(cards)} cards rendered, {fresh} new")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--out", default="quotes.csv")
    args = ap.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(user_agent="portfolio-demo/1.0")
        page = ctx.new_page()
        try:
            rows = scrape(page, args.pages)
        finally:
            browser.close()

    if not rows:
        print("no rows scraped", file=sys.stderr)
        return 1

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {args.out}: {len(rows)} rows, {len(FIELDS)} columns")
    print("sample:", re.sub(r"\s+", " ", rows[0]["quote"])[:60])
    return 0


if __name__ == "__main__":
    sys.exit(main())
