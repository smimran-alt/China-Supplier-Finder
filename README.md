# China Supplier Finder — v2.0

A product-agnostic Streamlit supplier discovery dashboard. Search indexed listings of Chinese manufacturers, wholesalers and sourcing agents, with English/Chinese keywords and CSV export.

## Run locally
1. Install Python 3.11+.
2. `pip install -r requirements.txt`
3. Obtain a Brave Search API key at https://api-dashboard.search.brave.com/
4. Set environment variable `BRAVE_SEARCH_API_KEY` or place it in your local `.streamlit/secrets.toml`:

```toml
BRAVE_SEARCH_API_KEY = "YOUR_KEY"
```

5. `streamlit run app.py`

## Deploy online
1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Create a new app from repository `smimran-alt/China-Supplier-Finder`, branch `main`, file `app.py`.
3. In Advanced settings / Secrets, add the TOML secret above. **Never commit API keys to GitHub.**
4. Deploy, then open your assigned Streamlit URL.

## Scope and limitations
The dashboard discovers publicly indexed **leads**, not an exhaustive supplier database. Results can include directories, intermediaries and duplicates. Categories indicate search intent, not independently verified factory status. Some marketplaces may not be indexed; access their data through permitted APIs or licensed sources. The app does not bypass login, anti-bot or robots restrictions. Check registration, factory ownership, compliance documents and payment details independently.

API usage may incur costs. The first version is not yet live-tested against a real API key.
