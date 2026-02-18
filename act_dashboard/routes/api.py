"""
API routes - execution, batch, status, approve, reject.
"""

from flask import Blueprint, request, jsonify, current_app
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_google_ads_client
from act_dashboard.utils import dict_to_recommendation, validate_recommendation_dict
from act_dashboard.validation import validate_execution_request, validate_batch_execution_request
from act_autopilot.executor import Executor
import duckdb
import json
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
                    "message": "This recommendation type cannot be executed via the dashboard",
                    "error": "Non-executable action type (e.g., review recommendations)"
                }), 400
            
            result = execution_summary["results"][0]
        except Exception as e:
            current_app.logger.error(f'Execution failed for rec_id {rec_id}: {str(e)}')
            return jsonify({
                "success": False,
                "message": "Execution failed",
                "error": str(e)
            }), 500
        
        # Log execution
        if result["success"]:
            current_app.logger.info(
                f'Execution successful: user={request.remote_addr}, '
                f'rec_id={rec_id}, page={page or "file"}, '
                f'dry_run={dry_run}, change_id={result.get("change_id")}'
            )
        else:
            current_app.logger.warning(
                f'Execution failed: user={request.remote_addr}, '
                f'rec_id={rec_id}, error={result.get("error")}'
            )
        
        # Return result (result is a dict, not an object)
        return jsonify({
            "success": result["success"],
            "message": result["message"],
            "change_id": result.get("change_id"),
            "error": result.get("error")
        })
        
    except Exception as e:
        current_app.logger.error(f'Unexpected error in execute_recommendation: {str(e)}')
        return jsonify({
            "success": False,
            "message": f"Execution failed: {str(e)}",
            "error": str(e)
        }), 500


@bp.route("/execute-batch", methods=["POST"])
@login_required
def execute_batch():
    """
    Execute multiple recommendations in batch.
    
    Request JSON:
        {
            "recommendation_ids": [int, int, ...],
            "date_str": str,
            "dry_run": bool
        }
        
    Returns JSON:
        {
            "success": bool,
            "results": [...],
            "summary": {"total": int, "succeeded": int, "failed": int}
        }
    """
    try:
        # Rate limit: 10 requests per minute per IP (stricter for batch)
        ip_address = request.remote_addr or 'unknown'
        rate_key = f"execute-batch:{ip_address}"
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
        page = data.get("page")  # 'keywords', 'ads', 'shopping'
        dry_run = data.get("dry_run", True)
        
        if not rec_ids:
            return jsonify({
                "success": False,
                "message": "No recommendations selected",
                "error": "recommendation_ids is required and must not be empty"
            }), 400
        
        config = get_current_config()
        
        # Load recommendations (from cache or file)
        if page:
            cache = current_app.config.get('RECOMMENDATIONS_CACHE', {})
            all_recommendations = cache.get(page, [])
            
            if not all_recommendations:
                return jsonify({
                    "success": False,
                    "message": f"No {page} recommendations in cache",
                    "error": f"Please refresh the {page} page"
                }), 404
        else:
            if not date_str:
                date_str = date.today().isoformat()
            
            suggestions_path = config.get_suggestions_path(date_str)
            if not suggestions_path.exists():
                return jsonify({
                    "success": False,
                    "message": "Recommendations file not found",
                    "error": f"No file for {date_str}"
                }), 404
            
            with open(suggestions_path, "r") as f:
                suggestions = json.load(f)
            all_recommendations = suggestions.get("recommendations", [])
        
        # Validate batch request
        is_valid, error_msg = validate_batch_execution_request(data, all_recommendations)
        if not is_valid:
            return jsonify({
                "success": False,
                "message": "Invalid batch request",
                "error": error_msg
            }), 400
        
        # Validate IDs and collect recommendations
        recs_to_execute = []
        for rec_id in rec_ids:
            rec_dict = all_recommendations[rec_id]
            
            # Validate and convert
            is_valid, error = validate_recommendation_dict(rec_dict)
            if not is_valid:
                return jsonify({
                    "success": False,
                    "message": f"Invalid recommendation at ID {rec_id}",
                    "error": error
                }), 400
            
            try:
                rec_obj = dict_to_recommendation(rec_dict)
                recs_to_execute.append(rec_obj)
            except (ValueError, TypeError) as e:
                return jsonify({
                    "success": False,
                    "message": f"Failed to convert recommendation {rec_id}",
                    "error": str(e)
                }), 500
        
        # Initialize executor
        google_ads_client = None
        if not dry_run:
            try:
                google_ads_client = get_google_ads_client(config)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": "Google Ads authentication failed",
                    "error": str(e)
                }), 500
        
        executor = Executor(config.customer_id, config.db_path, google_ads_client)
        
        # Execute batch
        try:
            execution_summary = executor.execute(recs_to_execute, dry_run=dry_run)
            
            # Log batch execution
            current_app.logger.info(
                f'Batch execution: user={request.remote_addr}, '
                f'count={len(rec_ids)}, page={page or "file"}, '
                f'dry_run={dry_run}, succeeded={execution_summary["successful"]}, '
                f'failed={execution_summary["failed"]}'
            )
            
            return jsonify({
                "success": True,
                "results": execution_summary["results"],
                "summary": {
                    "total": execution_summary["total"],
                    "succeeded": execution_summary["successful"],
                    "failed": execution_summary["failed"]
                }
            })
        except Exception as e:
            current_app.logger.error(f'Batch execution failed: {str(e)}')
            return jsonify({
                "success": False,
                "message": "Batch execution failed",
                "error": str(e)
            }), 500
            
    except Exception as e:
        current_app.logger.error(f'Unexpected error in execute_batch: {str(e)}')
        return jsonify({
            "success": False,
            "message": f"Batch execution failed: {str(e)}",
            "error": str(e)
        }), 500


@bp.route("/execution-status/<int:change_id>", methods=["GET"])
@login_required
def execution_status(change_id):
    """
    Get status of an executed change.
    
    Returns JSON:
        {
            "success": bool,
            "change_id": int,
            "status": str,
            "details": {...}
        }
    """
    try:
        config = get_current_config()
        conn = duckdb.connect(config.db_path, read_only=True)
        
        # Query change log
        query = """
        SELECT
            change_id,
            customer_id,
            change_date,
            campaign_id,
            lever,
            old_value,
            new_value,
            change_pct,
            rule_id,
            rollback_status,
            executed_at
        FROM analytics.change_log
        WHERE change_id = ?
        """
        
        result = conn.execute(query, [change_id]).fetchone()
        conn.close()
        
        if not result:
            return jsonify({
                "success": False,
                "message": "Change not found",
                "error": f"No change found with ID {change_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "change_id": result[0],
            "status": result[9] or "active",  # rollback_status
            "details": {
                "customer_id": result[1],
                "change_date": str(result[2]),
                "campaign_id": result[3],
                "lever": result[4],
                "old_value": result[5],
                "new_value": result[6],
                "change_pct": result[7],
                "rule_id": result[8],
                "executed_at": str(result[10])
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Status check failed: {str(e)}",
            "error": str(e)
        }), 500


@bp.route("/approve", methods=["POST"])
@login_required
def approve_recommendation():
    """API endpoint to approve a recommendation."""
    config = get_current_config()
    data = request.json
    date_str = data.get("date")
    rule_id = data.get("rule_id")
    entity_id = data.get("entity_id")
    campaign_name = data.get("campaign_name", "N/A")
    action_type = data.get("action_type")

    approvals_path = config.get_approvals_path(date_str)

    # Load or create approvals file
    if approvals_path.exists():
        with open(approvals_path, "r") as f:
            approvals = json.load(f)
    else:
        approvals = {
            "snapshot_date": date_str,
            "client_name": config.client_name,
            "reviewed_at": None,
            "total_reviewed": 0,
            "approved": 0,
            "rejected": 0,
            "skipped": 0,
            "decisions": [],
        }
        approvals_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove any existing decision for this recommendation
    approvals["decisions"] = [
        d
        for d in approvals["decisions"]
        if not (d["rule_id"] == rule_id and d["entity_id"] == entity_id)
    ]

    # Add new approval
    approvals["decisions"].append(
        {
            "rule_id": rule_id,
            "entity_id": entity_id,
            "campaign_name": campaign_name,
            "action_type": action_type,
            "decision": "approved",
            "reviewed_at": datetime.utcnow().isoformat() + "Z",
        }
    )

    # Update counts
    approvals["total_reviewed"] = len(approvals["decisions"])
    approvals["approved"] = len(
        [d for d in approvals["decisions"] if d["decision"] == "approved"]
    )
    approvals["rejected"] = len(
        [d for d in approvals["decisions"] if d["decision"] == "rejected"]
    )
    approvals["reviewed_at"] = datetime.utcnow().isoformat() + "Z"

    # Save
    with open(approvals_path, "w") as f:
        json.dump(approvals, f, indent=2)

    return jsonify({"success": True})


@bp.route("/reject", methods=["POST"])
@login_required
def reject_recommendation():
    """API endpoint to reject a recommendation."""
    config = get_current_config()
    data = request.json
    date_str = data.get("date")
    rule_id = data.get("rule_id")
    entity_id = data.get("entity_id")
    campaign_name = data.get("campaign_name", "N/A")
    action_type = data.get("action_type")

    approvals_path = config.get_approvals_path(date_str)

    # Load or create approvals file
    if approvals_path.exists():
        with open(approvals_path, "r") as f:
            approvals = json.load(f)
    else:
        approvals = {
            "snapshot_date": date_str,
            "client_name": config.client_name,
            "reviewed_at": None,
            "total_reviewed": 0,
            "approved": 0,
            "rejected": 0,
            "skipped": 0,
            "decisions": [],
        }
        approvals_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove any existing decision for this recommendation
    approvals["decisions"] = [
        d
        for d in approvals["decisions"]
        if not (d["rule_id"] == rule_id and d["entity_id"] == entity_id)
    ]

    # Add rejection
    approvals["decisions"].append(
        {
            "rule_id": rule_id,
            "entity_id": entity_id,
            "campaign_name": campaign_name,
            "action_type": action_type,
            "decision": "rejected",
            "reviewed_at": datetime.utcnow().isoformat() + "Z",
        }
    )

    # Update counts
    approvals["total_reviewed"] = len(approvals["decisions"])
    approvals["approved"] = len(
        [d for d in approvals["decisions"] if d["decision"] == "approved"]
    )
    approvals["rejected"] = len(
        [d for d in approvals["decisions"] if d["decision"] == "rejected"]
    )
    approvals["reviewed_at"] = datetime.utcnow().isoformat() + "Z"

    # Save
    with open(approvals_path, "w") as f:
        json.dump(approvals, f, indent=2)

    return jsonify({"success": True})
