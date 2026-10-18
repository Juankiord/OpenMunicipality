"""Builds data/conprel/mayors.csv.gz from the lists of mayors published by the
Spanish Ministry of Territorial Policy: one spreadsheet per past term
("Alcaldes del mandato de 2.019 a 2.023") and, for the current term, the
"Ficha de Alcaldes de la Legislatura 2023" exported from the Ministry's query
service, which lists only the mayor in office on the day of the export:

    pip install openpyxl
    python scripts/build_mayors.py --since 2010-01-01 \
        Alcaldes_Mandato_2007_2011.xlsx Alcaldes_Mandato_2011_2015.xlsx \
        Alcaldes_Mandato_2015_2019.xlsx Alcaldes_Mandato_2019_2023.xlsx \
        ficha_alcaldes_2023_17-10-2026_18_36_29.xlsx

One row per mayor and term: INE code, term, name, list (as registered, with
spelling variants unified) and the dates in office. Dates missing in the
source are filled from the neighbouring mayors or the start/end of the term;
the build reports how many. A term still in progress ends on the date of the
export (taken from the file name, or --as-of). --since drops the mayors who
had left office before that date. Existing terms in the output are kept
unless they are rebuilt.
"""
import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.mayors import PARTICLES, person_key  # noqa: E402

OUT = ROOT / 'data' / 'conprel' / 'mayors.csv.gz'

# Councils formed after each municipal election (Spain): the first day of
# each term; a term ends the day before the next one starts
TERM_STARTS = {2007: date(2007, 6, 16), 2011: date(2011, 6, 11),
               2015: date(2015, 6, 13), 2019: date(2019, 6, 15),
               2023: date(2023, 6, 17), 2027: date(2027, 6, 12)}

# Only spelling variants of the same label; lists are otherwise kept as the
# register records them (coalitions appear as "C. ELECTORAL", for example)
LIST_VARIANTS = {
    "C's": 'Cs', 'C´s': 'Cs', 'CS': 'Cs',
    'C.ELECTORAL': 'C. ELECTORAL', 'C. ELECTORAL': 'C. ELECTORAL',
    'C.GEST.': 'C. GEST.', 'C. GEST': 'C. GEST.', 'C.GEST': 'C. GEST.',
    'IND.': 'IND', 'PNV': 'EAJ-PNV', 'PPSO': 'P.P.SO.',
}
DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{4})')


def readable_name(name: str) -> str:
    """'MARIA DEL CARMEN CRESPO DIAZ' -> 'Maria del Carmen Crespo Diaz'.
    Words already in mixed case are kept as written."""
    words = str(name).split()
    out = []
    for i, word in enumerate(words):
        if word.isupper():
            lower = word.lower()
            word = lower if (i and lower in PARTICLES) else \
                '-'.join(p[:1].upper() + p[1:] for p in lower.split('-'))
        out.append(word)
    return ' '.join(out)


def parse_date(value) -> date | None:
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date()
    if isinstance(value, date):
        return value
    match = DATE_RE.search(str(value)) if value is not None else None
    if not match:  # blank or "SIN FECHA"
        return None
    if match.group(1):
        return date.fromisoformat(match.group(1))
    day, month, year = match.group(2).split('/')
    return date(int(year), int(month), int(day))


def term_of(sheet: pd.DataFrame, path: Path) -> int:
    """First year of the term, from the title ('mandato de 2.019 a 2.023',
    'Legislatura 2023') or, failing that, from the file name."""
    for value in sheet.to_numpy().ravel():
        match = re.search(r'(?:mandato de|legislatura) (\d)\.?(\d{3})',
                          str(value), re.I)
        if match:
            return int(match.group(1) + match.group(2))
    match = re.search(r'(20\d\d)', path.name)
    if not match:
        raise SystemExit(f'Cannot tell the term of {path.name}')
    return int(match.group(1))


def export_date(path: Path) -> date | None:
    """'ficha_alcaldes_2023_17-10-2026_18_36_29.xlsx' -> 17 October 2026."""
    match = re.search(r'(\d{2})-(\d{2})-(\d{4})', path.name)
    return date(int(match.group(3)), int(match.group(2)),
                int(match.group(1))) if match else None


def text(value) -> str:
    return '' if pd.isna(value) else ' '.join(str(value).split())


def read_sheet(path: Path) -> pd.DataFrame:
    """Either format: the lists of past terms (NOMBRE, LISTA, FECHA
    POSESIÓN, FECHA BAJA) or the current-term export (Nombre, 1er Apellido,
    2º Apellido, Fecha de Posesión, Partido; no end dates)."""
    raw = pd.read_excel(path, header=None, dtype=object)
    header = next(i for i, row in raw.iterrows()
                  if any(str(v).strip().upper() == 'CÓDIGO INE' for v in row))
    term = term_of(raw.iloc[:header], path)
    table = raw.iloc[header + 1:].copy()
    table.columns = [str(c).strip().upper() for c in raw.iloc[header]]
    table = table[table['CÓDIGO INE'].notna()]
    code = table['CÓDIGO INE'].astype(str).str.strip().str.replace(
        r'\.0$', '', regex=True)
    # From 2011 the codes carry a check digit (6 digits; a lost leading zero
    # leaves 5); the 2007-2011 list has plain 5-digit codes
    if (code.str.len() == 6).mean() > 0.5:
        code = code.str.zfill(6).str[:5]
    else:
        code = code.str.zfill(5)
    if '1ER APELLIDO' in table.columns:  # current-term export
        names = [' '.join(p for p in (text(a), text(b), text(c)) if p)
                 for a, b, c in zip(table['NOMBRE'], table['1ER APELLIDO'],
                                    table['2º APELLIDO'])]
        lists, ends = table['PARTIDO'], [None] * len(table)
        starts = table['FECHA DE POSESIÓN']
    else:
        names = [text(n) for n in table['NOMBRE']]
        lists, ends = table['LISTA'], table['FECHA BAJA'].map(parse_date)
        starts = table['FECHA POSESIÓN']
    return pd.DataFrame({
        'ine_code': code.to_numpy(),
        'term': term,
        'name': [readable_name(n) for n in names],
        'list': [LIST_VARIANTS.get(text(v), text(v)) for v in lists],
        'start': [parse_date(v) for v in starts],
        'end': list(ends),
    })


def merge_duplicates(rows: pd.DataFrame) -> pd.DataFrame:
    """The same person listed twice in one council and term (it happens in
    the source) becomes one row covering both periods."""
    rows = rows.assign(person=rows['name'].map(person_key))
    merged = rows.groupby(['ine_code', 'term', 'person'], sort=False).agg(
        name=('name', 'first'), list=('list', 'first'),
        start=('start', lambda s: min((d for d in s if d), default=None)),
        end=('end', lambda s: max((d for d in s if d), default=None)))
    return merged.reset_index().drop(columns='person')


def fill_dates(rows: pd.DataFrame,
               as_of: dict[int, date] | None = None
               ) -> tuple[pd.DataFrame, int]:
    """Orders the mayors of each council and term and fills missing or
    overlapping dates from their neighbours and the term limits. A term in
    progress ends on its export date (as_of[term])."""
    filled = 0
    out = []
    rows = merge_duplicates(rows)
    for (code, term), group in rows.groupby(['ine_code', 'term'], sort=False):
        first = TERM_STARTS.get(term, date(term, 6, 15))
        last = TERM_STARTS.get(term + 4, date(term + 4, 6, 15)) - \
            timedelta(days=1)
        if as_of and term in as_of:
            last = min(last, as_of[term])
        group = group.assign(order=[s or e or first for s, e in
                                    zip(group['start'], group['end'])])
        group = group.sort_values('order').drop(columns='order')
        starts, ends = list(group['start']), list(group['end'])
        for i in range(len(starts)):
            if starts[i] is None:
                starts[i] = ends[i - 1] + timedelta(days=1) if i and \
                    ends[i - 1] else first
                filled += 1
        for i in range(len(ends)):
            following = starts[i + 1] - timedelta(days=1) \
                if i + 1 < len(starts) else last
            if ends[i] is None:
                ends[i] = following
                filled += i + 1 < len(starts)  # the last one is the term end
            elif ends[i] > following:
                ends[i] = following
                filled += 1
            if ends[i] < starts[i]:  # inconsistent in the source
                ends[i] = starts[i]
                filled += 1
        out.append(group.assign(start=starts, end=ends))
    return pd.concat(out, ignore_index=True), filled


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--since', type=date.fromisoformat,
                        help='drop mayors who left office before this date')
    parser.add_argument('--as-of', type=date.fromisoformat,
                        help='date of a current-term export (default: from '
                             'the file name, else today)')
    args = parser.parse_args()
    sheets = [read_sheet(p) for p in args.files]
    # Terms still in progress end on the day their list was exported
    as_of = {}
    for path, sheet in zip(args.files, sheets):
        term = int(sheet['term'].iloc[0])
        if TERM_STARTS.get(term + 4, date(term + 4, 6, 15)) > date.today():
            as_of[term] = args.as_of or export_date(path) or date.today()
    new, filled = fill_dates(pd.concat(sheets, ignore_index=True), as_of)
    if args.since:
        dropped = new['end'] < args.since
        print(f'Mayors who left before {args.since}: {dropped.sum()} dropped')
        new = new[~dropped]
    if OUT.exists():  # keep the terms that were not rebuilt
        old = pd.read_csv(OUT, dtype={'ine_code': str})
        old = old[~old['term'].isin(new['term'])]
        old['start'] = pd.to_datetime(old['start']).dt.date
        old['end'] = pd.to_datetime(old['end']).dt.date
        new = pd.concat([old, new], ignore_index=True)
    new = new.sort_values(['ine_code', 'start']).reset_index(drop=True)
    new[['ine_code', 'term', 'name', 'list', 'start', 'end']].to_csv(
        OUT, index=False)

    known = ROOT / 'data' / 'conprel' / 'all_municipalities.csv.gz'
    if known.exists():
        codes = set(pd.read_csv(known, dtype=str)['ine_code'])
        unknown = sorted(set(new['ine_code']) - codes)
        print(f'Codes not in the current INE list (merged councils): '
              f'{len(unknown)} {unknown[:10]}')
    for term, rows in new.groupby('term'):
        print(f'{term}-{term + 4}: {rows["ine_code"].nunique()} councils, '
              f'{len(rows)} mayors')
    print(f'Dates filled or corrected from neighbouring mayors: {filled}')
    print(f'Written to {OUT}')


if __name__ == '__main__':
    main()
