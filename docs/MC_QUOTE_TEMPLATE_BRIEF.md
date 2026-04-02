# MC Quote Template — Brief
**Date:** 2026-03-30
**Objective:** Build a reusable HTML quote template (A4, print-to-PDF) and generate the first quote for Objection Experts.

---

## TASK 1: Build Reusable Quote Template

Create an A4 single-page HTML file that can be opened in a browser and saved as PDF via print.

**File location:** `potential_clients/quote_template.html`

**Design:**
- Clean, professional, minimal — not flashy
- A4 portrait (210mm x 297mm), print-friendly with proper margins
- Colour palette matching the reports: navy (#1B2A4A), teal accent (#00B4D8), charcoal text (#2C3E50), light grey backgrounds (#F5F6FA)
- Christopher Hoole branding: name, "Google Ads Specialist", christopherhoole.com, email, phone

**Sections to include (top to bottom):**

1. **Header** — Christopher Hoole branding + logo/name, "Google Ads Specialist", contact details
2. **Quote For** — Client name, company, date, quote reference number, valid until date
3. **Scope of Work** — Bulleted list of what's included in the engagement. Placeholder text that gets customised per client.
4. **Pricing Table** — Two rows minimum:
   - Setup Fee (one-off): description + price
   - Monthly Management Fee: description + price
   - Optional additional line items
   - Total row
5. **What's Included** — Brief list of deliverables (e.g., weekly optimisation, monthly reports, search term reviews, ad copy testing, etc.)
6. **Payment Terms** — When setup fee is due, when monthly billing starts, payment method, notice period
7. **Terms & Conditions** — Short, essential terms: minimum contract period, notice period, what's not included, liability disclaimer
8. **Acceptance** — Signature line, printed name, date, "Please sign and return to confirm"
9. **Footer** — Christopher Hoole, christopherhoole.com, small print

**Technical notes:**
- All content should be easy to edit by changing text values directly in the HTML
- Use inline CSS or a single `<style>` block — no external dependencies
- Must print cleanly to PDF from Chrome (File → Print → Save as PDF)
- `@media print` rules to hide browser chrome and ensure clean output
- `@page` rules for A4 sizing and margins

**Browser-verify:** Open in Chrome, check it looks professional, print to PDF and verify the output is clean A4.

---

## TASK 2: Generate Objection Experts Quote

Copy the template to `potential_clients/objection_experts/quote_objection_experts.html` and fill in for this specific client:

**Client details:**
- Client: Owen Hoare
- Company: Objection Experts
- Website: objectionexperts.com

**Scope of work (customise for this client):**
- Google Ads account audit and restructure (as per Reports 1-3)
- Conversion tracking fix (Email Click → Secondary)
- Bid strategy optimisation (set target CPA)
- Negative keyword framework implementation
- Ad copy A/B testing (3 RSA variants)
- Ad schedule and device bid adjustments
- Weekly search term review and negative keyword management
- Monthly performance report
- Ongoing campaign optimisation

**Pricing (leave the actual numbers as placeholders for Christopher to fill in):**
- Setup Fee: £[SETUP_FEE] — one-off account restructure and implementation of all quick wins from the audit reports
- Monthly Management Fee: £[MONTHLY_FEE] — ongoing optimisation, monitoring, reporting, and strategic management

**Payment terms:**
- Setup fee due on acceptance
- Monthly fee billed on the 1st of each month, starting the month after setup
- 30-day notice period to cancel

**Minimum term:**
- 3-month minimum after setup (to allow optimisations to take effect)

**Browser-verify:** Open in Chrome, check all details are correct, print to PDF and verify clean output.

---

## SESSION TOTAL: 2 tasks

| # | Task | Output |
|---|------|--------|
| 1 | Build reusable quote template | `potential_clients/quote_template.html` |
| 2 | Generate Objection Experts quote | `potential_clients/objection_experts/quote_objection_experts.html` |

**END OF BRIEF**
