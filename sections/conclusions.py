import streamlit as st

from utils.constants import NOMENCLATURE_BREAK
from utils.metrics import (
    by_department, cmr_share, fmt_t, pct_change, tonnes_by_year,
)


def render(ctx):
    dept = ctx["dept"]
    start, end = ctx["years"]
    if dept.empty:
        st.warning("No data for these filters.")
        return
    series = tonnes_by_year(dept)
    insights = []

    if start != end and start in series and end in series:
        ch = pct_change(series.get(end, 0), series.get(start, 0))
        trend = "down" if ch < 0 else "up"
        insights.append(
            f"Sales are {trend} {abs(ch):.0f}% over the period. From {fmt_t(series[start])} "
            f"in {start} to {fmt_t(series[end])} in {end}. "
            f"The peak of the period was {int(series.idxmax())} ({fmt_t(series.max())})."
        )

    uses = (dept[dept["annee"] == end].groupby("fonction_group")["qty_kg"].sum()
            .sort_values(ascending=False))
    if len(uses) >= 2:
        share = uses.iloc[:2].sum() / uses.sum() * 100
        insights.append(
            f"Two uses dominate. {uses.index[0]} and {uses.index[1].lower()} make up "
            f"{share:.0f}% of tonnes sold in {end}."
        )

    dep = by_department(dept, end).sort_values("tonnes", ascending=False)
    top3 = dep.head(3)
    top10_share = dep.head(10)["tonnes"].sum() / dep["tonnes"].sum() * 100
    insights.append(
        f"A few departments weigh a lot. 10 departments out of {len(dep)} make "
        f"{top10_share:.0f}% of sales in {end}. The top 3 are "
        f"{', '.join(top3['departement'].str.title())}."
    )

    first_new = max(start, NOMENCLATURE_BREAK)
    if end > first_new:
        s0, s1 = cmr_share(dept, first_new), cmr_share(dept, end)
        if s0 is not None and s1 is not None:
            move = s1 - s0
            verb = "barely moves" if abs(move) < 2 else ("falls" if move < 0 else "rises")
            insights.append(
                f"The CMR share {verb}. It went from {s0:.1f}% in {first_new} "
                f"to {s1:.1f}% in {end} ({s1 - s0:+.1f} pts), on a comparable classification."
            )

    st.subheader("What we learned")
    st.info("\n".join(f"- {text}" for text in insights))
    st.caption("These sentences update with the sidebar filters.")

    st.subheader("So what?")
    st.info(
        "- Weight alone is a weak target. A drop in tonnes can hide a switch to "
        "lighter but more potent molecules. Track hazard classes and treated surfaces too.\n"
        "- Act where sales concentrate. A few departments carry most of the volume: "
        "water catchments there deserve priority monitoring.\n"
        "- Watch flagged molecules. Substances marked for substitution or exclusion are "
        "the most direct lever for public health."
    )

    st.subheader("Next steps")
    st.info(
        "- Join with the purchase files (buyer postcode) to get closer to real use.\n"
        "- Divide by agricultural area per department to compare intensity, not size.\n"
        "- Cross with water quality data (pesticides in groundwater) to test the link "
        "between sales and contamination.\n"
        "- Add the NODU indicator (doses per hectare) to correct the weight bias."
    )
    st.caption("This analysis shows associations in sales data. It does not prove any effect "
               "on health or the environment.")