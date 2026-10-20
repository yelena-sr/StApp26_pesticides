"""Build the processed tables used by the app.

Usage (from the project root):
    python scripts/build_data.py

Reads data/raw/*VENTE_DPT_SUBSTANCE_*.csv.gz and writes data/processed/*.parquet.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.constants import PROCESSED_DIR, SOURCE_EDITION, SOURCE_URL  # noqa: E402
from utils.prep import build_tables  # noqa: E402


def main():
    tables = build_tables(verbose=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_parquet(PROCESSED_DIR / f"{name}.parquet", index=False)
        print(f"wrote {name}.parquet ({len(df):,} rows)")
    meta = {
        "built_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "source_url": SOURCE_URL,
        "source_edition": SOURCE_EDITION,
        "raw_files": tables["quality"]["file"].tolist(),
    }
    (PROCESSED_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    print("done")


if __name__ == "__main__":
    main()
