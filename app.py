"""PestiScope - pesticide sales in France, a data story (EFREI Data Stories 2026).

Run: streamlit run app.py
"""

import streamlit as st

from sections import conclusions, deep_dives, intro, overview, patterns, quality
from utils.constants import FUNCTION_ORDER, NOMENCLATURE_BREAK, REGIONS
from utils.io import load_processed, processed_exists, source_caption
from utils.prep import build_tables, filter_dept, filter_substance

st.set_page_config(
    page_title="PestiScope - Pesticide sales in France",
    page_icon="assets/icon.png",
    layout="wide",
)
st.logo("assets/logo.png", size="large", icon_image="assets/icon.png")

SCOPES = {
    "All active substances": None,
    "Toxic / CMR substances only": "cmr",
    "Substances flagged for substitution or exclusion": "flagged",
}


@st.cache_data(show_spinner="Loading data...")
def get_data():
    """Pre-aggregated tables. Built from raw files if the parquet cache is missing."""
    if processed_exists():
        return load_processed()
    tables = build_tables()
    tables["meta"] = {"built_at_utc": "built on the fly from data/raw"}
    return tables


@st.cache_data(show_spinner=False)
def apply_filters(dept, subst, years, regions, functions, scope):
    d = filter_dept(dept, years, regions, functions)
    s = filter_substance(subst, years, regions, functions)
    if scope == "cmr":
        d, s = d[d["hazard_group"] == "Toxic / CMR"], s[s["hazard_group"] == "Toxic / CMR"]
    elif scope == "flagged":
        d, s = d[d["mention"] != "None"], s[s["mention"] != "None"]
    return d, s


tables = get_data()
dept_all, subst_all = tables["dept_year"], tables["substance_year"]
year_min, year_max = int(dept_all["annee"].min()), int(dept_all["annee"].max())

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("Filters")
    if year_min < year_max:
        years = st.slider("Years (start = baseline, end = focus year)",
                          year_min, year_max, (year_min, year_max))
    else:
        years = (year_min, year_max)
        st.info(f"Only one year available: {year_min}.")
    regions = st.multiselect("Regions (empty = all France)", list(REGIONS.keys()),
                             help="Region of the selling point, not of the farm.")
    default_fn = [f for f in FUNCTION_ORDER if f != "Not plant protection"]
    functions = st.multiselect("Uses", FUNCTION_ORDER, default=default_fn,
                               help="'Not plant protection' = biocides and misreported "
                                    "substances. Excluded by default.")
    scope_label = st.selectbox("Substances to measure", list(SCOPES.keys()),
                               help="Toxic / CMR: carcinogenic, mutagenic or reprotoxic "
                                    "(before 2019: toxic, very toxic or CMR). "
                                    "Flags exist only from 2019.")
    st.divider()
    st.caption("All quantities are kilograms of active substance, shown in tonnes.")

if not functions:
    st.warning("Select at least one use in the sidebar.")
    st.stop()

if SCOPES[scope_label] == "flagged" and years[0] < NOMENCLATURE_BREAK:
    if years[1] < NOMENCLATURE_BREAK:
        st.warning(f"Substitution and exclusion flags exist only from {NOMENCLATURE_BREAK}. "
                   "Move the end year to 2019 or later.")
        st.stop()
    years = (NOMENCLATURE_BREAK, years[1])
    st.sidebar.info(f"Flags exist only from {NOMENCLATURE_BREAK}: baseline set to "
                    f"{NOMENCLATURE_BREAK}.")

dept, subst = apply_filters(dept_all, subst_all, tuple(years), tuple(regions),
                            tuple(functions), SCOPES[scope_label])
missing_years = sorted(set(range(years[0], years[1] + 1)) - set(dept_all["annee"].unique()))

ctx = {
    "tables": tables, "dept": dept, "subst": subst, "dept_all": dept_all,
    "years": tuple(years), "regions": regions, "functions": functions,
    "scope_label": scope_label, "scope": SCOPES[scope_label],
}

# ------------------------------------------------------------------ page
st.image("assets/logo.png", width=380)  # logo with the app name, used as page title
st.markdown("#### Pesticide sales in France, 2009-2024: are we really selling less?")
st.caption(source_caption())
if missing_years:
    st.warning(f"Missing years in the data: {', '.join(map(str, missing_years))}. "
               "Add the matching files to data/raw/ and run scripts/build_data.py.")

# tabs spread evenly over the full width
st.markdown(
    """<style>
    .stTabs [role="tablist"] { width: 100%; display: flex; gap: 0; }
    .stTabs [role="tablist"] [role="tab"] { flex: 1 1 0; justify-content: center; text-align: center; }
    </style>""",
    unsafe_allow_html=True,
)
tabs = st.tabs(["Why it matters", "The big picture", "Where and what",
                "Hidden patterns", "Data quality", "Takeaways"])
with tabs[0]:
    intro.render(ctx)
with tabs[1]:
    overview.render(ctx)
with tabs[2]:
    deep_dives.render(ctx)
with tabs[3]:
    patterns.render(ctx)
with tabs[4]:
    quality.render(ctx)
with tabs[5]:
    conclusions.render(ctx)