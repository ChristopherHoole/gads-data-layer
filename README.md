# gads-data-layer

Local-first Google Ads data layer for Ads Control Tower.

## Quick start
1) Create venv + install
2) Configure `configs/google-ads.yaml` and a client config in `configs/`
3) Run:
   `python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 1`

## Notes
- Credentials/config files may contain secrets. Do not commit real production credentials.
