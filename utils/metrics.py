import pandas as pd


def tonnes_by_year(dept):
    return dept.groupby("annee")["qty_kg"].sum().div(1000)


def total_t(dept, year):
    return dept.loc[dept["annee"] == year, "qty_kg"].sum() / 1000


def pct_change(new, old):
    if old is None or old == 0 or pd.isna(old):
        return None
    return (new - old) / old * 100


def cmr_share(dept, year):
    d = dept[dept["annee"] == year]
    total = d["qty_kg"].sum()
    if total == 0:
        return None
    return d.loc[d["hazard_group"] == "Toxic / CMR", "qty_kg"].sum() / total * 100


def n_substances(subst, year):
    return subst.loc[subst["annee"] == year, "substance"].nunique()


def by_department(dept, year):
    d = dept[dept["annee"] == year]
    return (d.groupby(["code_departement", "departement", "region"], as_index=False)["qty_kg"]
             .sum().assign(tonnes=lambda x: x["qty_kg"] / 1000))


def change_by_department(dept, start, end):
    a = by_department(dept, start)[["code_departement", "tonnes"]].rename(columns={"tonnes": "t0"})
    b = by_department(dept, end)
    out = b.merge(a, on="code_departement", how="left")
    out["change_pct"] = (out["tonnes"] - out["t0"]) / out["t0"] * 100
    return out.dropna(subset=["change_pct"])


def region_index(dept, start):
    """Tonnes per region and year, indexed to 100 in the start year."""
    g = dept.groupby(["region", "annee"], as_index=False)["qty_kg"].sum()
    g["tonnes"] = g["qty_kg"] / 1000
    base = g[g["annee"] == start].set_index("region")["tonnes"]
    g["index"] = g["tonnes"] / g["region"].map(base) * 100
    return g.dropna(subset=["index"])


def fmt_t(value):
    return f"{value:,.0f} tonnes".replace(",", " ")


def fmt_pct(value, signed=True):
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:+.1f}%" if signed else f"{value:.1f}%"


def peak_note(series):
    """Annotation for the 2018 spike, only if the data really show a spike in 2018."""
    if {2017, 2018, 2019} <= set(series.index):
        if series[2018] > series[2017] and series[2018] > series[2019]:
            return {"x": 2018, "y": series[2018],
                    "text": "2018 peak: buying ahead of the<br>2019 tax increase (press reports)"}
    return None