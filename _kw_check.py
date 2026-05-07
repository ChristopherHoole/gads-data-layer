import sys
path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\User\Desktop\dentalbydesign-repo\apps\web\src\pages\google\dental-implant-clinic-near-me.astro'
keywords = sys.argv[2].split('|') if len(sys.argv) > 2 else []
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().lower()
for kw in keywords:
    n = text.count(kw.lower())
    flag = 'OK' if n >= 1 else 'MISS'
    print(f"  [{flag}] {n:>3}  {kw}")
