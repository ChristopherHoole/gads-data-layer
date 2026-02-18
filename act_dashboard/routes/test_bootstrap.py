"""
Test Bootstrap Blueprint
Provides test page to verify Bootstrap 5 integration.
"""

from flask import Blueprint, render_template, session
from act_dashboard.auth import login_required

# Create blueprint
bp = Blueprint('test_bootstrap', __name__)


@bp.route('/test-bootstrap')
@login_required
def test_bootstrap():
    """
    Test page to verify Bootstrap 5 integration.
    
    Shows all Bootstrap components to ensure:
    - Bootstrap CSS loaded correctly
    - Bootstrap JS loaded correctly
    - Bootstrap Icons loaded correctly
    - Custom CSS applied correctly
    - Sidebar, navbar, and metrics bar working
    
    Returns:
        Rendered test_bootstrap.html template
    """
    # Get client info from session (for navbar display)
    client_name = session.get('client_name', 'Test Client')
    current_client_config = session.get('client_config')
    
    return render_template(
        'test_bootstrap.html',
        client_name=client_name,
        current_client_config=current_client_config
    )
