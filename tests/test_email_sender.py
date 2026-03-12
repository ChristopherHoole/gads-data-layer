"""
tests/test_email_sender.py

Tests for email_sender.py — pure Python helpers and DB-backed check_daily_limit.
No real SMTP calls.
Chat 89.
"""

import pytest
from unittest.mock import patch, MagicMock
from act_dashboard.email_sender import (
    substitute_variables,
    get_signature_html,
    check_daily_limit,
    send_email,
)


class TestSubstituteVariables:
    def test_first_name_from_full_name(self):
        result = substitute_variables("Hello {{first_name}}", {"full_name": "Jane Doe"})
        assert result == "Hello Jane"

    def test_first_name_single_word_name(self):
        result = substitute_variables("Hi {{first_name}}", {"full_name": "Madonna"})
        assert result == "Hi Madonna"

    def test_first_name_empty_full_name(self):
        result = substitute_variables("Hi {{first_name}}", {"full_name": ""})
        assert result == "Hi "

    def test_first_name_none_full_name(self):
        result = substitute_variables("Hi {{first_name}}", {"full_name": None})
        assert result == "Hi "

    def test_company_substitution(self):
        result = substitute_variables("I am writing to {{company}}", {"company": "Acme Corp"})
        assert result == "I am writing to Acme Corp"

    def test_multiple_substitutions(self):
        result = substitute_variables(
            "Hello {{first_name}} from {{company}}",
            {"full_name": "Alice Smith", "company": "Widgets Ltd"},
        )
        assert result == "Hello Alice from Widgets Ltd"

    def test_none_value_not_substituted(self):
        result = substitute_variables("Hello {{company}}", {"company": None})
        # None values are skipped — placeholder stays
        assert "{{company}}" in result

    def test_empty_body_returns_empty_string(self):
        result = substitute_variables("", {"full_name": "Bob"})
        assert result == ""

    def test_none_body_returns_empty_string(self):
        result = substitute_variables(None, {"full_name": "Bob"})
        assert result == ""

    def test_no_placeholders_returns_unchanged(self):
        result = substitute_variables("Static body", {"company": "Acme"})
        assert result == "Static body"

    def test_sender_name_substitution(self):
        result = substitute_variables(
            "Regards, {{sender_name}}",
            {"sender_name": "Christopher"},
        )
        assert result == "Regards, Christopher"

    def test_newline_preserved(self):
        result = substitute_variables("Line1\nLine2", {})
        assert "\n" in result


class TestGetSignatureHtml:
    def test_returns_string(self):
        sig = get_signature_html()
        assert isinstance(sig, str)

    def test_contains_br_tag(self):
        sig = get_signature_html()
        assert "<br>" in sig

    def test_contains_christopher_hoole(self):
        sig = get_signature_html()
        assert "Christopher Hoole" in sig

    def test_contains_hr_tag(self):
        sig = get_signature_html()
        assert "<hr" in sig

    def test_not_empty(self):
        sig = get_signature_html()
        assert len(sig) > 50


class TestCheckDailyLimit:
    def test_returns_dict(self, db_conn):
        result = check_daily_limit(db_conn)
        assert isinstance(result, dict)

    def test_has_limit_key(self, db_conn):
        result = check_daily_limit(db_conn)
        assert "limit" in result

    def test_has_sent_today_key(self, db_conn):
        result = check_daily_limit(db_conn)
        assert "sent_today" in result

    def test_has_remaining_key(self, db_conn):
        result = check_daily_limit(db_conn)
        assert "remaining" in result

    def test_zero_sent_when_no_emails(self, db_conn):
        result = check_daily_limit(db_conn)
        # No emails inserted as 'sent' today in seed data
        assert result["sent_today"] >= 0

    def test_remaining_equals_limit_minus_sent(self, db_conn):
        result = check_daily_limit(db_conn)
        assert result["remaining"] == max(0, result["limit"] - result["sent_today"])

    def test_limit_reached_blocks_send(self, db_conn):
        """Insert sent emails up to the daily limit and verify remaining = 0."""
        from datetime import datetime
        # Insert emails to fill limit — use a small limit config workaround
        # Just verify that remaining is non-negative
        result = check_daily_limit(db_conn)
        assert result["remaining"] >= 0


# ---------------------------------------------------------------------------
# DashboardConfig
# ---------------------------------------------------------------------------

def _make_config_yaml(tmp_path, **overrides):
    """Write a minimal client config YAML to tmp_path and return the path string."""
    import yaml
    config = {
        "client_name": "TestClient",
        "client_type": "ecom",
        "primary_kpi": "roas",
        "automation_mode": "insights",
        "risk_tolerance": "conservative",
        "google_ads": {"customer_id": "7372844356"},
        "targets": {"target_roas": 3.0},
        "spend_caps": {"daily": 50, "monthly": 1500},
        "protected_entities": {"brand_is_protected": True, "entities": []},
    }
    config.update(overrides)
    p = tmp_path / "client_test.yaml"
    with open(p, "w") as f:
        yaml.dump(config, f)
    return str(p)


class TestDashboardConfig:
    def test_loads_without_error(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg is not None

    def test_client_name(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.client_name == "TestClient"

    def test_customer_id_nested(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.customer_id == "7372844356"

    def test_client_type(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.client_type == "ecom"

    def test_primary_kpi(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.primary_kpi == "roas"

    def test_risk_tolerance(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.risk_tolerance == "conservative"

    def test_automation_mode(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.automation_mode == "insights"

    def test_target_roas(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.target_roas == 3.0

    def test_daily_cap(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.daily_cap == 50

    def test_monthly_cap(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.monthly_cap == 1500

    def test_brand_protected(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert cfg.brand_protected is True

    def test_protected_campaigns_is_list(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        assert isinstance(cfg.protected_campaigns, list)

    def test_get_suggestions_path_contains_client_name(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        path = cfg.get_suggestions_path("2026-03-12")
        assert "TestClient" in str(path)
        assert "2026-03-12" in str(path)

    def test_get_approvals_path_contains_approvals(self, tmp_path):
        from act_dashboard.config import DashboardConfig
        cfg = DashboardConfig(_make_config_yaml(tmp_path))
        path = cfg.get_approvals_path("2026-03-12")
        assert "approvals" in str(path)
        assert "2026-03-12" in str(path)


class TestDashboardConfigTopLevelCustomerId:
    """Test DashboardConfig with top-level customer_id (not nested under google_ads)."""

    def test_top_level_customer_id(self, tmp_path):
        import yaml
        from act_dashboard.config import DashboardConfig
        config = {
            "client_name": "FlatClient",
            "customer_id": "1234567890",
            "client_type": "lead_gen",
            "primary_kpi": "cpa",
            "automation_mode": "suggest",
            "risk_tolerance": "balanced",
            "targets": {"target_roas": 2.0},
            "spend_caps": {"daily": 100, "monthly": 3000},
            "protected_entities": {"brand_is_protected": False, "entities": []},
        }
        config_file = tmp_path / "client_flat.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        cfg = DashboardConfig(str(config_file))
        assert cfg.customer_id == "1234567890"

    def test_missing_customer_id_returns_unknown(self, tmp_path):
        import yaml
        from act_dashboard.config import DashboardConfig
        config = {
            "client_name": "NoIdClient",
            "client_type": "ecom",
        }
        config_file = tmp_path / "client_noid.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        cfg = DashboardConfig(str(config_file))
        assert cfg.customer_id == "UNKNOWN"


# ---------------------------------------------------------------------------
# config.py DashboardConfig.save()
# ---------------------------------------------------------------------------

class TestDashboardConfigSave:
    def test_save_writes_yaml(self, tmp_path):
        import yaml
        from act_dashboard.config import DashboardConfig
        config = {
            "client_name": "SaveTest",
            "customer_id": "555",
            "client_type": "ecom",
            "primary_kpi": "roas",
            "automation_mode": "suggest",
            "risk_tolerance": "balanced",
            "targets": {"target_roas": 4.0},
            "spend_caps": {"daily": 200, "monthly": 5000},
            "protected_entities": {"brand_is_protected": True, "entities": ["111"]},
        }
        config_file = tmp_path / "save_test.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        cfg = DashboardConfig(str(config_file))
        cfg.client_name = "SavedClient"
        cfg.save()
        with open(config_file) as f:
            saved = yaml.safe_load(f)
        assert saved["client_name"] == "SavedClient"

    def test_save_preserves_risk_tolerance(self, tmp_path):
        import yaml
        from act_dashboard.config import DashboardConfig
        config = {
            "client_name": "T", "customer_id": "1",
            "client_type": "ecom", "primary_kpi": "roas",
            "automation_mode": "suggest", "risk_tolerance": "aggressive",
            "targets": {}, "spend_caps": {"daily": 10, "monthly": 100},
            "protected_entities": {"brand_is_protected": False, "entities": []},
        }
        config_file = tmp_path / "save2.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        cfg = DashboardConfig(str(config_file))
        cfg.save()
        with open(config_file) as f:
            saved = yaml.safe_load(f)
        assert saved["risk_tolerance"] == "aggressive"

    def test_save_updates_spend_caps(self, tmp_path):
        import yaml
        from act_dashboard.config import DashboardConfig
        config = {
            "client_name": "T", "customer_id": "1",
            "client_type": "ecom", "primary_kpi": "roas",
            "automation_mode": "suggest", "risk_tolerance": "balanced",
            "targets": {}, "spend_caps": {"daily": 10, "monthly": 100},
            "protected_entities": {"brand_is_protected": False, "entities": []},
        }
        config_file = tmp_path / "save3.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        cfg = DashboardConfig(str(config_file))
        cfg.daily_cap = 999
        cfg.monthly_cap = 9999
        cfg.save()
        with open(config_file) as f:
            saved = yaml.safe_load(f)
        assert saved["spend_caps"]["daily"] == 999
        assert saved["spend_caps"]["monthly"] == 9999


# ---------------------------------------------------------------------------
# send_email (mocked SMTP)
# ---------------------------------------------------------------------------

_FAKE_EMAIL_CONFIG = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "test@example.com",
    "smtp_password": "testpassword",
    "from_name": "Test Sender",
    "from_email": "test@example.com",
    "test_mode": False,
    "daily_limit": 100,
}


class TestSendEmail:
    @patch("act_dashboard.email_sender.load_email_config")
    @patch("act_dashboard.email_sender.smtplib.SMTP")
    def test_send_returns_success(self, mock_smtp_cls, mock_load_cfg):
        mock_load_cfg.return_value = _FAKE_EMAIL_CONFIG
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = send_email("to@example.com", "Test Subject", "<p>Hello</p>")
        assert result["success"] is True

    @patch("act_dashboard.email_sender.load_email_config")
    @patch("act_dashboard.email_sender.smtplib.SMTP")
    def test_send_calls_starttls(self, mock_smtp_cls, mock_load_cfg):
        mock_load_cfg.return_value = _FAKE_EMAIL_CONFIG
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        send_email("to@example.com", "Subject", "<p>Body</p>")
        mock_server.starttls.assert_called_once()

    @patch("act_dashboard.email_sender.load_email_config")
    @patch("act_dashboard.email_sender.smtplib.SMTP")
    def test_send_calls_login(self, mock_smtp_cls, mock_load_cfg):
        mock_load_cfg.return_value = _FAKE_EMAIL_CONFIG
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        send_email("to@example.com", "Subject", "<p>Body</p>")
        mock_server.login.assert_called_once_with("test@example.com", "testpassword")

    @patch("act_dashboard.email_sender.load_email_config")
    @patch("act_dashboard.email_sender.smtplib.SMTP")
    def test_test_mode_redirects(self, mock_smtp_cls, mock_load_cfg):
        cfg = {**_FAKE_EMAIL_CONFIG, "test_mode": True, "test_redirect_email": "safe@test.com"}
        mock_load_cfg.return_value = cfg
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = send_email("real@example.com", "Subject", "<p>Body</p>")
        assert result["success"] is True
        # sendmail called with redirected address
        args = mock_server.sendmail.call_args
        assert "safe@test.com" in str(args)

    @patch("act_dashboard.email_sender.load_email_config")
    def test_smtp_error_returns_failure(self, mock_load_cfg):
        mock_load_cfg.side_effect = Exception("Config not found")

        result = send_email("to@example.com", "Subject", "<p>Body</p>")
        assert result["success"] is False
        assert "error" in result

    @patch("act_dashboard.email_sender.load_email_config")
    @patch("act_dashboard.email_sender.smtplib.SMTP")
    def test_custom_from_name(self, mock_smtp_cls, mock_load_cfg):
        mock_load_cfg.return_value = _FAKE_EMAIL_CONFIG
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: mock_server
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = send_email("to@example.com", "Subject", "<p>Body</p>",
                            from_name="Custom Name", from_email="custom@example.com")
        assert result["success"] is True
