import streamlit as st

from utils import viz
from utils.constants import (
    FUNCTION_COLORS, HAZARD_COLORS, HAZARD_LABELS, HAZARD_SINCE_2019, NOMENCLATURE_BREAK,
)
from utils.prep import correspondence_analysis


def render(ctx):
    dept = ctx["dept"]
    start, end = ctx["years"]
    # intro to correspondence analysis
    st.subheader("Do regions have their own pesticide profile?")
    st.markdown(
        "A table *region × category* hides a lot of structure. "
        "Correspondence analysis (AFC, see course CM2) compares each region's mix "
        "with the national mix. On the map below, a region close to a category sells "
        "relatively more of it than the national average. Regions close to the centre "
        "have an average profile."
    )

    # user controls
    choice = st.radio("Compare regions by", ["Use (herbicides, fungicides...)",
                                             "Hazard class (2019 and later)"], horizontal=True)
    drop_dom = st.checkbox("Exclude overseas departments", value=True,
                           help="Overseas crops (banana, sugar cane) are very different and "
                                "pull one axis on their own.")
    d = dept[dept["region"] != "Unknown"]
    # overseas filter
    if drop_dom:
        d = d[d["region"] != "Overseas"]
    # category choice: use or hazard class
    if choice.startswith("Use"):
        col, colors = "fonction_group", FUNCTION_COLORS
        d = d[d["annee"] == end]
        period = str(end)
    else:
        col, colors = "classification", HAZARD_COLORS
        first = max(start, NOMENCLATURE_BREAK)
        d = d[d["annee"].between(first, end) & d["classification"].isin(HAZARD_SINCE_2019)]
        period = f"{first}-{end}" if first < end else str(end)
        if end < NOMENCLATURE_BREAK:
            st.warning("Choose an end year from 2019 to use the new hazard classes.")
            return

    # contingency table region x category
    table = d.pivot_table(index="region", columns=col, values="qty_kg", aggfunc="sum",
                          fill_value=0)
    table = table.loc[table.sum(axis=1) > 0, table.sum(axis=0) > 0]
    # minimum size check
    if table.shape[0] < 3 or table.shape[1] < 3:
        st.info("Not enough regions or categories with these filters (need at least 3 of each). "
                "Clear the region filter or add uses.")
        return

    # correspondence analysis | biplot | inertia per axis
    rows, cols, inertia, total_inertia = correspondence_analysis(table)
    left, right = st.columns([3, 2])
    with left:
        viz.show(viz.ca_biplot(rows, cols, inertia, colors),
                 f"Correspondence analysis map for {period}. Grey dots are regions (size = weight "
                 "in sales), coloured diamonds are categories. Axis 1 and 2 summarise "
                 f"{(inertia[0] + inertia[1]):.0%} of the differences between regions.")
    with right:
        st.markdown("##### How much does the map show?")
        viz.show(viz.inertia_bar(inertia), "Bar chart of the share of inertia on each axis.")
        st.caption(f"Total inertia: {total_inertia:.3f}. It measures how far regional profiles "
                   "are from the national profile (0 = all regions identical).")

    # automatic reading of axis 1
    a1 = cols["Dim1"].sort_values()
    r1 = rows["Dim1"].sort_values()
    st.markdown(
        f"Reading axis 1 ({inertia[0]:.0%}). It opposes {a1.index[0]} "
        f"(left, with {', '.join(r1.index[:2])}) to {a1.index[-1]} "
        f"(right, with {', '.join(r1.index[-2:])})."
    )
    if col == "classification":
        st.caption(" · ".join(f"{k}: {v}" for k, v in HAZARD_LABELS.items()))

    # row profiles
    with st.expander("Row profiles (% of each region's tonnes) - the data behind the map"):
        profiles = table.div(table.sum(axis=1), axis=0)
        viz.show(viz.profile_heatmap(profiles),
                 "Heatmap: each row is a region, each cell the share of a category in that "
                 "region's sales.")
    # method and limits
    with st.expander("Method and limits"):
        st.markdown(
            "- Input: contingency table of kilograms sold, region × category.\n"
            "- Steps: frequencies, row and column margins, standardised residuals, SVD.\n"
            "- Distances use the chi-square metric, so a category with a small weight can still "
            "pull a region if it is over-represented there.\n"
            "- No chi-square test is shown: counts here are kilograms, not independent "
            "observations, so a p-value would be meaningless.\n"
            "- Hover a region to see its cos²: below 0.5 the point is poorly represented "
            "on this plane, so read its position with care."
        )