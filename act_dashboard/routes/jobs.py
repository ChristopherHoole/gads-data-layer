"""
Jobs route — Job Tracker for PPC/Google Ads role hunting.
Chat 115: Task 2 — Database table + CRUD API endpoints.
Chat 115: Task 4b — URL auto-fill (fetch job details from URL).
"""

import csv
import io
import json
import logging
import re
from datetime import datetime

import requests as http_requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, render_template, request

from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_db_connection, get_page_context

logger = logging.getLogger(__name__)

bp = Blueprint("jobs", __name__)


# ==================== DATABASE SETUP ====================

def _ensure_jobs_table(conn):
    """Create jobs table and sequence if they don't exist."""
    conn.execute("CREATE SEQUENCE IF NOT EXISTS jobs_seq START 1")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id          INTEGER PRIMARY KEY DEFAULT nextval('jobs_seq'),
            source          VARCHAR DEFAULT 'other',
            title           VARCHAR NOT NULL,
            company         VARCHAR,
            location        VARCHAR,
            salary          VARCHAR,
            job_url         VARCHAR,
            description     VARCHAR,
            status          VARCHAR DEFAULT 'saved',
            notes           VARCHAR,
            date_found      DATE DEFAULT CURRENT_DATE,
            date_applied    DATE,
            date_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            contact_name    VARCHAR,
            contact_email   VARCHAR,
            contact_phone   VARCHAR,
            follow_up_date  DATE,
            priority        VARCHAR DEFAULT 'medium'
        )
    """)
    # Migrate: add contact_phone column if table already existed without it
    try:
        conn.execute("ALTER TABLE jobs ADD COLUMN contact_phone VARCHAR")
    except Exception:
        pass  # Column already exists


# ==================== PAGE ROUTE ====================

@bp.route("/jobs")
@login_required
def jobs_page():
    """Display the Jobs Tracker page."""
    config, clients, current_client_path = get_page_context()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)
        return render_template(
            "jobs.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_path=current_client_path,
        )
    finally:
        conn.close()


# ==================== JSON API ENDPOINTS ====================

@bp.route("/jobs/data")
@login_required
def jobs_data():
    """GET /jobs/data — return all jobs as JSON for the table."""
    config = get_current_config()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)
        rows = conn.execute("""
            SELECT * FROM jobs ORDER BY date_found DESC, job_id DESC
        """).fetchall()
        cols = [d[0] for d in conn.description]
        jobs = [dict(zip(cols, row)) for row in rows]

        # Serialize dates/timestamps to ISO strings
        for job in jobs:
            for k, v in job.items():
                if isinstance(v, (datetime,)):
                    job[k] = v.isoformat()
                elif hasattr(v, "isoformat"):
                    job[k] = v.isoformat()

        return jsonify({"success": True, "data": jobs})
    except Exception as e:
        logger.error(f"jobs_data error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@bp.route("/jobs/check-duplicate", methods=["POST"])
@login_required
def check_duplicate():
    """POST /jobs/check-duplicate — check if a job already exists."""
    config = get_current_config()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)
        data = request.get_json()
        matches = []

        job_url = (data.get("job_url") or "").strip()
        title = (data.get("title") or "").strip()
        company = (data.get("company") or "").strip()

        # Check 1: Exact URL match
        if job_url:
            rows = conn.execute(
                "SELECT job_id, title, company, status, date_updated FROM jobs WHERE LOWER(job_url) = LOWER(?)",
                [job_url],
            ).fetchall()
            for r in rows:
                matches.append({
                    "id": r[0], "title": r[1], "company": r[2],
                    "status": r[3], "date_added": str(r[4])[:10] if r[4] else "",
                    "match_type": "exact_url",
                })

        # Check 2: Fuzzy title + company match (case-insensitive)
        if title and company and not matches:
            rows = conn.execute(
                "SELECT job_id, title, company, status, date_updated FROM jobs WHERE LOWER(title) = LOWER(?) AND LOWER(company) = LOWER(?)",
                [title, company],
            ).fetchall()
            for r in rows:
                matches.append({
                    "id": r[0], "title": r[1], "company": r[2],
                    "status": r[3], "date_added": str(r[4])[:10] if r[4] else "",
                    "match_type": "title_company",
                })

        return jsonify({"success": True, "duplicates": matches, "count": len(matches)})
    except Exception as e:
        logger.error(f"check_duplicate error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@bp.route("/jobs/create", methods=["POST"])
@login_required
def create_job():
    """POST /jobs/create — add a new job."""
    config = get_current_config()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)
        data = request.get_json()

        if not data or not data.get("title"):
            return jsonify({"success": False, "error": "Job title is required"}), 400

        conn.execute("""
            INSERT INTO jobs (
                source, title, company, location, salary, job_url,
                description, status, notes, date_found, date_applied,
                date_updated, contact_name, contact_email, contact_phone,
                follow_up_date, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
        """, [
            data.get("source", "other"),
            data["title"],
            data.get("company"),
            data.get("location"),
            data.get("salary"),
            data.get("job_url"),
            data.get("description"),
            data.get("status", "saved"),
            data.get("notes"),
            data.get("date_found") or datetime.now().strftime("%Y-%m-%d"),
            data.get("date_applied") or None,
            data.get("contact_name"),
            data.get("contact_email"),
            data.get("contact_phone"),
            data.get("follow_up_date") or None,
            data.get("priority", "low"),
        ])

        return jsonify({"success": True, "message": "Job created"})
    except Exception as e:
        logger.error(f"create_job error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@bp.route("/jobs/update", methods=["PUT"])
@login_required
def update_job():
    """PUT /jobs/update — update an existing job."""
    config = get_current_config()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)
        data = request.get_json()
        job_id = data.get("job_id")

        if not job_id:
            return jsonify({"success": False, "error": "job_id is required"}), 400

        conn.execute("""
            UPDATE jobs SET
                source = ?, title = ?, company = ?, location = ?, salary = ?,
                job_url = ?, description = ?, status = ?, notes = ?,
                date_found = ?, date_applied = ?,
                contact_name = ?, contact_email = ?, contact_phone = ?,
                follow_up_date = ?, priority = ?
            WHERE job_id = ?
        """, [
            data.get("source", "other"),
            data.get("title"),
            data.get("company"),
            data.get("location"),
            data.get("salary"),
            data.get("job_url"),
            data.get("description"),
            data.get("status", "saved"),
            data.get("notes"),
            data.get("date_found"),
            data.get("date_applied") or None,
            data.get("contact_name"),
            data.get("contact_email"),
            data.get("contact_phone"),
            data.get("follow_up_date") or None,
            data.get("priority", "low"),
            job_id,
        ])

        return jsonify({"success": True, "message": "Job updated"})
    except Exception as e:
        logger.error(f"update_job error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@bp.route("/jobs/delete", methods=["DELETE"])
@login_required
def delete_job():
    """DELETE /jobs/delete — remove a job."""
    config = get_current_config()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)
        data = request.get_json()
        job_id = data.get("job_id")

        if not job_id:
            return jsonify({"success": False, "error": "job_id is required"}), 400

        conn.execute("DELETE FROM jobs WHERE job_id = ?", [job_id])
        return jsonify({"success": True, "message": "Job deleted"})
    except Exception as e:
        logger.error(f"delete_job error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


# ==================== URL AUTO-FILL ====================

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


def _detect_source(url):
    """Detect job board source from URL domain."""
    url_lower = url.lower()
    if "indeed.com" in url_lower or "indeed.co" in url_lower:
        return "indeed"
    if "linkedin.com" in url_lower:
        return "linkedin"
    return "other"


def _extract_json_ld(soup):
    """Extract job data from JSON-LD structured data (schema.org/JobPosting)."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            # Handle both direct objects and arrays
            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") == "JobPosting":
                    return _parse_job_posting(item)
                # Check nested @graph
                if "@graph" in item:
                    for node in item["@graph"]:
                        if node.get("@type") == "JobPosting":
                            return _parse_job_posting(node)
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
    return None


def _parse_job_posting(jp):
    """Parse a schema.org JobPosting object into our fields."""
    result = {}

    result["title"] = jp.get("title", "")

    # Company
    org = jp.get("hiringOrganization", {})
    if isinstance(org, dict):
        result["company"] = org.get("name", "")
    elif isinstance(org, str):
        result["company"] = org

    # Location
    loc = jp.get("jobLocation", {})
    if isinstance(loc, dict):
        address = loc.get("address", {})
        if isinstance(address, dict):
            parts = [
                address.get("addressLocality", ""),
                address.get("addressRegion", ""),
                address.get("addressCountry", ""),
            ]
            result["location"] = ", ".join(p for p in parts if p)
        elif isinstance(address, str):
            result["location"] = address
    elif isinstance(loc, list) and loc:
        # Multiple locations — take first
        first = loc[0] if isinstance(loc[0], dict) else {}
        address = first.get("address", {})
        if isinstance(address, dict):
            parts = [
                address.get("addressLocality", ""),
                address.get("addressRegion", ""),
                address.get("addressCountry", ""),
            ]
            result["location"] = ", ".join(p for p in parts if p)

    # Salary
    salary = jp.get("baseSalary", {})
    if isinstance(salary, dict):
        value = salary.get("value", {})
        currency = salary.get("currency", "")
        if isinstance(value, dict):
            min_v = value.get("minValue", "")
            max_v = value.get("maxValue", "")
            unit = value.get("unitText", "")
            if min_v and max_v:
                result["salary"] = f"{currency}{min_v} - {currency}{max_v} {unit}".strip()
            elif min_v:
                result["salary"] = f"{currency}{min_v} {unit}".strip()
        elif value:
            result["salary"] = f"{currency}{value}".strip()
    elif isinstance(salary, str):
        result["salary"] = salary

    # Description (strip HTML)
    desc = jp.get("description", "")
    if desc:
        desc_soup = BeautifulSoup(desc, "html.parser")
        result["description"] = desc_soup.get_text(separator="\n").strip()

    # Date posted
    result["date_found"] = jp.get("datePosted", "")

    return result


def _extract_linkedin_guest(job_id):
    """Extract job data from LinkedIn's guest API endpoint."""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        resp = http_requests.get(url, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        result = {}

        title_el = soup.find("h2", class_="top-card-layout__title")
        if title_el:
            result["title"] = title_el.get_text(strip=True)

        company_el = soup.find("a", class_="topcard__org-name-link")
        if not company_el:
            company_el = soup.find("span", class_="topcard__flavor")
        if company_el:
            result["company"] = company_el.get_text(strip=True)

        location_el = soup.find("span", class_="topcard__flavor--bullet")
        if location_el:
            result["location"] = location_el.get_text(strip=True)

        # Salary (LinkedIn sometimes shows it)
        salary_el = soup.find("div", class_="salary")
        if not salary_el:
            salary_el = soup.find("div", class_="compensation__salary")
        if salary_el:
            result["salary"] = salary_el.get_text(strip=True)

        desc_el = soup.find("div", class_="description__text")
        if not desc_el:
            desc_el = soup.find("div", class_="show-more-less-html__markup")
        if desc_el:
            result["description"] = desc_el.get_text(separator="\n", strip=True)

        # Posted date
        time_el = soup.find("span", class_="posted-time-ago__text")
        if time_el:
            result["date_posted_text"] = time_el.get_text(strip=True)

        # Hiring person / poster — look for profile links inside base-card
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/in/" in href and "linkedin.com" in href:
                name_span = a_tag.find("span", class_="sr-only")
                if name_span:
                    poster_name = name_span.get_text(strip=True)
                    if poster_name:
                        result["contact_name"] = poster_name
                        # Get their role/title from the card
                        parent_card = a_tag.find_parent(
                            class_=lambda c: c and "base-main-card" in c
                        )
                        if parent_card:
                            subtitle = parent_card.find(
                                class_=lambda c: c and "subtitle" in str(c)
                            )
                            if subtitle:
                                role = subtitle.get_text(strip=True)
                                result["contact_name"] = f"{poster_name} — {role}"
                        break  # Take the first profile match

        return result if result.get("title") else None
    except Exception as e:
        logger.warning(f"LinkedIn guest API failed: {e}")
        return None


def _extract_meta_tags(soup):
    """Fallback: extract job data from Open Graph and standard meta tags."""
    result = {}

    # Try og:title or <title>
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        result["title"] = og_title["content"].strip()
    elif soup.title and soup.title.string:
        # Often format: "Job Title - Company | Indeed"
        raw = soup.title.string.strip()
        # Remove trailing " | Indeed", " - LinkedIn", etc.
        raw = re.sub(r"\s*[\|–—-]\s*(Indeed|LinkedIn|Glassdoor|Reed|Totaljobs).*$", "", raw, flags=re.IGNORECASE)
        result["title"] = raw.strip()

    # og:description
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        result["description"] = og_desc["content"].strip()

    # Try to extract company from Indeed-specific meta
    company_meta = soup.find("meta", attrs={"name": "author"})
    if company_meta and company_meta.get("content"):
        result["company"] = company_meta["content"].strip()

    return result


def _extract_indeed_specific(soup, url):
    """Indeed-specific extraction from page content."""
    result = {}

    # Indeed job title
    title_el = soup.find("h1", class_=re.compile(r"jobsearch-JobInfoHeader-title"))
    if not title_el:
        title_el = soup.find("h1", attrs={"data-testid": "jobsearch-JobInfoHeader-title"})
    if title_el:
        result["title"] = title_el.get_text(strip=True)

    # Company name
    company_el = soup.find("div", attrs={"data-testid": "inlineHeader-companyName"})
    if not company_el:
        company_el = soup.find("div", attrs={"data-company-name": True})
    if company_el:
        result["company"] = company_el.get_text(strip=True)

    # Location
    loc_el = soup.find("div", attrs={"data-testid": "inlineHeader-companyLocation"})
    if not loc_el:
        loc_el = soup.find("div", attrs={"data-testid": "job-location"})
    if loc_el:
        result["location"] = loc_el.get_text(strip=True)

    # Salary
    salary_el = soup.find("div", id="salaryInfoAndJobType")
    if not salary_el:
        salary_el = soup.find("span", class_=re.compile(r"salary-snippet"))
    if salary_el:
        result["salary"] = salary_el.get_text(strip=True)

    # Description
    desc_el = soup.find("div", id="jobDescriptionText")
    if desc_el:
        result["description"] = desc_el.get_text(separator="\n", strip=True)

    return result


@bp.route("/jobs/fetch-url", methods=["POST"])
@login_required
def fetch_url():
    """POST /jobs/fetch-url — fetch job details from a URL."""
    data = request.get_json()
    url = (data or {}).get("url", "").strip()

    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400

    # Ensure URL has protocol
    if not url.startswith("http"):
        url = "https://" + url

    source = _detect_source(url)

    try:
        resp = http_requests.get(url, headers=_HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except http_requests.RequestException as e:
        logger.warning(f"fetch_url failed for {url}: {e}")
        # Still return the URL and detected source so they get populated
        partial = {"job_url": url, "source": source}
        hint = ""
        if "403" in str(e):
            hint = (
                "This site blocks automated requests. "
                "The URL and source have been set — please fill in the other details manually."
            )
        else:
            hint = f"Could not fetch URL: {e}"
        return jsonify({
            "success": False,
            "error": hint,
            "data": partial,
        })

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try extraction methods in order of reliability
    result = _extract_json_ld(soup) or {}

    # LinkedIn: use guest API for much better extraction
    if source == "linkedin" and not result.get("title"):
        job_id_match = re.search(r"/jobs/view/(\d+)", url)
        if job_id_match:
            linkedin_data = _extract_linkedin_guest(job_id_match.group(1))
            if linkedin_data:
                for k, v in linkedin_data.items():
                    if v and not result.get(k):
                        result[k] = v

    # Indeed-specific selectors as supplement/fallback
    if source == "indeed":
        indeed_data = _extract_indeed_specific(soup, url)
        for k, v in indeed_data.items():
            if v and not result.get(k):
                result[k] = v

    # Meta tag fallback for anything still missing
    meta_data = _extract_meta_tags(soup)
    for k, v in meta_data.items():
        if v and not result.get(k):
            result[k] = v

    # Always set the URL and source
    result["job_url"] = url
    result["source"] = source

    # Clean up empty strings
    result = {k: v for k, v in result.items() if v}

    if not result.get("title"):
        return jsonify({
            "success": False,
            "error": "Could not extract job title from this page. You may need to fill in the details manually.",
            "data": result,
        })

    return jsonify({"success": True, "data": result})


# ==================== JOB SEARCH (JobSpy) ====================

_SITE_MAP = {
    "indeed": "indeed",
    "linkedin": "linkedin",
    "glassdoor": "glassdoor",
    "zip_recruiter": "zip_recruiter",
    "google": "google",
}

_TIME_MAP = {
    "24h": 24,
    "3d": 72,
    "7d": 168,
    "14d": 336,
    "30d": 720,
}


@bp.route("/jobs/search", methods=["POST"])
@login_required
def search_jobs():
    """POST /jobs/search — search for jobs using JobSpy."""
    data = request.get_json() or {}
    keywords = (data.get("keywords") or "").strip()
    location = (data.get("location") or "").strip()
    sites = data.get("sites") or ["indeed", "linkedin"]
    time_range = data.get("time_range") or "7d"
    is_remote = data.get("is_remote", False)
    results_wanted = min(int(data.get("results_wanted", 25)), 50)

    if not keywords:
        return jsonify({"success": False, "error": "Search keywords are required"}), 400

    # Map site names
    valid_sites = [_SITE_MAP[s] for s in sites if s in _SITE_MAP]
    if not valid_sites:
        valid_sites = ["indeed", "linkedin"]

    hours_old = _TIME_MAP.get(time_range, 168)

    # Determine country for Indeed
    country_indeed = "UK"
    loc_lower = location.lower() if location else ""
    if any(x in loc_lower for x in ["usa", "us", "united states", "america", "new york", "california", "texas", "remote, us"]):
        country_indeed = "USA"

    # Filter out sites that don't work well for certain regions
    # ZipRecruiter is US-only
    if country_indeed == "UK" and "zip_recruiter" in valid_sites:
        logger.info("Removing zip_recruiter from UK search (US-only)")
        valid_sites = [s for s in valid_sites if s != "zip_recruiter"]
        if not valid_sites:
            valid_sites = ["indeed"]

    try:
        from jobspy import scrape_jobs

        kwargs = {
            "site_name": valid_sites,
            "search_term": keywords,
            "results_wanted": results_wanted,
            "hours_old": hours_old,
            "is_remote": is_remote,
            "country_indeed": country_indeed,
        }
        if location:
            kwargs["location"] = location

        jobs_df = scrape_jobs(**kwargs)

        # Convert DataFrame to list of dicts
        results = []
        for _, row in jobs_df.iterrows():
            # Format salary
            salary = ""
            min_amt = row.get("min_amount")
            max_amt = row.get("max_amount")
            currency = row.get("currency", "")
            interval = row.get("interval", "")
            if min_amt and max_amt and not (str(min_amt) == "nan" or str(max_amt) == "nan"):
                salary = f"{currency}{min_amt:,.0f} - {currency}{max_amt:,.0f}"
                if interval:
                    salary += f" {interval}"
            elif min_amt and str(min_amt) != "nan":
                salary = f"{currency}{min_amt:,.0f}"
                if interval:
                    salary += f" {interval}"

            # Format date
            date_posted = ""
            dp = row.get("date_posted")
            if dp and str(dp) != "NaT" and str(dp) != "nan":
                try:
                    date_posted = str(dp)[:10]
                except Exception:
                    pass

            # Use job_url_direct if available (goes straight to posting), else job_url
            primary_url = str(row.get("job_url") or "")
            direct_url = str(row.get("job_url_direct") or "")

            job = {
                "title": str(row.get("title") or ""),
                "company": str(row.get("company") or ""),
                "location": str(row.get("location") or ""),
                "salary": salary,
                "source": str(row.get("site") or ""),
                "job_url": primary_url,
                "job_url_direct": direct_url if direct_url != "None" and direct_url != "nan" else "",
                "description": str(row.get("description") or ""),
                "date_posted": date_posted,
                "is_remote": bool(row.get("is_remote")),
                "job_type": str(row.get("job_type") or ""),
                "company_industry": str(row.get("company_industry") or ""),
                "company_url": str(row.get("company_url") or ""),
                "company_num_employees": str(row.get("company_num_employees") or ""),
            }
            # Clean up "nan" strings
            for k, v in job.items():
                if v == "nan" or v == "None":
                    job[k] = ""
            results.append(job)

        logger.info(
            f"JobSpy search: '{keywords}' in '{location}' "
            f"sites={valid_sites} hours_old={hours_old} remote={is_remote} "
            f"country_indeed={country_indeed} → {len(results)} results"
        )

        return jsonify({
            "success": True,
            "data": results,
            "count": len(results),
            "query": {
                "keywords": keywords,
                "location": location,
                "sites": valid_sites,
                "hours_old": hours_old,
                "is_remote": is_remote,
                "country_indeed": country_indeed,
            },
        })

    except Exception as e:
        logger.error(f"search_jobs error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== GOOGLE SHEET SYNC ====================

# Google Sheet: "Indeed Job Feed"
# Direct export URL — works because the sheet is shared/public
_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1-SHdoCBzrHSLb9oJcUHCuMpv8SCGr8pWEIg59aRY658"
    "/export?format=csv&gid=0"
)


@bp.route("/jobs/sync-sheet", methods=["POST"])
@login_required
def sync_sheet():
    """POST /jobs/sync-sheet — import new jobs from Google Sheet CSV."""
    config = get_current_config()
    conn = get_db_connection(config)
    try:
        _ensure_jobs_table(conn)

        # Fetch CSV from Google Sheets
        resp = http_requests.get(_SHEET_CSV_URL, timeout=20)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        reader = csv.DictReader(io.StringIO(resp.text))
        if not reader.fieldnames:
            return jsonify({"success": False, "error": "Sheet appears to be empty or has no headers."})

        # Validate required column
        if "title" not in reader.fieldnames:
            return jsonify({
                "success": False,
                "error": f"Missing 'title' column. Found columns: {', '.join(reader.fieldnames)}",
            })

        # Get existing job URLs for duplicate check
        existing_urls = set()
        rows = conn.execute("SELECT job_url FROM jobs WHERE job_url IS NOT NULL").fetchall()
        for row in rows:
            if row[0]:
                existing_urls.add(row[0].strip().lower())

        imported = 0
        skipped = 0
        errors = 0

        for row in reader:
            title = (row.get("title") or "").strip()
            if not title:
                continue  # Skip blank rows

            job_url = (row.get("job_url") or "").strip()

            # Duplicate check by URL
            if job_url and job_url.lower() in existing_urls:
                skipped += 1
                continue

            try:
                conn.execute("""
                    INSERT INTO jobs (
                        source, title, company, location, salary, job_url,
                        description, status, notes, date_found, date_applied,
                        date_updated, contact_name, contact_email, follow_up_date, priority
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'saved', NULL, CURRENT_DATE, NULL,
                              CURRENT_TIMESTAMP, NULL, NULL, NULL, 'medium')
                """, [
                    (row.get("source") or "indeed").strip(),
                    title,
                    (row.get("company") or "").strip() or None,
                    (row.get("location") or "").strip() or None,
                    (row.get("salary") or "").strip() or None,
                    job_url or None,
                    (row.get("description") or "").strip() or None,
                ])
                imported += 1
                if job_url:
                    existing_urls.add(job_url.lower())
            except Exception as e:
                logger.warning(f"sync_sheet row error: {e} — row: {row}")
                errors += 1

        msg_parts = []
        if imported:
            msg_parts.append(f"{imported} new job{'s' if imported != 1 else ''} imported")
        if skipped:
            msg_parts.append(f"{skipped} duplicate{'s' if skipped != 1 else ''} skipped")
        if errors:
            msg_parts.append(f"{errors} error{'s' if errors != 1 else ''}")
        if not msg_parts:
            msg_parts.append("No new jobs found in the sheet")

        return jsonify({
            "success": True,
            "message": ". ".join(msg_parts) + ".",
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
        })

    except http_requests.RequestException as e:
        logger.error(f"sync_sheet fetch error: {e}")
        return jsonify({"success": False, "error": f"Could not fetch Google Sheet: {e}"}), 500
    except Exception as e:
        logger.error(f"sync_sheet error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()
