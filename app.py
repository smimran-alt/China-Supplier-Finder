import csv
import io
import re
import time
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="China Supplier Finder", page_icon="🔎", layout="wide")
st.title("China Supplier Finder — Direct Crawler")
st.caption("No search API key. Crawl permitted public pages starting from URLs you provide.")

AGENT = "ChinaSupplierFinder/3.0 (+research crawler; respects robots.txt)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": AGENT, "Accept-Language": "en,zh-CN;q=0.8"})
CATEGORY_TERMS = {
    "Manufacturer": ["manufacturer", "factory", "oem", "odm", "制造商", "工厂", "厂家", "生产"],
    "Wholesaler": ["wholesale", "distributor", "bulk", "批发", "经销"],
    "Sourcing agent": ["sourcing agent", "procurement", "trading company", "采购代理", "贸易公司"],
}
ROBOTS = {}

def allowed(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in ROBOTS:
        robot = RobotFileParser()
        robot.set_url(origin + "/robots.txt")
        try:
            response = SESSION.get(origin + "/robots.txt", timeout=8)
            if response.status_code == 200:
                robot.parse(response.text.splitlines())
                ROBOTS[origin] = robot
            elif response.status_code in (401, 403, 429) or response.status_code >= 500:
                ROBOTS[origin] = False
            else:
                ROBOTS[origin] = True
        except requests.RequestException:
            ROBOTS[origin] = False
    policy = ROBOTS[origin]
    return policy.can_fetch(AGENT, url) if isinstance(policy, RobotFileParser) else policy

def crawl(seed_urls, product, chinese, depth, max_pages, delay):
    queue = deque()
    seeds = set()
    for raw in seed_urls.splitlines():
        url = raw.strip()
        if not url:
            continue
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            continue
        seeds.add(parsed.netloc.lower())
        queue.append((url, 0))
    visited, rows, errors = set(), [], []
    product_terms = [t.lower() for t in (product.strip(), chinese.strip()) if t.strip()]
    while queue and len(visited) < max_pages:
        url, level = queue.popleft()
        url = urldefrag(url)[0]
        if url in visited:
            continue
        parsed = urlparse(url)
        if parsed.netloc.lower() not in seeds:
            continue
        visited.add(url)
        if not allowed(url):
            errors.append(f"Blocked by robots policy or unavailable robots.txt: {url}")
            continue
        try:
            response = SESSION.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            if urlparse(response.url).netloc.lower() not in seeds:
                continue
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(response.text[:1_500_000], "html.parser")
            for node in soup(["script", "style", "nav", "footer"]):
                node.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else ""
            body = soup.get_text(" ", strip=True)[:12000]
            content = (title + " " + body).lower()
            matched_product = any(term in content for term in product_terms)
            types = [label for label, terms in CATEGORY_TERMS.items() if any(t in content for t in terms)]
            if matched_product:
                rows.append({
                    "product": product,
                    "page_title": title[:250],
                    "possible_business_types": ", ".join(types) or "Unclassified",
                    "website": urlparse(response.url).netloc,
                    "source_url": response.url,
                    "excerpt": body[:450],
                    "verification": "Unverified lead",
                })
            if level < depth:
                for link in soup.select("a[href]"):
                    next_url = urldefrag(urljoin(response.url, link.get("href", "")))[0]
                    p = urlparse(next_url)
                    if p.scheme in ("http", "https") and p.netloc.lower() in seeds and next_url not in visited:
                        if not re.search(r"\.(pdf|jpg|jpeg|png|gif|zip|exe)(\?|$)", p.path, re.I):
                            queue.append((next_url, level + 1))
        except requests.RequestException as exc:
            errors.append(f"{url}: {exc}")
        time.sleep(delay)
    return rows, errors, len(visited)

with st.form("crawler"):
    product = st.text_input("Product in English", "perfume")
    chinese = st.text_input("Product in Chinese (optional)", "香水")
    seeds = st.text_area("Starting website URLs (one per line)", placeholder="https://example-supplier-directory.com/category/perfume", height=120)
    c1, c2, c3 = st.columns(3)
    depth = c1.slider("Link depth", 0, 3, 1)
    max_pages = c2.slider("Maximum pages", 5, 100, 25, 5)
    delay = c3.slider("Delay between requests (seconds)", 1.0, 5.0, 2.0, 0.5)
    submitted = st.form_submit_button("Start direct crawl", type="primary")

if submitted:
    if not product.strip() or not seeds.strip():
        st.error("Enter a product and at least one public website URL.")
    else:
        with st.spinner("Crawling allowed pages..."):
            rows, errors, visited = crawl(seeds, product, chinese, depth, max_pages, delay)
        st.session_state["results"] = (rows, errors, visited)

if "results" in st.session_state:
    rows, errors, visited = st.session_state["results"]
    st.metric("Pages checked", visited)
    st.metric("Product-matching pages", len(rows))
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        st.download_button("Download supplier leads CSV", buffer.getvalue(), "supplier_leads.csv", "text/csv")
    if errors:
        with st.expander(f"Skipped pages and errors ({len(errors)})"):
            for error in errors[:100]:
                st.write(error)
    if not rows:
        st.info("No matching pages found. Try more relevant starting URLs or a greater crawl depth.")

st.warning("This is a direct crawler, not an internet-wide search engine. Provide seed websites that allow automated access. Listings are not verified manufacturers or sourcing agents.")
