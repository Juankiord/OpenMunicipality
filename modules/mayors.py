"""Who held the mayoralty of each council, and how it lines up with the
budgets.

The data (data/conprel/mayors.csv.gz, built by scripts/build_mayors.py from
the lists of the Ministry of Territorial Policy) has one row per mayor and
term. Two rules connect it with the budgets, and the app states them:

- the budget of a year belongs to whoever held the mayoralty on 1 January,
  normally the person who prepared it;
- what was spent in a year (outturn) belongs to whoever held the mayoralty
  for most of that year.

Changes of mayor are detected by person, not by list: the register records
the same mayor under different labels in different terms (a party, then the
coalition it ran in), so a new label alone is not a change of government.
"""
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from modules.conprel import DATA_DIR

# Municipal election days (Spain), marked on the timeline
ELECTIONS = {2011: date(2011, 5, 22), 2015: date(2015, 5, 24),
             2019: date(2019, 5, 26), 2023: date(2023, 5, 28)}

PARTICLES = {'de', 'del', 'la', 'las', 'los', 'y', 'i', 'e', 'da', 'das',
             'do', 'dos', 'el', 'en', 'van', 'von'}


def load(data_dir: Path = DATA_DIR) -> pd.DataFrame | None:
    """All mayors, or None when the dataset has no mayors file."""
    path = data_dir / 'mayors.csv.gz'
    if not path.exists():
        return None
    mayors = pd.read_csv(path, dtype={'ine_code': str, 'name': str,
                                      'list': str})
    for column in ('start', 'end'):
        mayors[column] = pd.to_datetime(mayors[column]).dt.date
    return mayors


def person_key(name: str) -> str:
    """Accent-, case- and particle-free key of a name."""
    text = unicodedata.normalize('NFKD', str(name).lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    words = re.sub(r"[^a-z ]+", ' ', text).split()
    return ' '.join(sorted(w for w in words if w not in PARTICLES))


def _same_word(u: str, v: str) -> bool:
    """Spelling variants of one word: 'vicent' and 'vicente' (Valencian and
    Spanish forms), or one letter apart ('gonzales', 'gonzalez'), but not a
    final a/o, which marks a different person (Francisco, Francisca)."""
    if u == v or u + 'e' == v or v + 'e' == u:
        return True
    if len(u) != len(v) or len(u) < 5:
        return False
    diff = [i for i, (p, q) in enumerate(zip(u, v)) if p != q]
    return len(diff) == 1 and not (diff[0] == len(u) - 1
                                   and {u[-1], v[-1]} == {'a', 'o'})


def same_person(a: str, b: str) -> bool:
    """'JOSE MARIA GONZALEZ SANTOS' and 'José María González Santos Kichi'
    are the same person, and so are 'Vicent' and 'Vicente Grimalt Boronat':
    one name contains the other, or at least three quarters of their words
    match, allowing spelling variants of a word."""
    x, y = person_key(a).split(), person_key(b).split()
    if not x or not y:
        return False
    left, matched = list(y), 0
    for word in x:
        found = next((w for w in left if _same_word(word, w)), None)
        if found is not None:
            left.remove(found)
            matched += 1
    return (matched == min(len(x), len(y))
            or matched / (len(x) + len(y) - matched) >= 0.75)


def periods(mayors: pd.DataFrame | None, ine_code: str) -> list[dict]:
    """The council's mayoralties in order, consecutive terms of the same
    person joined: name, lists (in order, without repeats), start, end."""
    if mayors is None:
        return []
    rows = mayors[mayors['ine_code'] == ine_code].sort_values('start')
    # Whoever was already mayor when the register starts may have been in
    # office before: their start is the first day of the data, not of office
    data_start = min(mayors['start']) + pd.Timedelta(days=31)
    out: list[dict] = []
    for row in rows.itertuples():
        last = out[-1] if out else None
        if last and same_person(last['name'], row.name) and \
                (row.start - last['end']).days <= 31:
            last['end'] = max(last['end'], row.end)
            last['name'] = row.name  # the most recent spelling
            if row.list not in last['lists']:
                last['lists'].append(row.list)
        else:
            out.append({'name': row.name, 'lists': [row.list],
                        'start': row.start, 'end': row.end,
                        'earlier': row.start <= data_start})
    return out


def on_date(spans: list[dict], day: date) -> dict | None:
    """The mayoralty in force on a day (the latest one if two overlap)."""
    found = [s for s in spans if s['start'] <= day <= s['end']]
    return found[-1] if found else None


def in_year(spans: list[dict], year: int) -> list[dict]:
    first, last = date(year, 1, 1), date(year, 12, 31)
    return [s for s in spans if s['start'] <= last and s['end'] >= first]


def for_budget(spans: list[dict], year: int) -> dict | None:
    """Whoever held the mayoralty on 1 January of the budget's year."""
    return on_date(spans, date(year, 1, 1))


def for_outturn(spans: list[dict], year: int) -> dict | None:
    """Whoever held the mayoralty for most of the year (more than half)."""
    first, last = date(year, 1, 1), date(year, 12, 31)
    best, best_days = None, 0
    for span in in_year(spans, year):
        days = (min(span['end'], last) - max(span['start'], first)).days + 1
        if days > best_days:
            best, best_days = span, days
    return best if best_days > 182 else None


# The mayors file starts with whoever was in office in 2010, the first year
# of the budgets (earlier mayors of the 2007-2011 term are left out)
DATA_FROM = date(2010, 1, 1)


def coverage(mayors: pd.DataFrame | None) -> tuple[date, date] | None:
    """First and last day the register covers."""
    if mayors is None or mayors.empty:
        return None
    return max(min(mayors['start']), DATA_FROM), max(mayors['end'])


def current_term_start(mayors: pd.DataFrame | None) -> date | None:
    """First day of the latest term in the file. For the current term the
    Ministry publishes only the mayor in office on the day of the export."""
    if mayors is None or mayors.empty:
        return None
    latest = mayors[mayors['term'] == mayors['term'].max()]
    return min(latest['start'])


def gaps(spans: list[dict], first: date, last: date,
         year: int | None = None) -> list[tuple[date, date]]:
    """Stretches of more than a month with no mayor recorded between first
    and last (only those touching `year`, if given): a council run by a
    caretaker body, or, in the current term, the mayors before the one in
    office when the list was exported, which the Ministry does not publish."""
    out, cursor = [], first
    for span in sorted(spans, key=lambda s: s['start']):
        if (span['start'] - cursor).days > 31:
            out.append((cursor, span['start'] - timedelta(days=1)))
        cursor = max(cursor, span['end'] + timedelta(days=1))
    if (last - cursor).days > 31:
        out.append((cursor, last))
    if year is not None:
        out = [g for g in out if g[0].year <= year <= g[1].year]
    return out


def label(span: dict) -> str:
    """'Name (PP)' or 'Name (OTROS, C. ELECTORAL)' when the register
    recorded the same person under several lists."""
    return f"{span['name']} ({', '.join(span['lists'])})"


def short_name(name: str) -> str:
    """'Manuela Carmena Castrillo' -> 'Manuela Carmena': the second surname
    is dropped from names of three or more words, for chart labels."""
    words = name.split()
    if len(words) >= 3 and words[-2].lower() not in PARTICLES:
        words = words[:-1]
    return ' '.join(words)


def since(span: dict, lang: str, long: bool = True) -> str:
    """Start date, or 'at least since' when the register starts with this
    mayor already in office."""
    from modules.i18n import long_date, short_date, t
    day = (long_date if long else short_date)(span['start'], lang)
    return t(lang, 'at_least', day=day) if span.get('earlier') else day


def changed(a: dict | None, b: dict | None) -> bool:
    """Two mayoralties held by different people (both known)."""
    return bool(a and b and a is not b
                and not same_person(a['name'], b['name']))


def balance(spans: list[dict], per_res: dict[int, float],
            invest: dict[int, float], rolled_over: set[int],
            spent_vs_plan: dict[int, float],
            cpi: dict[int, float] | None = None) -> pd.DataFrame:
    """One row per mayoralty with the budgets that belong to it:
    spending per resident in its first and last budget and the change
    between them (after inflation when cpi is given), average investment
    per resident, budgets rolled over, and the median share of the plan
    that was spent in its outturn years."""
    def known(values: dict) -> dict:
        return {int(k): float(v) for k, v in values.items()
                if v is not None and pd.notna(v)}

    per_res, invest = known(per_res), known(invest)
    spent_vs_plan = known(spent_vs_plan)
    rows = []
    for span in spans:
        years = sorted(y for y in per_res if for_budget(spans, y) is span)
        spent = [spent_vs_plan[y] for y in spent_vs_plan
                 if for_outturn(spans, y) is span]
        row = {'name': span['name'], 'lists': ', '.join(span['lists']),
               'start': span['start'], 'end': span['end'],
               'budgets': years, 'first': None, 'last': None,
               'change_pct': None, 'invest': None,
               'rolled_over': sum(y in rolled_over for y in years),
               'spent_pct': (float(pd.Series(spent).median()) * 100
                             if spent else None)}
        if years:
            first, last = years[0], years[-1]
            row['first'], row['last'] = per_res[first], per_res[last]
            if len(years) > 1 and per_res[first] > 0:
                growth = per_res[last] / per_res[first]
                if cpi is not None:
                    prices = 1.0
                    for y in range(first + 1, last + 1):
                        prices *= 1 + cpi.get(y, float('nan')) / 100
                    growth /= prices
                row['change_pct'] = (growth - 1) * 100
            values = [invest[y] for y in years if y in invest]
            row['invest'] = sum(values) / len(values) if values else None
        rows.append(row)
    return pd.DataFrame(rows)
