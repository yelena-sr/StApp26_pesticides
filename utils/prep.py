"""Cleaning, validation and aggregation of the BNV-D substance files.

Pipeline for each yearly file:
1. normalise text fields and department codes;
2. count and drop exact duplicate rows;
3. check quantities (missing, zero or negative values are excluded from totals);
4. add features: region, function group, coarse hazard group;
5. aggregate to two light tables used by the app.
"""

import pandas as pd

from utils.constants import (
    DEPT_TO_REGION, FIRST_YEAR, FUNCTION_OTHER, FUNCTION_RULES, NOMENCLATURE_BREAK,
)
from utils.io import list_raw_files, read_raw_file

TEXT_COLS = ["code_departement", "departement", "amm", "substance", "cas",
             "fonction", "classification", "classification_mention"]


# ------------------------------------------------------------------ feature engineering
def function_group(label):
    text = str(label).lower()
    for keyword, group in FUNCTION_RULES:
        if keyword in text:
            return group
    return FUNCTION_OTHER


def hazard_group(label):
    """Map both nomenclatures (2008-2018 and 2019+) to 4 comparable groups."""
    text = str(label).lower().strip()
    if "cmr" in text or text.startswith("t") and "+" in text:
        return "Toxic / CMR"
    if "santé" in text or "sante" in text:
        return "Health"
    if text.startswith("env") or text.startswith("n "):  # "Env A/B" or "N minéral/organique"
        return "Environment"
    if "autre" in text:
        return "No hazard class"
    return "Unknown"


def normalise_dept(code):
    code = str(code).strip().upper()
    return code.zfill(2) if code.isdigit() and len(code) < 3 else code


# ------------------------------------------------------------------ cleaning
def clean_year(raw):
    """Clean one yearly DataFrame. Returns (clean_df, quality_dict)."""
    df = raw.copy()
    year = int(df["annee"].dropna().mode().iloc[0])
    quality = {"annee": year, "rows_raw": len(df)}

    # missing values per column, measured before any change
    for col in df.columns:
        quality[f"missing_{col}"] = int(df[col].isna().sum())

    # text normalisation
    for col in TEXT_COLS:
        df[col] = df[col].str.strip()
    df["substance"] = df["substance"].str.lower()
    df["code_departement"] = df["code_departement"].map(normalise_dept)

    # duplicates
    quality["duplicates"] = int(df.duplicated().sum())
    df = df.drop_duplicates()

    # quantity checks
    qty = pd.to_numeric(df["quantite_substance"], errors="coerce")
    quality["qty_missing"] = int(qty.isna().sum())
    quality["qty_non_positive"] = int((qty <= 0).sum())
    df["qty_kg"] = qty
    df = df[df["qty_kg"] > 0]

    # features
    df["region"] = df["code_departement"].map(DEPT_TO_REGION)
    quality["unknown_dept_rows"] = int(df["region"].isna().sum())
    df["region"] = df["region"].fillna("Unknown")

    df["fonction"] = df["fonction"].fillna("RAV")
    df["fonction_group"] = df["fonction"].map(function_group)

    df["classification"] = df["classification"].fillna("Unknown")
    df["hazard_group"] = df["classification"].map(hazard_group)
    quality["unknown_hazard_rows"] = int((df["hazard_group"] == "Unknown").sum())
    quality["hazard_labels"] = ", ".join(sorted(df["classification"].unique()))

    df["mention"] = df["classification_mention"].fillna("None")
    df["cas"] = df["cas"].fillna("n/a")

    quality["rows_clean"] = len(df)
    quality["total_t"] = round(df["qty_kg"].sum() / 1000, 1)
    quality["n_departments"] = int(df["code_departement"].nunique())
    quality["n_substances"] = int(df["substance"].nunique())
    quality["nomenclature"] = "2019+" if year >= NOMENCLATURE_BREAK else "2008-2018"
    return df, quality


# ------------------------------------------------------------------ aggregation
def aggregate_year(df):
    """Two light tables: one per department, one per region x substance."""
    dept = (
        df.groupby(
            ["annee", "code_departement", "departement", "region", "fonction_group",
             "classification", "hazard_group", "mention"],
            as_index=False, observed=True,
        )
        .agg(qty_kg=("qty_kg", "sum"), n_rows=("qty_kg", "size"))
    )
    subst = (
        df.groupby(
            ["annee", "region", "substance", "cas", "fonction_group",
             "classification", "hazard_group", "mention"],
            as_index=False, observed=True,
        )
        .agg(qty_kg=("qty_kg", "sum"))
    )
    return dept, subst


def build_tables(verbose=False):
    """Read every raw file, clean it and return the aggregated tables."""
    files = list_raw_files()
    if not files:
        raise FileNotFoundError(
            "No raw file found in data/raw. Run: python scripts/download_data.py"
        )
    dept_parts, subst_parts, quality_rows = [], [], []
    for year, path in files.items():
        clean, quality = clean_year(read_raw_file(path))
        quality["file"] = path.name
        quality["used_in_analysis"] = year >= FIRST_YEAR
        quality_rows.append(quality)
        if year >= FIRST_YEAR:
            dept, subst = aggregate_year(clean)
            dept_parts.append(dept)
            subst_parts.append(subst)
        if verbose:
            print(f"{year}: {quality['rows_raw']:>7} rows -> {quality['rows_clean']:>7} clean, "
                  f"{quality['total_t']:>9} t")
    tables = {
        "dept_year": pd.concat(dept_parts, ignore_index=True),
        "substance_year": pd.concat(subst_parts, ignore_index=True),
        "quality": pd.DataFrame(quality_rows).sort_values("annee").reset_index(drop=True),
    }
    for name in ("dept_year", "substance_year"):
        tables[name]["annee"] = tables[name]["annee"].astype(int)
    return tables


# ------------------------------------------------------------------ filters used by the app
def filter_dept(dept, years, regions, functions):
    mask = dept["annee"].between(*years) & dept["fonction_group"].isin(functions)
    if regions:
        mask &= dept["region"].isin(regions)
    return dept[mask]


def filter_substance(subst, years, regions, functions):
    mask = subst["annee"].between(*years) & subst["fonction_group"].isin(functions)
    if regions:
        mask &= subst["region"].isin(regions)
    return subst[mask]


# ------------------------------------------------------------------ correspondence analysis (CM2)
def correspondence_analysis(table):
    """Correspondence analysis (AFC) of a contingency table, computed with numpy.

    Returns row coordinates, column coordinates and the share of inertia per axis.
    Steps follow the course: frequencies, margins, standardised residuals, SVD.
    """
    import numpy as np

    n = table.to_numpy(dtype=float)
    p = n / n.sum()
    r = p.sum(axis=1)
    c = p.sum(axis=0)
    residuals = (p - np.outer(r, c)) / np.sqrt(np.outer(r, c))
    u, s, vt = np.linalg.svd(residuals, full_matrices=False)
    eig = s ** 2
    rows = (u * s) / np.sqrt(r)[:, None]
    cols = (vt.T * s) / np.sqrt(c)[:, None]
    row_df = pd.DataFrame(rows[:, :2], index=table.index, columns=["Dim1", "Dim2"])
    col_df = pd.DataFrame(cols[:, :2], index=table.columns, columns=["Dim1", "Dim2"])
    row_df["mass"] = r
    col_df["mass"] = c
    # quality of representation of each row on the first plane (cos2)
    dist2 = (((p / r[:, None]) - c) ** 2 / c).sum(axis=1)
    row_df["cos2"] = (rows[:, :2] ** 2).sum(axis=1) / dist2
    inertia_share = eig / eig.sum()
    return row_df, col_df, inertia_share, eig.sum()
