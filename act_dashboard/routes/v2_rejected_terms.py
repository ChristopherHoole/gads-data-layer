"""N3 Part A — /v2/rejected-terms.

IA refactor (13 May 2026): Rejected Terms moved into the Search Terms
page as a right-aligned tab. The standalone page is gone; this route
preserves the old URL for bookmarks/links by redirecting to the new
tab on /v2/search-term-review.
"""
from flask import Blueprint, redirect, request, url_for

v2_rejected_terms_bp = Blueprint('v2_rejected_terms', __name__)


@v2_rejected_terms_bp.route('/v2/rejected-terms')
def rejected_terms_page():
    client = request.args.get('client')
    target = url_for('v2_search_term_review.search_term_review_page')
    qs = ['tab=rejected']
    if client:
        qs.append(f'client={client}')
    return redirect(f"{target}?{'&'.join(qs)}", code=302)
