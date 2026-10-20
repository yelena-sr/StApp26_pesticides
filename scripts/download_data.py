"""Download the yearly BNV-D substance files from data.gouv.fr (with a local cache).

Usage (from the project root):
    python scripts/download_data.py            # all years from 2009
    python scripts/download_data.py --from 2015

Files already present in data/raw are skipped. If the portal API changes,
download the files by hand from the dataset page (link printed below) and
drop them in data/raw/.
"""

import argparse
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.constants import FIRST_YEAR, RAW_DIR, SOURCE_SLUG, SOURCE_URL  # noqa: E402

API_V2 = f"https://www.data.gouv.fr/api/2/datasets/{SOURCE_SLUG}/resources/?page_size=200"
API_V1 = f"https://www.data.gouv.fr/api/1/datasets/{SOURCE_SLUG}/"
FILE_RE = re.compile(r"VENTE_DPT_SUBSTANCE_(\d{4})\.csv(\.gz)?$")


def list_resources():
    """Return a list of (title, url) from the data.gouv.fr API (v2, then v1)."""
    for url, key in ((API_V2, "data"), (API_V1, "resources")):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            items = resp.json().get(key, [])
            if items:
                return [(it.get("title", ""), it.get("url", "")) for it in items]
        except (requests.RequestException, ValueError) as err:
            print(f"API call failed ({url}): {err}")
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="first", type=int, default=FIRST_YEAR)
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    targets = []
    for title, url in list_resources():
        name = title or url.rsplit("/", 1)[-1]
        match = FILE_RE.search(name) or FILE_RE.search(url)
        if match and int(match.group(1)) >= args.first:
            targets.append((int(match.group(1)), name, url))

    if not targets:
        print("No file found through the API.")
        print(f"Download the VENTE_DPT_SUBSTANCE files by hand from:\n  {SOURCE_URL}")
        print(f"and put them in {RAW_DIR}")
        return

    for year, name, url in sorted(targets):
        dest = RAW_DIR / Path(name).name
        if dest.exists():
            print(f"{year}: cached ({dest.name})")
            continue
        print(f"{year}: downloading {dest.name}")
        with requests.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
    print("done - now run: python scripts/build_data.py")


if __name__ == "__main__":
    main()
