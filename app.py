"""Run: streamlit run app.py"""

import streamlit as st

from sections import conclusions, deep_dives, intro, overview, patterns, quality
from utils.constants import FUNCTION_ORDER, NOMENCLATURE_BREAK, REGIONS
from utils import style
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
    st.caption("All quantities are kilograms of active substance, shown in tonnes.")

    # author card
    st.divider()
    st.image("assets/efrei_logo.png", width=140)
    st.markdown("##### Yéléna SAINTE-ROSE BRUNY")
    st.markdown(
        "Program: Master Data & AI, Bio-informatics major  \n"
        "Year: I2-BIO 2026/2027  \n"
        "Email: [yelena.sainte-rose-bruny@efrei.net](mailto:yelena.sainte-rose-bruny@efrei.net)  \n"
        "LinkedIn: [linkedin.com/in/yelesr](https://www.linkedin.com/in/yelesr/)  \n"
        "GitHub: [yelena-sr/StApp26_pesticides](https://github.com/yelena-sr/StApp26_pesticides)"
    )

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
CHAPTERS = [
    ("Why it matters", "Hook and context", intro.render),
    ("The big picture", "Key insight 1: the trend", overview.render),
    ("Where and what", "Key insight 2: places and molecules", deep_dives.render),
    ("Hidden patterns", "Key insight 3: regional profiles", patterns.render),
    ("Data quality", "Can we trust the data?", quality.render),
    ("Takeaways", "Implications and next steps", conclusions.render),
]
NAMES = [c[0] for c in CHAPTERS]

style.inject_css()
style.hero("PestiScope", "Pesticide sales in France, 2009-2024: are we really selling less?")
style.source_line(source_caption())
if missing_years:
    st.warning(f"Missing years in the data: {', '.join(map(str, missing_years))}. "
               "Add the matching files to data/raw/ and run scripts/build_data.py.")

def go_to(chapter_name):
    st.session_state.chapter = chapter_name


# chapter navigation: one button per chapter over the full width, the active one is filled
if st.session_state.get("chapter") not in NAMES:
    st.session_state.chapter = NAMES[0]
idx = NAMES.index(st.session_state.chapter)
for i, col in enumerate(st.columns(len(NAMES), gap="small")):
    col.button(NAMES[i], key=f"nav_{i}", on_click=go_to, args=(NAMES[i],), width="stretch",
               type="primary" if i == idx else "secondary")

name, kicker, render = CHAPTERS[idx]
style.chapter(idx + 1, kicker, name)
render(ctx)

# step-by-step reading of the story
st.write("")
left, _, right = st.columns([1, 2, 1])
if idx > 0:
    left.button(f"← {NAMES[idx - 1]}", on_click=go_to, args=(NAMES[idx - 1],), width="stretch")
if idx < len(NAMES) - 1:
    right.button(f"{NAMES[idx + 1]} →", on_click=go_to, args=(NAMES[idx + 1],),
                 type="primary", width="stretch")