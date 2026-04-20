"""N1 — Negatives Module engine package.

Rules-only v1:
 - _common      : normalize/tokenize helpers (symmetric on data + query side)
 - pass1        : 7-rule classifier (keep / block / review)
 - pass2        : routes blocks to target list_role
 - pass3        : phrase-fragment mining from pushed terms
 - reference_locations : UK postcode regex + major-cities reference set
"""
