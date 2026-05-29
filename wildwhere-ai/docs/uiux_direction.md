# UI/UX Direction

WildWhere AI should feel like a modern wildlife intelligence workspace rather than a generic dashboard. The product should combine the quiet precision of GIS tools with the emotional pull of national parks: dark, spatial, analytical, and visually grounded in real landscapes and species.

## Visual Direction

The default interface should use a dark mode foundation inspired by contemporary mapping and observability platforms. The palette should avoid a flat black UI; deep green-gray surfaces, warm highlight colors, and restrained elevation will make the product feel outdoors-oriented without becoming decorative.

Suggested palette:

- Background: `#0F1714`
- Surface: `#17231F`
- Raised surface: `#20302A`
- Primary accent: `#7FB069`
- Secondary accent: `#D9A441`
- Alert/accent: `#D66A50`
- Text primary: `#F3F5EF`
- Text secondary: `#A8B5AA`
- Grid/map lines: `#34453D`

## Typography

Use a clean sans-serif interface family such as Inter, IBM Plex Sans, or Source Sans 3. Numeric tables and chart annotations can use a tabular option for stable scanning. Headings should be compact and confident, not oversized marketing type.

## Layout Philosophy

The future dashboard should lead with the working surface: map, filters, and trends. Avoid a landing-page feel. The first screen should immediately answer: which park, which species, which season, and what evidence supports the insight?

Recommended layout:

- Left rail for park/species filters.
- Main map panel for observations and park geography.
- Right insight panel for selected species, confidence notes, and recent patterns.
- Lower trend band for seasonality, weather overlays, and visitation context.

## Interaction Philosophy

Interactions should feel exploratory but controlled. Users should be able to filter by park, species group, season, weather condition, and observation density without losing context. Every generated insight should remain linked to the underlying data slice.

Important interaction patterns:

- Map brushing should update charts.
- Species search should support common and scientific names.
- Filters should be visible and reversible.
- Tooltips should show source, date, and observation metadata.
- Empty states should explain whether data is missing, filtered out, or unavailable.

## Future Dashboard Pages

- Wildlife Map: sightings by park, species, and season.
- Species Explorer: observation history, habitat notes, and seasonality.
- Park Intelligence: park-level trends across wildlife, weather, and visitation.
- Weather Context: temperature and precipitation overlays.
- Model Lab: later-stage prediction outputs with transparent uncertainty.
- Data Quality: source coverage, missingness, and known limitations.

## Product Feel

The interface should be minimal, map-forward, and analytical. Wildlife imagery can be used sparingly for species context, but charts and maps should do most of the work. The final experience should feel credible to data scientists, useful to park visitors, and polished enough for a portfolio review.

## Data Transparency UX

WildWhere AI should build trust by showing where the data comes from and how uncertain it is. The dashboard should not hide raw data limitations behind polished visuals.

Future UI patterns:

- Source badges on maps, charts, and detail panels for GBIF, NPSpecies, NPS Stats, and NOAA.
- Confidence labels that distinguish boundary-filtered records from bounding-box records.
- Data freshness indicators showing the latest source access date and the latest event date in the current filter.
- Map disclaimers for coordinate uncertainty and near-park records.
- Plain-language copy such as "reported observations, not confirmed wildlife presence."
- Filters for source, park, species, date range, record basis, and location filter method.
- Sparse-data warnings when a park/species/date slice has too few records for reliable interpretation.
- Detail panels that expose source URL, license, coordinate uncertainty, and station distance when relevant.

The dashboard should make uncertainty visible without making the product feel weak. The goal is credible exploration, not false precision.
