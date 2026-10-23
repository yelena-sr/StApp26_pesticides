import base64
from functools import lru_cache
from html import escape

import streamlit as st

from utils.constants import ROOT

GREEN = "#1B4332"
GREEN_SOFT = "#E8F1EC"
VIOLET = "#7E57C2"
VIOLET_SOFT = "#F3EEFB"
INK = "#1F2A24"
MUTED = "#5B6B62"
RED = "#B2182B"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=DM+Sans:wght@400;500;700&display=swap');

.stApp p, .stApp li, .stApp label, .stApp td, .stApp th {{ font-family: 'DM Sans', sans-serif; }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {{ font-family: 'Fraunces', serif; color: {GREEN}; }}

/* hero banner */
.ps-hero {{ display: flex; align-items: center; gap: 28px; padding: 26px 32px; border-radius: 18px;
           background: linear-gradient(120deg, {GREEN} 0%, #2D6A4F 60%, #40916C 100%); color: white;
           margin-bottom: 18px; }}
.ps-hero img {{ height: 74px; background: white; border-radius: 14px; padding: 8px 12px; }}
.ps-hero h1 {{ color: white !important; font-family: 'Fraunces', serif; font-size: 2.1rem;
              margin: 0; padding: 0; line-height: 1.15; }}
.ps-hero p {{ color: #D8F3DC !important; margin: 6px 0 0 0; font-size: 1rem; }}
.ps-source {{ font-size: 0.78rem; color: {MUTED}; margin: -6px 0 14px 4px; }}

/* chapter navigation buttons: the active chapter is violet */
.stApp button[kind="primary"] {{ background: {VIOLET}; border-color: {VIOLET}; }}
.stApp button[kind="primary"]:hover {{ background: #6A45B0; border-color: #6A45B0; }}
.stApp button[kind="secondary"] p, .stApp button[kind="primary"] p {{ font-family: 'DM Sans', sans-serif; font-weight: 500; }}

/* chapter header */
.ps-chapter {{ display: flex; align-items: center; gap: 14px; margin: 18px 0 6px 0;
              padding-bottom: 4px; }}
.ps-chapter .num {{ font-family: 'Fraunces', serif; font-size: 2.6rem; color: {VIOLET}; line-height: 1; }}
.ps-chapter .kicker {{ font-size: 0.78rem; letter-spacing: .12em; text-transform: uppercase; color: {MUTED}; }}
.ps-chapter .title {{ font-family: 'Fraunces', serif; font-size: 1.9rem; color: {GREEN}; line-height: 1.2; }}

/* KPI cards */
.ps-kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 10px 0 18px 0; }}
.ps-kpi {{ background: white; border-left: 6px solid {GREEN}; border-radius: 10px; padding: 14px 16px;
          box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
.ps-kpi.violet {{ border-left-color: {VIOLET}; }}
.ps-kpi .label {{ font-size: .9rem; color: {MUTED}; }}
.ps-kpi .value {{ font-family: 'Fraunces', serif; font-size: 1.7rem; white-space: nowrap; color: {INK}; margin: 4px 0 2px 0; }}
.ps-kpi .note {{ font-size: .85rem; color: {MUTED}; }}
.ps-kpi .note.bad {{ color: {RED}; }}
.ps-kpi .note.good {{ color: {GREEN}; }}

/* callouts */
.ps-callout {{ background: {VIOLET_SOFT}; border-left: 5px solid {VIOLET}; border-radius: 0 12px 12px 0;
              padding: 14px 18px; margin: 8px 0 14px 0; color: {INK}; }}
.ps-callout.green {{ background: {GREEN_SOFT}; border-left-color: {GREEN}; }}
.ps-callout .ctitle {{ font-family: 'Fraunces', serif; font-size: 1.1rem; color: {GREEN}; margin-bottom: 6px; }}
.ps-callout ul, .ps-callout ol {{ margin: 0; padding-left: 20px; }}
.ps-callout li {{ margin-bottom: 4px; }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


@lru_cache(maxsize=4)
def _b64(path):
    return base64.b64encode((ROOT / path).read_bytes()).decode()


def hero(title, subtitle, logo="assets/icon.png"):
    st.markdown(
        f'<div class="ps-hero"><img src="data:image/png;base64,{_b64(logo)}" alt="PestiScope logo">'
        f"<div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div></div>",
        unsafe_allow_html=True,
    )


def source_line(text):
    st.markdown(f'<div class="ps-source">{escape(text)}</div>', unsafe_allow_html=True)


def chapter(num, kicker, title):
    st.markdown(
        f'<div class="ps-chapter"><span class="num">{num:02d}</span>'
        f'<div class="title">{escape(title)}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_cards(cards):
    """cards: list of dicts with label, value, note, tone ('bad', 'good' or '') and accent."""
    html = ['<div class="ps-kpis">']
    for c in cards:
        accent = " violet" if c.get("accent") == "violet" else ""
        tone = c.get("tone", "")
        html.append(
            f'<div class="ps-kpi{accent}"><div class="label">{escape(c["label"])}</div>'
            f'<div class="value">{escape(c["value"])}</div>'
            f'<div class="note {tone}">{escape(c.get("note") or "")}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def callout(items, title=None, tone="violet", ordered=False):
    """A styled box with an optional title and a list of plain-text items."""
    tag = "ol" if ordered else "ul"
    head = f'<div class="ctitle">{escape(title)}</div>' if title else ""
    body = "".join(f"<li>{escape(i)}</li>" for i in items)
    cls = "ps-callout green" if tone == "green" else "ps-callout"
    st.markdown(f'<div class="{cls}">{head}<{tag}>{body}</{tag}></div>', unsafe_allow_html=True)