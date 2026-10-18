# Mayors: source and processing

**Source:** Ministerio de Política Territorial, Sistema de Información Local
(SIL), "Alcaldes y concejales"
(<https://mpt.gob.es/politica-territorial/local/sistema_de_informacion_local_-SIL-/alcaldes_y_concejales.html>):

- simplified lists of previous terms, `Alcaldes mandato 2007-2011`,
  `2011-2015`, `2015-2019` and `2019-2023` (XLSX);
- for the current term, "Ficha de Alcaldes de la Legislatura 2023", exported
  on 17 October 2026 from the Ministry's query service
  (<https://concejales.redsara.es/consulta/>). It lists only the mayor in
  office on that day.

Spanish public-sector information, reusable with attribution (Ley 37/2007).

**Built with**

```bash
pip install openpyxl
python scripts/build_mayors.py --since 2010-01-01 \
    Alcaldes_Mandato_2007_2011.xlsx Alcaldes_Mandato_2011_2015.xlsx \
    Alcaldes_Mandato_2015_2019.xlsx Alcaldes_Mandato_2019_2023.xlsx \
    ficha_alcaldes_2023_17-10-2026_18_36_29.xlsx
```

One row per mayor and term: `ine_code`, `term`, `name`, `list`, `start`, `end`
(42,661 rows).

Processing:

- From the 2007-2011 list only the mayors still in office on 1 January 2010,
  the first year of the budgets, are kept (620 earlier ones are dropped). Their
  start date is the start of that term or later, so the app says "in office
  since at least…" for whoever was already mayor when the data begin.
- INE codes: the 2007-2011 list has 5-digit codes; later lists add a check
  digit (6 digits), of which the first five are kept, restoring leading zeros
  lost in the spreadsheets.
- Names in capitals are written in title case; the current-term export splits
  them into first name and two surnames, which are joined. Accents missing in
  the source are not added.
- Lists are kept as registered, with spelling variants of the same label
  unified (`C's`/`CS` → `Cs`, `C.ELECTORAL` → `C. ELECTORAL`, `IND.` → `IND`…).
  Past terms often record coalitions as `C. ELECTORAL`; the current-term export
  gives the party or coalition name (`PSC-CP`, `ERC - AM`…).
- Missing or overlapping dates are filled from the neighbouring mayors or the
  limits of the term (1,275 in all); the same person listed twice in a term
  becomes one row. The current term ends on the export date.
- Four codes belong to councils that have since merged (15026, 15063, 36011,
  36012) and do not match a current municipality.

Coverage: 1 January 2010 – 17 October 2026. For the current term, mayors who
left office before the export date are not published: in 638 councils whose
mayor took office after the 2023 constitution, the time between June 2023
and that date has no mayor, and the app says so.
