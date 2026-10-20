"""Project-wide constants: paths, source metadata, lookup tables and colours."""

from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
GEOJSON_PATH = ROOT / "data" / "geo" / "departements.geojson"

RAW_PATTERN = "*VENTE_DPT_SUBSTANCE_*.csv*"
FIRST_YEAR = 2009  # 2008 is the first declaration year and is excluded (see README)

# ---------------------------------------------------------------- source
SOURCE_TITLE = "BNV-D Traçabilité - sales of plant protection products by department"
SOURCE_PRODUCER = "Office français de la biodiversité (OFB)"
SOURCE_URL = (
    "https://www.data.gouv.fr/datasets/"
    "bnv-d-tracabilite-donnees-sur-les-ventes-de-produits-phytopharmaceutiques"
)
SOURCE_SLUG = "bnv-d-tracabilite-donnees-sur-les-ventes-de-produits-phytopharmaceutiques"
SOURCE_EDITION = "Edition 2025-11-25 (sales 2008-2024)"
SOURCE_LICENSE = (
    "No licence stated on the data.gouv.fr page. Public data from OFB, "
    "reused here for non-commercial academic work with full citation."
)
GEOJSON_SOURCE = "github.com/gregoiredavid/france-geojson (simplified departments)"

# ---------------------------------------------------------------- departments -> regions (2016 map)
REGIONS = {
    "Auvergne-Rhône-Alpes": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"],
    "Bourgogne-Franche-Comté": ["21", "25", "39", "58", "70", "71", "89", "90"],
    "Bretagne": ["22", "29", "35", "56"],
    "Centre-Val de Loire": ["18", "28", "36", "37", "41", "45"],
    "Corse": ["2A", "2B", "20"],
    "Grand Est": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"],
    "Hauts-de-France": ["02", "59", "60", "62", "80"],
    "Île-de-France": ["75", "77", "78", "91", "92", "93", "94", "95"],
    "Normandie": ["14", "27", "50", "61", "76"],
    "Nouvelle-Aquitaine": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"],
    "Occitanie": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"],
    "Pays de la Loire": ["44", "49", "53", "72", "85"],
    "Provence-Alpes-Côte d'Azur": ["04", "05", "06", "13", "83", "84"],
    "Overseas": ["971", "972", "973", "974", "976"],
}
DEPT_TO_REGION = {code: region for region, codes in REGIONS.items() for code in codes}

# ---------------------------------------------------------------- function groups
# Raw "fonction" labels are mapped to 6 readable groups (first matching keyword wins).
FUNCTION_RULES = [
    ("sa non phyto", "Not plant protection"),
    ("rav", "Not plant protection"),
    ("herbicide", "Herbicides"),
    ("fongicide", "Fungicides"),
    ("bactéricide", "Fungicides"),
    ("insecticide", "Insecticides"),
    ("nématicide", "Insecticides"),
    ("régulateur", "Growth regulators"),
]
FUNCTION_OTHER = "Other uses"
FUNCTION_ORDER = [
    "Herbicides", "Fungicides", "Insecticides",
    "Growth regulators", "Other uses", "Not plant protection",
]

# ---------------------------------------------------------------- hazard classes
# The official nomenclature changed in 2019 (see metadata PDF, field "classification").
HAZARD_SINCE_2019 = ["CMR", "Santé A", "Env A", "Env B", "Autre"]
HAZARD_LABELS = {
    "CMR": "CMR (carcinogenic, mutagenic, reprotoxic)",
    "Santé A": "Health hazard (acute / organ toxicity)",
    "Env A": "Environment hazard - high",
    "Env B": "Environment hazard - moderate",
    "Autre": "No hazard class",
}
# Coarse groups that exist in both nomenclatures (2009-2018 and 2019+)
HAZARD_GROUP_ORDER = ["Toxic / CMR", "Health", "Environment", "No hazard class"]
NOMENCLATURE_BREAK = 2019

# ---------------------------------------------------------------- colours (colour-blind safe, Okabe-Ito based)
FUNCTION_COLORS = {
    "Herbicides": "#E69F00",
    "Fungicides": "#0072B2",
    "Insecticides": "#D55E00",
    "Growth regulators": "#009E73",
    "Other uses": "#CC79A7",
    "Not plant protection": "#999999",
}
HAZARD_COLORS = {
    "Toxic / CMR": "#B2182B",
    "Health": "#EF8A62",
    "Environment": "#2166AC",
    "No hazard class": "#BABABA",
    "CMR": "#B2182B",
    "Santé A": "#EF8A62",
    "Env A": "#2166AC",
    "Env B": "#67A9CF",
    "Autre": "#BABABA",
}
ACCENT = "#1B4332"
