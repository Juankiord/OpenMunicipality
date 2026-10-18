# OpenMunicipality

Explains a municipal budget in plain language. Type the name of a Spanish
municipality and the app tells you how much the council plans to spend and
how much it actually spent, how much that is per resident, where the money
goes and comes from, how it compares with municipalities of a similar size and
what has changed since the previous year. Interface in Spanish and English.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23451732.svg)](https://doi.org/10.5281/zenodo.23451732)

Version 1.0.0 · MIT licence · Python ≥ 3.10

## What it does

- **Search by name** among the 8,132 Spanish municipalities (accents and
  capitals ignored; Enter on an exact name opens it). Municipalities absent
  from the Ministry's database are explained, not just "not found".
- **Plain-language summary**: a headline sentence and key points generated from
  the data.
- **Per resident and benchmarks**: totals, per resident or "out of every €100",
  against the median of municipalities of a similar size.
- **Areas, types and programmes**: 17 plain-language spending areas, spending
  types (staff, purchases, grants, investment, debt) and the official
  programmes inside each area.
- **Planned and spent**: budgets (what was planned) and outturns (what was
  actually spent), side by side by area and by type of spending.
- **Change over time** from 2010 to 2025, optionally adjusted for inflation
  (INE consumer price index), with flags for large changes.
- **Who was in office**: the mayor of each year (from 2010 to the current
  term, Ministry of Territorial Policy) next to the budget, a timeline of spending per resident
  over the mayoralties and a record of each one (budgets, change, investment,
  rolled-over budgets, share of the plan spent). A budget is assigned to
  whoever was mayor on 1 January; an outturn, to whoever was mayor for more
  than half the year. Lists appear as registered and get no colour.
- **Comparison** with a second municipality, **sharing** (summary image, CSV,
  embed code) and **data warnings** for exceptional figures.
- **Accessibility**: text size, contrast, spacing, colour mode, tables under
  every chart, colour-blind-safe palettes, a highly legible font; the
  system's reduce-motion setting is respected.

Every view keeps its state in the address
(`?lang=en&m=11012&s=executed&y=2024&c=41091`), so it can be bookmarked or
shared.

## Run it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py              # opens http://localhost:8501
```

Or double-click the launcher for your system (`iniciar_mac.command`,
`iniciar_windows.bat`, `iniciar_linux.sh`): the first run creates the
environment and installs the libraries, later runs open the app directly.

## Official data (Spain)

`data/conprel/` is a normalised extract of the Spanish Ministry of Finance
database **CONPREL** (*Presupuestos y Liquidaciones de las Entidades Locales*):
consolidated data for each council and its agencies, with population from the
municipal register. Its format is described in `data/conprel/datapackage.json`.

- Budgets 2010–2025: between 5,874 (2016) and 7,454 (2022) municipalities
  a year.
- Outturns (*liquidaciones*) 2010–2024: between 6,717 (2022) and 7,967
  (2011) municipalities a year; spending is the recognised obligations and
  income the recognised rights.
- 8,126 of the 8,132 current municipalities appear at least once.
- Until 2013, municipalities with fewer than 5,000 residents could report
  spending only by area and policy, so their programme detail is missing for
  those years (the app says so).
- Budgets identical to the previous year in every area are flagged as most
  likely rolled over (*prorrogados*); outturns below half or above twice the
  budget are flagged too.
- Spending: the 24 national spending policies (Orden EHA/3565/2008) grouped
  into 17 areas, the programmes (90 until 2014, 88 from 2015, after the 2014
  revision; each year shows the names in force) and the 9 economic chapters;
  income: the 9 economic chapters. The build stops unless the three
  spending views add up to the same total for every municipality.
- Benchmarks: median euros per resident by population band (zeros included).
- Full INE municipality list (via Code for Spain, public domain) and the INE
  consumer price index 2010–2025 (`cpi_SOURCE.md`).

- Mayors from 2010 (`mayors.csv.gz`, `mayors_SOURCE.md`): Ministry of
  Territorial Policy lists for the 2007–2011 to 2019–2023 terms and the
  current mayors of the 2023–2027 term (exported on 17 October 2026; earlier
  mayors of this term are not published). Rebuilt with
  `python scripts/build_mayors.py --since 2010-01-01 <files>` (needs
  openpyxl).
  Changes of mayor are detected by person, because the register can file the
  same mayor under a party one term and a coalition the next.

Budget and outturn tables are stored one file per stage
(`lines_budget.csv.gz`, `lines_executed.csv.gz`…), about 68 MB in all. To add
new years, download "Datos por Entidad Local. Máximo nivel de desglose
(ACCESS)" from <https://serviciostelematicosext.hacienda.gob.es/SGFAL/CONPREL>
and run:

```bash
# needs mdbtools: apt install mdbtools / brew install mdbtools
python scripts/build_conprel.py Presupuestos2026.zip Liquidaciones2025.zip
```

or use the **Update official data** workflow in GitHub Actions. Each yearly
file takes a few minutes; existing years are kept.

Source: Ministerio de Hacienda, CONPREL. The MIT licence covers the code; the
data follow the reuse conditions of their sources (Spanish public-sector
information, reusable with attribution under Ley 37/2007; the municipal code
list under ODC-PDDL). Cite Ministerio de Hacienda (CONPREL) and INE when reusing
them, and the Ministerio de Política Territorial for the mayors. How the
official spending policies become the app's areas:
`docs/CATEGORIES.md`.

## Other countries

The app reads any folder in the same normalised format:
`OPENMUNICIPALITY_DATA_DIR=/path/to/dataset streamlit run app.py`. See
`docs/ADDING_A_DATA_SOURCE.md`.

## Tests and quality

```bash
pip install -r requirements-dev.txt
python -m pytest
```

GitHub Actions runs the tests, with a coverage report, on Python 3.10–3.13
(92 % of the application code, 83 % including the data-build scripts).
Readability of the generated texts for all municipalities:
`docs/readability.md` (median INFLESZ 69.3, "fairly easy").

## Structure

```
app.py                       Streamlit interface
modules/conprel.py           Official dataset: search, data, benchmarks, checks
modules/mayors.py            Mayors: periods in office, budget attribution
modules/metrics_engine.py    Per-resident, share and year-on-year indicators
modules/narrative.py         Plain-language sentences
modules/i18n.py              Texts (es/en), category names, number formats
modules/visualizer.py        Plotly charts
modules/share.py             Summary image and embed code
modules/ui.py                Appearance and accessibility settings
scripts/build_conprel.py     Builds data/conprel/ from the CONPREL Access files
scripts/build_municipality_list.py   Full INE municipality list
scripts/build_mayors.py      Builds mayors.csv.gz from the Ministry lists
scripts/readability.py       Readability study of the generated texts
data/conprel/                Normalised dataset (see datapackage.json)
docs/                        Publishing guide (es), data-source guide, readability
static/fonts/                Atkinson Hyperlegible Next (SIL Open Font License)
```

## Citation

Roa Domínguez, J. A. (2026). *OpenMunicipality* (version 1.0.0) [Computer
software]. Zenodo. <https://doi.org/10.5281/zenodo.23451732>

Citation metadata: `CITATION.cff`. Source code:
<https://github.com/juankiord/OpenMunicipality>.

Licence: MIT. The bundled font is under the SIL Open Font License 1.1
(`static/fonts/OFL.txt`).
