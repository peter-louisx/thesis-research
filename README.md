# Thesis Research

## Dataset Scraper

### Requirements

* Node
* NPM

1. Installation

```bash

npm install 
```

2. Run scraper&#x20;

```bash

npx tweet-harvest
```

You will be prompted for these:

* X auth token (Inspect -> Application -> Cookies -> [https://x.com](https://x.com) -> Copy auth\_token&#x20;
* Keywords (Format: \<Keyword> since:\<Start Date> until:\<End Date> lang:\<Language>  , eg: ChatGPT since:2024-10-30 until:2024-11-01 lang\:id)
* Format (CSV/Excel)

Result will be saved in `tweets-data/`
