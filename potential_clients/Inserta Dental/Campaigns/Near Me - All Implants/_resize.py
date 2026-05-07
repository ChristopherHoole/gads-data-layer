"""Resize all PNG/JPG images in this folder to max 1300px on the longest side.
Overwrites originals. Run after taking screenshots.

Usage:  python _resize.py
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_SIDE = 1300

for name in os.listdir(HERE):
    if not name.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue
    path = os.path.join(HERE, name)
    try:
        img = Image.open(path)
        w, h = img.size
        longest = max(w, h)
        if longest <= MAX_SIDE:
            print(f'skip (already small): {name}  {w}x{h}')
            continue
        scale = MAX_SIDE / longest
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img.save(path, optimize=True)
        print(f'resized: {name}  {w}x{h} -> {new_w}x{new_h}')
    except Exception as e:
        print(f'FAILED: {name}  {e}')
