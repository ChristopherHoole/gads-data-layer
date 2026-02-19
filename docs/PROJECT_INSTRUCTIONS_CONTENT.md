# PROJECT INSTRUCTIONS - COPY THIS INTO PROJECT INSTRUCTIONS

---

## USER IDENTITY & COMMUNICATION

User's name is Christopher.

Christopher prefers SHORT, DIRECT responses without unnecessary explanation or waffle.

Christopher wants responses to be PAINFULLY EXPLICIT and to the point.

Christopher prefers COMPLETE, READY-TO-USE FILES over code snippets for all deliverables.

Christopher describes himself as "NOT A CODER" and needs EXACT COMMANDS with clear expectations.

Christopher prefers INDIVIDUAL FILES over ZIP archives.

Christopher wants EXPLICIT NOTIFICATION when switching between software tools.

Christopher needs EXPLICIT INSTRUCTIONS about what to expect after running scripts.

---

## PROJECT IDENTITY

Project name: "Ads Control Tower" (A.C.T)

Purpose: Automated Google Ads optimization platform that generates and executes optimization recommendations with safety guardrails.

Location: C:\Users\User\Desktop\gads-data-layer

Development pattern: Master Chat (coordination) + Worker Chats (execution)

Real Google Ads customer ID: 7372844356
Test/Synthetic customer ID: 9999999999

---

## MANDATORY WORKING RULES (NON-NEGOTIABLE)

**RULE 1: EVERY worker chat MUST start by requesting 3 uploads:**
1. Codebase ZIP (C:\Users\User\Desktop\gads-data-layer)
2. PROJECT_ROADMAP.md (C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md)
3. CHAT_WORKING_RULES.md (C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md)

Christopher WILL REFUSE to proceed if these uploads are not provided.

**RULE 2: BEFORE editing ANY file, MUST request current version from Christopher.**
NEVER use cached versions. NEVER assume file hasn't changed.

**RULE 3: ALWAYS use FULL Windows paths.**
CORRECT: C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py
WRONG: routes/campaigns.py

---

## TECHNICAL STACK

Backend: Python 3.11, Flask, DuckDB for analytics
Frontend: Bootstrap 5 (NOT Tailwind), Chart.js, Vanilla JavaScript (NO jQuery)
Templates: MUST extend base_bootstrap.html (NOT base.html)
Database: Use ro.analytics.* prefix for readonly database

---

## KEY CONSTRAINTS

All automated changes MUST pass Constitution framework safety guardrails.

Constitution enforces: daily limits, 7-day cooldown periods, change magnitude restrictions, data sufficiency requirements.

ALL work MUST be tested before reporting complete (NO EXCEPTIONS).

Primary browser: Opera (test in Chrome if issues occur)

Git: Frequent commits with clear messages required

---

## STRATEGIC PRIORITIES

Dashboard UI takes PRIORITY over reports/alerts (familiar interface first).

System designed for multi-client agency use.

Christopher follows systematic multi-chat approach with comprehensive handoff documentation.

---

## DEVELOPMENT APPROACH

Christopher emphasizes: thorough documentation, comprehensive testing, methodical progression.

Debugging: Provide exact error outputs and terminal logs for precise diagnosis.

Workflow: Current file versions before editing + comprehensive testing before proceeding.

Christopher has patience with iterative debugging BUT escalates rather than continue circular problem-solving.

---

## SYSTEM ARCHITECTURE

Constitution framework: safety constraints (cooldowns, magnitude limits, data sufficiency)

Components: data layer (ingestion), Lighthouse (analytics/diagnostics), Autopilot (rules engine), execution engine, Radar (monitoring/rollback), dashboard interface

Autopilot: 16+ optimization rules across budget, bid target, campaign status

Execution: dry-run and live modes for keywords, ads, Shopping campaigns

Multi-client: session-based switching with audit trails

---

## CRITICAL LESSONS

Explicit dictionary mapping > Python's asdict() for complex serialization
Flask application cache > session storage (cookie size limits)
Systematic testing at each stage is CRITICAL
Escalate issues rather than continue inefficient debugging
Recent refactoring eliminated dual recommendation systems

---

END OF PROJECT INSTRUCTIONS
