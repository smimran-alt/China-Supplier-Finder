import csv
import io
import os
import re
import time
from urllib.parse import urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="China Supplier Finder", page_icon="🔎", layout="wide")
st.title("China Supplier Finder")
st.caption("Find public supplier leads for any product. Results are not verified businesses.")

SITES = {
    "Alibaba": "alibaba.com",
    "Made-in-China": "made-in-china.com",
    "Global Sources": "globalsources.com",
    "1688": "1688.com",
    "Independent websites": "",
}
CATEGORIES = {
    "Manufacturers": ["manufacturer", "厂家"],
    "Wholesalers": ["wholesale supplier", "批发"],
    "Sourcing agents": ["sourcing agent", "采购代理"],
}

def clean(value):
    return re.sub(r"\s+", " ", BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)).strip()

def api_key():
    try:
        return os.getenv("BING_SEARCH_KEY") or st.secrets.get("BING_SEARCH_KEY", "")
    except (FileNotFoundError, KeyError):
        return os.getenv("BING_SEARCH_KEY", "")

def search(query, limit):
    key = api_key()
    if not key:
        raise RuntimeError("Search API not configured. See README; Bing legacy API may be retired.")
    response = requests.get(
        "https://api.bing.microsoft.com/v7.0/search",
        headers={"Ocp-Apim-Subscription-Key": key},
        params={"q": query, "count": min(limit, 50), "mkt": "en-US"},
        timeout=25,
    )
    response.raise_for_status()
    return response.json().get("webPages", {}).get("value", [])

def collect(product, chinese, categories, sites, limit):
    rows, seen, errors = [], set(), []
    for category in categories:
        for site in sites:
            for keyword in CATEGORIES[category]:
                term = chinese if re.search(r"[\u3400-\u9fff]", keyword) and chinese else product
                domain = SITES[site]
                query = f"{term} {keyword} China" + (f" site:{domain}" if domain else "")
                try:
                    hits = search(query, limit)
                except (requests.RequestException, RuntimeError, ValueError) as exc:
                    errors.append(f"{site} / {category}: {exc}")
                    continue
                for hit in hits:
                    url = hit.get("url", "")
                    parsed = urlparse(url)
                    if parsed.scheme not in ("http", "https") or not parsed.netloc:
                        continue
                    normalized = url.rstrip("/").lower()
                    if normalized in seen:
                        continue
                    seen.add(normalized)
                    rows.append({
                        "product": product,
                        "category_searched": category,
                        "platform": site,
                        "listing_title": clean(hit.get("name", "")),
                        "website_domain": parsed.netloc,
                        "source_url": url,
                        "description": clean(hit.get("snippet", "")),
                        "search_query": query,
                        "verification": "Not verified",
                    })
                time.sleep(0.15)
    return rows, errors

with st.form("supplier_search"):
    a, b = st.columns(2)
    product = a.text_input("Product (English)", "perfume")
    chinese = b.text_input("Chinese translation (optional)", "香水")
    categories = st.multiselect("Business types", list(CATEGORIES), default=list(CATEGORIES))
    sites = st.multiselect("Sources", list(SITES), default=list(SITES))
    limit = st.slider("Results per query", 5, 30, 10)
    submitted = st.form_submit_button("Find suppliers", type="primary")

if submitted:
    if not product.strip() or not categories or not sites:
        st.error("Enter a product and select at least one business type and source.")
    else:
        with st.spinner("Searching public indexed pages..."):
            rows, errors = collect(product.strip(), chinese.strip(), categories, sites, limit)
        st.session_state["rows"] = rows
        st.session_state["errors"] = errors

if "rows" in st.session_state:
    rows = st.session_state["rows"]
    st.metric("Unique listing URLs", len(rows))
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        st.download_button("Download CSV", buffer.getvalue(), "china_supplier_leads.csv", "text/csv")
    else:
        st.info("No leads collected. Check API configuration and search results.")
    if st.session_state.get("errors"):
        with st.expander("Search errors"):
            for error in dict.fromkeys(st.session_state["errors"]):
                st.warning(error)

st.info("Search-category labels do not prove a company is a factory. Verify business registration and capabilities independently.")
