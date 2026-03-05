#!/usr/bin/env python3
"""
tools/generate_outreach_data.py

Generates synthetic data for the outreach system.
Tables: outreach_leads, outreach_emails, outreach_tracking_events, outreach_templates
Target: warehouse.duckdb (writable)

Run from project root:
    python tools/generate_outreach_data.py
"""

import duckdb
import uuid
import random
from datetime import datetime, timedelta, date
from pathlib import Path

random.seed(42)

WAREHOUSE_PATH = Path(__file__).parent.parent / "warehouse.duckdb"

STATUS_STAGE = {
    'cold': 1,
    'queued': 2,
    'contacted': 3,
    'followed_up': 4,
    'replied': 5,
    'meeting': 6,
    'won': 8,
    'lost': 8,
    'no_reply': 4,
}

# Maps template sequence_step -> email_type value stored on outreach_emails
FOLLOWUP_TYPE = {
    2: 'follow_up_1',
    3: 'follow_up_2',
    4: 'follow_up_3',
}

COUNTRY_TZ_DEFAULT = {
    'UK': 'GMT',
    'USA': 'EST',
    'UAE': 'GST',
    'Canada': 'EST',
    'Australia': 'AEST',
}


def gen_id():
    return str(uuid.uuid4())


def rnd_dt(start_days_ago, end_days_ago=0):
    """Return a random datetime between start_days_ago and end_days_ago from now."""
    now = datetime.now()
    start = now - timedelta(days=start_days_ago)
    end = now - timedelta(days=end_days_ago)
    diff = max(int((end - start).total_seconds()), 1)
    return start + timedelta(seconds=random.randint(0, diff))


def get_timezone(country, city_state):
    """Return timezone based on country and city/state."""
    if country == 'USA':
        if city_state and any(x in city_state for x in ['CA', 'WA', 'OR']):
            return 'PST'
        elif city_state and any(x in city_state for x in ['TX', 'IL']):
            return 'CST'
        elif city_state and any(x in city_state for x in ['CO', 'AZ']):
            return 'MST'
        return 'EST'
    return COUNTRY_TZ_DEFAULT.get(country, 'GMT')


def create_tables(conn):
    """Drop and recreate all outreach tables."""
    conn.execute("DROP TABLE IF EXISTS outreach_tracking_events")
    conn.execute("DROP TABLE IF EXISTS outreach_emails")
    conn.execute("DROP TABLE IF EXISTS outreach_leads")
    conn.execute("DROP TABLE IF EXISTS outreach_templates")

    conn.execute("""
        CREATE TABLE outreach_leads (
            lead_id         VARCHAR PRIMARY KEY,
            first_name      VARCHAR,
            last_name       VARCHAR,
            full_name       VARCHAR,
            company         VARCHAR,
            role            VARCHAR,
            email           VARCHAR,
            linkedin_url    VARCHAR,
            website         VARCHAR,
            city_state      VARCHAR,
            country         VARCHAR,
            timezone        VARCHAR,
            track           VARCHAR,
            source          VARCHAR,
            lead_type_score INTEGER,
            status          VARCHAR,
            progress_stage  INTEGER,
            notes           TEXT,
            added_date      DATE,
            last_activity   TIMESTAMP,
            sequence_step   INTEGER DEFAULT 0,
            do_not_contact  BOOLEAN DEFAULT false
        )
    """)

    conn.execute("""
        CREATE TABLE outreach_emails (
            email_id        VARCHAR PRIMARY KEY,
            lead_id         VARCHAR,
            template_id     VARCHAR,
            email_type      VARCHAR,
            subject         VARCHAR,
            body            TEXT,
            status          VARCHAR,
            cv_attached     BOOLEAN DEFAULT false,
            sent_at         TIMESTAMP,
            scheduled_at    TIMESTAMP,
            tracking_id     VARCHAR UNIQUE,
            opened_at       TIMESTAMP,
            open_count      INTEGER DEFAULT 0,
            clicked_at      TIMESTAMP,
            click_count     INTEGER DEFAULT 0,
            cv_opened_at    TIMESTAMP,
            cv_open_count   INTEGER DEFAULT 0,
            reply_received  BOOLEAN DEFAULT false,
            reply_read      BOOLEAN DEFAULT false,
            reply_at        TIMESTAMP,
            reply_text      TEXT,
            followup_due    DATE,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE outreach_tracking_events (
            event_id        VARCHAR PRIMARY KEY,
            tracking_id     VARCHAR,
            event_type      VARCHAR,
            event_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address      VARCHAR,
            user_agent      VARCHAR,
            click_url       VARCHAR
        )
    """)

    conn.execute("""
        CREATE TABLE outreach_templates (
            template_id         VARCHAR PRIMARY KEY,
            name                VARCHAR,
            email_type          VARCHAR,
            sequence_step       INTEGER,
            subject             VARCHAR,
            body                TEXT,
            send_delay_days     INTEGER,
            cv_attached_default BOOLEAN,
            times_sent          INTEGER DEFAULT 0,
            times_replied       INTEGER DEFAULT 0,
            active              BOOLEAN DEFAULT true,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  Tables created (dropped and recreated)")


def insert_templates(conn):
    """Insert 4 email sequence templates."""
    body1 = (
        "Hi {first_name},\n\n"
        "I'm a Google Ads specialist with 16 years of hands-on experience managing over £50M in ad spend "
        "across 200+ accounts — and I'm currently looking for my next opportunity.\n\n"
        "I specialise in Search, Shopping and Performance Max across both B2B lead gen and ecommerce. "
        "Most recently I've built Ads Control Tower — a proprietary AI-powered platform that automates "
        "Google Ads optimisation.\n\n"
        "I've attached my CV and you can see more at christopherhoole.online.\n\n"
        "Would love to connect if you have any relevant roles or opportunities.\n\n"
        "Best regards,\nChristopher Hoole\n+44 7999 500 184"
    )

    body2 = (
        "Hi {first_name},\n\n"
        "Just a quick follow-up to my email last week — wanted to make sure it didn't get buried in your inbox.\n\n"
        "I'm still actively looking for my next contract or permanent role in Google Ads. With 16 years of "
        "hands-on experience and £50M+ managed, I'm confident I can add real value.\n\n"
        "Happy to send over more details or jump on a call whenever suits.\n\n"
        "Christopher"
    )

    body3 = (
        "Hi {first_name},\n\n"
        "I wanted to reach out one more time in case my previous emails got lost.\n\n"
        "I'm a Google Ads specialist with 16 years' experience — Search, Shopping, Performance Max — "
        "currently available for contract or permanent roles. I've managed £50M+ across 200+ accounts.\n\n"
        "If there's ever a good time to chat, I'd love to hear from you.\n\n"
        "Christopher"
    )

    body4 = (
        "Hi {first_name},\n\n"
        "This will be my last email — I don't want to be a nuisance!\n\n"
        "If you're ever looking for a senior Google Ads specialist in the future, I'd love to hear from you. "
        "My profile is at christopherhoole.online.\n\n"
        "Thanks for your time.\nChristopher Hoole"
    )

    templates = [
        (gen_id(), "Initial Outreach",  "initial",     1,
         "Google Ads Specialist — 16 Years Experience, Available Now", body1, 0,  True),
        (gen_id(), "Follow-up 1",       "follow_up_1", 2,
         "Re: Google Ads Specialist — 16 Years Experience",            body2, 5,  False),
        (gen_id(), "Follow-up 2",       "follow_up_2", 3,
         "Re: Google Ads Specialist — 16 Years Experience",            body3, 7,  False),
        (gen_id(), "Final Message",     "follow_up_3", 4,
         "Re: Google Ads Specialist — Last message",                   body4, 7,  False),
    ]

    for t in templates:
        conn.execute(
            """INSERT INTO outreach_templates
               (template_id, name, email_type, sequence_step, subject, body,
                send_delay_days, cv_attached_default, times_sent, times_replied,
                active, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,0,0,true,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)""",
            list(t)
        )
    print(f"  Templates: {len(templates)} rows")
    return templates


def insert_leads(conn):
    """Insert leads with correct status distribution."""
    # Columns: first, last, company, role, email, linkedin, website, city_state, country, track, source, score, status, notes
    leads_raw = [
        # ── AGENCY ──────────────────────────────────────────────────────────────────────────────
        ("James",    "Thornton",    "PPC Masters Ltd",          "Managing Director",
         "james@ppcmasters.co.uk",               "linkedin.com/in/jamesthornton",
         "ppcmasters.co.uk",          "London",            "UK",        "Agency",    "Apollo", 5, "cold",        ""),
        ("Emma",     "Watson",      "Digital Pulse Agency",     "Head of PPC",
         "emma@digitalpulse.com",                "linkedin.com/in/emmawatson-ppc",
         "digitalpulse.com",          "Manchester",        "UK",        "Agency",    "Apollo", 5, "contacted",   "Sent initial email. No response yet."),
        ("Oliver",   "Davis",       "SearchFirst Ltd",          "Director",
         "oliver@searchfirst.co.uk",             "linkedin.com/in/oliverdavis",
         "searchfirst.co.uk",         "Birmingham",        "UK",        "Agency",    "Apollo", 5, "followed_up", "Followed up twice. Opened email but no reply."),
        ("Chris",    "Lee",         "Ignite Growth Agency",     "VP Marketing",
         "chris@ignitegrowth.com",               "linkedin.com/in/chrislee-marketing",
         "ignitegrowth.com",          "San Francisco, CA", "USA",       "Agency",    "Apollo", 3, "contacted",   ""),
        ("Lisa",     "Sanchez",     "Rocket PPC",               "Founder",
         "lisa@rocketppc.com",                   "linkedin.com/in/lisasanchez",
         "rocketppc.com",             "Houston, TX",       "USA",       "Agency",    "Apollo", 3, "meeting",     "Meeting booked for 15 Mar. Very positive!"),
        ("Mark",     "Johnson",     "Blue Sky Digital",         "Head of PPC",
         "mark@blueskydigital.com",              "linkedin.com/in/markjohnson-ppc",
         "blueskydigital.com",        "Chicago, IL",       "USA",       "Agency",    "Apollo", 5, "cold",        ""),
        ("Pierre",   "Leblanc",     "Maple Leaf Media",         "Founder",
         "pierre@mapleleafmedia.ca",             "linkedin.com/in/pierreeleblanc",
         "mapleleafmedia.ca",         "Montreal, QC",      "Canada",    "Agency",    "Apollo", 3, "followed_up", ""),
        ("Ryan",     "Fletcher",    "Harbour Digital",          "Managing Director",
         "ryan@harbourdigital.com.au",           "linkedin.com/in/ryanfletcher",
         "harbourdigital.com.au",     "Melbourne",         "Australia", "Agency",    "Apollo", 5, "cold",        ""),
        ("Alex",     "Dupont",      "North Star Marketing",     "Director",
         "alex@northstarmarketing.ca",           "linkedin.com/in/alexdupont",
         "northstarmarketing.ca",     "Toronto, ON",       "Canada",    "Agency",    "Apollo", 5, "queued",      ""),
        ("Emma",     "Roberts",     "Velocity Digital",         "CEO",
         "emma@velocitydigital.co.uk",           "linkedin.com/in/emmaroberts-dig",
         "velocitydigital.co.uk",     "Bristol",           "UK",        "Agency",    "Apollo", 3, "no_reply",    "Sent 2 emails, opened both but no reply."),
        ("Rachel",   "Chen",        "Grow Digital",             "CEO",
         "rachel@growdigital.com",               "linkedin.com/in/rachelchen",
         "growdigital.com",           "Los Angeles, CA",   "USA",       "Agency",    "Apollo", 3, "replied",     "Replied positively. Interested in freelance PPC."),
        ("Tom",      "Clarke",      "Apex Digital Solutions",   "CEO",
         "tom@apexdigital.co.uk",                "linkedin.com/in/tomclarke-apex",
         "apexdigital.co.uk",         "Birmingham",        "UK",        "Agency",    "Manual", 5, "meeting",     "In-person meeting planned for 20 Mar."),
        ("Sarah",    "Hall",        "Click Depot",              "Director",
         "sarah@clickdepot.com",                 "linkedin.com/in/sarahhall-ppc",
         "clickdepot.com",            "New York, NY",      "USA",       "Agency",    "Apollo", 5, "contacted",   ""),
        ("Ben",      "Adams",       "Pulse Digital",            "Head of Paid Media",
         "ben@pulsedigital.co.uk",               "linkedin.com/in/benadams-paid",
         "pulsedigital.co.uk",        "London",            "UK",        "Agency",    "Apollo", 5, "followed_up", ""),
        ("Caroline", "Hughes",      "TechScale Agency",         "Managing Director",
         "caroline@techscale.co.uk",             "linkedin.com/in/carolinehughes",
         "techscale.co.uk",           "London",            "UK",        "Agency",    "Apollo", 5, "followed_up", ""),
        # Agency — replied
        ("Natasha",  "Brooks",      "Bloom Digital",            "Director",
         "natasha@bloomdigital.co.uk",           "linkedin.com/in/natashabrooks",
         "bloomdigital.co.uk",        "London",            "UK",        "Agency",    "Apollo", 4, "replied",     "Replied asking about contract vs perm preference."),
        ("Dominic",  "Walsh",       "ClickPath Agency",         "Head of PPC",
         "dominic@clickpathagency.com",          "linkedin.com/in/dominicwalsh-ppc",
         "clickpathagency.com",       "Denver, CO",        "USA",       "Agency",    "Apollo", 4, "replied",     "Open to project-based work. New ecommerce client onboarding."),
        ("Amy",      "Thornton",    "Peak Performance Media",   "Managing Director",
         "amy@peakperformancemedia.com.au",      "linkedin.com/in/amythornton-ppmc",
         "peakperformancemedia.com.au","Melbourne",        "Australia", "Agency",    "Apollo", 4, "replied",     "Interested. Asked about remote work arrangement."),
        ("Marcus",   "Reid",        "BrightEdge Digital",       "VP Digital",
         "marcus@brightedgedigital.ca",          "linkedin.com/in/marcusreid-digital",
         "brightedgedigital.ca",      "Toronto, ON",       "Canada",    "Agency",    "Apollo", 4, "replied",     "Keen to discuss. Performance Max experience relevant."),
        ("Elena",    "Vasquez",     "Digiboost Agency",         "CEO",
         "elena@digiboostagency.com",            "linkedin.com/in/elenavasquez-digi",
         "digiboostagency.com",       "Miami, FL",         "USA",       "Agency",    "Apollo", 3, "replied",     "Asked for day rate. Mostly contract engagements."),
        ("Kevin",    "O'Brien",     "MediaFirst",               "Director",
         "kevin@mediafirst.ie",                  "linkedin.com/in/kevinobrien-media",
         "mediafirst.ie",             "Dublin",            "UK",        "Agency",    "Apollo", 4, "replied",     "Has enterprise SaaS client needing Google Ads support."),
        ("Yuki",     "Tanaka",      "Pacific Digital",          "Head of Paid",
         "yuki@pacificdigital.com.au",           "linkedin.com/in/yukitanaka-paid",
         "pacificdigital.com.au",     "Sydney",            "Australia", "Agency",    "Apollo", 4, "replied",     "Specialises in ecommerce. Asked about AEST hours."),
        ("Laura",    "Fitzgerald",  "Redline Agency",           "Managing Director",
         "laura@redlineagency.co.uk",            "linkedin.com/in/laurafitzgerald-rl",
         "redlineagency.co.uk",       "Edinburgh",         "UK",        "Agency",    "Apollo", 5, "replied",     "Looking for senior PPC resource. Will loop in next week."),
        # Agency — meeting
        ("Jorge",    "Ramirez",     "TurboAds Agency",          "CEO",
         "jorge@turboadsagency.com",             "linkedin.com/in/jorgeramirez-turbo",
         "turboadsagency.com",        "New York, NY",      "USA",       "Agency",    "Apollo", 5, "meeting",     "Call booked Wednesday 10am EST. DTC ecommerce focus."),
        ("Nadia",    "Petrov",      "Eastern Growth Partners",  "Director",
         "nadia@easterngrowth.ae",               "linkedin.com/in/nadiapetrov-egp",
         "easterngrowth.ae",          "Dubai",             "UAE",       "Agency",    "Apollo", 5, "meeting",     "Meeting next week Mon/Tue. Expanding across Middle East."),
        ("Felix",    "Hoffmann",    "EuroDigital GmbH",         "Managing Director",
         "felix@eurodigital.de",                 "linkedin.com/in/felixhoffmann-ed",
         "eurodigital.de",            "London",            "UK",        "Agency",    "Apollo", 5, "meeting",     "Call later this week. B2B SaaS clients Germany and UK."),
        # Agency — won
        ("Thomas",   "Grant",       "GrantMedia Agency",        "CEO",
         "thomas@grantmediaagency.co.uk",        "linkedin.com/in/thomasgrant-gma",
         "grantmediaagency.co.uk",    "Manchester",        "UK",        "Agency",    "Manual", 5, "won",         "Contract won. Scaling PPC team. Start in April."),
        ("Lena",     "Fischer",     "DigitalEurope AG",         "Head of PPC",
         "lena@digitaleurope.ca",                "linkedin.com/in/lenafischer-de",
         "digitaleurope.ca",          "Vancouver, BC",     "Canada",    "Agency",    "Apollo", 5, "won",         "Won. 3 new ecommerce clients starting next month."),
        # ── RECRUITER ───────────────────────────────────────────────────────────────────────────
        ("Sarah",    "Mitchell",    "Digital Talent Group",     "Head of Recruitment",
         "sarah@digitaltalentgroup.com",         "linkedin.com/in/sarahmitchell",
         "digitaltalentgroup.com",    "New York, NY",      "USA",       "Recruiter", "Apollo", 4, "replied",
         "Replied quickly — seems genuinely interested. Mentioned 2 live roles (fintech NYC contract + DTC ecommerce Austin perm). Follow up after weekend to book call."),
        ("Michael",  "Brown",       "Hays Digital",             "Senior Consultant",
         "m.brown@hays.com",                     "linkedin.com/in/michaelbrown-hays",
         "hays.com",                  "Manchester",        "UK",        "Recruiter", "Manual", 2, "cold",        ""),
        ("Jessica",  "Wong",        "Talent Digital AU",        "Senior Recruiter",
         "jessica@talentdigitalau.com",          "linkedin.com/in/jessicawong-recruit",
         "talentdigitalau.com",       "Sydney",            "Australia", "Recruiter", "Apollo", 4, "contacted",   ""),
        ("David",    "Kim",         "TalentBridge USA",         "Partner",
         "david@talentbridgeusa.com",            "linkedin.com/in/davidkim-talent",
         "talentbridgeusa.com",       "Seattle, WA",       "USA",       "Recruiter", "Apollo", 2, "cold",        ""),
        ("Hannah",   "Clarke",      "Reed Digital",             "Recruitment Consultant",
         "h.clarke@reed.co.uk",                  "linkedin.com/in/hannahclarke-reed",
         "reed.co.uk",                "London",            "UK",        "Recruiter", "Apollo", 2, "replied",
         "Positive reply. Has a PPC manager role at a fintech startup."),
        ("Sophie",   "Martin",      "Peak Talent Group",        "Director",
         "sophie@peaktalentgroup.ca",            "linkedin.com/in/sophiemartin-talent",
         "peaktalentgroup.ca",        "Vancouver, BC",     "Canada",    "Recruiter", "Apollo", 4, "followed_up", ""),
        ("James",    "Cooper",      "Robert Half",              "Account Manager",
         "j.cooper@roberthalf.com",              "linkedin.com/in/jamescooper-rh",
         "roberthalf.com",            "New York, NY",      "USA",       "Recruiter", "Apollo", 2, "contacted",   ""),
        ("Victoria", "Osei",        "Heidrick & Struggles",     "Partner",
         "v.osei@heidrick.com",                  "linkedin.com/in/victoriaosei",
         "heidrick.com",              "Dubai",             "UAE",       "Recruiter", "Apollo", 4, "queued",      ""),
        # Recruiter — replied
        ("Charlotte","Webb",        "Clearway Media",           "Recruitment Manager",
         "charlotte@clearwaymedia.co.uk",        "linkedin.com/in/charlottewebb-cm",
         "clearwaymedia.co.uk",       "London",            "UK",        "Recruiter", "Apollo", 4, "replied",     "Has contract and perm PPC roles. Asked for 15-min call."),
        ("Ethan",    "Morgan",      "TalentSphere USA",         "Senior Consultant",
         "ethan@talentsphereusa.com",            "linkedin.com/in/ethanmorgan-ts",
         "talentsphereusa.com",       "Austin, TX",        "USA",       "Recruiter", "Apollo", 3, "replied",     "Has clients looking for senior Google Ads expertise."),
        ("Isabelle", "Laurent",     "Paris Digital Recruits",   "Director",
         "isabelle@parisdigitalrecruits.com",    "linkedin.com/in/isabellelaurent-pdr",
         "parisdigitalrecruits.com",  "Dubai",             "UAE",       "Recruiter", "Apollo", 4, "replied",     "Places specialists across GCC and Europe. Wants CV + rate card."),
        # Recruiter — meeting
        ("Chloe",    "Beaumont",    "Prestige Recruit",         "Head of Technology",
         "chloe@prestigerecruit.co.uk",          "linkedin.com/in/chloebeaumont-pr",
         "prestigerecruit.co.uk",     "London",            "UK",        "Recruiter", "Apollo", 5, "meeting",     "Call booked Thursday 3pm. Multiple tech clients hiring."),
        ("Amara",    "Diallo",      "Westfield Talent",         "Senior Consultant",
         "amara@westfieldtalent.com",            "linkedin.com/in/amaradiallo-wt",
         "westfieldtalent.com",       "New York, NY",      "USA",       "Recruiter", "Apollo", 5, "meeting",     "30-min call arranged. Fintech client growing fast, needs PPC."),
        # ── DIRECT ──────────────────────────────────────────────────────────────────────────────
        ("Fatima",   "Al-Mansoori", "Emirates Growth Co",       "Managing Director",
         "fatima@emiratesgrowth.ae",             "linkedin.com/in/fatimamansoori",
         "emiratesgrowth.ae",         "Dubai",             "UAE",       "Direct",    "Manual", 5, "replied",
         "Very warm response. Has £500k/mo budget across GCC. Looking for freelance Google Ads specialist."),
        ("William",  "Hartley",     "Sterling Commerce",        "Chief Marketing Officer",
         "w.hartley@sterlingcommerce.co.uk",     "linkedin.com/in/williamhartley",
         "sterlingcommerce.co.uk",    "London",            "UK",        "Direct",    "Manual", 5, "cold",        ""),
        ("Jennifer", "Park",        "Conversion Lab",           "Marketing Director",
         "jennifer@conversionlab.io",            "linkedin.com/in/jenniferpark",
         "conversionlab.io",          "Denver, CO",        "USA",       "Direct",    "Manual", 3, "contacted",   ""),
        ("Khalid",   "Al-Rashid",   "Gulf Media Group",         "Chief Marketing Officer",
         "khalid@gulfmediagroup.ae",             "linkedin.com/in/khalidalrashid",
         "gulfmediagroup.ae",         "Dubai",             "UAE",       "Direct",    "Manual", 5, "won",
         "Contract won. Starting April. Budget £30k/mo."),
        # Direct — replied
        ("Priya",    "Sharma",      "Growthify Digital",        "Marketing Director",
         "priya@growthifydigital.co.uk",         "linkedin.com/in/priyasharma-gd",
         "growthifydigital.co.uk",    "London",            "UK",        "Direct",    "Manual", 5, "replied",     "Burning through Google Ads budget. Wants specialist urgently."),
        ("Connor",   "Davis",       "Adcelerate",               "Founder",
         "connor@adcelerate.io",                 "linkedin.com/in/connordavis-acc",
         "adcelerate.io",             "Austin, TX",        "USA",       "Direct",    "Manual", 4, "replied",     "DTC brand. Considering freelance arrangement to start."),
        ("Mei",      "Lin",         "Dragon Digital",           "Head of Marketing",
         "mei@dragondigital.co.uk",              "linkedin.com/in/meilin-dd",
         "dragondigital.co.uk",       "London",            "UK",        "Direct",    "Manual", 4, "replied",     "Growing brand spending heavily on Google Ads. Wants specialist."),
        ("Aditya",   "Patel",       "GrowthForge",              "Chief Marketing Officer",
         "aditya@growthforge.ae",                "linkedin.com/in/aditypatel-gf",
         "growthforge.ae",            "Dubai",             "UAE",       "Direct",    "Manual", 5, "replied",     "Scaling across UAE. Asked for call Thursday."),
        # Direct — meeting
        ("Sam",      "Okafor",      "Lagos Digital",            "Founder",
         "sam@lagosdigital.co.uk",               "linkedin.com/in/samokafor-ld",
         "lagosdigital.co.uk",        "London",            "UK",        "Direct",    "Manual", 4, "meeting",     "Google Ads audit and rebuild. Budget £15k/mo. Call arranged."),
        ("Haruto",   "Nakamura",    "Summit Media JP",          "Director",
         "haruto@summitmediajp.com",             "linkedin.com/in/harutonakamura-sm",
         "summitmediajp.com",         "London",            "UK",        "Direct",    "Manual", 5, "meeting",     "Pan-Asian campaigns. Zoom call booked Friday."),
        # Direct — won
        ("Divya",    "Menon",       "VentureAds",               "VP Marketing",
         "divya@ventureads.ae",                  "linkedin.com/in/divyamenon-va",
         "ventureads.ae",             "Dubai",             "UAE",       "Direct",    "Manual", 5, "won",         "Won. Accounts across UAE and India. 3-month contract, strong rate."),
        ("Dana",     "Kowalski",    "PrecisionPPC",             "Marketing Director",
         "dana@precisionppc.com",                "linkedin.com/in/danakowalski-pppc",
         "precisionppc.com",          "Chicago, IL",       "USA",       "Direct",    "Manual", 5, "won",         "Won. Contract role, previous agency underperformed on Google Ads."),
        # ── JOB ─────────────────────────────────────────────────────────────────────────────────
        ("",         "",            "Greenfield Marketing",     "Hiring Manager",
         "jobs@greenfieldmarketing.co.uk",       "",
         "greenfieldmarketing.co.uk", "Leeds",             "UK",        "Job",       "Indeed", 1, "cold",
         "Google Ads Manager role posted on Indeed."),
        ("",         "",            "Performance Media Inc",    "Hiring Manager",
         "careers@performancemedia.com",         "",
         "performancemedia.com",      "Miami, FL",         "USA",       "Job",       "Indeed", 1, "queued",
         "PPC Specialist contract role."),
        ("",         "",            "Adcentric UK",             "Hiring Manager",
         "careers@adcentric.co.uk",              "",
         "adcentric.co.uk",           "London",            "UK",        "Job",       "Indeed", 1, "cold",
         "Google Ads Specialist role, permanent."),
    ]

    # Show distribution (no hard assert — total grows as we add leads)
    dist = {}
    for row in leads_raw:
        s = row[12]
        dist[s] = dist.get(s, 0) + 1
    print(f"  Status distribution: {dist}")
    print(f"  Total leads: {sum(dist.values())}")
    replied_total = dist.get('replied', 0) + dist.get('meeting', 0) + dist.get('won', 0)
    print(f"  Replies-page leads (replied+meeting+won): {replied_total}")

    now = datetime.now()
    leads_out = []

    for row in leads_raw:
        first, last, company, role, email, linkedin, website, city_state, country, track, source, score, status, notes = row
        full_name = f"{first} {last}".strip()
        tz = get_timezone(country, city_state)
        stage = STATUS_STAGE.get(status, 1)
        added_days_ago = random.randint(3, 45)
        added_dt = now - timedelta(days=added_days_ago)
        added_date = added_dt.date()
        last_activity = now - timedelta(days=random.randint(0, max(added_days_ago - 1, 1)))
        lead_id = gen_id()

        conn.execute(
            """INSERT INTO outreach_leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [lead_id, first, last, full_name, company, role, email,
             linkedin, website, city_state, country, tz, track, source,
             score, status, stage, notes,
             added_date, last_activity, 0, False]
        )

        leads_out.append({
            'lead_id':     lead_id,
            'first_name':  first,
            'last_name':   last,
            'full_name':   full_name,
            'company':     company,
            'role':        role,
            'email':       email,
            'city_state':  city_state,
            'country':     country,
            'timezone':    tz,
            'track':       track,
            'source':      source,
            'score':       score,
            'status':      status,
            'stage':       stage,
            'notes':       notes,
            'added_date':  added_date,
        })

    print(f"  Leads: {len(leads_out)} rows")
    return leads_out


def insert_emails(conn, leads):
    """Insert emails consistent with lead statuses."""
    rows = conn.execute(
        "SELECT template_id, sequence_step, subject, body FROM outreach_templates ORDER BY sequence_step"
    ).fetchall()
    templates = {r[1]: (r[0], r[2], r[3]) for r in rows}

    def tmpl(step):
        return templates[step]  # (template_id, subject, body)

    # Unique reply texts keyed by full_name (replied + meeting + won leads)
    reply_texts = {
        # ── EXISTING REPLIED ────────────────────────────────────────────────────────────────────
        'Sarah Mitchell': (
            "Hi Christopher,\n\nThanks for reaching out. We do have a couple of Google Ads roles on right now — "
            "one is a 6-month contract with a fintech company in NYC, and the other is a permanent role at a DTC "
            "ecommerce brand in Austin.\n\nWould you be open to a quick call this week to discuss? "
            "I'm free Thursday or Friday afternoon.\n\nBest,\nSarah"
        ),
        'Hannah Clarke': (
            "Hi Christopher,\n\nThanks for your email. I do have a Google Ads Manager role at a fintech startup "
            "that might be a great fit — they're looking for someone with strong Shopping experience.\n\n"
            "Would you be free for a 20-minute call later this week?\n\nBest,\nHannah"
        ),
        'Rachel Chen': (
            "Hi Christopher,\n\nGreat to hear from you. We're actually in the process of bringing our Google Ads "
            "in-house and would love to chat with you about a potential freelance arrangement while we get set up.\n\n"
            "Are you available for a call next week?\n\nRachel"
        ),
        'Fatima Al-Mansoori': (
            "Hi Christopher,\n\nExcellent timing — we're looking for a Google Ads specialist to manage our GCC "
            "campaigns across Search and Shopping. Budget is around £30k/month.\n\nCan you send your rate card "
            "and availability?\n\nFatima"
        ),
        # ── NEW REPLIED (Agency) ─────────────────────────────────────────────────────────────────
        'Natasha Brooks': (
            "Hi Christopher,\n\nThanks for reaching out. We're always on the lookout for strong PPC talent. "
            "I'd love to hear more about what you're looking for — contract or perm?\n\nBest,\nNatasha"
        ),
        'Dominic Walsh': (
            "Hi Christopher,\n\nGreat timing — we're about to onboard a new ecommerce client and could use some "
            "extra firepower on the Google Ads side. Are you open to project-based work?\n\nDom"
        ),
        'Amy Thornton': (
            "Hi Christopher,\n\nThanks for your email. Your CV looks impressive — 16 years is serious experience. "
            "We're based in Melbourne but a lot of our work is remote.\n\n"
            "Could you let me know your preferred working arrangement?\n\nAmy"
        ),
        'Marcus Reid': (
            "Hi Christopher,\n\nWe're actively building out our PPC team here at BrightEdge. "
            "Your background with Performance Max is particularly interesting.\n\n"
            "Are you open to a short video call this week?\n\nMarcus"
        ),
        'Elena Vasquez': (
            "Hi Christopher,\n\nWe've been looking for a senior Google Ads person for a while — "
            "most candidates don't have the depth of experience you're describing.\n\n"
            "Can you share your day rate? We mostly do contract engagements.\n\nElena"
        ),
        "Kevin O'Brien": (
            "Hi Christopher,\n\nGreat to hear from you — your profile looks strong. We have an enterprise SaaS "
            "client who needs dedicated Google Ads support. Based in Dublin but happy to work remotely.\n\nKev"
        ),
        'Yuki Tanaka': (
            "Hi Christopher,\n\nThanks for reaching out. We specialise in ecommerce clients and your Shopping "
            "experience is very relevant. Are you able to work Australian business hours, even partially?\n\nYuki"
        ),
        'Laura Fitzgerald': (
            "Hi Christopher,\n\nI was just talking to a colleague about finding senior PPC resource. "
            "Your background looks exactly right.\n\nI'll loop you into our next availability conversation — "
            "can you share what you're looking for in terms of engagement type?\n\nLaura"
        ),
        # ── NEW REPLIED (Recruiter) ──────────────────────────────────────────────────────────────
        'Charlotte Webb': (
            "Hi Christopher,\n\nThanks for your message. We have a couple of senior PPC roles I'm working on "
            "right now — one contract and one perm. Your experience level fits both perfectly.\n\n"
            "Are you available for a quick 15-minute call?\n\nCharlotte"
        ),
        'Ethan Morgan': (
            "Hi Christopher,\n\nGreat profile — 16 years of Google Ads is rare. "
            "I've got a couple of clients actively searching for that level of expertise.\n\n"
            "I'll reach out once I have more details on the roles. Mind if I connect on LinkedIn too?\n\nEthan"
        ),
        'Isabelle Laurent': (
            "Hi Christopher,\n\nYour email came at the right time. We place digital marketing specialists "
            "across the GCC and Europe. There's strong demand for Google Ads expertise right now.\n\n"
            "Could you send your CV and rate card?\n\nIsabelle"
        ),
        # ── NEW REPLIED (Direct) ─────────────────────────────────────────────────────────────────
        'Priya Sharma': (
            "Hi Christopher,\n\nExcellent — we're actually in the market right now. We've been burning through "
            "budget on Google Ads without great results and we need someone who really knows what they're doing.\n\n"
            "Would love to chat this week if you're free.\n\nPriya"
        ),
        'Connor Davis': (
            "Hi Christopher,\n\nWe're a scrappy DTC brand and our Google Ads performance has been all over the "
            "place. We've been managing in-house but I think we need a proper specialist.\n\n"
            "Would you be open to a freelance arrangement to start?\n\nConnor"
        ),
        'Mei Lin': (
            "Hi Christopher,\n\nThanks for your email. We're a growing digital brand and have been spending "
            "heavily on Google Ads without the results we'd expect.\n\n"
            "I'd like to understand more about how you work — do you have capacity right now?\n\nMei"
        ),
        'Aditya Patel': (
            "Hi Christopher,\n\nVery timely email. We're scaling rapidly across the UAE and need experienced "
            "hands on our Google Ads accounts.\n\nLet's get on a call this week — are you free Thursday?\n\nAditya"
        ),
        # ── EXISTING MEETING ─────────────────────────────────────────────────────────────────────
        'Lisa Sanchez': (
            "Hi Christopher,\n\nThanks for the email — your experience looks exactly like what we need right now. "
            "We're growing fast and need someone who knows Google Ads inside out.\n\n"
            "I've got a slot open Wednesday at 2pm CST. Does that work for you?\n\nLisa"
        ),
        'Tom Clarke': (
            "Hi Christopher,\n\nGreat to hear from you. We've got a couple of Google Ads clients who need some "
            "serious attention and I think you could be a great fit.\n\n"
            "Would you be up for an in-person chat in Birmingham? Week of 20 Mar works for me.\n\nTom"
        ),
        # ── NEW MEETING (Agency) ─────────────────────────────────────────────────────────────────
        'Jorge Ramirez': (
            "Hi Christopher,\n\nYour email really stood out. We manage a lot of DTC brands and Google Ads "
            "is the core of our media mix.\n\nI'd love to set up a call — I've got a slot open Wednesday "
            "10am EST. Does that work?\n\nJorge"
        ),
        'Nadia Petrov': (
            "Hi Christopher,\n\nThank you for reaching out. We're expanding our digital offering across the "
            "Middle East and your experience managing large budgets is exactly what we need.\n\n"
            "Can we book a call for next week? I'm mostly free Monday and Tuesday.\n\nNadia"
        ),
        'Felix Hoffmann': (
            "Hi Christopher,\n\nYour profile is impressive — we work with B2B SaaS clients in Germany and "
            "the UK and we're always looking for senior Google Ads expertise.\n\n"
            "Can we arrange a call later this week?\n\nFelix"
        ),
        # ── NEW MEETING (Recruiter) ──────────────────────────────────────────────────────────────
        'Chloe Beaumont': (
            "Hi Christopher,\n\nThanks for your email. I have several tech companies on my books right now "
            "who are actively looking for senior PPC talent.\n\n"
            "I've pencilled in a call for Thursday at 3pm — does that suit?\n\nChloe"
        ),
        'Amara Diallo': (
            "Hi Christopher,\n\nI've been looking for someone with your level of Google Ads experience for "
            "one of my fintech clients. They're growing fast and need serious PPC firepower.\n\n"
            "I'll send over the full brief — are you free for a 30-minute call?\n\nAmara"
        ),
        # ── NEW MEETING (Direct) ─────────────────────────────────────────────────────────────────
        'Sam Okafor': (
            "Hi Christopher,\n\nGreat timing — we're looking for someone to audit and rebuild our Google Ads "
            "setup. Budget is around £15k/month but we know we're not getting the most from it.\n\n"
            "Would love a call to walk you through the account.\n\nSam"
        ),
        'Haruto Nakamura': (
            "Hi Christopher,\n\nThank you for getting in touch. We run pan-Asian campaigns across several "
            "markets and need senior Google Ads oversight.\n\n"
            "Would you be available for a Zoom call this Friday?\n\nHaruto"
        ),
        # ── EXISTING WON ────────────────────────────────────────────────────────────────────────
        'Khalid Al-Rashid': (
            "Hi Christopher,\n\nImpressive background — exactly the expertise we're looking for. "
            "Our GCC campaigns are underperforming and we need someone with your level of experience.\n\n"
            "Let's arrange a call early next week. I can offer a competitive rate for the right person.\n\nKhalid"
        ),
        # ── NEW WON (Agency) ────────────────────────────────────────────────────────────────────
        'Thomas Grant': (
            "Hi Christopher,\n\nYour profile is exactly what we need. I've been managing Google Ads for "
            "our clients but we're scaling too fast to keep it in-house.\n\n"
            "I'd like to explore bringing you on as our dedicated PPC specialist. When can we talk?\n\nThomas"
        ),
        'Lena Fischer': (
            "Hi Christopher,\n\nFantastic timing. We're onboarding three new ecommerce clients next month "
            "and need someone who can handle their Google Ads properly.\n\n"
            "Would you be available to start in early April on a contract basis?\n\nLena"
        ),
        # ── NEW WON (Direct) ────────────────────────────────────────────────────────────────────
        'Divya Menon': (
            "Hi Christopher,\n\nExcellent profile! We have accounts across the UAE and India that need "
            "serious restructuring.\n\nLet's arrange a call — I can offer an initial 3-month contract "
            "with strong rates.\n\nDivya"
        ),
        'Dana Kowalski': (
            "Hi Christopher,\n\nYour experience speaks for itself. We've been badly burned by agencies "
            "who overpromise and underdeliver on Google Ads.\n\n"
            "I'd love to bring someone in on a contract. What's your availability and rate?\n\nDana"
        ),
    }

    emails_out = []

    def insert_email(lead_id, tmpl_step, email_type, status,
                     cv_attached=False, sent_at=None, scheduled_at=None,
                     open_count=0, reply_received=False, reply_read=False,
                     reply_at=None, reply_text=None, followup_due=None,
                     greeting='there'):
        tid, subj, body_tmpl = tmpl(tmpl_step)
        body = body_tmpl.replace('{first_name}', greeting)
        e_id = gen_id()
        tracking_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO outreach_emails
               (email_id, lead_id, template_id, email_type, subject, body, status,
                cv_attached, sent_at, scheduled_at, tracking_id, open_count,
                reply_received, reply_read, reply_at, reply_text, followup_due)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [e_id, lead_id, tid, email_type, subj, body, status,
             cv_attached, sent_at, scheduled_at, tracking_id, open_count,
             reply_received, reply_read, reply_at, reply_text, followup_due]
        )
        emails_out.append({'email_id': e_id, 'tracking_id': tracking_id,
                           'status': status, 'lead_id': lead_id})
        return e_id, tracking_id

    now = datetime.now()

    for lead in leads:
        lid      = lead['lead_id']
        status   = lead['status']
        greeting = lead['first_name'] or 'there'
        full_name = lead['full_name']

        if status == 'cold':
            pass  # No emails

        elif status == 'queued':
            sched = now + timedelta(days=random.randint(1, 3), hours=random.randint(7, 10))
            insert_email(lid, 1, 'initial', 'queued', cv_attached=True,
                         scheduled_at=sched,
                         followup_due=(sched + timedelta(days=5)).date(),
                         greeting=greeting)

        elif status == 'contacted':
            sent = rnd_dt(14, 3)
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent, open_count=random.choice([0, 1, 2]),
                         followup_due=(sent + timedelta(days=5)).date(),
                         greeting=greeting)

        elif status == 'followed_up':
            sent1 = rnd_dt(21, 14)
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=random.choice([1, 2, 3]),
                         followup_due=(sent1 + timedelta(days=5)).date(),
                         greeting=greeting)
            sent2 = sent1 + timedelta(days=5)
            insert_email(lid, 2, 'follow_up_1', 'sent',
                         sent_at=sent2, open_count=random.choice([0, 1]),
                         followup_due=(sent2 + timedelta(days=7)).date(),
                         greeting=greeting)

        elif status == 'no_reply':
            sent1 = rnd_dt(30, 21)
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=2, greeting=greeting)
            sent2 = sent1 + timedelta(days=5)
            insert_email(lid, 2, 'follow_up_1', 'sent',
                         sent_at=sent2, open_count=1, greeting=greeting)
            sent3 = sent2 + timedelta(days=7)
            insert_email(lid, 3, 'follow_up_2', 'sent',
                         sent_at=sent3, open_count=1, greeting=greeting)

        elif status == 'replied':
            reply_text_val = reply_texts.get(full_name, (
                "Hi Christopher,\n\nThanks for reaching out. Interested in having a chat — "
                "could you send over more details?\n\nBest regards"
            ))
            sent1 = rnd_dt(25, 18)
            reply_at = sent1 + timedelta(days=random.randint(3, 8))
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=2,
                         reply_received=True, reply_read=False,  # unread by default
                         reply_at=reply_at, reply_text=reply_text_val,
                         followup_due=(reply_at + timedelta(days=2)).date(),
                         greeting=greeting)
            sent2 = sent1 + timedelta(days=5)
            insert_email(lid, 2, 'follow_up_1', 'sent',
                         sent_at=sent2, open_count=1, greeting=greeting)

        elif status == 'meeting':
            reply_text_val = reply_texts.get(full_name, (
                "Hi Christopher,\n\nThanks for reaching out — great timing. "
                "Would love to connect. Can we book a call for next week?\n\nBest"
            ))
            sent1 = rnd_dt(20, 15)
            reply_at = sent1 + timedelta(days=random.randint(2, 5))
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=3,
                         reply_received=True, reply_read=False,  # unread by default
                         reply_at=reply_at, reply_text=reply_text_val,
                         greeting=greeting)
            sent2 = sent1 + timedelta(days=4)
            insert_email(lid, 2, 'follow_up_1', 'sent',
                         sent_at=sent2, open_count=1, greeting=greeting)
            sent3 = sent2 + timedelta(days=6)
            insert_email(lid, 3, 'follow_up_2', 'sent',
                         sent_at=sent3, open_count=2, greeting=greeting)

        elif status == 'won':
            reply_text_val = reply_texts.get(full_name, (
                "Hi Christopher,\n\nExcellent profile! Let's set up a call this week "
                "to discuss our Google Ads requirements.\n\nKind regards"
            ))
            sent1 = rnd_dt(35, 28)
            reply_at = sent1 + timedelta(days=2)
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=3,
                         reply_received=True, reply_read=False,  # unread by default
                         reply_at=reply_at, reply_text=reply_text_val,
                         greeting=greeting)
            for step, days_offset in [(2, 4), (3, 8), (4, 12)]:
                sent = sent1 + timedelta(days=days_offset)
                insert_email(lid, step, FOLLOWUP_TYPE[step], 'sent',
                             sent_at=sent, open_count=2, greeting=greeting)

    print(f"  Emails: {len(emails_out)} rows")
    return emails_out


def insert_tracking_events(conn, emails):
    """Insert ~60 tracking events for sent emails."""
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
    ]
    IPS = ["91.108.4.1", "185.76.8.22", "104.28.33.12", "52.70.123.45", "13.42.88.201"]

    count = 0
    for email in emails:
        if email['status'] != 'sent':
            continue
        tracking_id = email['tracking_id']
        num_opens = random.randint(1, 3)
        for _ in range(num_opens):
            event_at = datetime.now() - timedelta(days=random.randint(0, 20))
            conn.execute(
                "INSERT INTO outreach_tracking_events VALUES (?,?,?,?,?,?,?)",
                [gen_id(), tracking_id, 'open', event_at,
                 random.choice(IPS), random.choice(USER_AGENTS), None]
            )
            count += 1
        if random.random() < 0.4:
            click_at = datetime.now() - timedelta(days=random.randint(0, 15))
            conn.execute(
                "INSERT INTO outreach_tracking_events VALUES (?,?,?,?,?,?,?)",
                [gen_id(), tracking_id, 'click', click_at,
                 random.choice(IPS), random.choice(USER_AGENTS),
                 'https://christopherhoole.online']
            )
            count += 1

    print(f"  Tracking events: {count} rows")


def main():
    print(f"warehouse.duckdb: {WAREHOUSE_PATH}")
    conn = duckdb.connect(str(WAREHOUSE_PATH))

    print("\n--- Creating tables ---")
    create_tables(conn)

    print("\n--- Inserting templates ---")
    insert_templates(conn)

    print("\n--- Inserting leads ---")
    leads = insert_leads(conn)

    print("\n--- Inserting emails ---")
    emails = insert_emails(conn, leads)

    print("\n--- Inserting tracking events ---")
    insert_tracking_events(conn, emails)

    print("\n--- Final row counts ---")
    for table in ['outreach_leads', 'outreach_emails', 'outreach_tracking_events', 'outreach_templates']:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {cnt} rows")

    # Verify replies-page data
    print("\n--- Replies page summary ---")
    reply_count = conn.execute(
        "SELECT COUNT(*) FROM outreach_leads WHERE status IN ('replied','meeting','won')"
    ).fetchone()[0]
    unread_count = conn.execute(
        "SELECT COUNT(*) FROM outreach_emails WHERE reply_received=true AND reply_read=false"
    ).fetchone()[0]
    print(f"  Leads on replies page: {reply_count}")
    print(f"  Unread replies: {unread_count}")

    conn.close()
    print("\nOutreach data generation complete!")


if __name__ == '__main__':
    main()
