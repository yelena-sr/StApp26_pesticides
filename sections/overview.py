"""KPIs and high-level trends."""

import streamlit as st

from utils import viz
from utils.constants import NOMENCLATURE_BREAK
from utils.metrics import (
    cmr_share, fmt_pct, fmt_t, n_substances, pct_change, peak_note, tonnes_by_year, total_t,
)


def kpi_row(ctx):
    dept, subst = ctx["dept"], ctx["subst"]
    start, end = ctx["years"]
    t_end, t_start = total_t(dept, end), total_t(dept, start)
    # CMR share is only comparable on the same nomenclature: baseline moves to 2019 if needed
    cmr_base = start if (start >= NOMENCLATURE_BREAK or end < NOMENCLATURE_BREAK) else NOMENCLATURE_BREAK
    share_end, share_start = cmr_share(dept, end), cmr_share(dept, cmr_base)
    n_end, n_start = n_substances(subst, end), n_substances(subst, start)
    series = tonnes_by_year(dept)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Sold in {end}", fmt_t(t_end),
              f"{fmt_pct(pct_change(t_end, t_start))} vs {start}" if start != end else None,
              delta_color="inverse", border=True,
              help="Tonnes of active substance, current filters.")
    if len(series):
        c2.metric(f"Yearly average {start}-{end}", fmt_t(series.mean()),
                  f"peak {int(series.idxmax())}", delta_color="off", border=True)
    if share_end is not None:
        delta = None
        if cmr_base != end and share_start is not None:
            delta = f"{share_end - share_start:+.1f} pts vs {cmr_base}"
        c3.metric(f"Toxic / CMR share in {end}", fmt_pct(share_end, signed=False), delta,
                  delta_color="inverse", border=True,
                  help="Share of tonnes in the 'Toxic / CMR' class. Compared with 2019 at the "
                       "earliest, because the classification changed that year.")
    c4.metric(f"Active substances sold in {end}", f"{n_end}",
              f"{n_end - n_start:+d} vs {start}" if start != end else None,
              delta_color="off", border=True)


def render(ctx):
    dept = ctx["dept"]
    start, end = ctx["years"]
    if dept.empty:
        st.warning("No data for these filters.")
        return
    kpi_row(ctx)

    series = tonnes_by_year(dept)
    change = pct_change(series.get(end, 0), series.get(start, 0))
    if start != end and change is not None:
        verb = "fell" if change < 0 else "rose"
        st.subheader(f"Between {start} and {end}, sales {verb} by {abs(change):.0f}%.")
    else:
        st.subheader(f"Sales in {end}")
    st.markdown(f"Scope: **{ctx['scope_label']}**, uses: {', '.join(ctx['functions'])}.")

    ts = (dept.groupby(["annee", "fonction_group"], as_index=False)["qty_kg"].sum()
              .assign(tonnes=lambda x: x["qty_kg"] / 1000))
    fig = viz.area_by_function(ts, ctx["years"], peak_note(series))
    top_use = ts[ts["annee"] == end].sort_values("tonnes", ascending=False)
    viz.show(fig, f"Stacked area chart of tonnes sold per year from {start} to {end}, by use. "
                  f"In {end}, the largest use is {top_use.iloc[0]['fonction_group'].lower()} "
                  f"with {fmt_t(top_use.iloc[0]['tonnes'])}.")
    st.caption("Year-to-year moves are large: farmers stock up before price or tax changes, "
               "and weather drives fungicide needs. Read the trend, not a single year.")

    st.subheader("How dangerous is what we sell?")
    sh = (dept.groupby(["annee", "hazard_group"], as_index=False)["qty_kg"].sum()
              .assign(tonnes=lambda x: x["qty_kg"] / 1000))
    sh["share"] = sh["tonnes"] / sh.groupby("annee")["tonnes"].transform("sum") * 100
    viz.show(viz.share_by_hazard(sh, ctx["years"]),
             "Stacked bar chart, one bar per year, showing the share of tonnes in each hazard "
             "group. A dotted line marks the 2019 change of classification.")
    if start < NOMENCLATURE_BREAK <= end:
        st.caption("Before 2019 the red class meant 'toxic, very toxic or CMR'. From 2019 it means "
                   "'CMR' only, and a new 'health' class appears. Compare years on the same side "
                   "of the line.")