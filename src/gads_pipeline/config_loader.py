import yaml
from pathlib import Path
from pydantic import ValidationError
from .config_models import ClientConfig, parse_client_config

def load_client_config(path: str) -> ClientConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Client config not found: {path}")

    data = yaml.safe_load(p.read_text(encoding="utf8"))
    if not isinstance(data, dict):
        raise ValueError("Client config must be a YAML mapping/object")

    return parse_client_config(data)
