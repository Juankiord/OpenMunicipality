"""Builds the bundled municipal dataset from the Spanish Ministry of Finance
CONPREL databases (Presupuestos y Liquidaciones de las Entidades Locales).

Download the "Datos por Entidad Local. Máximo nivel de desglose (ACCESS)" file
for each year and type from https://serviciostelematicosext.hacienda.gob.es/SGFAL/CONPREL
and run, for example:

    python scripts/build_conprel.py Presupuestos2025.zip Presupuestos2024.zip \
        Liquidaciones2024.zip

Requires mdbtools (`apt install mdbtools`, `brew install mdbtools`) to read
the Access files. Writes data/conprel/: municipalities, lines_<stage>,
programs_<stage>, program_names and benchmarks (.csv.gz).
Existing years/stages in the output are kept unless they are rebuilt.
"""
import argparse
import io
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.conprel import PROVINCES, parts  # noqa: E402

OUT = ROOT / 'data' / 'conprel'

# Spending policies (Orden EHA/3565/2008, 2-digit "política de gasto") grouped
# into plain-language areas. Codes are stable keys translated in modules/i18n.
POLICY_GROUPS = {
    '01': 'S_DEBT', '13': 'S_SAFETY', '15': 'S_HOUSING', '16': 'S_COMMUNITY',
    '17': 'S_ENVIRONMENT', '21': 'S_PENSIONS', '22': 'S_PENSIONS',
    '23': 'S_SOCIAL', '24': 'S_EMPLOYMENT', '31': 'S_HEALTH',
    '32': 'S_EDUCATION', '33': 'S_CULTURE', '34': 'S_SPORT',
    '41': 'S_ECONOMY', '42': 'S_ECONOMY', '43': 'S_ECONOMY', '46': 'S_ECONOMY',
    '49': 'S_ECONOMY', '44': 'S_TRANSPORT', '45': 'S_INFRA', '91': 'S_GOV',
    '92': 'S_GOV', '93': 'S_GOV', '94': 'S_TRANSFERS',
}
# Income economic chapters; consolidation adjustments (4t, 7t) join their chapter
INCOME_CHAPTERS = {str(c): f'I{c}' for c in range(1, 10)}
INCOME_CHAPTERS.update({'4t': 'I4', '7t': 'I7'})
# Spending by economic chapter (1 staff ... 6 investment ... 9 debt repayment)
EXPENSE_CHAPTERS = {str(c): f'E{c}' for c in range(1, 10)}

POP_BANDS = [0, 1_000, 5_000, 20_000, 50_000, 100_000, 500_000, float('inf')]
ARTICLES = {'la', 'las', 'el', 'los', 'les', 'els', 'es', 'a', 'o', 'as', 'os',
            "l'", 'sa', 'ses', 'lo'}


def readable_name(name: str) -> str:
    """'Coruña (A)' -> 'A Coruña'; 'Palmas, Las' -> 'Las Palmas'."""
    name = ' '.join(name.split())
    match = (re.fullmatch(r'(.+?) \(([^)]+)\)', name)
             or re.fullmatch(r'(.+?), ([^,]+)', name))
    if match and match.group(2).lower() in ARTICLES:
        article = match.group(2)
        sep = '' if article.endswith("'") else ' '
        return f'{article}{sep}{match.group(1)}'
    return name


def population_band(population: float) -> str:
    for low, high in zip(POP_BANDS, POP_BANDS[1:]):
        if low <= population < high:
            return f'{low}-{high}'
    return 'unknown'


def tables_in(db: Path) -> dict[str, str]:
    """Lower-case name -> real name of the tables in an Access file."""
    names = subprocess.run(['mdb-tables', '-1', str(db)], check=True,
                           capture_output=True, text=True).stdout.split()
    return {name.lower(): name for name in names}


def export_table(db: Path, table: str) -> pd.DataFrame:
    table = tables_in(db).get(table.lower(), table)  # names vary in case
    raw = subprocess.run(['mdb-export', str(db), table], check=True,
                         capture_output=True).stdout
    df = pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]
    return df.apply(lambda col: col.str.strip())


def year_and_stage(path: Path) -> tuple[int, str]:
    match = re.search(r'(presupuesto|liquidaci)\D*(\d{4})', path.name, re.I)
    if not match:
        raise SystemExit(f'Cannot infer type/year from file name: {path.name}')
    stage = 'budget' if match.group(1).lower().startswith('pres') else 'executed'
    year = int(match.group(2))
    if year < 2010:  # earlier years use the 1989 functional classification
        raise SystemExit(f'{path.name}: only 2010 and later are supported '
                         '(Orden EHA/3565/2008 programme classification)')
    return year, stage


def amount_column(df: pd.DataFrame) -> str:
    # Liquidations (2009+) report Importer: recognised rights/obligations
    return 'importer' if 'importer' in df.columns else 'importe'


def process(db: Path, year: int, stage: str):
    inv = export_table(db, 'tb_inventario')
    if 'tb_provincias' in tables_in(db):
        prov = export_table(db, 'tb_Provincias')
    else:  # some years (2018) ship without it: use the app's own list
        prov = pd.DataFrame({'provincia': list(PROVINCES),
                             'nombre': list(PROVINCES.values())})
    kind = inv['codbdgel'].str[5:7]
    mun = inv[kind.isin(['AA', 'ZZ']) & (inv['id'] == inv['idente'])].copy()
    mun = mun.drop_duplicates('id')
    mun['ine_code'] = mun['codbdgel'].str[:5]
    mun['name'] = mun['nombreppal'].map(readable_name)
    mun['province_code'] = mun['codbdgel'].str[:2]
    provinces = dict(zip(prov['provincia'], prov['nombre'].map(readable_name)))
    mun['province'] = mun['province_code'].map(provinces)
    mun['population'] = pd.to_numeric(mun['poblacion'], errors='coerce')
    ids = dict(zip(mun['id'], mun['ine_code']))

    eco = export_table(db, 'tb_economica_cons')
    eco = eco[eco['id'].isin(ids)]
    eco_amount = pd.to_numeric(eco[amount_column(eco)], errors='coerce')
    is_income = (eco['tipreig'] == 'I') & eco['cdcta'].isin(INCOME_CHAPTERS)
    income = pd.DataFrame({
        'ine_code': eco.loc[is_income, 'id'].map(ids), 'Type': 'Income',
        'Category': eco.loc[is_income, 'cdcta'].map(INCOME_CHAPTERS),
        'Amount': eco_amount[is_income]})
    is_chapter = (eco['tipreig'] == 'G') & eco['cdcta'].isin(EXPENSE_CHAPTERS)
    chapters = pd.DataFrame({
        'ine_code': eco.loc[is_chapter, 'id'].map(ids), 'Type': 'ExpenseChapter',
        'Category': eco.loc[is_chapter, 'cdcta'].map(EXPENSE_CHAPTERS),
        'Amount': eco_amount[is_chapter]})
    # Investment = chapters 6 (real investment) + 7 (capital transfers)
    investment = (chapters[chapters['Category'].isin(['E6', 'E7'])]
                  .groupby('ine_code', as_index=False)['Amount'].sum()
                  .assign(Type='ExpenseChapter', Category='E67'))

    fun_all = export_table(db, 'tb_funcional_cons')
    fun_all = fun_all[fun_all['id'].isin(ids)]
    fun = fun_all[fun_all['cdfgr'].str.len() == 2]
    unknown = set(fun['cdfgr']) - set(POLICY_GROUPS)
    if unknown:
        raise SystemExit(f'Unmapped spending policies: {sorted(unknown)}')
    spend = pd.DataFrame({
        'ine_code': fun['id'].map(ids), 'Type': 'Expense',
        'Category': fun['cdfgr'].map(POLICY_GROUPS),
        'Amount': pd.to_numeric(fun[amount_column(fun)], errors='coerce')})

    lines = (pd.concat([income, spend, chapters, investment])
             .groupby(['ine_code', 'Type', 'Category'], as_index=False)['Amount']
             .sum().round(2))
    lines.insert(1, 'Year', year)
    lines.insert(2, 'Stage', stage)

    # Detail: the 3-digit spending programmes inside each area
    prog = fun_all[fun_all['cdfgr'].str.len() == 3]
    programs = pd.DataFrame({
        'ine_code': prog['id'].map(ids),
        'Category': prog['cdfgr'].str[:2].map(POLICY_GROUPS),
        'Program': prog['cdfgr'],
        'Amount': pd.to_numeric(prog[amount_column(prog)], errors='coerce')})
    programs = (programs.groupby(['ine_code', 'Category', 'Program'],
                                 as_index=False)['Amount'].sum().round(2))
    programs = programs[programs['Amount'] != 0]
    programs.insert(1, 'Year', year)
    programs.insert(2, 'Stage', stage)
    names = export_table(db, 'tb_cuentasProgramas')
    names = names[names['cdfgr'].str.len() == 3].rename(
        columns={'cdfgr': 'Program', 'nombre': 'Name'})[['Program', 'Name']]
    names.insert(0, 'Year', year)  # codes can change meaning (2014 reform)

    programs = check_totals(lines, programs, year)

    meta = mun[['ine_code', 'name', 'province', 'population']].copy()
    meta.insert(1, 'Year', year)
    meta.insert(2, 'Stage', stage)
    meta = meta[meta['ine_code'].isin(lines['ine_code'])]
    return meta, lines, programs, names


def check_totals(lines: pd.DataFrame, programs: pd.DataFrame,
                 year: int) -> pd.DataFrame:
    """Spending by area, by economic chapter and by programme must add up to
    the same total for every municipality (to the cent). Returns the
    programme lines that can be shown.

    Until 2013, municipalities with up to 5,000 residents could report
    spending only down to areas and policies, not programmes (Hacienda,
    CONPREL methodology); for those years, incomplete programme detail is
    dropped instead of stopping the build. From 2014, a few municipalities
    (at most 1 %) with inconsistent programme detail in the source lose that
    detail; more than that stops the build. Areas and chapters always must
    match."""
    def total(frame):
        return frame.groupby('ine_code')['Amount'].sum()
    by_area = total(lines[lines['Type'] == 'Expense'])
    by_chapter = total(lines[(lines['Type'] == 'ExpenseChapter')
                             & (lines['Category'] != 'E67')])
    by_programme = total(programs)
    for name, other in (('economic chapter', by_chapter),
                        ('programme', by_programme)):
        gap = (by_area - other.reindex(by_area.index, fill_value=0)).abs()
        bad = gap[gap > 0.01]
        if bad.empty:
            continue
        if name == 'programme' and (year < 2014
                                    or len(bad) <= 0.01 * len(by_area)):
            reason = ('allowed before 2014' if year < 2014
                      else 'inconsistent in the source: ' + ', '.join(bad.index))
            print(f'  {len(bad)} municipalities without complete programme '
                  f'detail ({reason}): their programme detail is dropped')
            return programs[~programs['ine_code'].isin(bad.index)]
        raise SystemExit(f'Totals by area and by {name} differ for '
                         f'{len(bad)} municipalities, e.g. {bad.idxmax()} '
                         f'({bad.max():.2f} €)')
    return programs


def benchmarks(meta: pd.DataFrame, lines: pd.DataFrame) -> pd.DataFrame:
    """Median euros per resident by population band, including zeros for
    municipalities that spend nothing in an area."""
    keys = ['Year', 'Stage']
    m = meta.assign(band=meta['population'].map(population_band))
    m = m[m['population'] > 0]
    totals = (lines.groupby(keys + ['ine_code', 'Type'], as_index=False)
              ['Amount'].sum().assign(Category='_TOTAL'))
    full = pd.concat([lines, totals])
    wide = full.pivot_table(index=keys + ['ine_code'], columns=['Type', 'Category'],
                            values='Amount', fill_value=0)
    long = wide.stack(['Type', 'Category'], future_stack=True).rename('Amount')
    long = long.reset_index().merge(m[keys + ['ine_code', 'population', 'band']],
                                    on=keys + ['ine_code'])
    long['Per_Capita'] = long['Amount'] / long['population']
    out = (long.groupby(keys + ['band', 'Type', 'Category'])['Per_Capita']
           .agg(Median_Per_Capita='median', Municipalities='size').reset_index())
    out['Median_Per_Capita'] = out['Median_Per_Capita'].round(2)
    return out


def merge_existing(table: str, new: pd.DataFrame) -> pd.DataFrame:
    """Existing rows of a table plus the new ones; years and stages that were
    rebuilt replace the old rows."""
    files = parts(OUT, table)
    if not files:
        return new
    old = pd.concat([pd.read_csv(path, dtype={'ine_code': str, 'Program': str})
                     for path in files], ignore_index=True)
    rebuilt = new[['Year', 'Stage']].drop_duplicates()
    old = old.merge(rebuilt, how='left', indicator=True)
    old = old[old['_merge'] == 'left_only'].drop(columns='_merge')
    return pd.concat([old, new], ignore_index=True)


def name_periods(names: pd.DataFrame) -> pd.DataFrame:
    """Programme names by year -> one row per name and the first year it
    applies (Since). The national programme list was revised in 2014
    (Orden HAP/419/2014, applied from 2015): some codes changed meaning, e.g.
    134 'Protección civil' became 'Movilidad urbana'."""
    rows = names.assign(Year=names['Year'].astype(int),
                        Name=names['Name'].str.strip())
    rows = rows.sort_values(['Program', 'Year']).drop_duplicates(
        ['Program', 'Year'], keep='last')
    changed = rows['Name'] != rows.groupby('Program')['Name'].shift()
    return (rows[changed].rename(columns={'Year': 'Since'})
            [['Program', 'Since', 'Name']].reset_index(drop=True))


def write_by_stage(table: str, frame: pd.DataFrame) -> None:
    """One file per stage (lines_budget.csv.gz, lines_executed.csv.gz): the
    app reads them together and each stays well under 50 MB."""
    for old in parts(OUT, table):
        old.unlink()
    keys = [c for c in ('Year', 'ine_code', 'Type', 'Category', 'Program')
            if c in frame.columns]
    for stage, rows in frame.groupby('Stage'):
        rows.sort_values(keys).to_csv(OUT / f'{table}_{stage}.csv.gz',
                                      index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('files', nargs='+', type=Path,
                        help='CONPREL Access files (.accdb/.mdb or .zip)')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    metas, all_lines, all_programs, all_names = [], [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        for path in args.files:
            year, stage = year_and_stage(path)
            db = path
            if path.suffix.lower() == '.zip':
                with zipfile.ZipFile(path) as zf:
                    member = next(n for n in zf.namelist()
                                  if n.lower().endswith(('.accdb', '.mdb')))
                    db = Path(zf.extract(member, tmp))
            print(f'{path.name}: year {year}, stage {stage}')
            meta, lines, programs, names = process(db, year, stage)
            print(f'  {len(meta)} municipalities, {len(lines)} lines, '
                  f'{len(programs)} programme lines')
            metas.append(meta)
            all_lines.append(lines)
            all_programs.append(programs)
            all_names.append(names)

    meta = merge_existing('municipalities', pd.concat(metas))
    lines = merge_existing('lines', pd.concat(all_lines))
    programs = merge_existing('programs', pd.concat(all_programs))
    names = pd.concat(all_names)
    if (OUT / 'program_names.csv.gz').exists():
        known = pd.read_csv(OUT / 'program_names.csv.gz', dtype=str)
        if 'Since' in known.columns:
            names = pd.concat([known.rename(columns={'Since': 'Year'}), names])
    name_periods(names).to_csv(OUT / 'program_names.csv.gz', index=False)
    meta.to_csv(OUT / 'municipalities.csv.gz', index=False)
    write_by_stage('lines', lines)
    write_by_stage('programs', programs)
    benchmarks(meta, lines).to_csv(OUT / 'benchmarks.csv.gz', index=False)
    print(f'Written to {OUT}')


if __name__ == '__main__':
    main()
