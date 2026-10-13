# China Supplier Finder

A product-agnostic Streamlit application that discovers public supplier leads for manufacturers, wholesalers and sourcing agents in China.

## Run locally

1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Configure `BING_SEARCH_KEY` in your environment or Streamlit secrets **only if you have access to a working Bing-compatible API**. Microsoft's legacy Bing Search APIs have been retired; this search adapter may require replacement with a supported licensed search provider.
4. Run `streamlit run app.py`.
5. Enter a product, optionally its Chinese translation, and select categories and sites. Export results as CSV.

## Deployment

Deploy `app.py` with Streamlit Community Cloud and configure any API keys in app secrets, never in GitHub.

## Limitations

Search results are unverified leads, not proof of manufacturer status. The app does not guarantee all suppliers in China or extract verified contact information. Respect website terms and independently check company registration, factory ownership, certifications, pricing and payment details.
