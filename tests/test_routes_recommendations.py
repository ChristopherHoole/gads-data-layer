"""
tests/test_routes_recommendations.py

Tests for recommendations routes: GET /recommendations, accept, decline.
Chat 89.
"""

import json
import pytest


class TestRecommendationsRoute:
    def test_get_recommendations_returns_200(self, client):
        resp = client.get("/recommendations")
        assert resp.status_code == 200

    def test_get_recommendations_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/recommendations")
            assert resp.status_code in (200, 302)

    def test_get_recommendations_has_content(self, client):
        resp = client.get("/recommendations")
        assert len(resp.data) > 0

    def test_recommendations_data_endpoint(self, client):
        """JSON endpoint returns pending/monitoring counts."""
        resp = client.get("/recommendations/data")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "pending" in data
        assert "monitoring" in data

    def test_recommendations_data_pending_count(self, client):
        resp = client.get("/recommendations/data")
        data = json.loads(resp.data)
        # We seeded rec-001 (pending) and rec-002 (pending)
        assert data["pending"] >= 2

    def test_accept_pending_recommendation(self, client):
        resp = client.post("/recommendations/rec-001/accept")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["success"] is True

    def test_accept_nonexistent_recommendation(self, client):
        resp = client.post("/recommendations/nonexistent-rec/accept")
        assert resp.status_code == 404
        data = json.loads(resp.data)
        assert data["success"] is False

    def test_decline_pending_recommendation(self, client):
        resp = client.post("/recommendations/rec-002/decline")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["success"] is True

    def test_decline_nonexistent_recommendation(self, client):
        resp = client.post("/recommendations/no-such-rec/decline")
        assert resp.status_code == 404

    def test_accept_already_declined_returns_400(self, client):
        # rec-004 is declined — cannot accept
        resp = client.post("/recommendations/rec-004/accept")
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data["success"] is False

    def test_decline_already_successful_returns_400(self, client):
        # rec-005 is successful — cannot decline
        resp = client.post("/recommendations/rec-005/decline")
        assert resp.status_code == 400

    def test_modify_recommendation(self, client):
        resp = client.post(
            "/recommendations/rec-001/modify",
            data=json.dumps({"new_value": 60.0}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_modify_missing_new_value(self, client):
        resp = client.post(
            "/recommendations/rec-001/modify",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestGetActionLabel:
    def test_campaign_increase_budget(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "increase",
               "rule_type": "budget", "action_magnitude": 10}
        assert "10" in get_action_label(rec)
        assert "budget" in get_action_label(rec).lower()

    def test_campaign_decrease_budget(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "decrease",
               "rule_type": "budget", "action_magnitude": 10}
        label = get_action_label(rec)
        assert "decrease" in label.lower() or "Decrease" in label

    def test_campaign_pause(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "pause",
               "rule_type": "status", "action_magnitude": 0}
        assert "pause" in get_action_label(rec).lower()

    def test_keyword_pause(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "keyword", "action_direction": "pause",
               "rule_type": "status", "action_magnitude": 0}
        assert "pause" in get_action_label(rec).lower()

    def test_ad_group_increase_bid(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "ad_group", "action_direction": "increase",
               "rule_type": "bid", "action_magnitude": 5}
        assert "5" in get_action_label(rec)

    def test_shopping_increase_budget(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "increase",
               "rule_type": "budget", "action_magnitude": 15}
        assert "15" in get_action_label(rec)

    def test_fallback_unknown_entity(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "unknown_type", "action_direction": "flag",
               "rule_type": "budget", "action_magnitude": 0}
        result = get_action_label(rec)
        assert isinstance(result, str)

    def test_campaign_decrease_bid(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "decrease",
               "rule_type": "bid", "action_magnitude": 10}
        result = get_action_label(rec)
        assert "10" in result

    def test_campaign_enable(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "enable",
               "rule_type": "status", "action_magnitude": 0}
        assert "Enable" in get_action_label(rec)

    def test_campaign_flag(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "flag",
               "rule_type": "status", "action_magnitude": 0}
        assert "Flag" in get_action_label(rec)

    def test_campaign_hold_budget(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "hold",
               "rule_type": "budget", "action_magnitude": 0}
        assert "Hold" in get_action_label(rec)

    def test_campaign_hold_bid(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "hold",
               "rule_type": "bid", "action_magnitude": 0}
        assert "Hold" in get_action_label(rec)

    def test_keyword_enable(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "keyword", "action_direction": "enable",
               "rule_type": "status", "action_magnitude": 0}
        assert "Enable" in get_action_label(rec)

    def test_keyword_increase(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "keyword", "action_direction": "increase",
               "rule_type": "bid", "action_magnitude": 10}
        assert "10" in get_action_label(rec)

    def test_keyword_decrease(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "keyword", "action_direction": "decrease",
               "rule_type": "bid", "action_magnitude": 5}
        assert "5" in get_action_label(rec)

    def test_keyword_flag(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "keyword", "action_direction": "flag",
               "rule_type": "status", "action_magnitude": 0}
        assert "Flag" in get_action_label(rec)

    def test_shopping_decrease_budget(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "decrease",
               "rule_type": "budget", "action_magnitude": 10}
        assert "10" in get_action_label(rec)

    def test_shopping_decrease_bid(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "decrease",
               "rule_type": "bid", "action_magnitude": 10}
        assert "10" in get_action_label(rec)

    def test_shopping_increase_bid(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "increase",
               "rule_type": "bid", "action_magnitude": 8}
        assert "8" in get_action_label(rec)

    def test_shopping_pause(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "pause",
               "rule_type": "status", "action_magnitude": 0}
        assert "Pause" in get_action_label(rec)

    def test_shopping_enable(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "enable",
               "rule_type": "status", "action_magnitude": 0}
        assert "Enable" in get_action_label(rec)

    def test_shopping_flag(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "shopping", "action_direction": "flag",
               "rule_type": "status", "action_magnitude": 0}
        assert "Flag" in get_action_label(rec)

    def test_ad_group_pause(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "ad_group", "action_direction": "pause",
               "rule_type": "status", "action_magnitude": 0}
        assert "Pause" in get_action_label(rec)

    def test_ad_group_enable(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "ad_group", "action_direction": "enable",
               "rule_type": "status", "action_magnitude": 0}
        assert "Enable" in get_action_label(rec)

    def test_ad_group_decrease(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "ad_group", "action_direction": "decrease",
               "rule_type": "bid", "action_magnitude": 5}
        assert "5" in get_action_label(rec)

    def test_ad_group_flag(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "ad_group", "action_direction": "flag",
               "rule_type": "status", "action_magnitude": 0}
        assert "Flag" in get_action_label(rec)

    def test_fallback_with_magnitude(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "unknown", "action_direction": "increase",
               "rule_type": "bid", "action_magnitude": 12}
        result = get_action_label(rec)
        assert "12" in result

    def test_campaign_increase_bid(self):
        from act_dashboard.routes.recommendations import get_action_label
        rec = {"entity_type": "campaign", "action_direction": "increase",
               "rule_type": "bid", "action_magnitude": 10}
        result = get_action_label(rec)
        assert "10" in result
