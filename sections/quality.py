import pandas as pd
import streamlit as st

from utils import viz
from utils.constants import FIRST_YEAR, NOMENCLATURE_BREAK


def checks_table(q):
    used = q[q["used_in_analysis"]]
    years = used["annee"].tolist()
    gaps = sorted(set(range(min(years), max(years) + 1)) - set(years)) if years else []
    checks = [
        ("Every year present, no gap", not gaps,
         f"{min(years)}-{max(years)}" + (f", missing: {gaps}" if gaps else "")),
        ("No exact duplicate rows", used["duplicates"].sum() == 0,
         f"{int(used['duplicates'].sum())} duplicates removed"),
        ("No zero or negative quantity", used["qty_non_positive"].sum() == 0,
         f"{int(used['qty_non_positive'].sum())} rows excluded"),
        ("Every department code is valid", used["unknown_dept_rows"].sum() == 0,
         f"{int(used['unknown_dept_rows'].sum())} rows with unknown code"),
        ("Every hazard label is known", used["unknown_hazard_rows"].sum() == 0,
         f"{int(used['unknown_hazard_rows'].sum())} rows with unknown label"),
        ("Quantity missing in < 5% of rows",
         (used["qty_missing"] / used["rows_raw"]).max() < 0.05,
         f"max {(used['qty_missing'] / used['rows_raw']).max():.1%} in one year"),
    ]
    return pd.DataFrame(
        [{"Check": c, "Result": "Pass" if ok else "Warning", "Detail": d} for c, ok, d in checks]
    )


def render(ctx):
    q = ctx["tables"]["quality"]
    used = q[q["used_in_analysis"]]
    st.subheader("Can we trust these numbers?")
    total_raw, total_clean = int(used["rows_raw"].sum()), int(used["rows_clean"].sum())
    st.markdown(
        f"The app reads {len(used)} yearly files ({total_raw:,} raw rows). "
        f"After cleaning, {total_clean:,} rows ({total_clean / total_raw:.1%}) feed the charts. "
        "Cleaning runs in `utils/prep.py`; the steps are listed below."
    )

    st.markdown("#### Validation checks")
    st.dataframe(checks_table(q), hide_index=True, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        viz.show(viz.quality_bar(used, "qty_missing", "Rows with no quantity"),
                 "Bar chart of rows with a missing quantity, per year.")
    with c2:
        viz.show(viz.quality_bar(used, "n_substances", "Distinct substances"),
                 "Bar chart of the number of distinct active substances declared each year.")

    st.markdown("#### Missing values per column (raw files)")
    miss_cols = [c for c in q.columns if c.startswith("missing_")]
    miss_cols = [c for c in miss_cols if c != "missing_annee"]
    miss = used.set_index("annee")[miss_cols].rename(columns=lambda c: c.replace("missing_", ""))
    miss.index.name = "Year"
    st.dataframe(miss, width="stretch")
    st.caption("`classification_mention` is empty by design for most rows: it only exists for "
               "substances flagged 'Substitution' or 'Exclusion', from 2019. Missing `cas` "
               "numbers concern mixtures and micro-organisms that have no CAS number.")

    st.markdown("#### Cleaning steps")
    st.markdown(
        "1. Strip spaces, lower-case substance names, pad department codes (`1` → `01`).\n"
        "2. Remove exact duplicate rows.\n"
        "3. Exclude rows with a missing, zero or negative quantity from totals.\n"
        "4. Add features: region (2016 map), use group (6 groups), hazard group "
        "(4 groups that exist in both nomenclatures).\n"
        f"5. Keep years from {FIRST_YEAR}. 2008 is the first declaration year and is "
        "known to be incomplete.\n"
        "6. Pre-aggregate to two small tables (department × year × category, "
        "region × substance × year) saved as Parquet, so the app loads in under a second."
    )

    st.markdown("#### Known biases and limits")
    st.markdown(
        "- Seller location. Sales are attached to the department of the distributor. "
        "Border areas and big distribution hubs are over-stated.\n"
        "- Sales ≠ use. Stocks bought one year can be used the next (see the 2018 peak).\n"
        f"- Classification change in {NOMENCLATURE_BREAK}. Before: N minéral, N organique, "
        "T/T+/CMR, Autre. After: CMR, Santé A, Env A, Env B, Autre. The coarse groups in this "
        "app smooth the break but do not remove it.\n"
        "- Revisions. Each new edition can correct past years. This app uses the "
        "2025-11-25 edition only.\n"
        "- Weight is not toxicity. Tonnes favour heavy mineral products (sulphur, copper)."
    )

    with st.expander("Full quality table per file"):
        st.dataframe(q, hide_index=True, width="stretch")