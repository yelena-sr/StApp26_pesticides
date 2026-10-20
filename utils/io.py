"""Data access: raw files, processed tables, GeoJSON and source text."""

import json
import re

import pandas as pd
import streamlit as st

from utils.constants import (
    GEOJSON_PATH, PROCESSED_DIR, RAW_DIR, RAW_PATTERN,
    SOURCE_EDITION, SOURCE_LICENSE, SOURCE_PRODUCER, SOURCE_TITLE, SOURCE_URL,
)

RAW_DTYPES = {
    "annee": "Int64",
    "code_departement": "string",
    "departement": "string",
    "amm": "string",
    "substance": "string",
    "cas": "string",
    "fonction": "string",
    "classification": "string",
    "classification_mention": "string",
}
TABLES = ["dept_year", "substance_year", "quality"]


def list_raw_files():
    """Return {year: path} for every raw substance file found in data/raw."""
    files = {}
    for path in sorted(RAW_DIR.glob(RAW_PATTERN)):
        match = re.search(r"SUBSTANCE_(\d{4})\.csv", path.name)
        if match:
            files[int(match.group(1))] = path
    return files


def read_raw_file(path):
    """Read one yearly file (.csv or .csv.gz). Separator ';', decimal '.', UTF-8."""
    return pd.read_csv(path, sep=";", dtype=RAW_DTYPES, encoding="utf-8")


def processed_exists():
    return all((PROCESSED_DIR / f"{name}.parquet").exists() for name in TABLES)


def load_processed():
    """Load the pre-aggregated tables written by scripts/build_data.py."""
    tables = {name: pd.read_parquet(PROCESSED_DIR / f"{name}.parquet") for name in TABLES}
    meta_path = PROCESSED_DIR / "meta.json"
    tables["meta"] = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    return tables


@st.cache_data(show_spinner=False)
def load_geojson():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def source_caption():
    return (
        f"Source: {SOURCE_TITLE} - {SOURCE_PRODUCER} - data.gouv.fr - "
        f"{SOURCE_EDITION}. {SOURCE_LICENSE}"
    )


def source_url():
    return SOURCE_URL
