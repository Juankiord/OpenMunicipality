# Adding a data source (another country or region)

The app does not read any official database directly. It reads a **dataset
folder** in a small normalised format, described field by field in
`data/conprel/datapackage.json`. The Spanish dataset is one such folder, built
by `scripts/build_conprel.py` from the Ministry of Finance CONPREL database.

To support another country or region:

1. **Write a builder** (for example `scripts/build_<source>.py`) that turns the
   official files into the same files:

   | File | Required | Content |
   |------|----------|---------|
   | `municipalities.csv.gz` | yes | `ine_code, Year, Stage, name, province, population` |
   | `lines.csv.gz` | yes | `ine_code, Year, Stage, Type, Category, Amount` |
   | `benchmarks.csv.gz` | yes | medians per resident by population band |
   | `categories.csv` | if you use new codes | `code, name_es, name_en` |
   | `programs.csv.gz`, `program_names.csv.gz` | no | detail inside each area; names as `Program, Name` or `Program, Since, Name` when codes change meaning |
   | `all_municipalities.csv.gz` | no | full list, to explain missing data |
   | `cpi.csv` | no | annual inflation, for the "adjust for inflation" switch |
   | `mayors.csv.gz` | no | `ine_code, term, name, list, start, end`: who held the mayoralty, for the "Who was in office" tab |

   `lines` and `programs` can also be split into parts named
   `lines_<anything>.csv.gz` (for example one per stage); the app reads all
   the parts together. The bundled Spanish dataset does this to keep each
   file small.

   - `ine_code` is the official code of each municipality in that country.
   - `Stage` is `budget` (planned) or `executed` (outturn).
   - `Type` is `Expense` (by area), `Income` (by source) or `ExpenseChapter`
     (by economic nature: `E1` staff, `E2` purchases, `E3` interest, `E4`
     grants, `E5` contingency, `E6` investment, `E7` capital transfers, `E8`
     financial assets, `E9` debt repayment, `E67` = `E6` + `E7`).
   - Spending areas can reuse the built-in codes (`S_SOCIAL`, `S_EDUCATION`,
     `S_COMMUNITY`…, see `OFFICIAL_CATEGORIES` in `modules/i18n.py`), which
     makes the plain-language names available at once, or define new codes
     in `categories.csv`.
   - The `benchmarks` function in `scripts/build_conprel.py` can be reused
     as is.

2. **Point the app to the folder** and run it:

   ```bash
   OPENMUNICIPALITY_DATA_DIR=/path/to/dataset streamlit run app.py
   ```

3. **Add a test** that loads a few rows of the new dataset, as
   `tests/test_data_source.py` does with a made-up country.

Texts that mention Spanish institutions (the Ministry of Finance, the foral
regime of Álava and Navarre) live in `modules/i18n.py` and should be adapted
for the new source.
