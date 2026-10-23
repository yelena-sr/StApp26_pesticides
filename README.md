# PestiScope - Pesticides in France: are we really selling less?

Individual Student Project - Streamlit Dashboard - EFREI Data Stories 2026
Author: Yéléna SAINTE-ROSE BRUNY (20230361), I2-BIO 2026/2027
Course: Data analysis and visualization - Supervisor: Mano Joseph MATHEW

- Deployed app: https://pesticides-france-sainte-rose.streamlit.app/
- Repository: https://github.com/yelena-sr/StApp26_pesticides
- Demo video: included in the submission zip (Project_recording.mp4)
- Storyboard: https://github.com/yelena-sr/StApp26_pesticides/blob/main/STORYBOARD.md


## 1. Overview

France has run plans to reduce pesticide use since 2008. This Streamlit app uses the
national register of pesticide sales to check what actually happened between 2009 and 2024.

The app follows a simple narrative: why the topic matters, how sales evolved, where and
which substances are sold, how regions differ, how reliable the data is, and what we can
conclude.

Four questions guide the analysis:

1. Are pesticide sales going down in France?
2. Which departments and which substances weigh the most?
3. Do regions have different profiles of use and hazard?
4. What does this mean for public health and environmental policy?

The intended audience is citizens, students in health and environment fields, and local
decision makers who need a regional view.


## 2. Data

Source: BNV-D Traçabilité - données sur les ventes de produits phytopharmaceutiques,
published by the Office français de la biodiversité (OFB) on data.gouv.fr.

https://www.data.gouv.fr/datasets/bnv-d-tracabilite-donnees-sur-les-ventes-de-produits-phytopharmaceutiques

Files used: `BNVD_TRACABILITE_20251125_VENTE_DPT_SUBSTANCE_{year}.csv.gz`, one file per
year from 2009 to 2024 (edition of 25 November 2025). The metadata document
`bnvd_eaufrance_metadonnees_vente_20251125.pdf` describes every field.

The data comes from mandatory declarations. Since the 2006 Water Act (LEMA), every
approved distributor must declare its yearly sales before 31 March of the next year. The
declarations are then converted into quantities of active substance using the composition
of each product.

Each row gives the quantity of one active substance sold in one department in one year,
in kilograms. The department is the location of the seller. Each substance has a use
(herbicide, fungicide, insecticide...) and a hazard class (CMR, health, environment, none).

No licence is stated on the dataset page. The data is public and is reused here for
non-commercial academic work, with full citation of the producer.

Department shapes for the map come from github.com/gregoiredavid/france-geojson.


## 3. Installation and run

The project was developed and tested with Python 3.11. All dependencies are pinned in
`requirements.txt`.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The processed tables are included in `data/processed/`, so the app runs without the raw
files. To rebuild everything from the original data:

```bash
python scripts/download_data.py  # or download the files by hand into data/raw/
python scripts/build_data.py
```

If the processed tables are missing, the app rebuilds them from `data/raw/` on first load.
No random sampling is used: all tables are deterministic aggregations of the full files
(see `seeds.json`).


## 4. Data preparation

The cleaning pipeline is in `utils/prep.py`. For each yearly file, it:

1. normalises text fields and department codes (for example `1` becomes `01`);
2. removes exact duplicate rows;
3. excludes rows with a missing, zero or negative quantity from the totals;
4. adds three features: region (2016 map), use group (6 groups built from the `fonction`
   field) and hazard group (4 groups that exist in both classification systems);
5. aggregates the result into two small Parquet tables, one by department and one by
   region and substance.

The year 2008 is excluded because it is the first declaration year. Every check is shown
in the Data quality chapter of the app.


## 5. App content

The app is organised in six chapters, read in order with the navigation buttons. The sidebar filters apply to all of them: period
(start year as baseline, end year as focus year), regions, uses and type of substance.

1. Why it matters: context, audience, questions and main caveats.
2. The big picture: KPIs linked to the filters, sales per year by use, and the share of
   each hazard class over time.
3. Where and what: choropleth map by department, ranking, regional trends as small
   multiples, and the most sold substances.
4. Hidden patterns: a correspondence analysis (AFC) that compares the profile of each
   region with the national profile, by use or by hazard class.
5. Data quality: validation checks, missing values per column, cleaning steps and known
   biases.
6. Takeaways: findings computed from the data, implications and next steps.

All charts are interactive, with hover details, labelled axes and units, and a short text
description for accessibility. Colours come from a colour-blind safe palette.


## 6. Main findings

With all filters at their default values:

- Sales in 2024 reached 70,853 tonnes of active substances, 10% more than in 2009.
- Sales peaked in 2018, then dropped sharply in 2019. This is consistent with buyers
  stocking up before the tax increase of January 2019.
- Fungicides and herbicides account for most of the tonnage.
- Ten departments represent 37% of sales in 2024. Gironde and Marne come first.
- Sulphur is by far the most sold substance by weight, followed by glyphosate and
  prosulfocarb.

The texts in the app are generated from the data, so they update with the filters.


## 7. Limits

- Sales are located at the seller, not where the product is used. Departments with large
  distributors are over-represented.
- A product sold one year can be used later, so yearly sales do not equal yearly use.
- The hazard classification changed in 2019. The app groups the classes so that both
  periods can be shown together, but the comparison remains approximate.
- Tonnes do not measure toxicity. Heavy mineral products such as sulphur dominate the
  totals, which is why official indicators also use doses per hectare (NODU).
- The analysis shows associations in sales data. It does not prove any effect on health
  or the environment.


## 8. Project structure

```
app.py                  page configuration, sidebar filters, chapter navigation
sections/
  intro.py              chapter 1: context, audience, questions
  overview.py           chapter 2: KPIs and trends
  deep_dives.py         chapter 3: map, ranking, regions, substances
  patterns.py           chapter 4: correspondence analysis
  quality.py            chapter 5: data quality
  conclusions.py        chapter 6: findings and next steps
utils/
  constants.py          paths, source, regions, groups, colours
  io.py                 data loading
  prep.py               cleaning, feature engineering, aggregation
  metrics.py            shared calculations
  viz.py                chart functions with a common style
  style.py              visual identity: banner, KPI cards, callouts
scripts/
  download_data.py      downloads the raw files from data.gouv.fr
  build_data.py         builds data/processed/ from data/raw/
data/
  raw/                  raw yearly files (not versioned)
  processed/            aggregated Parquet tables used by the app
  geo/                  department shapes
requirements.txt        pinned dependencies
```
