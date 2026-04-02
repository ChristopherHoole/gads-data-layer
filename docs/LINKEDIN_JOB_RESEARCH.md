# LinkedIn & Job Search API Research

**Date:** 2026-03-27
**Purpose:** Evaluate options for pulling job listings (LinkedIn, Indeed, etc.) into the ACT Dashboard Jobs tracker.

---

## Current Pipeline

We already have:
- **Indeed MCP Connector** in claude.ai (working) — searches Indeed, outputs to Google Sheet
- **Google Sheet Sync** in ACT — reads from published CSV, imports into DuckDB
- **URL Auto-Fill** in ACT slide-in — paste a LinkedIn/Indeed URL, scrapes job details

The goal is to find additional/better ways to get job data into ACT, especially from LinkedIn.

---

## Option 1: LinkedIn MCP Server (stickerdaniel)

**URL:** https://github.com/stickerdaniel/linkedin-mcp-server

**What it does:** Open-source MCP server that connects Claude Desktop to your LinkedIn account. Scrapes profiles, companies, and job listings.

**Key tools available:**
- Search for jobs by keyword
- Get job details for specific listings
- Get your personalised recommended jobs
- Scrape company and person profiles

**How it works:** Uses Patchright (browser automation) with a persistent browser profile to maintain your LinkedIn session. Runs locally.

**Pros:**
- Free and open-source
- Direct LinkedIn access with your own credentials
- Gets personalised job recommendations
- Works with Claude Desktop / Claude Code
- Full job details including description, company, salary

**Cons:**
- Requires running a local server (Node.js/Python)
- LinkedIn actively blocks scraping — can break at any time
- Uses your personal LinkedIn session (risk of account restriction)
- Rate limited — LinkedIn blocks after ~10 pages of results
- Requires Patchright browser automation setup

**Pricing:** Free (open-source)

**Verdict:** High risk of LinkedIn account issues. Best for occasional use, not daily automated scraping.

---

## Option 2: JobSpy (Python Library)

**URL:** https://github.com/speedyapply/JobSpy

**What it does:** Python library that scrapes job postings from multiple job boards concurrently and returns results as a pandas DataFrame.

**Supported boards:** LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter, Bayt, Naukri, BDJobs

**Key features:**
- `pip install -U python-jobspy` (Python 3.10+)
- Search by keyword, location, job type, remote, hours since posted
- Returns structured data: title, company, location, salary, description, URL
- Can scrape multiple boards simultaneously

**Example usage:**
```python
from jobspy import scrape_jobs
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "glassdoor"],
    search_term="Google Ads Manager",
    location="Remote, UK",
    results_wanted=20,
    is_remote=True,
    country_indeed="UK"
)
```

**Pros:**
- Free and open-source
- Multi-board aggregation in one call
- Returns pandas DataFrame (easy to process)
- Indeed scraper has no rate limiting
- Actively maintained (v1.1.79, March 2026)
- Could integrate directly into ACT's Flask backend

**Cons:**
- LinkedIn rate limits after ~10 pages per IP
- Still scraping — sites can block at any time
- May need proxy rotation for heavy use
- No official API backing — fragile

**Pricing:** Free (open-source)

**Verdict:** BEST OPTION for direct integration into ACT. Could add a "Search Jobs" feature that calls JobSpy from the Flask backend and populates the jobs table directly. No MCP, no Google Sheets, no manual steps.

---

## Option 3: JSearch API (via RapidAPI)

**URL:** https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

**What it does:** REST API that aggregates job postings from Google for Jobs (which indexes LinkedIn, Indeed, Glassdoor, ZipRecruiter, and thousands of other sources).

**Key features:**
- Real-time job search with 30+ data points per listing
- Up to 500 results per query
- Salary estimates included
- Company details and job requirements extracted

**Pros:**
- Legitimate API with stable endpoints
- Aggregates from all major boards via Google for Jobs
- Structured JSON responses
- No scraping risk to personal accounts
- Good documentation

**Cons:**
- Paid service (free tier is very limited)
- Pricing not fully transparent — requires RapidAPI account to see tiers
- Free tier likely limited to ~100-200 requests/month
- Adds a third-party dependency
- Data is from Google for Jobs index (slight delay vs direct board)

**Pricing:** Free tier available (limited). Paid tiers on RapidAPI (exact pricing requires account).

**Verdict:** Good stable option if free tier covers your needs (1-2 daily searches). Worth signing up to check exact limits.

---

## Option 4: Adzuna API

**URL:** https://developer.adzuna.com/

**What it does:** Job search API from Adzuna, a UK-based job board that aggregates listings from thousands of sources.

**Key features:**
- REST API with JSON responses
- Covers UK, USA, and 10+ other countries
- Salary data and statistics
- Category-based search

**Pros:**
- UK-based company — strong UK job coverage
- Free tier available
- Legitimate API (not scraping)
- Good for UK + USA searches
- Historical salary data

**Cons:**
- Doesn't directly index LinkedIn (aggregates from other sources)
- Free tier rate limits unclear (not documented publicly)
- Smaller dataset than Google for Jobs
- Registration required for API keys

**Pricing:** Free tier available. Rate limit increases available on request for commercial use.

**Verdict:** Worth registering for free API keys. Good supplementary source, especially for UK roles.

---

## Option 5: Indeed MCP (Already Connected)

**What we have:** Indeed connector in claude.ai, syncing to Google Sheet, imported into ACT.

**Pros:**
- Already working
- Official Indeed API access via MCP
- Reliable and structured data
- Covers UK and USA

**Cons:**
- Requires manual prompt in claude.ai to trigger search
- Pipeline: claude.ai → Google Sheet → ACT (multiple steps)
- Can't be automated end-to-end from ACT

**Verdict:** Keep as primary source. Works well for the daily workflow.

---

## Option 6: Apify Job Scrapers

**URL:** https://apify.com/store

**What it does:** Cloud-based web scraping platform with pre-built scrapers for LinkedIn, Indeed, and Glassdoor.

**Pros:**
- Pre-built, maintained scrapers
- Cloud-hosted — no local setup
- API access to results
- Can schedule recurring scrapes

**Cons:**
- Paid service (free tier: $5/month credit)
- Still scraping (same blocking risks)
- Another third-party dependency

**Pricing:** Free: $5/month credit. Personal: $49/month. Team: $499/month.

**Verdict:** Overkill for personal job search. Better suited for recruiters or data companies.

---

## Recommendation

### Immediate (no extra setup):
Keep the current pipeline: **Indeed MCP → Google Sheet → ACT Sync**

### Short-term (best ROI):
Integrate **JobSpy** directly into ACT's Flask backend:
- Add a "Search Jobs" button on the Jobs page
- User enters keywords, location, remote preference
- Backend calls JobSpy to search Indeed + LinkedIn + Glassdoor simultaneously
- Results displayed in a preview table
- User selects which jobs to import → saved to DuckDB
- Zero manual copy/paste, zero Google Sheets, zero claude.ai required

### Medium-term (stability):
Register for **JSearch API** (free tier) and **Adzuna API** (free tier) as fallback sources if JobSpy scraping gets blocked.

### Integration Architecture:
```
ACT Jobs Page
    ├── "Search Jobs" button → JobSpy (primary, free, multi-board)
    ├── "Sync from Sheet" button → Google Sheet (Indeed MCP backup)
    ├── "Add Job" → URL auto-fill (paste any URL)
    └── Future: JSearch API / Adzuna API fallbacks
```

---

## Sources

- [LinkedIn MCP Server (stickerdaniel)](https://github.com/stickerdaniel/linkedin-mcp-server)
- [JobSpy Library](https://github.com/speedyapply/JobSpy)
- [JSearch API on RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- [Adzuna Developer API](https://developer.adzuna.com/)
- [Apify Job Scrapers](https://apify.com/store)
- [Best Job Posting APIs 2026 (TheirStack)](https://theirstack.com/en/blog/best-job-posting-apis)
- [Best Job APIs 2026 (Bright Data)](https://brightdata.com/blog/web-data/best-job-apis)
- [Composio LinkedIn MCP](https://composio.dev/toolkits/linkedin/framework/claude-code)
