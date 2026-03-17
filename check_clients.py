"""
Diagnostic: Show full details of all ACT client configurations
"""
import yaml
from pathlib import Path

configs_dir = Path('configs')
print("=" * 70)
print("ACT CLIENT CONFIGURATIONS")
print("=" * 70)

config_files = sorted(configs_dir.glob('*.yaml'))
print(f"\nFound {len(config_files)} config files:\n")

for i, cf in enumerate(config_files):
    print(f"{'='*50}")
    print(f"File: {cf}")
    try:
        with open(cf) as f:
            cfg = yaml.safe_load(f)
        # Print every key/value
        for k, v in cfg.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"  ERROR reading: {e}")
    print()

print("=" * 70)
print("✅ Done.")
