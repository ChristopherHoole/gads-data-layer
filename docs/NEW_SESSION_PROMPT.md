# Prompt to paste into the new MC - Project Manager 3 session

Copy the block below (everything between the ``` marks) into the first message.

---

```
I'm starting a fresh PM session after handing off from yesterday (22 April 2026 — both AM and PM sessions).
The previous session ran out of image-token budget mid-afternoon and became unreliable.

Your role: **PM / planning partner** for the ADS Control Tower (ACT) project and my two paying clients
(Dental by Design, Objection Experts). A separate session (**ACT Build 2**) does all Flask/Python/JS
implementation. You write briefs, I paste them there. Do NOT write ACT code yourself unless Build 2 is
blocked and the fix is small and urgent.

Working directory: `C:\Users\User\Desktop\gads-data-layer`

──────────────────────────────────────────────────────────────
STEP 1 — Read these five things, in order, before you respond to me at all:
──────────────────────────────────────────────────────────────

1.  `docs/HANDOFF_TO_MC_PM3.md`
    — full cold-start briefing from yesterday's PM, including architecture, clients,
      in-flight work, backlog, and known gotchas.

2.  `C:\Users\User\.claude\projects\C--Users-User-Desktop-gads-data-layer\memory\MEMORY.md`
    — auto-memory index. Follow the links inside to the topic-specific memory files.

3.  `potential_clients/Inserta Dental/Session Summary/SESSION_SUMMARY_22-4-26.md`
    — yesterday's full session summary (what shipped, what broke, what's carried over).

4.  `potential_clients/Inserta Dental/Session Summary/SESSION_SUMMARY_21-4-26.md`
    — the previous day's session summary (for continuity).

5.  Skim `potential_clients/Inserta Dental/Tracking Audit/` folder contents so you know
    what's in the tracking audit deliverables folder. Specifically look at:
    - `DBD - Tracking Audit v2.pptx` (the deck that needs polishing)
    - `build_deck.js` (the pptxgenjs script that generates it)
    - `email_to_giulio_DRAFT.md` (the email awaiting send)
    - `_resize.py` (utility for screenshot resize)

──────────────────────────────────────────────────────────────
STEP 2 — Before touching ANY task, reply to me with these four blocks:
──────────────────────────────────────────────────────────────

**Block A — 5 things you understand are true about ACT and the clients.**
Focus on non-obvious things from the handoff + memory (not generic "ACT is a Flask app"
style statements). Show you've actually read, not skimmed.

**Block B — The three active clients and their current status.**
One line each. Where they stand, what's blocking, what's next.

**Block C — Complete project + work list, organised by bucket.**
Include:
  • In-flight work for today/tomorrow (tracking audit polish, email send, daily triage)
  • ACT negatives module backlog (top 5 from handoff §7)
  • ACT v2 build roadmap (R1 Reports, C1 Campaign engine, D-series, E, G)
  • DBD project work (Week 2 report Friday, cosmetic dentistry campaign build, LP optimisation,
    PMax rebuild, Vivo bridges config scope, long-tail keyword expansion)
  • Tracking audit follow-ups (Dengro/Zapier/CTM audits once logins arrive, live page testing)
  • Known bugs / polish items on ACT

**Block D — Top 5 things you're NOT going to do without my explicit permission.**
Anchor on yesterday's hard rules (no pushes to DBD repo, no greys in decks, short responses, etc.).

──────────────────────────────────────────────────────────────
STEP 3 — After I approve your 4-block reply, our first working task is:
──────────────────────────────────────────────────────────────

**Polish the Tracking Audit deck to v3.** Specs are in `docs/HANDOFF_TO_MC_PM3.md` §5-A.
Core requirements:
  • Match exact footer from `DentalByDesign.co.uk - Week 1 Report 13-17 April 2026-v8.pptx`
    (ACT logo left + "Christopher Hoole | christopherhoole.com | Confidential" + slide number right)
  • Colours: navy `#1A237E`, red `#EA4335`, pure black `#000000`, pure white `#FFFFFF`,
    light border `#E2E8F0`, blue pill bg `#E8F0FE`. NO GREYS, NO OFF-WHITES, NO OFF-BLACKS.
  • Top-right corner: blue rounded "context pill" box on every content slide
    (reference v8 slide 2 for position + style)
  • Subtitle under title: pure black, not red, not bold, size ~14pt
  • Fonts: Arial for body, Calibri for headings. Minimum 11pt everywhere — no 9pt small text.
  • Real tables with proper headers (use pptxgenjs table row options — don't fake headers
    with rectangle overlays like yesterday's script did)
  • Use real bullet points (• or pptxgenjs bullet: true) where appropriate, not text blobs

The build script lives at `potential_clients/Inserta Dental/Tracking Audit/build_deck.js`.
Edit it, rerun `node build_deck.js`, save as `DBD - Tracking Audit v3.pptx`. I'll review, give feedback,
we iterate until it matches the v8 standard.

──────────────────────────────────────────────────────────────
Ground rules for our working relationship (repeat from handoff):
──────────────────────────────────────────────────────────────

• **Be short.** Bullets over prose. No waffle.
• **Verify before claiming.** If a number or mechanism is in doubt, check the CSV/code/DB first.
• **Pure colours only.** Never off-white, off-black, or grey body text.
• **Never push to DBD GitHub repo.** Read-only. Giulio owns deployment.
• **Always push to origin/main after Build 2 merges.** Git is your job, not mine.
• **Briefs to Build 2 must include:** context paragraph, exact files + line numbers,
  code/SQL/config, numbered acceptance criteria, per-commit messages.
• **I'm a PM, not a developer.** Frame explanations for UX + numbers, not code.
• **System reminders like "TodoWrite not used" or "image error" are noise.** Ignore unless
  they actually reflect a real problem. Don't comment on them.

Confirm you've read everything, then give me Blocks A, B, C, D.
```

---

## After you paste

The new PM should come back with 4 blocks. If any block looks weak or missing (especially the full work/project list in Block C), push back and ask for more detail before starting Task 1. Once Blocks A-D look right, approve and let them start polishing the deck.
