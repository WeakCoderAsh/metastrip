#!/usr/bin/env python3
"""
TagHatao — AI images (aur kisi bhi image) se AI tags aur saara metadata saaf karta hai.
https://github.com/WeakCoderAsh/taghatao

Hatata hai:
  - EXIF (camera, GPS, software, date, artist, copyright...)
  - XMP / IPTC
  - PNG text chunks (ComfyUI / Stable Diffusion prompt, workflow, parameters, seed...)
  - C2PA / Content Credentials manifest (file me embed hota hai, pixel re-encode se jata hai)
  - ICC profile, JPEG comments, saare ancillary chunks

Kaise kaam karta hai:
  Image ke sirf pixels ko naye saaf file me re-encode karta hai — metadata copy hi nahi hota.
  Isi liye original file kabhi touch nahi hoti; output hamesha nayi file banti hai.

Limit (sach):
  Ye tool PIXEL-level invisible watermarks (jaise Google SynthID) NAHI hatata —
  wo metadata me nahi, pixels ke andar hote hain. Aur AI-detector jo pixels dekh kar
  pehchante hain, unpar bhi metadata saaf karne ka koi asar nahi padta.

Usage:
  python3 strip_metadata.py photo.png                 # -> photo_clean.png
  python3 strip_metadata.py a.jpg b.png               # multiple files
  python3 strip_metadata.py --out-dir cleaned/ *.jpg  # batch, alag folder me
  python3 strip_metadata.py --check photo.png         # sirf report, koi file nahi banegi
"""
import argparse
import io
import os
import sys

from PIL import Image

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def inspect(path):
    """File me jo metadata mile, uski chhoti report (naam + chhota preview)."""
    found = []
    raw = open(path, "rb").read()
    try:
        img = Image.open(path)
    except Exception as e:
        return [f"(image khul nahi payi: {e})"]
    # EXIF
    try:
        exif = img.getexif()
        if exif:
            for tag_id, val in exif.items():
                name = img.getexif().get_ifd(0).get(tag_id, tag_id) if False else tag_id
                found.append(f"EXIF tag {tag_id}: {str(val)[:60]}")
    except Exception:
        pass
    # PIL info keys (PNG text, JPEG comment, ICC, XMP...)
    for k, v in (img.info or {}).items():
        if k in ("jfif", "jfif_version", "jfif_density", "jfif_unit"):
            continue
        found.append(f"info[{k}]: {str(v)[:80]}")
    # PNG text chunks
    if hasattr(img, "text"):
        for k, v in img.text.items():
            found.append(f"PNG text[{k}]: {str(v)[:80]}")
    # Byte-level markers
    if b"<x:xmpmeta" in raw or b"http://ns.adobe.com/xap/1.0/" in raw:
        found.append("XMP packet (Adobe metadata)")
    if b"c2pa" in raw.lower():
        found.append("C2PA / Content Credentials manifest")
    if b"ICC_PROFILE" in raw:
        found.append("ICC color profile")
    if b"prompt" in raw.lower() and img.format == "PNG":
        if not any("prompt" in f.lower() for f in found):
            found.append("PNG chunk me 'prompt' jaisa text (AI generation data ho sakta hai)")
    return found


def strip_one(src, dst):
    img = Image.open(src)
    img.load()
    # Sirf pixels: mode + data se nayi image — koi info/exif/pnginfo carry nahi hota
    clean = Image.frombytes(img.mode, img.size, img.tobytes())
    ext = os.path.splitext(dst)[1].lower()
    if ext in (".jpg", ".jpeg"):
        if clean.mode not in ("RGB", "L", "CMYK"):
            clean = clean.convert("RGB")
        clean.save(dst, "JPEG", quality=95, subsampling=1, optimize=True)
    elif ext == ".png":
        clean.save(dst, "PNG", optimize=True)
    elif ext == ".webp":
        clean.save(dst, "WEBP", quality=95, method=6)
    elif ext in (".tif", ".tiff"):
        clean.save(dst, "TIFF")
    elif ext == ".bmp":
        clean.save(dst, "BMP")
    else:
        clean.save(dst)
    return dst


def main():
    ap = argparse.ArgumentParser(description="AI image metadata stripper")
    ap.add_argument("files", nargs="+", help="image files")
    ap.add_argument("--out-dir", default=None, help="output folder (default: source folder)")
    ap.add_argument("--suffix", default="_clean", help="output naam ka suffix (default: _clean)")
    ap.add_argument("--check", action="store_true", help="sirf metadata report, strip mat karo")
    args = ap.parse_args()

    for src in args.files:
        if not os.path.isfile(src):
            print(f"✗ {src}: file nahi mili")
            continue
        ext = os.path.splitext(src)[1].lower()
        if ext not in SUPPORTED:
            print(f"✗ {src}: format support nahi hai ({ext})")
            continue
        print(f"\n=== {src} ===")
        before = inspect(src)
        if before:
            print("  Mila metadata:")
            for f in before:
                print(f"    - {f}")
        else:
            print("  Koi metadata nahi mila — pehle se saaf hai.")
        if args.check:
            continue
        out_dir = args.out_dir or os.path.dirname(os.path.abspath(src))
        os.makedirs(out_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(out_dir, base + args.suffix + ext)
        strip_one(src, dst)
        after = inspect(dst)
        size_b = os.path.getsize(src)
        size_a = os.path.getsize(dst)
        print(f"  ✓ Clean file: {dst}  ({size_b} -> {size_a} bytes)")
        leftover = [f for f in after if "ICC" not in f]
        if leftover:
            print("  ⚠ Kuch reh gaya:")
            for f in leftover:
                print(f"    - {f}")
        else:
            print("  ✓ Verification: clean file me koi metadata nahi bacha.")


if __name__ == "__main__":
    main()
