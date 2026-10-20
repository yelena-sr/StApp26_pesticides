# PestiScope - Storyboard

Project: Pesticide sales in France, 2009-2024: are we really selling less?
Author: Yéléna SAINTE-ROSE (20230361), BIO

This storyboard shows how the app tells its story. Each scene matches one tab of the app.
For each scene, it gives the question, what the user sees, what the user can do, and the
message to remember.


## Audience and goal

Audience: citizens, students in health and environment fields, and local decision makers.

Goal: check with official data whether France really sells fewer pesticides, and show where
and which substances matter most.

Main message: sales did not go down. In 2024, France sold 10% more active substances than
in 2009.


## Story arc

Hook, then context, then key insights, then implications.

1. Why it matters (hook and context)
2. The big picture (key insight 1: the trend)
3. Where and what (key insight 2: places and molecules)
4. Hidden patterns (key insight 3: regional profiles)
5. Data quality (trust and limits)
6. Takeaways (implications and next steps)


## Scene 1 - Why it matters

Question: why should we care about pesticide sales?

On screen: the 2024 tonnage, the link with soils, water and health, the target audience,
the four questions of the story, and three caveats.

Interaction: none needed. The sidebar is introduced here.

Message: France still sells around 70,000 tonnes of active substances each year, and some
of them are CMR (carcinogenic, mutagenic or toxic for reproduction).


## Scene 2 - The big picture

Question: are pesticide sales going down?

On screen: four KPIs (tonnes sold, yearly average, CMR share, number of substances), a
stacked area chart of sales per year by use, and a stacked bar chart of hazard classes.

Annotations: the 2018 peak (buying ahead of the 2019 tax increase) and the 2019 change of
hazard classification.

Interaction: year range slider (baseline and focus year), choice of uses, choice of
substances (all, CMR only, flagged for substitution).

Message: sales rose by 10% between 2009 and 2024. The 2019 drop was temporary. The CMR share
went up by 1.5 points since 2019.


## Scene 3 - Where and what

Question: where are pesticides sold, and which substances weigh the most?

On screen: a map of departments, a ranking with the median department, one small chart per
region (index 100 in the baseline year), and the top substances coloured by hazard.

Interaction: switch the map between tonnes and percentage change, choose the number of
departments and substances, filter by region.

Message: ten departments make 37% of sales, led by Gironde and Marne (wine and cereal areas).
Regions do not follow the same trend. Sulphur, glyphosate and prosulfocarb are the most sold
substances.


## Scene 4 - Hidden patterns

Question: do regions have their own pesticide profile?

On screen: a correspondence analysis (course CM2) of regions by use or by hazard class, the
share of inertia per axis, and the table of regional profiles.

Interaction: choose uses or hazard classes, include or exclude overseas departments, hover
points to read their weight and quality of representation.

Message: in 2024, the first axis summarises 75% of the differences between regions. It
opposes southern wine and fruit regions (Occitanie, Provence-Alpes-Côte d'Azur), where
fungicides make more than 70% of tonnes, to northern field-crop regions (Île-de-France,
Normandie, Hauts-de-France, Centre-Val de Loire), which lean towards herbicides and growth
regulators.


## Scene 5 - Data quality

Question: can we trust these numbers?

On screen: automatic validation checks, missing values per year and per column, cleaning
steps, and known biases.

Interaction: open the full quality table.

Message: all 16 years from 2009 to 2024 are present, and cleaning keeps more than 98% of
rows each year. But sales are not use, the location is the seller's, and the hazard classes
changed in 2019.


## Scene 6 - Takeaways

Question: what should we do with this?

On screen: key findings computed from the data, three implications, and next steps.

Interaction: findings update with the sidebar filters.

Message: tonnage alone is a weak target. Hazard classes, local concentration and flagged
molecules matter more. Next steps: buyer locations, agricultural area, water quality data
and dose-based indicators (NODU).
