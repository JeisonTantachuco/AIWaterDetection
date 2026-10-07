"""Download and unzip the EuroSAT multispectral dataset (13 Sentinel-2 bands).

Source: Zenodo record 7711810 (official EuroSAT release, Helber et al. 2019).
Result: data/eurosat/EuroSAT_MS/<ClassName>/<ClassName>_<n>.tif  (27,000 tiles, 64x64 px)

Run from the project root:
    python src/download_eurosat.py

NOTE: this is boilerplate (written by the agent). It is not part of the learning core,
but read the comments: they explain choices you will reuse in your own scripts.
"""

import hashlib
import urllib.request
import zipfile
from pathlib import Path

URL = "https://zenodo.org/api/records/7711810/files/EuroSAT_MS.zip/content"
# The MD5 is published on Zenodo. Checking it proves the 2 GB file arrived complete and
# uncorrupted -- a broken zip would otherwise fail much later, in a confusing way.
MD5 = "091174add3c8e680a49244acf185b9f0"

# Paths are built relative to this file, so the script works no matter which folder you
# run it from. data/ is in .gitignore: datasets never go into git.
ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "eurosat"
ZIP_PATH = OUT_DIR / "EuroSAT_MS.zip"


def md5sum(path, chunk=1024 * 1024):
    # Read in 1 MB chunks: never load a 2 GB file into memory at once.
    h = hashlib.md5()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def show_progress(blocks, block_size, total):
    done = blocks * block_size
    if total > 0:
        print(f"\r  {done / 1e6:7.0f} / {total / 1e6:.0f} MB ({100 * done / total:5.1f}%)", end="")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Skip the download if a valid zip is already there (re-running the script is safe).
    if ZIP_PATH.exists() and md5sum(ZIP_PATH) == MD5:
        print(f"Zip already downloaded and verified: {ZIP_PATH}")
    else:
        print(f"Downloading EuroSAT_MS (~2.1 GB) to {ZIP_PATH}")
        urllib.request.urlretrieve(URL, ZIP_PATH, reporthook=show_progress)
        print()
        if md5sum(ZIP_PATH) != MD5:
            raise RuntimeError("MD5 mismatch: download is corrupted. Delete the zip and retry.")
        print("Checksum OK.")

    print("Unzipping...")
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(OUT_DIR)

    # Quick sanity check: count tiles per class. EuroSAT should have 10 classes, 27,000 tiles.
    tif_files = list(OUT_DIR.rglob("*.tif"))
    classes = sorted({p.parent.name for p in tif_files})
    print(f"Done: {len(tif_files)} tiles in {len(classes)} classes")
    for c in classes:
        n = sum(1 for p in tif_files if p.parent.name == c)
        print(f"  {c:22s} {n}")


if __name__ == "__main__":
    main()
