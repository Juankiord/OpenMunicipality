"""Access to an official budget dataset in the app's normalised format.

The bundled dataset (data/conprel/) is built from the Spanish Ministry of
Finance CONPREL database by scripts/build_conprel.py. Any other country or
region can be plugged in by producing the same files in another folder and
pointing OPENMUNICIPALITY_DATA_DIR to it (see docs/ADDING_A_DATA_SOURCE.md).
"""
import os
import re
import unicodedata
from pathlib import Path

import pandas as pd

from modules.i18n import register_categories

DATA_DIR = Path(os.environ.get(
    'OPENMUNICIPALITY_DATA_DIR', Path(__file__).resolve().parents[1] / 'data' / 'conprel'))
BANDS = [0, 1_000, 5_000, 20_000, 50_000, 100_000, 500_000, float('inf')]
# Repeated text columns kept as categories: the 2010-2025 tables take about a
# fifth of the memory. Rows handed to the rest of the app are plain strings.
COMPACT = {'ine_code': 'category', 'Stage': 'category', 'Type': 'category',
           'Category': 'category', 'Program': 'category', 'Year': 'int16'}
ARTICLE_RE = r'^(la|las|el|los|les|els|es|a|o|as|os|l|sa|ses|lo) '


def parts(data_dir: Path, table: str) -> list[Path]:
    """A table is one file (lines.csv.gz) or several parts that are read
    together (lines_budget.csv.gz, lines_executed.csv.gz...), which keeps
    each file small enough for code hosting sites."""
    single = data_dir / f'{table}.csv.gz'
    return [single] if single.exists() else sorted(
        data_dir.glob(f'{table}_*.csv.gz'))


def read_table(data_dir: Path, table: str) -> pd.DataFrame:
    files = parts(data_dir, table)
    if not files:
        raise FileNotFoundError(f'No {table}*.csv.gz files in {data_dir}')
    frames = [pd.read_csv(path, dtype=COMPACT) for path in files]
    # Parts share one set of categories, so joining them keeps them compact
    for column in frames[0].columns:
        if isinstance(frames[0][column].dtype, pd.CategoricalDtype):
            union = sorted(set().union(*(f[column].cat.categories
                                         for f in frames)))
            for frame in frames:
                frame[column] = frame[column].cat.set_categories(union)
    return pd.concat(frames, ignore_index=True)


def available() -> bool:
    return bool(parts(DATA_DIR, 'lines'))


def load(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame,
                                             pd.DataFrame]:
    """Returns (municipalities, budget lines, benchmarks). Optional
    categories.csv (code, name_es, name_en) names the dataset's own codes."""
    if (data_dir / 'categories.csv').exists():
        register_categories(pd.read_csv(data_dir / 'categories.csv', dtype=str))
    meta = pd.read_csv(data_dir / 'municipalities.csv.gz',
                       dtype={'ine_code': str})
    lines = read_table(data_dir, 'lines')
    bench = pd.read_csv(data_dir / 'benchmarks.csv.gz')
    return meta, lines, bench


def normalise(text: str) -> str:
    """Lower case, no accents, no punctuation: 'A Coruña' -> 'a coruna'."""
    text = unicodedata.normalize('NFKD', str(text).lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return ' '.join(re.sub(r"[^a-z0-9ñ ]+", ' ', text).split())


def search_index(meta: pd.DataFrame,
                 everyone: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per municipality ready for searching. With the full INE list
    (`everyone`), municipalities without data in the Ministry's database are
    also found, flagged has_data=False."""
    latest = meta.sort_values('Year').drop_duplicates('ine_code', keep='last')
    index = latest[['ine_code', 'name', 'province', 'population']].copy()
    index['has_data'] = True
    if everyone is not None:
        missing = everyone[~everyone['ine_code'].isin(index['ine_code'])].copy()
        missing['province'] = missing['ine_code'].str[:2].map(PROVINCES)
        missing['population'] = 0
        missing['has_data'] = False
        index = pd.concat([index, missing[index.columns]], ignore_index=True)
    index['province'] = index['province'].fillna('')
    index['key'] = index['name'].map(normalise)
    index['core'] = index['key'].str.replace(ARTICLE_RE, '', regex=True)
    index['label'] = index['name'] + (' (' + index['province'] + ')').where(
        index['province'] != '', '')
    return index.set_index('ine_code')


def search(index: pd.DataFrame, query: str, limit: int = 8) -> pd.DataFrame:
    """Ranks municipalities: exact name (with or without its article), then
    names with a word starting with the query, then any other match; within
    each group, larger towns first. Accents and capitals are ignored."""
    q = normalise(query)
    if not q:
        return index.iloc[0:0]
    key = index['key']
    tier = pd.Series(3, index=index.index)
    tier[key.str.contains(q, regex=False)] = 2
    tier[(' ' + key).str.contains(' ' + q, regex=False)] = 1
    tier[(key == q) | (index['core'] == q)] = 0
    tier[key.str.len() == 0] = 3
    found = index.assign(tier=tier)[tier < 3]
    return found.sort_values(['tier', 'has_data', 'population'],
                             ascending=[True, False, False]).head(limit)


def municipality(meta: pd.DataFrame, lines: pd.DataFrame, ine_code: str,
                 stage: str) -> tuple[pd.DataFrame, dict[int, int], str]:
    """Budget lines in the app schema, population by year and display name."""
    rows = lines[(lines['ine_code'] == ine_code) & (lines['Stage'] == stage)
                 & lines['Type'].isin(['Expense', 'Income'])]
    df = rows[['Category', 'Type', 'Amount', 'Year']].astype(
        {'Category': str, 'Type': str, 'Year': int}).reset_index(drop=True)
    info = meta[(meta['ine_code'] == ine_code) & (meta['Stage'] == stage)]
    population = dict(zip(info['Year'].astype(int),
                          info['population'].astype(int)))
    name = info['name'].iloc[-1] if len(info) else ''
    return df, population, name


def stages(lines: pd.DataFrame, ine_code: str) -> list[str]:
    found = set(lines.loc[lines['ine_code'] == ine_code, 'Stage'])
    return [s for s in ('budget', 'executed') if s in found]


def band(population: float) -> str:
    for low, high in zip(BANDS, BANDS[1:]):
        if low <= population < high:
            return f'{low}-{high}'
    return 'unknown'


def benchmark(bench: pd.DataFrame, year: int, stage: str,
              population: float) -> tuple[str, pd.DataFrame]:
    """Median euros per resident in municipalities of a similar size."""
    b = band(population)
    rows = bench[(bench['Year'] == year) & (bench['Stage'] == stage)
                 & (bench['band'] == b)]
    return b, rows[['Type', 'Category', 'Median_Per_Capita', 'Municipalities']]


# ------------------------------------------------------------- extensions
PROVINCES = {
    '01': 'Araba/Álava',
    '02': 'Albacete',
    '03': 'Alicante / Alacant',
    '04': 'Almería',
    '05': 'Avila',
    '06': 'Badajoz',
    '07': 'Illes Balears',
    '08': 'Barcelona',
    '09': 'Burgos',
    '10': 'Cáceres',
    '11': 'Cádiz',
    '12': 'Castellón / Castelló',
    '13': 'Ciudad Real',
    '14': 'Córdoba',
    '15': 'A Coruña',
    '16': 'Cuenca',
    '17': 'Girona',
    '18': 'Granada',
    '19': 'Guadalajara',
    '20': 'Gipuzkoa',
    '21': 'Huelva',
    '22': 'Huesca',
    '23': 'Jaén',
    '24': 'León',
    '25': 'Lleida',
    '26': 'La Rioja',
    '27': 'Lugo',
    '28': 'Madrid',
    '29': 'Málaga',
    '30': 'Murcia',
    '31': 'Navarra',
    '32': 'Ourense',
    '33': 'Asturias',
    '34': 'Palencia',
    '35': 'Las Palmas',
    '36': 'Pontevedra',
    '37': 'Salamanca',
    '38': 'Santa Cruz de Tenerife',
    '39': 'Cantabria',
    '40': 'Segovia',
    '41': 'Sevilla',
    '42': 'Soria',
    '43': 'Tarragona',
    '44': 'Teruel',
    '45': 'Toledo',
    '46': 'Valencia / València',
    '47': 'Valladolid',
    '48': 'Bizkaia',
    '49': 'Zamora',
    '50': 'Zaragoza',
    '51': 'Ceuta',
    '52': 'Melilla',
}
FORAL_PROVINCES = {'01', '31'}  # Araba/Álava and Navarra
# Economic chapters of spending grouped into plain-language kinds
KINDS = {'K_STAFF': ['E1'], 'K_PURCHASES': ['E2'], 'K_GRANTS': ['E4'],
         'K_INVEST': ['E6', 'E7'], 'K_DEBT': ['E3', 'E9'],
         'K_OTHER': ['E5', 'E8']}
# Kinds whose benchmark is a single stored series (medians cannot be summed)
KIND_BENCH = {'K_STAFF': 'E1', 'K_PURCHASES': 'E2', 'K_GRANTS': 'E4',
              'K_INVEST': 'E67'}


def load_programs(data_dir: Path = DATA_DIR
                  ) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """Programme detail and names, or None when the dataset has none (the
    detail is optional; the rest of the app works without it)."""
    if not parts(data_dir, 'programs') or \
            not (data_dir / 'program_names.csv.gz').exists():
        return None
    programs = read_table(data_dir, 'programs')
    names = pd.read_csv(data_dir / 'program_names.csv.gz', dtype=str)
    return programs, names


def program_names(names: pd.DataFrame, year: int) -> dict[str, str]:
    """Programme code -> official name in force in that year. Optional
    column Since (first year a name applies) handles codes whose meaning
    changed; without it, one name per code for every year."""
    if 'Since' in names.columns:
        names = (names[names['Since'].astype(int) <= year]
                 .sort_values('Since').drop_duplicates('Program', keep='last'))
    return dict(zip(names['Program'], names['Name'].str.strip()))


def load_all_municipalities(path: Path = DATA_DIR /
                            'all_municipalities.csv.gz') -> pd.DataFrame | None:
    return pd.read_csv(path, dtype=str) if path.exists() else None


def kinds(lines: pd.DataFrame, ine_code: str, stage: str,
          year: int) -> pd.DataFrame:
    """Spending of one year grouped by kind (staff, purchases, investment…)."""
    rows = lines[(lines['ine_code'] == ine_code) & (lines['Stage'] == stage)
                 & (lines['Year'] == year)
                 & (lines['Type'] == 'ExpenseChapter')]
    amounts = dict(zip(rows['Category'].astype(str), rows['Amount']))
    return pd.DataFrame({
        'Category': list(KINDS), 'Type': 'Expense',
        'Amount': [sum(amounts.get(c, 0.0) for c in chapters)
                   for chapters in KINDS.values()]})


def programs_of(programs: pd.DataFrame, ine_code: str, stage: str, year: int,
                category: str) -> pd.DataFrame:
    rows = programs[(programs['ine_code'] == ine_code)
                    & (programs['Stage'] == stage) & (programs['Year'] == year)
                    & (programs['Category'] == category)]
    return (rows[['Program', 'Amount']].astype({'Program': str})
            .sort_values('Amount', ascending=False))


def years_of(meta: pd.DataFrame, stage: str) -> list[int]:
    """Years the dataset covers for a stage (budget or outturn)."""
    return sorted(int(y) for y in set(meta['Year'][meta['Stage'] == stage]))


def years_without_data(meta: pd.DataFrame, ine_code: str,
                       stage: str = 'budget') -> list[int]:
    """Years in the dataset for which this municipality sent no budget (or
    no outturn)."""
    present = set(meta['Year'][(meta['ine_code'] == ine_code)
                               & (meta['Stage'] == stage)])
    return [y for y in years_of(meta, stage) if y not in present]


def execution(lines: pd.DataFrame, ine_code: str,
              year: int) -> tuple[float, float] | None:
    """(planned, actually spent) for a year with both budget and outturn."""
    rows = lines[(lines['ine_code'] == ine_code) & (lines['Year'] == year)
                 & (lines['Type'] == 'Expense')]
    totals = rows.groupby('Stage', observed=True)['Amount'].sum()
    if {'budget', 'executed'} <= set(totals.index):
        return float(totals['budget']), float(totals['executed'])
    return None


def yearly_totals(meta: pd.DataFrame, lines: pd.DataFrame,
                  ine_code: str) -> pd.DataFrame:
    """One row per year with the figures the mayoralty view lines up:
    planned and spent per resident, planned investment per resident,
    whether the budget repeats the previous one area by area (rolled over),
    and the share of the plan that was spent."""
    rows = lines[lines['ine_code'] == ine_code].astype(
        {'Stage': str, 'Type': str, 'Category': str})
    info = meta[meta['ine_code'] == ine_code]
    people = {(str(s), int(y)): int(p) for s, y, p in
              zip(info['Stage'], info['Year'], info['population'])}
    spend = rows[rows['Type'] == 'Expense']
    totals = spend.groupby(['Stage', 'Year'])['Amount'].sum()
    chapters = rows[(rows['Type'] == 'ExpenseChapter')
                    & (rows['Stage'] == 'budget')]
    # A year with chapters but no investment ones invested nothing
    invest = chapters['Amount'].where(
        chapters['Category'].isin(KINDS['K_INVEST']), 0.0).groupby(
        chapters['Year']).sum()
    by_area = {int(y): dict(zip(g['Category'], g['Amount'])) for y, g in
               spend[spend['Stage'] == 'budget'].groupby('Year')}
    out = []
    for year in sorted({int(y) for y in rows['Year']}):
        row = {'Year': year}
        for stage in ('budget', 'executed'):
            total = totals.get((stage, year))
            residents = people.get((stage, year))
            row[f'{stage}_per_res'] = (float(total) / residents
                                       if total is not None and residents
                                       else None)
        residents = people.get(('budget', year))
        row['invest_per_res'] = (float(invest[year]) / residents
                                 if year in invest.index and residents
                                 else None)
        now, before = by_area.get(year), by_area.get(year - 1)
        row['rolled_over'] = bool(now and before and set(now) == set(before)
                                  and all(abs(now[c] - before[c]) < 0.01
                                          for c in now))
        planned = totals.get(('budget', year))
        spent = totals.get(('executed', year))
        row['spent_vs_plan'] = (float(spent) / float(planned)
                                if planned and spent is not None
                                and planned > 0 else None)
        out.append(row)
    return pd.DataFrame(out)


def load_cpi(path: Path = DATA_DIR / 'cpi.csv') -> dict[int, float]:
    """Annual average CPI change (%) by year, INE."""
    if not path.exists():
        return {}
    cpi = pd.read_csv(path)
    return dict(zip(cpi['Year'].astype(int),
                    cpi['CPI_annual_average_change_pct'].astype(float)))


def real_change(nominal_pct: float, inflation_pct: float) -> float:
    """Change after discounting inflation: (1 + n) / (1 + p) - 1."""
    return ((1 + nominal_pct / 100) / (1 + inflation_pct / 100) - 1) * 100


def same_as_previous(year_dev: pd.DataFrame) -> bool:
    """Every spending area exactly as the year before: the usual trace of a
    budget rolled over (prorrogado) because no new one was approved."""
    rows = year_dev.dropna(subset=['Previous_Amount'])
    return (len(rows) > 0 and len(rows) == len(year_dev)
            and (rows['Amount'] - rows['Previous_Amount']).abs().max() < 0.01)


def data_warnings(kpis: dict, prev_kpis: dict | None, stage: str,
                  population: int, prev_population: int | None,
                  usual_per_res: float | None,
                  rolled_over: bool = False,
                  execution_rate: float | None = None
                  ) -> list[tuple[str, dict]]:
    """Signs that a figure may be wrong or exceptional: (text key, values).
    execution_rate: spent / planned in the same year, when both exist."""
    found = []
    if rolled_over and stage == 'budget':
        found.append(('warn_rollover', {}))
    spend = kpis['total_expenditure']
    if prev_kpis and prev_kpis['total_expenditure'] > 0:
        change = (spend / prev_kpis['total_expenditure'] - 1) * 100
        if abs(change) >= 40:
            found.append(('warn_jump' if stage == 'budget'
                          else 'warn_jump_executed', {'pct': change}))
    if usual_per_res and usual_per_res > 0:
        ratio = kpis['per_capita_expenditure'] / usual_per_res
        if ratio >= 3 or ratio <= 1 / 3:
            found.append(('warn_unusual', {'ratio': ratio}))
    if stage == 'budget' and spend > 0 and \
            kpis['total_revenue'] < spend * 0.995:
        found.append(('warn_deficit', {}))
    if prev_population and population and \
            abs(population / prev_population - 1) >= 0.2:
        found.append(('warn_population', {}))
    if execution_rate is not None and not 0.5 <= execution_rate <= 2:
        found.append(('warn_execution', {'pct': execution_rate * 100}))
    return found

