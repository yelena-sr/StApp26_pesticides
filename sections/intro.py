import streamlit as st

from utils.io import source_url
from utils.metrics import fmt_t, tonnes_by_year


def render(ctx):
    full = tonnes_by_year(ctx["dept_all"][ctx["dept_all"]["fonction_group"] != "Not plant protection"])
    last_year = int(full.index.max())

    st.subheader("Why it matters")
    st.markdown(
        f"In {last_year}, distributors in France declared the sale of "
        f"{fmt_t(full[last_year])} of active substances used to protect crops. "
        "These molecules end up in soils, rivers, groundwater and sometimes in food. "
        "Some of them are classified as carcinogenic, mutagenic or toxic for reproduction (CMR)."
    )
    st.markdown(
        "France has run reduction plans (Ecophyto) since 2008. "
        "This app checks what the sales data say, using the official national register."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Who is this for?")
        st.markdown(
            "- Citizens and students who want facts, not slogans.\n"
            "- Local decision makers (regions, water agencies) who need a local view.\n"
            "- Public health and environment students (bio-informatics, toxicology)."
        )
    with c2:
        st.markdown("#### Four questions")
        st.markdown(
            "1. Are sales really going down? (see The big picture)\n"
            "2. Where are they sold, and which molecules? (see Where and what)\n"
            "3. Do regions have different profiles? (see Hidden patterns)\n"
            "4. What should we do with this? (see Takeaways)"
        )

    st.markdown("#### How to read this app")
    st.markdown(
        "Use the sidebar to choose a period, regions, uses and the type of substance. "
        "The start year is the baseline and the end year is the focus year: "
        "every KPI compares the two. Hover any chart to see exact values."
    )

    st.info(
        "Three caveats before you start:\n\n"
        "- Sales are not use. A product can be bought one year and used later, "
        "and the department is the one of the seller, not of the field.\n"
        "- Weight is not risk. One tonne of sulphur and one tonne of a strong "
        "insecticide do not have the same impact.\n"
        "- Hazard classes changed in 2019. Before and after are not strictly comparable "
        "(details in Data quality)."
    )
    st.caption(f"Dataset page: {source_url()}")