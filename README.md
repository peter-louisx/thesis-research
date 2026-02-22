# Thesis Research

## Dataset Scraper

### Requirements

* Node
* NPM

1. Installation

```tsx

npm install 
```

1. Run scraper&#x20;

```tsx

npx tweet-harvest
```

You will be prompted for these:

* **X auth token** (Inspect -> Application -> Cookies -> [https://x.com](https://x.com) -> Copy `auth_token`)
* **Keyword** (Format: \<Keyword> since:\<Start Date> until:\<End Date> lang:\<Language>  , eg: ChatGPT since:2024-10-30 until:2024-11-01 lang\:id)
* **Format** (CSV/Excel)

Result will be saved in `tweets-data/`
