# ACT Vision — The $100M Roadmap
**Session:** ACT Vision — The $100M Roadmap
**Date:** 2026-04-02
**Objective:** Thought exercise to explore what business model and growth path could take ACT to a $100M valuation. This is a strategy discussion, not a build session. No code.

---

## Context

### What ACT Is Today
ACT (Ads Control Tower) is a Google Ads optimization platform built by Christopher Hoole. It currently runs as a local Flask + DuckDB app with:
- 75 optimization rules + 99 monitoring flags across 6 entity types
- Recommendations engine with accept/decline/monitoring across all entities
- Cold outreach system for client acquisition
- Job tracker with Indeed/LinkedIn integration
- Built for one user (Christopher) managing client accounts

### What Makes ACT Unique
No existing product combines all of these:
- Rule-based optimization at every level (account → campaign → ad group → keyword → ad → shopping)
- Strategy-aware rules (different logic for Max Clicks vs tCPA vs tROAS vs Manual CPC)
- Recommendations with human approval workflow
- Post-acceptance monitoring with auto-rollback (Radar — planned)
- Flags system for anomaly detection
- All in one platform

### Competitive Landscape
- **Hyros** ($110M exit) — multi-touch attribution tracking. Tells you which ads work. Doesn't optimize them.
- **Optmyzr** — Google Ads optimization scripts and rules. Closest competitor but less depth in rule engine.
- **Adalysis** — Ad testing and optimization. Narrower scope.
- **Google Ads recommendations** — Free but generic, not customisable, often self-serving (Google wants you to spend more).
- **WordStream** — SMB Google Ads management tool. Acquired by Gannett.
- **None of these** combine deep rule-based optimization + recommendations engine + monitoring + rollback in one platform.

### Christopher's Current Situation
- Actively job hunting (60+ applications, outreach to recruiters/agencies launching)
- First potential client (Objection Experts) — quote sent for ~£1,500/month account
- Running Google Ads for own lead gen (christopherhoole.com)
- ACT optimization architecture needs a fundamental redesign before scaling (174 rules too complex)
- No external funding, no team, bootstrapped

---

## Discussion Topics

This is a free-form strategy discussion. Work through these topics in order, but go where the conversation leads.

### 1. The Four-Phase Growth Model

Discuss and validate this phased approach:

**Phase 1: Agency (now)**
- Christopher uses ACT to manage clients himself
- Revenue = monthly management fees
- ACT is his competitive advantage, not the product
- Goal: Prove ACT works on real accounts, generate income

**Phase 2: White-Label / Licensing**
- License ACT to other freelancers and small agencies
- They pay monthly to use ACT on their clients
- Revenue = SaaS subscriptions from other PPC professionals
- Goal: Revenue without Christopher managing every account

**Phase 3: Self-Serve SaaS**
- Businesses connect their own Google Ads accounts
- ACT runs optimization automatically with human approval
- Revenue = monthly subscriptions at scale
- Goal: Product-led growth, thousands of users

**Phase 4: Marketplace / Platform**
- Businesses post their accounts
- ACT-certified managers compete to manage them
- Revenue = platform fees on management contracts
- Goal: Network effects, platform dominance

For each phase, discuss:
- What revenue looks like (pricing, volume, margins)
- What ACT needs technically (deployment, multi-tenant, API, etc.)
- What the team looks like (solo → small team → company)
- How long each phase takes realistically
- What validates moving to the next phase

### 2. Revenue Modelling

For each phase, build rough revenue models:

**Phase 1 targets:**
- How many clients at what fee to hit £10k/month? £50k/month?
- What's the max number of clients one person can manage with ACT?

**Phase 2 targets:**
- How many licensees at what price to hit £100k/month?
- What's the conversion rate from free trial to paid?

**Phase 3 targets:**
- How many SaaS users at what MRR to hit £1M ARR? £10M ARR?
- What's the pricing tier structure?

**Phase 4 targets:**
- What GMV and take rate to hit £10M+ revenue?

**The $100M valuation math:**
- SaaS companies typically valued at 10-15x ARR
- So £7-10M ARR ≈ $100M valuation
- What does that require in terms of users/clients/pricing?

### 3. What to Build Now That Doesn't Block Later

This is the most actionable output. Given the four phases, what architectural decisions should Christopher make NOW to avoid painting himself into a corner?

Consider:
- Database: DuckDB → PostgreSQL? When?
- Multi-tenancy: How to structure accounts/clients from the start?
- API: Should the backend be API-first for future integrations?
- Deployment: Cloud hosting, containerization, CI/CD
- Google Ads API: What access level is needed for each phase?
- Authentication: Multi-user from Phase 2 onwards
- Billing: Stripe integration for subscriptions
- Data isolation: Client data separation for security/compliance

### 4. The Optimization Redesign Through This Lens

Christopher has identified that the current 174 rules are too complex for real-world use. How does the $100M vision inform the redesign?

- Phase 1 (agency) needs: practical daily workflow for managing 5-20 accounts
- Phase 2 (white-label) needs: configurable rules that other PPC people can customize
- Phase 3 (SaaS) needs: simple enough for a business owner to understand, smart enough to actually work
- Phase 4 (marketplace) needs: standardized optimization that works across any account

The redesign should serve Phase 1 first but be architecturally compatible with Phases 2-4.

### 5. Competitive Moat

What makes ACT defensible? Why can't someone else build this?

- Depth of rule engine (75 rules across 6 entities, strategy-aware)
- Recommendations with monitoring and rollback
- Domain expertise embedded in the rules (Christopher's 10+ years of PPC knowledge)
- Network effects (Phase 4 — more managers and clients = more data = better optimization)
- First-mover in this specific niche?

### 6. Risks and Blockers

Be honest about what could go wrong:
- Google Ads API access limitations
- Google building better native optimization (they have incentive NOT to — they want you to spend more)
- Competition from funded startups
- Scaling from one person to a team
- Technical debt from the current local-only architecture

---

## Output Expected

By the end of this session, have clear answers to:

1. **Phase plan** — validated 4-phase model with realistic timelines
2. **Revenue targets** — specific numbers for each phase milestone
3. **$100M math** — exactly what ARR/user count/pricing gets there
4. **Architecture decisions** — what to build now that serves all phases
5. **Next 90 days** — what Christopher should focus on given all of the above
6. **Optimization redesign guidance** — how the vision informs the current rebuild

Save the output as a document in `docs/ACT_VISION_100M_ROADMAP.md`.

---

## Rules

- This is a DISCUSSION session. No code.
- Be specific with numbers. No hand-waving.
- Challenge assumptions. If something is unrealistic, say so.
- Reference real companies and their growth paths where relevant (Hyros, Optmyzr, WordStream, etc.)
- Keep it grounded — Christopher is a solo bootstrapper, not a VC-backed startup. The plan must be achievable step by step.

---

**END OF BRIEF**
