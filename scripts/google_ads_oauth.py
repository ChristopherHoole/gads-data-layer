# File: scripts/google_ads_oauth.py
# Purpose: Generate a Google Ads OAuth refresh token (Desktop app flow) and write secrets/google-ads.yaml

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except Exception as e:
    raise SystemExit(
        "Missing dependency: google-auth-oauthlib.\n"
        "Install it with:\n"
        "  python -m pip install google-auth-oauthlib\n"
        f"\nOriginal error: {e}"
    )

try:
    import yaml  # type: ignore
except Exception as e:
    raise SystemExit(
        "Missing dependency: PyYAML.\n"
        "Install it with:\n"
        "  python -m pip install pyyaml\n"
        f"\nOriginal error: {e}"
    )


ADWORDS_SCOPE = "https://www.googleapis.com/auth/adwords"


def _read_client_secret(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Client secret JSON not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Failed to read JSON: {path}\n{e}")

    if "installed" in data:
        return data["installed"]
    if "web" in data:
        return data["web"]
    raise SystemExit(
        "Unexpected client secret JSON format. Expected top-level 'installed' or 'web' object."
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--client-secret",
        default=str(Path("secrets") / "google_ads_client_secret.json"),
        help="Path to OAuth client secret JSON (Desktop app).",
    )
    p.add_argument(
        "--out-yaml",
        default=str(Path("secrets") / "google-ads.yaml"),
        help="Output path for google-ads.yaml",
    )
    p.add_argument(
        "--developer-token",
        default=os.environ.get("GADS_DEVELOPER_TOKEN", ""),
        help="Optional developer token (or set env var GADS_DEVELOPER_TOKEN).",
    )
    p.add_argument(
        "--login-customer-id",
        default=os.environ.get("GADS_LOGIN_CUSTOMER_ID", ""),
        help="Optional login_customer_id (MCC) (or set env var GADS_LOGIN_CUSTOMER_ID).",
    )
    p.add_argument(
        "--no-browser",
        action="store_true",
        help="Print auth URL instead of trying to auto-open a browser.",
    )
    args = p.parse_args()

    client_secret_path = Path(args.client_secret).resolve()
    out_yaml_path = Path(args.out_yaml).resolve()
    out_yaml_path.parent.mkdir(parents=True, exist_ok=True)

    _ = _read_client_secret(client_secret_path)  # validates file format

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        scopes=[ADWORDS_SCOPE],
    )

    if args.no_browser:
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        print("\nOPEN THIS URL IN YOUR BROWSER, THEN COMPLETE AUTH:\n")
        print(auth_url)
        print("\nAfter approving, paste the full redirect URL here and press Enter:")
        redirect_url = input("> ").strip()
        flow.fetch_token(authorization_response=redirect_url)
        creds = flow.credentials
    else:
        # Opens browser + runs a local callback server automatically
        creds = flow.run_local_server(
            host="localhost",
            port=0,
            authorization_prompt_message="Please visit this URL to authorize: {url}",
            success_message="Authorization complete. You can close this tab and return to PowerShell.",
            open_browser=True,
        )

    if not getattr(creds, "refresh_token", None):
        raise SystemExit(
            "No refresh_token returned. This usually happens if you previously authorized this client.\n"
            "Fix:\n"
            "  1) Go to https://myaccount.google.com/permissions and remove access for this OAuth app\n"
            "  2) Re-run this script\n"
            "  3) Ensure the flow uses prompt=consent + access_type=offline (this script does)"
        )

    # Minimal google-ads.yaml structure
    yaml_obj: Dict[str, Any] = {
        "use_proto_plus": True,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
    }

    if args.developer_token:
        yaml_obj["developer_token"] = args.developer_token
    if args.login_customer_id:
        # Google Ads expects no dashes
        yaml_obj["login_customer_id"] = (
            str(args.login_customer_id).replace("-", "").strip()
        )

    out_yaml_path.write_text(
        yaml.safe_dump(yaml_obj, sort_keys=False), encoding="utf-8"
    )

    print("\nOK: OAuth refresh token generated.")
    print(f"OK: Wrote: {out_yaml_path}")
    print("NOTE: Keep this file private (it contains credentials).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
