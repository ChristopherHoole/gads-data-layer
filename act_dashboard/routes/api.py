"""
API routes - execution, batch, status, approve, reject, leads (Chat 32).
"""

from flask import Blueprint, request, jsonify, current_app
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_google_ads_client
from act_dashboard.utils import dict_to_recommendation, validate_recommendation_dict
from act_dashboard.validation import validate_execution_request, validate_batch_execution_request
from act_autopilot.executor import Executor
import duckdb
import json
import re
import logging
from datetime import datetime, date
from time import time

bp = Blueprint('api', __name__)


def check_rate_limit(key, limit=10, window=60):
    """
    Check if rate limit is exceeded.
    
    Args:
        key: Unique key for this endpoint/user
        limit: Maximum requests allowed
        window: Time window in seconds
        
    Returns:
        (allowed, remaining, reset_time) tuple
    """
    now = time()
    rate_limit_data = current_app.config.setdefault('RATE_LIMIT_DATA', {})
    
    if key not in rate_limit_data:
        rate_limit_data[key] = []
    
    # Remove expired timestamps
    rate_limit_data[key] = [ts for ts in rate_limit_data[key] if now - ts < window]
    
    # Check if limit exceeded
    if len(rate_limit_data[key]) >= limit:
        oldest = min(rate_limit_data[key])
        reset_time = oldest + window
        return False, 0, int(reset_time - now)
    
    # Add current request
    rate_limit_data[key].append(now)
    remaining = limit - len(rate_limit_data[key])
    return True, remaining, window



@bp.route("/execute-recommendation", methods=["POST"])
@login_required
def execute_recommendation():
    """
    Execute a single recommendation.
    
    Request JSON:
        {
            "recommendation_id": int,  # Index in recommendations list
            "date_str": str,           # Date of recommendations file
            "dry_run": bool            # True for dry-run, False for live
        }
        
    Returns JSON:
        {
            "success": bool,
            "message": str,
            "change_id": int or null,
            "error": str or null
        }
    """
    try:
        # Rate limit: 10 requests per minute per IP
        ip_address = request.remote_addr or 'unknown'
        rate_key = f"execute:{ip_address}"
        allowed, remaining, reset_seconds = check_rate_limit(rate_key, limit=10, window=60)
        
        if not allowed:
            return jsonify({
                "success": False,
                "message": "Rate limit exceeded",
                "error": f"Maximum 10 requests per minute. Try again in {reset_seconds} seconds.",
                "retry_after": reset_seconds
            }), 429
        
        data = request.get_json()
        rec_id = data.get("recommendation_id")
        date_str = data.get("date_str")  # Optional - for file-based recommendations
        page = data.get("page")  # Optional - 'keywords', 'ads', 'shopping' for session-based
        dry_run = data.get("dry_run", True)
        
        if rec_id is None:
            return jsonify({
                "success": False,
                "message": "Missing recommendation_id",
                "error": "recommendation_id is required"
            }), 400
        
        # Get current config
        config = get_current_config()
        
        # ==================== LOAD RECOMMENDATION ====================
        # Two sources: FILE (main recommendations page) or SESSION (keywords/ads/shopping)
        
        recommendation = None
        recommendations = []  # Will be populated below
        
        # Option 1: Load from CACHE (live recommendations from keywords/ads/shopping)
        if page:
            cache = current_app.config.get('RECOMMENDATIONS_CACHE', {})
            recommendations = cache.get(page, [])
            
            if not recommendations:
                return jsonify({
                    "success": False,
                    "message": f"No {page} recommendations in cache",
                    "error": f"Please refresh the {page} page to generate recommendations"
                }), 404
            
            # Validate request against available recommendations
            is_valid, error_msg = validate_execution_request(data, recommendations)
            if not is_valid:
                return jsonify({
                    "success": False,
                    "message": "Invalid execution request",
                    "error": error_msg
                }), 400
            
            recommendation = recommendations[rec_id]
        
        # Option 2: Load from FILE (main recommendations page)
        else:
            if not date_str:
                date_str = date.today().isoformat()
            
            suggestions_path = config.get_suggestions_path(date_str)
            if not suggestions_path.exists():
                return jsonify({
                    "success": False,
                    "message": "Recommendations file not found",
                    "error": f"No recommendations file for {date_str}. Try refreshing the Recommendations page."
                }), 404
            
            with open(suggestions_path, "r") as f:
                suggestions = json.load(f)
            
            recommendations = suggestions.get("recommendations", [])
            
            # Validate request against available recommendations
            is_valid, error_msg = validate_execution_request(data, recommendations)
            if not is_valid:
                return jsonify({
                    "success": False,
                    "message": "Invalid execution request",
                    "error": error_msg
                }), 400
            
            recommendation = recommendations[rec_id]
        
        # ==================== VALIDATE RECOMMENDATION ====================
        
        # Validate recommendation dict
        is_valid, validation_error = validate_recommendation_dict(recommendation)
        if not is_valid:
            return jsonify({
                "success": False,
                "message": "Invalid recommendation format",
                "error": f"Validation failed: {validation_error}"
            }), 400
        
        # Check if already blocked
        if recommendation.get("blocked", False):
            return jsonify({
                "success": False,
                "message": "Recommendation is blocked",
                "error": recommendation.get("block_reason", "This recommendation was blocked by guardrails")
            }), 400
        
        # Convert dict to Recommendation object
        try:
            rec_obj = dict_to_recommendation(recommendation)
        except (ValueError, TypeError) as e:
            return jsonify({
                "success": False,
                "message": "Failed to convert recommendation",
                "error": str(e)
            }), 500
        
        # Initialize executor
        # Only initialize Google Ads client for live execution, not dry-run
        google_ads_client = None
        if not dry_run:
            try:
                google_ads_client = get_google_ads_client(config)
            except FileNotFoundError as e:
                return jsonify({
                    "success": False,
                    "message": "Google Ads credentials not found",
                    "error": "Please configure Google Ads API credentials in secrets/google-ads.yaml"
                }), 500
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": "Google Ads authentication failed",
                    "error": str(e)
                }), 500
        
        executor = Executor(config.customer_id, config.db_path, google_ads_client)
        
        # Execute (pass Recommendation object, not dict)
        try:
            execution_summary = executor.execute([rec_obj], dry_run=dry_run)
            # Executor returns: {"total": 1, "successful": 1, "failed": 0, "results": [...]}
            
            # Check if any recommendations were executable
            if len(execution_summary["results"]) == 0:
                return jsonify({
                    "success": False,
                    "message": "No executable recommendations",
                    "error": "Recommendation passed validation but Executor returned no results"
                }), 500
            
            # Check result for this recommendation
            result = execution_summary["results"][0]
            
            if result["success"]:
                # Success response
                response_data = {
                    "success": True,
                    "message": "Dry-run successful" if dry_run else "Executed successfully",
                    "change_id": result.get("change_id"),
                    "result": result.get("message")
                }
                
                # Add prediction if available
                if result.get("predicted_impact"):
                    response_data["predicted_impact"] = result["predicted_impact"]
                
                return jsonify(response_data), 200
            else:
                # Execution failed
                return jsonify({
                    "success": False,
                    "message": "Execution failed",
                    "error": result.get("error", "Unknown error during execution")
                }), 500
                
        except Exception as e:
            logging.error(f"Execution error: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Execution failed",
                "error": str(e)
            }), 500
            
    except Exception as e:
        logging.error(f"Request error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Request failed",
            "error": str(e)
        }), 500


@bp.route("/execute-batch", methods=["POST"])
@login_required
def execute_batch():
    """
    Execute multiple recommendations in batch.
    
    Request JSON:
        {
            "recommendation_ids": [int],  # List of indexes in recommendations list
            "date_str": str,              # Date of recommendations file
            "dry_run": bool               # True for dry-run, False for live
        }
        
    Returns JSON:
        {
            "success": bool,
            "message": str,
            "results": [{
                "recommendation_id": int,
                "success": bool,
                "message": str,
                "change_id": int or null
            }],
            "summary": {
                "total": int,
                "successful": int,
                "failed": int
            }
        }
    """
    try:
        # Rate limit: 5 batch requests per minute per IP
        ip_address = request.remote_addr or 'unknown'
        rate_key = f"batch:{ip_address}"
        allowed, remaining, reset_seconds = check_rate_limit(rate_key, limit=5, window=60)
        
        if not allowed:
            return jsonify({
                "success": False,
                "message": "Rate limit exceeded",
                "error": f"Maximum 5 batch requests per minute. Try again in {reset_seconds} seconds.",
                "retry_after": reset_seconds
            }), 429
        
        data = request.get_json()
        rec_ids = data.get("recommendation_ids", [])
        date_str = data.get("date_str")
        page = data.get("page")  # Optional - 'keywords', 'ads', 'shopping' for session-based
        dry_run = data.get("dry_run", True)
        
        if not rec_ids or not isinstance(rec_ids, list):
            return jsonify({
                "success": False,
                "message": "Missing recommendation_ids",
                "error": "recommendation_ids must be a non-empty list"
            }), 400
        
        # Get current config
        config = get_current_config()
        
        # ==================== LOAD RECOMMENDATIONS ====================
        
        recommendations = []
        
        # Option 1: Load from CACHE (live recommendations from keywords/ads/shopping)
        if page:
            cache = current_app.config.get('RECOMMENDATIONS_CACHE', {})
            recommendations = cache.get(page, [])
            
            if not recommendations:
                return jsonify({
                    "success": False,
                    "message": f"No {page} recommendations in cache",
                    "error": f"Please refresh the {page} page to generate recommendations"
                }), 404
        
        # Option 2: Load from FILE (main recommendations page)
        else:
            if not date_str:
                date_str = date.today().isoformat()
            
            suggestions_path = config.get_suggestions_path(date_str)
            if not suggestions_path.exists():
                return jsonify({
                    "success": False,
                    "message": "Recommendations file not found",
                    "error": f"No recommendations file for {date_str}. Try refreshing the Recommendations page."
                }), 404
            
            with open(suggestions_path, "r") as f:
                suggestions = json.load(f)
            
            recommendations = suggestions.get("recommendations", [])
        
        # ==================== VALIDATE BATCH REQUEST ====================
        
        # Validate batch request
        is_valid, error_msg = validate_batch_execution_request(data, recommendations)
        if not is_valid:
            return jsonify({
                "success": False,
                "message": "Invalid batch execution request",
                "error": error_msg
            }), 400
        
        # Extract selected recommendations
        selected_recs = []
        for rec_id in rec_ids:
            if 0 <= rec_id < len(recommendations):
                rec_dict = recommendations[rec_id]
                
                # Validate each recommendation
                is_valid, validation_error = validate_recommendation_dict(rec_dict)
                if not is_valid:
                    return jsonify({
                        "success": False,
                        "message": f"Invalid recommendation {rec_id}",
                        "error": validation_error
                    }), 400
                
                # Check if blocked
                if rec_dict.get("blocked", False):
                    continue  # Skip blocked recommendations
                
                # Convert to Recommendation object
                try:
                    rec_obj = dict_to_recommendation(rec_dict)
                    selected_recs.append((rec_id, rec_obj))
                except (ValueError, TypeError) as e:
                    return jsonify({
                        "success": False,
                        "message": f"Failed to convert recommendation {rec_id}",
                        "error": str(e)
                    }), 500
        
        if not selected_recs:
            return jsonify({
                "success": False,
                "message": "No valid recommendations to execute",
                "error": "All selected recommendations are blocked or invalid"
            }), 400
        
        # Initialize executor
        # Only initialize Google Ads client for live execution, not dry-run
        google_ads_client = None
        if not dry_run:
            try:
                google_ads_client = get_google_ads_client(config)
            except FileNotFoundError as e:
                return jsonify({
                    "success": False,
                    "message": "Google Ads credentials not found",
                    "error": "Please configure Google Ads API credentials in secrets/google-ads.yaml"
                }), 500
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": "Google Ads authentication failed",
                    "error": str(e)
                }), 500
        
        executor = Executor(config.customer_id, config.db_path, google_ads_client)
        
        # Execute batch (pass list of Recommendation objects, not dicts)
        rec_objs = [rec for _, rec in selected_recs]
        try:
            execution_summary = executor.execute(rec_objs, dry_run=dry_run)
            # Executor returns: {"total": N, "successful": X, "failed": Y, "results": [...]}
            
            # Match results back to recommendation IDs
            results = []
            for i, (rec_id, _) in enumerate(selected_recs):
                if i < len(execution_summary["results"]):
                    result = execution_summary["results"][i]
                    results.append({
                        "recommendation_id": rec_id,
                        "success": result["success"],
                        "message": result.get("message", ""),
                        "change_id": result.get("change_id")
                    })
            
            return jsonify({
                "success": True,
                "message": f"Batch execution {'dry-run' if dry_run else 'live'} complete",
                "results": results,
                "summary": {
                    "total": execution_summary["total"],
                    "successful": execution_summary["successful"],
                    "failed": execution_summary["failed"]
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Batch execution error: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Batch execution failed",
                "error": str(e)
            }), 500
            
    except Exception as e:
        logging.error(f"Request error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Request failed",
            "error": str(e)
        }), 500


@bp.route("/status/<change_id>", methods=["GET"])
@login_required
def get_status(change_id):
    """
    Get status of an executed change.
    
    Returns JSON:
        {
            "success": bool,
            "change": {
                "change_id": int,
                "campaign_id": int,
                "change_type": str,
                "status": str,
                "created_at": str,
                "executed_at": str,
                "predicted_impact": {...}
            }
        }
    """
    try:
        config = get_current_config()
        
        # Query change_log table in warehouse
        conn = duckdb.connect(config.db_path)
        
        result = conn.execute("""
            SELECT 
                change_id,
                campaign_id,
                change_type,
                status,
                created_at,
                executed_at,
                predicted_impact
            FROM change_log
            WHERE change_id = ?
        """, [int(change_id)]).fetchone()
        
        conn.close()
        
        if not result:
            return jsonify({
                "success": False,
                "message": "Change not found",
                "error": f"No change found with ID {change_id}"
            }), 404
        
        # Parse result
        change = {
            "change_id": result[0],
            "campaign_id": result[1],
            "change_type": result[2],
            "status": result[3],
            "created_at": result[4].isoformat() if result[4] else None,
            "executed_at": result[5].isoformat() if result[5] else None,
            "predicted_impact": json.loads(result[6]) if result[6] else None
        }
        
        return jsonify({
            "success": True,
            "change": change
        }), 200
        
    except Exception as e:
        logging.error(f"Status query error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Query failed",
            "error": str(e)
        }), 500


@bp.route("/approve/<int:change_id>", methods=["POST"])
@login_required
def approve_change(change_id):
    """
    Approve a pending change (mark as approved).
    
    Returns JSON:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        config = get_current_config()
        
        # Update change_log table
        conn = duckdb.connect(config.db_path)
        
        conn.execute("""
            UPDATE change_log
            SET status = 'approved'
            WHERE change_id = ?
            AND status = 'pending'
        """, [change_id])
        
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Change {change_id} approved"
        }), 200
        
    except Exception as e:
        logging.error(f"Approve error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Approval failed",
            "error": str(e)
        }), 500


@bp.route("/reject/<int:change_id>", methods=["POST"])
@login_required
def reject_change(change_id):
    """
    Reject a pending change (mark as rejected).
    
    Request JSON (optional):
        {
            "reason": str  # Reason for rejection
        }
    
    Returns JSON:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        data = request.get_json() or {}
        reason = data.get("reason", "Rejected by user")
        
        config = get_current_config()
        
        # Update change_log table
        conn = duckdb.connect(config.db_path)
        
        conn.execute("""
            UPDATE change_log
            SET status = 'rejected',
                notes = ?
            WHERE change_id = ?
            AND status = 'pending'
        """, [reason, change_id])
        
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Change {change_id} rejected"
        }), 200
        
    except Exception as e:
        logging.error(f"Reject error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Rejection failed",
            "error": str(e)
        }), 500


# ==================== CHAT 32: LEADS ENDPOINT ====================

logger = logging.getLogger(__name__)


def _ensure_leads_table(conn):
    """
    Create leads table if it doesn't exist.
    
    Args:
        conn: DuckDB connection
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            company VARCHAR,
            role VARCHAR,
            looking_for VARCHAR,
            phone VARCHAR,
            source VARCHAR DEFAULT 'website',
            ip_address VARCHAR,
            user_agent VARCHAR,
            status VARCHAR DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)
    
    # Add sequence if it doesn't exist
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS leads_seq START 1
    """)


def validate_email(email):
    """
    Validate email format (basic regex).
    Returns bool.
    """
    if not email or not isinstance(email, str):
        return False
    
    # Permissive regex: allows most valid email formats including + and dots
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email.strip()))


def sanitize_input(text):
    """
    Sanitize text input by stripping whitespace and removing HTML tags.
    Returns sanitized string.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove HTML tags (basic XSS prevention)
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove potential script content
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text


def validate_lead_data(data):
    """
    Validate lead submission data.
    
    Returns:
        (is_valid, errors_dict) tuple
        - is_valid: bool
        - errors_dict: dict of field -> error message
    """
    errors = {}
    
    # Required: name
    name = data.get('name', '').strip()
    if not name:
        errors['name'] = 'Name is required'
    elif len(name) < 2:
        errors['name'] = 'Name must be at least 2 characters'
    elif len(name) > 100:
        errors['name'] = 'Name must be less than 100 characters'
    
    # Required: email
    email = data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Invalid email format'
    
    # Optional: company
    company = data.get('company', '').strip()
    if company and len(company) > 100:
        errors['company'] = 'Company name must be less than 100 characters'
    
    # Optional: role
    role = data.get('role', '').strip()
    if role and len(role) > 100:
        errors['role'] = 'Role must be less than 100 characters'
    
    # Optional: looking_for
    looking_for = data.get('looking_for', '').strip()
    if looking_for and len(looking_for) > 500:
        errors['looking_for'] = 'Message must be less than 500 characters'
    
    # Optional: phone
    phone = data.get('phone', '').strip()
    if phone and len(phone) > 50:
        errors['phone'] = 'Phone number must be less than 50 characters'
    
    is_valid = len(errors) == 0
    return is_valid, errors


@bp.route("/leads", methods=["POST", "OPTIONS"])
def submit_lead():
    """
    Contact form submission endpoint for christopherhoole.online website.
    
    Accepts POST requests with lead data, validates, stores in warehouse.duckdb,
    and optionally sends email notification.
    
    Also handles OPTIONS preflight requests for CORS.
    
    CSRF EXEMPT: This endpoint is called from external website (christopherhoole.online)
    which cannot obtain CSRF tokens. Protected by rate limiting instead.
    
    Request JSON:
        {
            "name": str (required),
            "email": str (required),
            "company": str (optional),
            "role": str (optional),
            "looking_for": str (optional),
            "phone": str (optional)
        }
    
    Returns JSON:
        Success: {"success": true, "message": str, "lead_id": int}
        Error: {"success": false, "message": str, "errors": {...}}
    """
    # CORS headers for all responses
    allowed_origins = [
        'https://www.christopherhoole.online',
        'https://christopherhoole.online',
        'http://localhost:3000'
    ]
    
    origin = request.headers.get('Origin')
    cors_headers = {}
    
    if origin in allowed_origins:
        cors_headers = {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return ('', 200, cors_headers)
    
    # Rate limiting: 3 submissions per hour per IP
    ip_address = request.remote_addr or 'unknown'
    rate_key = f"leads:{ip_address}"
    allowed, remaining, reset_seconds = check_rate_limit(rate_key, limit=3, window=3600)
    
    if not allowed:
        logger.warning(f"Rate limit exceeded for IP {ip_address}")
        response = jsonify({
            "success": False,
            "message": "Too many submissions. Please try again later.",
            "error": f"Maximum 3 submissions per hour. Try again in {reset_seconds // 60} minutes."
        })
        return (response, 429, cors_headers)
    
    try:
        # Parse JSON request
        data = request.get_json()
        
        if not data:
            response = jsonify({
                "success": False,
                "message": "Invalid request",
                "error": "Request body must be JSON"
            })
            return (response, 400, cors_headers)
        
        # Validate lead data
        is_valid, errors = validate_lead_data(data)
        
        if not is_valid:
            logger.info(f"Lead submission validation failed from {ip_address}: {errors}")
            response = jsonify({
                "success": False,
                "message": "Validation failed",
                "errors": errors
            })
            return (response, 400, cors_headers)
        
        # Sanitize all inputs
        name = sanitize_input(data.get('name', ''))
        email = sanitize_input(data.get('email', ''))
        company = sanitize_input(data.get('company', ''))
        role = sanitize_input(data.get('role', ''))
        looking_for = sanitize_input(data.get('looking_for', ''))
        phone = sanitize_input(data.get('phone', ''))
        
        # Get user agent for analytics
        user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length
        
        # Database connection (warehouse.duckdb - writable)
        # Following lesson #21: open read-write, no ATTACH needed for warehouse.duckdb writes
        conn = duckdb.connect('warehouse.duckdb')
        
        # Ensure leads table exists
        _ensure_leads_table(conn)
        
        # Insert lead
        result = conn.execute("""
            INSERT INTO leads (
                name, email, company, role, looking_for, phone,
                source, ip_address, user_agent, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING lead_id
        """, [
            name, email, company, role, looking_for, phone,
            'website', ip_address, user_agent, 'new'
        ]).fetchone()
        
        lead_id = result[0]
        conn.close()
        
        logger.info(f"Lead {lead_id} created: {name} <{email}> from {ip_address}")
        
        # Optional: Send email notification
        # Fully optional - don't block lead submission if email fails
        try:
            # Check if SMTP configured (would be in app config or environment)
            # For MVP, just log that email would be sent
            # Future: Implement actual email sending here
            logger.info(f"Email notification: New lead {lead_id} from {name} ({email})")
            # send_lead_notification_email(lead_id, name, email, company, role, looking_for, phone)
        except Exception as e:
            logger.warning(f"Email notification failed for lead {lead_id}: {e}")
            # Continue - don't block lead submission
        
        # Success response
        response = jsonify({
            "success": True,
            "message": "Thank you! We'll be in touch soon.",
            "lead_id": lead_id
        })
        return (response, 200, cors_headers)
        
    except Exception as e:
        logger.error(f"Lead submission error from {ip_address}: {str(e)}")
        response = jsonify({
            "success": False,
            "message": "Submission failed",
            "error": "An unexpected error occurred. Please try again."
        })
        return (response, 500, cors_headers)
