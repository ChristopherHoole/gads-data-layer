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

# Maps template sequence_step → email_type value stored on outreach_emails
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
    """Insert 30 leads with correct status distribution."""
    # Columns: first, last, company, role, email, linkedin, website, city_state, country, track, source, score, status, notes
    leads_raw = [
        # ── AGENCY (15) ─────────────────────────────────────────────────────────────────────
        ("James",    "Thornton",    "PPC Masters Ltd",         "Managing Director",
         "james@ppcmasters.co.uk",              "linkedin.com/in/jamesthornton",
         "ppcmasters.co.uk",         "London",           "UK",        "Agency",    "Apollo", 5, "cold",        ""),
        ("Emma",     "Watson",      "Digital Pulse Agency",    "Head of PPC",
         "emma@digitalpulse.com",               "linkedin.com/in/emmawatson-ppc",
         "digitalpulse.com",         "Manchester",       "UK",        "Agency",    "Apollo", 5, "contacted",   "Sent initial email. No response yet."),
        ("Oliver",   "Davis",       "SearchFirst Ltd",         "Director",
         "oliver@searchfirst.co.uk",            "linkedin.com/in/oliverdavis",
         "searchfirst.co.uk",        "Birmingham",       "UK",        "Agency",    "Apollo", 5, "followed_up", "Followed up twice. Opened email but no reply."),
        ("Chris",    "Lee",         "Ignite Growth Agency",    "VP Marketing",
         "chris@ignitegrowth.com",              "linkedin.com/in/chrislee-marketing",
         "ignitegrowth.com",         "San Francisco, CA","USA",       "Agency",    "Apollo", 3, "contacted",   ""),
        ("Lisa",     "Sanchez",     "Rocket PPC",              "Founder",
         "lisa@rocketppc.com",                  "linkedin.com/in/lisasanchez",
         "rocketppc.com",            "Houston, TX",      "USA",       "Agency",    "Apollo", 3, "meeting",     "Meeting booked for 15 Mar. Very positive!"),
        ("Mark",     "Johnson",     "Blue Sky Digital",        "Head of PPC",
         "mark@blueskydigital.com",             "linkedin.com/in/markjohnson-ppc",
         "blueskydigital.com",       "Chicago, IL",      "USA",       "Agency",    "Apollo", 5, "cold",        ""),
        ("Pierre",   "Leblanc",     "Maple Leaf Media",        "Founder",
         "pierre@mapleleafmedia.ca",            "linkedin.com/in/pierreeleblanc",
         "mapleleafmedia.ca",        "Montreal, QC",     "Canada",    "Agency",    "Apollo", 3, "followed_up", ""),
        ("Ryan",     "Fletcher",    "Harbour Digital",         "Managing Director",
         "ryan@harbourdigital.com.au",          "linkedin.com/in/ryanfletcher",
         "harbourdigital.com.au",    "Melbourne",        "Australia", "Agency",    "Apollo", 5, "cold",        ""),
        ("Alex",     "Dupont",      "North Star Marketing",    "Director",
         "alex@northstarmarketing.ca",          "linkedin.com/in/alexdupont",
         "northstarmarketing.ca",    "Toronto, ON",      "Canada",    "Agency",    "Apollo", 5, "queued",      ""),
        ("Emma",     "Roberts",     "Velocity Digital",        "CEO",
         "emma@velocitydigital.co.uk",          "linkedin.com/in/emmaroberts-dig",
         "velocitydigital.co.uk",    "Bristol",          "UK",        "Agency",    "Apollo", 3, "no_reply",    "Sent 2 emails, opened both but no reply."),
        ("Rachel",   "Chen",        "Grow Digital",            "CEO",
         "rachel@growdigital.com",              "linkedin.com/in/rachelchen",
         "growdigital.com",          "Los Angeles, CA",  "USA",       "Agency",    "Apollo", 3, "replied",     "Replied positively. Interested in freelance PPC."),
        ("Tom",      "Clarke",      "Apex Digital Solutions",  "CEO",
         "tom@apexdigital.co.uk",               "linkedin.com/in/tomclarke-apex",
         "apexdigital.co.uk",        "Birmingham",       "UK",        "Agency",    "Manual", 5, "meeting",     "In-person meeting planned for 20 Mar."),
        ("Sarah",    "Hall",        "Click Depot",             "Director",
         "sarah@clickdepot.com",                "linkedin.com/in/sarahhall-ppc",
         "clickdepot.com",           "New York, NY",     "USA",       "Agency",    "Apollo", 5, "contacted",   ""),
        ("Ben",      "Adams",       "Pulse Digital",           "Head of Paid Media",
         "ben@pulsedigital.co.uk",              "linkedin.com/in/benadams-paid",
         "pulsedigital.co.uk",       "London",           "UK",        "Agency",    "Apollo", 5, "followed_up", ""),
        ("Caroline", "Hughes",      "TechScale Agency",        "Managing Director",
         "caroline@techscale.co.uk",            "linkedin.com/in/carolinehughes",
         "techscale.co.uk",          "London",           "UK",        "Agency",    "Apollo", 5, "followed_up", ""),
        # ── RECRUITER (8) ────────────────────────────────────────────────────────────────────
        ("Sarah",    "Mitchell",    "Digital Talent Group",    "Head of Recruitment",
         "sarah@digitaltalentgroup.com",        "linkedin.com/in/sarahmitchell",
         "digitaltalentgroup.com",   "New York, NY",     "USA",       "Recruiter", "Apollo", 4, "replied",
         "Replied quickly — seems genuinely interested. Mentioned 2 live roles (fintech NYC contract + DTC ecommerce Austin perm). Follow up after weekend to book call."),
        ("Michael",  "Brown",       "Hays Digital",            "Senior Consultant",
         "m.brown@hays.com",                    "linkedin.com/in/michaelbrown-hays",
         "hays.com",                 "Manchester",       "UK",        "Recruiter", "Manual", 2, "cold",        ""),
        ("Jessica",  "Wong",        "Talent Digital AU",       "Senior Recruiter",
         "jessica@talentdigitalau.com",         "linkedin.com/in/jessicawong-recruit",
         "talentdigitalau.com",      "Sydney",           "Australia", "Recruiter", "Apollo", 4, "contacted",   ""),
        ("David",    "Kim",         "TalentBridge USA",        "Partner",
         "david@talentbridgeusa.com",           "linkedin.com/in/davidkim-talent",
         "talentbridgeusa.com",      "Seattle, WA",      "USA",       "Recruiter", "Apollo", 2, "cold",        ""),
        ("Hannah",   "Clarke",      "Reed Digital",            "Recruitment Consultant",
         "h.clarke@reed.co.uk",                 "linkedin.com/in/hannahclarke-reed",
         "reed.co.uk",               "London",           "UK",        "Recruiter", "Apollo", 2, "replied",
         "Positive reply. Has a PPC manager role at a fintech startup."),
        ("Sophie",   "Martin",      "Peak Talent Group",       "Director",
         "sophie@peaktalentgroup.ca",           "linkedin.com/in/sophiemartin-talent",
         "peaktalentgroup.ca",       "Vancouver, BC",    "Canada",    "Recruiter", "Apollo", 4, "followed_up", ""),
        ("James",    "Cooper",      "Robert Half",             "Account Manager",
         "j.cooper@roberthalf.com",             "linkedin.com/in/jamescooper-rh",
         "roberthalf.com",           "New York, NY",     "USA",       "Recruiter", "Apollo", 2, "contacted",   ""),
        ("Victoria", "Osei",        "Heidrick & Struggles",    "Partner",
         "v.osei@heidrick.com",                 "linkedin.com/in/victoriaosei",
         "heidrick.com",             "Dubai",            "UAE",       "Recruiter", "Apollo", 4, "queued",      ""),
        # ── DIRECT (4) ──────────────────────────────────────────────────────────────────────
        ("Fatima",   "Al-Mansoori", "Emirates Growth Co",      "Managing Director",
         "fatima@emiratesgrowth.ae",            "linkedin.com/in/fatimamansoori",
         "emiratesgrowth.ae",        "Dubai",            "UAE",       "Direct",    "Manual", 5, "replied",
         "Very warm response. Has £500k/mo budget across GCC. Looking for freelance Google Ads specialist."),
        ("William",  "Hartley",     "Sterling Commerce",       "Chief Marketing Officer",
         "w.hartley@sterlingcommerce.co.uk",    "linkedin.com/in/williamhartley",
         "sterlingcommerce.co.uk",   "London",           "UK",        "Direct",    "Manual", 5, "cold",        ""),
        ("Jennifer", "Park",        "Conversion Lab",          "Marketing Director",
         "jennifer@conversionlab.io",           "linkedin.com/in/jenniferpark",
         "conversionlab.io",         "Denver, CO",       "USA",       "Direct",    "Manual", 3, "contacted",   ""),
        ("Khalid",   "Al-Rashid",   "Gulf Media Group",        "Chief Marketing Officer",
         "khalid@gulfmediagroup.ae",            "linkedin.com/in/khalidalrashid",
         "gulfmediagroup.ae",        "Dubai",            "UAE",       "Direct",    "Manual", 5, "won",
         "Contract won. Starting April. Budget £30k/mo."),
        # ── JOB (3) ─────────────────────────────────────────────────────────────────────────
        ("",         "",            "Greenfield Marketing",    "Hiring Manager",
         "jobs@greenfieldmarketing.co.uk",      "",
         "greenfieldmarketing.co.uk","Leeds",            "UK",        "Job",       "Indeed", 1, "cold",
         "Google Ads Manager role posted on Indeed."),
        ("",         "",            "Performance Media Inc",   "Hiring Manager",
         "careers@performancemedia.com",        "",
         "performancemedia.com",     "Miami, FL",        "USA",       "Job",       "Indeed", 1, "queued",
         "PPC Specialist contract role."),
        ("",         "",            "Adcentric UK",            "Hiring Manager",
         "careers@adcentric.co.uk",             "",
         "adcentric.co.uk",          "London",           "UK",        "Job",       "Indeed", 1, "cold",
         "Google Ads Specialist role, permanent."),
    ]

    # Verify distribution
    dist = {}
    for row in leads_raw:
        s = row[12]
        dist[s] = dist.get(s, 0) + 1
    print(f"  Status distribution: {dist}")
    assert sum(dist.values()) == 30, f"Expected 30 leads, got {sum(dist.values())}"

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
    """Insert ~40 emails consistent with lead statuses."""
    rows = conn.execute(
        "SELECT template_id, sequence_step, subject, body FROM outreach_templates ORDER BY sequence_step"
    ).fetchall()
    templates = {r[1]: (r[0], r[2], r[3]) for r in rows}

    def tmpl(step):
        return templates[step]  # (template_id, subject, body)

    reply_texts = {
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
    }

    default_reply = (
        "Hi Christopher,\n\nThanks for reaching out. Interested in having a chat — "
        "could you send over more details?\n\nBest regards"
    )

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
        lid     = lead['lead_id']
        status  = lead['status']
        greeting = lead['first_name'] or 'there'

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
            full_name = lead['full_name']
            reply_text_val = reply_texts.get(full_name, default_reply)
            sent1 = rnd_dt(25, 18)
            reply_at = sent1 + timedelta(days=random.randint(3, 8))
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=2,
                         reply_received=True, reply_read=True,
                         reply_at=reply_at, reply_text=reply_text_val,
                         followup_due=(reply_at + timedelta(days=2)).date(),
                         greeting=greeting)
            sent2 = sent1 + timedelta(days=5)
            insert_email(lid, 2, 'follow_up_1', 'sent',
                         sent_at=sent2, open_count=1, greeting=greeting)

        elif status == 'meeting':
            reply_text_val = (
                "Hi Christopher,\n\nThanks for reaching out — great timing. "
                "Would love to connect.\n\nCan we book a call for next week?\n\nBest"
            )
            sent1 = rnd_dt(20, 15)
            reply_at = sent1 + timedelta(days=random.randint(2, 5))
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=3,
                         reply_received=True, reply_read=True,
                         reply_at=reply_at, reply_text=reply_text_val,
                         greeting=greeting)
            sent2 = sent1 + timedelta(days=4)
            insert_email(lid, 2, 'follow_up_1', 'sent',
                         sent_at=sent2, open_count=1, greeting=greeting)
            sent3 = sent2 + timedelta(days=6)
            insert_email(lid, 3, 'follow_up_2', 'sent',
                         sent_at=sent3, open_count=2, greeting=greeting)

        elif status == 'won':
            reply_text_val = (
                "Hi Christopher,\n\nExcellent profile! Let's set up a call this week "
                "to discuss our Google Ads requirements.\n\nKind regards"
            )
            sent1 = rnd_dt(35, 28)
            reply_at = sent1 + timedelta(days=2)
            insert_email(lid, 1, 'initial', 'sent', cv_attached=True,
                         sent_at=sent1, open_count=3,
                         reply_received=True, reply_read=True,
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

    conn.close()
    print("\nOutreach data generation complete!")


if __name__ == '__main__':
    main()
