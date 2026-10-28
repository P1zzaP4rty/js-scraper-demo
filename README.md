# JS-rendered scraper demo — browser → CSV

Second demo in the pair: the first scrapes a server-rendered site with `requests`, this
one scrapes a site whose content only exists after JavaScript runs. Same output shape,
different tool, because the hard part is different.

## Why a browser is required here

Measured on the target page, not assumed:

```
requests + BeautifulSoup :  div.quote count = 0   (5,806-byte shell, 2 <script> tags)
Playwright + Chrome      :  div.quote count = 10  (after networkidle)
```

`requests` gets an empty shell. Anything built on it returns zero rows and looks like
"the site blocks scrapers" when the real cause is that the DOM is assembled client-side.

## Input

`https://quotes.toscrape.com/js/page/N/` — public scraping sandbox, JS-rendered, paginated.

## Output

`quotes.csv` — 20 rows, 3 columns:

```
quote,author,tags
"The world as we have created it is a process of our thinking. ...",Albert Einstein,change;deep-thoughts;thinking;world
"It is our choices, Harry, that show what we truly are, ...",J.K. Rowling,abilities;choices
```

## Run

```bash
pip install playwright requests beautifulsoup4
# no browser download: uses the installed Chrome via channel="chrome"
python scrape_js.py --pages 2 --out quotes.csv
```

Verified run (`run.log`):

```
page 1: 10 cards rendered, 10 new
page 2: 10 cards rendered, 10 new

wrote quotes.csv: 20 rows, 3 columns
```

Checks on the output: 20 rows, 3 columns, 0 empty fields, 0 duplicate quotes, 15 distinct authors.

## Handling

- waits on `networkidle` **and** `div.quote` before reading, so it doesn't race the render
- dedupes by quote text across pages
- reuses the installed Chrome (`channel="chrome"`) — no 300 MB browser download on the client's machine
- exits 1 on zero rows so a scheduled run fails loudly instead of writing an empty file

## What it does not handle

- logins, 2FA, captchas, proxy rotation
- sites that detect headless browsers — that needs a stealth layer, priced separately
- infinite scroll (this one paginates; scroll-until-stable is a different loop)
- any site whose terms forbid scraping. Check first; this target is a sandbox built for it.
