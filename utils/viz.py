import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    ACCENT, FUNCTION_COLORS, FUNCTION_ORDER, HAZARD_COLORS, HAZARD_GROUP_ORDER,
    NOMENCLATURE_BREAK,
)

FONT = "Inter, Segoe UI, Helvetica, Arial, sans-serif"


def _style(fig, x_title, y_title, height=420, legend_title=None):
    fig.update_layout(
        height=height,
        font=dict(family=FONT, size=13),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(title=legend_title, orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(font_size=13),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title=x_title, showgrid=False)
    fig.update_yaxes(title=y_title, gridcolor="rgba(128,128,128,0.25)")
    return fig


def show(fig, alt_text):
    """Render a chart with a text alternative under it (accessibility)."""
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
    st.caption(f"Chart description: {alt_text}")


def _break_line(fig, years):
    if years[0] < NOMENCLATURE_BREAK <= years[1]:
        fig.add_vline(x=NOMENCLATURE_BREAK - 0.5, line_dash="dot", line_color="grey")
        fig.add_annotation(
            x=NOMENCLATURE_BREAK - 0.5, y=1.0, yref="paper", showarrow=False,
            text=" New hazard classes from 2019", xanchor="left", yanchor="bottom",
            font=dict(size=11, color="grey"),
        )


# ------------------------------------------------------------------ overview
def area_by_function(ts, years, peak_note=None):
    fig = px.area(
        ts, x="annee", y="tonnes", color="fonction_group",
        category_orders={"fonction_group": FUNCTION_ORDER},
        color_discrete_map=FUNCTION_COLORS,
        custom_data=["fonction_group"],
    )
    fig.update_traces(hovertemplate="%{customdata[0]}<br>%{x}: %{y:,.0f} tonnes<extra></extra>")
    _break_line(fig, years)
    if peak_note:
        fig.add_annotation(
            x=peak_note["x"], y=peak_note["y"], text=peak_note["text"], showarrow=True,
            arrowhead=2, ax=-120, ay=-10, xanchor="right", align="right", font=dict(size=11),
        )
    fig.update_xaxes(dtick=1, range=[years[0] - 0.3, years[1] + 0.3])
    return _style(fig, "Year of sale", "Active substances sold (tonnes)",
                  legend_title="Use")


def share_by_hazard(shares, years):
    fig = px.bar(
        shares, x="annee", y="share", color="hazard_group",
        category_orders={"hazard_group": HAZARD_GROUP_ORDER},
        color_discrete_map=HAZARD_COLORS, custom_data=["hazard_group", "tonnes"],
    )
    fig.update_traces(
        hovertemplate="%{customdata[0]}<br>%{x}: %{y:.1f}% (%{customdata[1]:,.0f} tonnes)<extra></extra>"
    )
    _break_line(fig, years)
    fig.update_layout(barmode="stack")
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return _style(fig, "Year of sale", "Share of tonnes sold (%)", legend_title="Hazard")


# ------------------------------------------------------------------ deep dives
def choropleth(df, geojson, value_col, label, diverging=False):
    if diverging:
        bound = max(abs(df[value_col].quantile(0.02)), abs(df[value_col].quantile(0.98)), 1)
        scale, rng = "RdBu_r", (-bound, bound)
    else:
        scale, rng = "YlOrBr", (0, df[value_col].quantile(0.98))
    fig = px.choropleth(
        df, geojson=geojson, locations="code_departement", featureidkey="properties.code",
        color=value_col, color_continuous_scale=scale, range_color=rng,
        hover_name="departement",
        hover_data={"code_departement": True, "region": True, value_col: ":,.1f"},
        labels={value_col: label, "code_departement": "Code", "region": "Region"},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=640, margin=dict(l=0, r=0, t=0, b=0),
                      coloraxis_colorbar=dict(title=label, thickness=14),
                      paper_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT, size=13))
    return fig


def ranking_bar(df, value_col, label, median=None):
    fig = px.bar(
        df, x=value_col, y="departement", orientation="h",
        labels={value_col: label, "departement": ""}, custom_data=["region"],
    )
    fig.update_traces(marker_color=ACCENT,
                      hovertemplate="%{y} (%{customdata[0]})<br>%{x:,.0f} tonnes<extra></extra>")
    fig.update_yaxes(categoryorder="total ascending")
    if median is not None:
        fig.add_vline(x=median, line_dash="dash", line_color="grey")
        fig.add_annotation(x=median, y=0, yref="paper", yanchor="top", showarrow=False,
                           text="median", font=dict(size=11, color="grey"))
    return _style(fig, label, "", height=max(320, 28 * len(df) + 80))


def small_multiples(idx):
    fig = px.line(
        idx, x="annee", y="index", facet_col="region", facet_col_wrap=4,
        facet_row_spacing=0.07, facet_col_spacing=0.04,
        custom_data=["region", "tonnes"],
    )
    fig.update_traces(line_color=ACCENT,
                      hovertemplate="%{customdata[0]}<br>%{x}: index %{y:.0f} "
                                    "(%{customdata[1]:,.0f} tonnes)<extra></extra>")
    fig.add_hline(y=100, line_dash="dot", line_color="grey")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=12)))
    n_rows = -(-idx["region"].nunique() // 4)
    _style(fig, None, None, height=190 * n_rows + 40)
    fig.update_xaxes(title=None, tickformat="d", nticks=4)
    fig.update_yaxes(title=None)
    return fig


def top_substances(df, label):
    df = df.sort_values("tonnes")
    fig = px.bar(
        df, x="tonnes", y="substance", orientation="h", color="hazard_group",
        category_orders={"hazard_group": HAZARD_GROUP_ORDER},
        color_discrete_map=HAZARD_COLORS,
        custom_data=["fonction_group", "classification", "mention"],
        labels={"tonnes": label, "substance": "", "hazard_group": "Hazard"},
    )
    fig.update_traces(hovertemplate="%{y}<br>%{x:,.0f} tonnes<br>Use: %{customdata[0]}"
                                    "<br>Class: %{customdata[1]}<br>Mention: %{customdata[2]}"
                                    "<extra></extra>")
    fig.update_yaxes(categoryorder="total ascending")
    return _style(fig, label, "", height=max(360, 28 * len(df)), legend_title="Hazard")


# ------------------------------------------------------------------ correspondence analysis
def ca_biplot(rows, cols, inertia, col_colors=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rows["Dim1"], y=rows["Dim2"], mode="markers+text", name="Regions",
        text=rows.index, textposition="top center", textfont=dict(size=11),
        marker=dict(size=8 + 40 * rows["mass"], color="#555555", opacity=0.75),
        customdata=rows[["mass", "cos2"]].to_numpy(),
        hovertemplate="%{text}<br>Weight: %{customdata[0]:.1%}"
                      "<br>Quality on this map (cos²): %{customdata[1]:.2f}<extra></extra>",
    ))
    colors = [(col_colors or {}).get(c, ACCENT) for c in cols.index]
    fig.add_trace(go.Scatter(
        x=cols["Dim1"], y=cols["Dim2"], mode="markers+text", name="Categories",
        text=cols.index, textposition="bottom center",
        textfont=dict(size=13, color=colors),
        marker=dict(symbol="diamond", size=14, color=colors, line=dict(width=1, color="white")),
        customdata=cols[["mass"]].to_numpy(),
        hovertemplate="%{text}<br>Weight: %{customdata[0]:.1%}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="grey", line_width=1)
    fig.add_vline(x=0, line_color="grey", line_width=1)
    xs = list(rows["Dim1"]) + list(cols["Dim1"])
    ys = list(rows["Dim2"]) + list(cols["Dim2"])
    pad_x, pad_y = 0.25 * (max(xs) - min(xs)), 0.15 * (max(ys) - min(ys))
    fig.update_xaxes(zeroline=False, range=[min(xs) - pad_x, max(xs) + pad_x])
    fig.update_yaxes(zeroline=False, range=[min(ys) - pad_y, max(ys) + pad_y])
    return _style(fig, f"Axis 1 ({inertia[0]:.1%} of inertia)",
                  f"Axis 2 ({inertia[1]:.1%} of inertia)", height=600)


def inertia_bar(inertia):
    import pandas as pd
    df = pd.DataFrame({"axis": [f"Axis {i + 1}" for i in range(len(inertia))],
                       "share": inertia * 100})
    fig = px.bar(df, x="axis", y="share", text_auto=".1f")
    fig.update_traces(marker_color=ACCENT, hovertemplate="%{x}: %{y:.1f}%<extra></extra>")
    fig.update_yaxes(ticksuffix="%")
    return _style(fig, "Axis", "Share of total inertia (%)", height=300)


def profile_heatmap(profiles):
    fig = px.imshow(profiles * 100, text_auto=".0f", aspect="auto",
                    color_continuous_scale="Greens",
                    labels=dict(x="Category", y="Region", color="% of region"))
    fig.update_traces(hovertemplate="%{y} - %{x}: %{z:.1f}%<extra></extra>")
    return _style(fig, None, None, height=520)


# ------------------------------------------------------------------ quality
def quality_bar(df, y, label):
    fig = px.bar(df, x="annee", y=y, labels={"annee": "Year", y: label})
    fig.update_traces(marker_color="#888888", hovertemplate="%{x}: %{y:,}<extra></extra>")
    fig.update_xaxes(dtick=1)
    return _style(fig, "Year of sale", label, height=300)