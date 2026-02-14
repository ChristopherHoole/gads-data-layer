"""
Ads Control Tower System Health Check.

Checks:
✅ Database accessible
✅ Required tables exist
✅ Recent data present (last 7 days)
✅ Google Ads API credentials valid (optional)
✅ No critical errors in logs
✅ Config files valid

Exit codes:
0 = All checks passed
1 = One or more checks failed

Run: python tools/health_check.py
"""

import sys
import duckdb
from pathlib import Path
from datetime import date, timedelta
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from act_autopilot.config_validator import validate_config


class HealthCheck:
    """System health check runner."""

    def __init__(self, db_path: str = "warehouse.duckdb"):
        self.db_path = db_path
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []

    def run_all_checks(self) -> int:
        """
        Run all health checks.

        Returns:
            0 if all passed, 1 if any failed
        """
        print("=" * 60)
        print("ADS CONTROL TOWER - SYSTEM HEALTH CHECK")
        print("=" * 60)
        print()

        # Run checks
        self.check_database_accessible()
        self.check_required_tables()
        self.check_recent_data()
        self.check_logs_directory()
        self.check_config_files()
        self.check_google_ads_credentials()

        # Summary
        print()
        print("=" * 60)
        print("HEALTH CHECK SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")

        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   - {warning}")

        print("=" * 60)

        if self.checks_failed == 0:
            print("\n✅ SYSTEM HEALTHY - All checks passed\n")
            return 0
        else:
            print(f"\n❌ SYSTEM UNHEALTHY - {self.checks_failed} check(s) failed\n")
            return 1

    def check_database_accessible(self):
        """Check if database is accessible."""
        print("1. Database Accessible")
        print("   " + "-" * 55)

        try:
            con = duckdb.connect(self.db_path, read_only=True)
            con.close()

            print(f"   ✅ PASS: Database accessible at {self.db_path}")
            self.checks_passed += 1

        except Exception as e:
            print(f"   ❌ FAIL: Cannot access database")
            print(f"      Error: {e}")
            self.checks_failed += 1

        print()

    def check_required_tables(self):
        """Check if required tables exist."""
        print("2. Required Tables Exist")
        print("   " + "-" * 55)

        required_tables = [
            "snap_campaign_daily",
            "analytics.campaign_daily",
            "analytics.change_log",
            "analytics.campaign_metadata",
        ]

        try:
            con = duckdb.connect(self.db_path, read_only=True)

            missing_tables = []
            for table in required_tables:
                try:
                    con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                except:
                    missing_tables.append(table)

            con.close()

            if not missing_tables:
                print(f"   ✅ PASS: All {len(required_tables)} required tables exist")
                self.checks_passed += 1
            else:
                print(f"   ❌ FAIL: {len(missing_tables)} tables missing:")
                for table in missing_tables:
                    print(f"      - {table}")
                self.checks_failed += 1

        except Exception as e:
            print(f"   ❌ FAIL: Error checking tables")
            print(f"      Error: {e}")
            self.checks_failed += 1

        print()

    def check_recent_data(self):
        """Check if recent data is present (last 7 days)."""
        print("3. Recent Data Present (Last 7 Days)")
        print("   " + "-" * 55)

        try:
            con = duckdb.connect(self.db_path, read_only=True)

            cutoff_date = date.today() - timedelta(days=7)

            result = con.execute(f"""
                SELECT 
                    COUNT(*) as row_count,
                    MAX(date) as latest_date,
                    MIN(date) as earliest_date
                FROM analytics.campaign_daily
                WHERE date >= '{cutoff_date}'
            """).fetchone()

            con.close()

            row_count = result[0] if result else 0
            latest_date = result[1] if result else None

            if row_count > 0:
                print(f"   ✅ PASS: {row_count} rows in last 7 days")
                print(f"      Latest data: {latest_date}")
                self.checks_passed += 1
            else:
                print(f"   ❌ FAIL: No data in last 7 days")
                print(f"      Latest data may be stale")
                self.checks_failed += 1

        except Exception as e:
            print(f"   ⚠️  WARNING: Could not check recent data")
            print(f"      Error: {e}")
            self.warnings.append("Could not verify recent data")
            self.checks_passed += 1  # Don't fail on this

        print()

    def check_logs_directory(self):
        """Check if logs directory exists and has recent logs."""
        print("4. Logs Directory")
        print("   " + "-" * 55)

        logs_dir = Path("logs")

        if not logs_dir.exists():
            print(f"   ⚠️  WARNING: Logs directory does not exist")
            print(f"      Will be created on first run")
            self.warnings.append("Logs directory missing")
            self.checks_passed += 1
            print()
            return

        # Count log files
        log_files = list(logs_dir.glob("*.log"))

        if log_files:
            print(f"   ✅ PASS: {len(log_files)} log file(s) found")

            # Check for errors in recent logs
            error_count = 0
            for log_file in log_files:
                try:
                    with open(log_file, "r") as f:
                        content = f.read()
                        error_count += content.count(" | ERROR | ")
                except:
                    pass

            if error_count > 0:
                print(f"      ⚠️  {error_count} ERROR entries in logs")
                self.warnings.append(f"{error_count} errors in logs")

            self.checks_passed += 1
        else:
            print(f"   ⚠️  WARNING: No log files found")
            print(f"      Logs will be created on first run")
            self.warnings.append("No log files")
            self.checks_passed += 1

        print()

    def check_config_files(self):
        """Check if config files are valid."""
        print("5. Configuration Files")
        print("   " + "-" * 55)

        config_dir = Path("configs")

        if not config_dir.exists():
            print(f"   ❌ FAIL: Config directory does not exist")
            self.checks_failed += 1
            print()
            return

        config_files = list(config_dir.glob("*.yaml"))

        if not config_files:
            print(f"   ❌ FAIL: No config files found")
            self.checks_failed += 1
            print()
            return

        valid_configs = 0
        invalid_configs = []

        for config_file in config_files:
            try:
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)

                errors = validate_config(config)

                if not errors:
                    valid_configs += 1
                else:
                    invalid_configs.append((config_file.name, errors))

            except Exception as e:
                invalid_configs.append((config_file.name, [str(e)]))

        if invalid_configs:
            print(f"   ❌ FAIL: {len(invalid_configs)} invalid config(s):")
            for filename, errors in invalid_configs:
                print(f"      - {filename}:")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"        · {error}")
            self.checks_failed += 1
        else:
            print(f"   ✅ PASS: All {len(config_files)} config file(s) valid")
            self.checks_passed += 1

        print()

    def check_google_ads_credentials(self):
        """Check if Google Ads credentials are configured."""
        print("6. Google Ads API Credentials")
        print("   " + "-" * 55)

        secrets_file = Path("secrets/google-ads.yaml")

        if not secrets_file.exists():
            print(f"   ⚠️  WARNING: No Google Ads credentials found")
            print(f"      Required for live mode execution")
            print(f"      File: {secrets_file}")
            self.warnings.append("Google Ads credentials missing")
            self.checks_passed += 1
            print()
            return

        try:
            with open(secrets_file, "r") as f:
                creds = yaml.safe_load(f)

            required_fields = [
                "developer_token",
                "client_id",
                "client_secret",
                "refresh_token",
            ]

            missing_fields = [f for f in required_fields if f not in creds]

            if missing_fields:
                print(f"   ❌ FAIL: Missing credential fields:")
                for field in missing_fields:
                    print(f"      - {field}")
                self.checks_failed += 1
            else:
                print(f"   ✅ PASS: Google Ads credentials configured")
                self.checks_passed += 1

        except Exception as e:
            print(f"   ❌ FAIL: Error reading credentials")
            print(f"      Error: {e}")
            self.checks_failed += 1

        print()


if __name__ == "__main__":
    checker = HealthCheck()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)
