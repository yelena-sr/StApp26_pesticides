"""Map, rankings, regional small multiples and top substances."""

import streamlit as st

from utils import viz
from utils.io import load_geojson
from utils.metrics import by_department, change_by_department, fmt_t, region_index


def render(ctx):
    dept, subst = ctx["dept"], ctx["subst"]
    start, end = ctx["years"]
    if dept.empty:
        st.warning("No data for these filters.")
        return

    # ---------------------------------------------------------- map
    by_dep = by_department(dept, end)
    top = by_dep.sort_values("tonnes", ascending=False)
    share_top10 = top.head(10)["tonnes"].sum() / top["tonnes"].sum() * 100
    st.subheader(f"In {end}, 10 departments account for {share_top10:.0f}% of sales.")

    options = [f"Tonnes sold in {end}"]
    if start != end:
        options.append(f"Change {start} → {end} (%)")
    view = st.radio("Map view", options, horizontal=True)
    if view.startswith("Tonnes"):
        map_df, col, label, div = by_dep, "tonnes", "Tonnes", False
        alt = (f"Map of mainland France by department, coloured by tonnes sold in {end}. "
               f"Highest: {top.iloc[0]['departement']} ({fmt_t(top.iloc[0]['tonnes'])}).")
    else:
        map_df = change_by_department(dept, start, end)
        col, label, div = "change_pct", "Change (%)", True
        alt = (f"Map of mainland France by department, coloured by % change between {start} "
               f"and {end}. Blue = decrease, red = increase.")
    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(viz.choropleth(map_df, load_geojson(), col, label, diverging=div),
                        width="stretch", config={"displaylogo": False})
        st.caption(f"Chart description: {alt} Overseas departments are not drawn on the map "
                   "but are included in all totals.")
    with right:
        n = st.slider("Departments in the ranking", 5, 25, 12)
        viz.show(viz.ranking_bar(top.head(n), "tonnes", f"Tonnes sold in {end}",
                                 median=top["tonnes"].median()),
                 f"Horizontal bar chart of the {n} departments with the highest sales in {end}, "
                 "with a dashed line at the median department.")
    st.caption("Big wine, cereal and potato areas sell the most. Some peaks also come from "
               "large distributors that sell to farms in nearby departments.")

    # ---------------------------------------------------------- small multiples
    if end - start >= 2:
        st.subheader("Not every region follows the national trend")
        idx = region_index(dept, start)
        idx = idx[idx["region"] != "Unknown"]
        last = idx[idx["annee"] == end].sort_values("index")
        if not last.empty:
            best, worst = last.iloc[0], last.iloc[-1]
            st.markdown(
                f"Index 100 = {start}. Lowest in {end}: **{best['region']}** "
                f"({best['index']:.0f}). Highest: **{worst['region']}** ({worst['index']:.0f})."
            )
        viz.show(viz.small_multiples(idx),
                 f"Small multiples: one line chart per region, sales indexed to 100 in {start}. "
                 "The dotted line marks the baseline.")
        st.caption("Regions with small volumes (Corse, Overseas) swing much more: a few "
                   "distributors or a change in declarations is enough to move the index.")

    # ---------------------------------------------------------- substances
    st.subheader(f"Which molecules weigh the most in {end}?")
    k = st.slider("Number of substances", 5, 30, 15)
    s = (subst[subst["annee"] == end]
         .groupby(["substance", "fonction_group", "classification", "hazard_group", "mention"],
                  as_index=False)["qty_kg"].sum()
         .assign(tonnes=lambda x: x["qty_kg"] / 1000)
         .sort_values("tonnes", ascending=False).head(k))
    if s.empty:
        st.info("No substance for these filters.")
        return
    first = s.iloc[0]
    viz.show(viz.top_substances(s, f"Tonnes sold in {end}"),
             f"Horizontal bar chart of the {k} substances sold in the largest amounts in {end}, "
             f"coloured by hazard group. First: {first['substance']} ({fmt_t(first['tonnes'])}).")
    st.caption("Mineral products such as sulphur, used a lot in vineyards and organic farming, "
               "weigh heavily in tonnes but are applied at high doses per hectare. This is why "
               "official indicators also count doses (NODU), not only weight.")