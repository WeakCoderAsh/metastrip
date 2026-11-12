<h1 align="center">🧹 MetaStrip</h1>

<p align="center"><em>Remove metadata from AI images — and any image — in one clean pass.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/works-offline-success" alt="Works offline">
</p>

---

## What it removes

- **EXIF** — camera, GPS, software, dates, artist, copyright
- **PNG text chunks** — ComfyUI / Stable Diffusion **prompts, workflows, seeds, parameters**
- **XMP / IPTC**
- **C2PA / Content Credentials** manifests embedded in the file
- **ICC profiles**, JPEG comments, and other ancillary chunks

## How it works

MetaStrip re-encodes **only the pixels** into a brand-new file. Metadata is never copied, so nothing survives — and the tool **verifies** the clean file afterwards and reports anything left behind.

- ✅ Your original file is never modified — output is always a new `_clean` file
- ✅ Works completely offline, no uploads anywhere
- ✅ Batch mode for whole folders

## Usage

```bash
pip install -r requirements.txt

python3 strip_metadata.py photo.png                  # -> photo_clean.png
python3 strip_metadata.py a.jpg b.png                # multiple files
python3 strip_metadata.py --out-dir cleaned/ *.jpg   # batch into a folder
python3 strip_metadata.py --check photo.png          # report only, no output file
```

Supported formats: **JPG, PNG, WebP, BMP, TIFF**

## Example report

```
=== photo.png ===
  Mila metadata:
    - PNG text[prompt]: {"3": {"class_type": "KSampler", ...
    - PNG text[workflow]: {"last_node_id": 12, ...
  ✓ Clean file: photo_clean.png  (184203 -> 171540 bytes)
  ✓ Verification: clean file me koi metadata nahi bacha.
```

## Honest limits

- Pixel-level invisible watermarks (like Google **SynthID**) live *inside the pixels*, not in metadata — no metadata tool can remove them.
- Detectors that analyse pixels are unaffected by metadata removal.
- MetaStrip is for **privacy and clean files** — it makes no "detector bypass" claims.

## Roadmap

- [ ] Drag & drop web UI (runs 100% in your browser)
- [ ] Video metadata support

## License

MIT — see [LICENSE](LICENSE).
