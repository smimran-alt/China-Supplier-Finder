# China Supplier Finder v3 — Direct Web Crawler

A Streamlit application to crawl **public, permitted websites** for any product and identify possible Chinese manufacturers, wholesalers, and sourcing agents. **No API key required.**

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

At https://share.streamlit.io/ choose repository `smimran-alt/China-Supplier-Finder`, branch `main`, entrypoint `app.py`. No secrets are required.

## Use

1. Enter a product, e.g. `perfume`, and optionally the Chinese translation `香水`.
2. Paste one or more **starting website URLs**, one per line, for public sites that permit crawling.
3. Choose link depth, page limit and polite request delay.
4. Start the crawl, review matched pages, and download CSV.

## Important limitations

This is a **seeded site crawler**, not an internet-wide search engine: it does not discover every supplier across China automatically. It follows links only within the supplied website hosts. It checks robots.txt, skips inaccessible websites, and does not bypass login, CAPTCHA, anti-bot systems or rate limits. Some marketplaces disallow automated crawling. A matching page is a lead, **not a verified company**. Validate registration, factory status, quality and contact details independently. The application may require changes to support JavaScript-only websites or high-volume crawling. The application has not been tested against live supplier websites.
