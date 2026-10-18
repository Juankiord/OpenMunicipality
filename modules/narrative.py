"""Turns computed indicators into short plain-language sentences."""
from datetime import date

import pandas as pd

from modules import mayors
from modules.i18n import (category_name, long_date, money, money_compact,
                          money_words, pct, t)


def change_pct(current: float, previous: float | None) -> float | None:
    if previous is None or previous <= 0:
        return None
    return (current - previous) / previous * 100


def headline(lang: str, year: int, kpis: dict, prev_kpis: dict | None,
             name: str = '', stage: str = 'budget',
             inflation: float | None = None,
             current_year: int | None = None) -> list[str]:
    """Returns the hero sentence followed by its supporting sentences.
    stage: 'budget' (planned) or 'executed' (actually spent). A budget for a
    year already over is told in the past ('planned to spend'); the current
    or a future year keeps the present ('plans to spend')."""
    who = t(lang, 'council_of', name=name) if name else t(lang, 'council')
    current_year = current_year or date.today().year
    sfx = ('_exec' if stage == 'executed'
           else '_past' if year < current_year else '')
    lines = [t(lang, 'hero' + sfx, year=year, who=who,
               total=money_words(kpis['total_expenditure'], lang),
               per_res=_per_res(kpis['per_capita_expenditure'], lang))]

    prev = year - 1
    delta = change_pct(kpis['total_expenditure'],
                       prev_kpis['total_expenditure'] if prev_kpis else None)
    real = ''
    if delta is not None and inflation is not None:
        delta = ((1 + delta / 100) / (1 + inflation / 100) - 1) * 100
        real = ' ' + t(lang, 'hero_real')
    if delta is None:
        lines.append(t(lang, 'hero_no_prev', prev=prev))
    elif round(delta, 1) == 0:
        lines.append(t(lang, 'hero_change_same', prev=prev))
    else:
        key = 'hero_change_up' if delta > 0 else 'hero_change_down'
        sentence = t(lang, key, pct=pct(abs(delta), lang), prev=prev)
        lines.append(sentence[:-1] + real + '.' if real else sentence)

    balance = kpis['net_balance']
    if abs(balance) < max(1_000, 0.0005 * kpis['total_expenditure']):
        balance = 0  # cents or rounding differences: treat as balanced
    if balance > 0:
        lines.append(t(lang, 'hero_balance_pos' + sfx,
                       bal=money_words(balance, lang)))
    elif balance < 0:
        lines.append(t(lang, 'hero_balance_neg' + sfx,
                       bal=money_words(balance, lang)))
    else:
        lines.append(t(lang, 'hero_balance_zero' + sfx))
    return lines


def key_points(lang: str, year: int, breakdown: pd.DataFrame,
               deviation: pd.DataFrame, threshold: float,
               bench: tuple[str, float, float] | None = None,
               inflation: float | None = None) -> list[str]:
    """Builds the 'key points' list for the selected year. bench is
    (population band, usual spending per resident, this council's value)."""
    points = []
    if bench:
        band, median, value = bench
        points.append(t(lang, 'kp_bench', band=t(lang, f'band_{band}'),
                        median=_per_res(median, lang),
                        who_short=t(lang, 'who_short'),
                        value=_per_res(value, lang)))
    if not breakdown.empty:
        top = breakdown.iloc[0]
        points.append(t(lang, 'kp_largest',
                        cat=category_name(lang, top['Category']),
                        share=_number(top['Share_pct'], lang),
                        per_res=_per_res(top['Per_Capita'], lang)))

    prev = year - 1
    year_dev = deviation[(deviation['Year'] == year)
                         & deviation['Delta_pct'].notna()]
    if not year_dev.empty:
        # Biggest movers in euros, so tiny budget lines don't dominate
        euros = year_dev['Amount'] - year_dev['Previous_Amount']
        rise = year_dev.loc[euros.idxmax()]
        fall = year_dev.loc[euros.idxmin()]
        if euros.max() > 0:
            points.append(t(lang, 'kp_rise',
                            cat=category_name(lang, rise['Category']),
                            amount=money_compact(euros.max(), lang),
                            pct=pct(rise['Delta_pct'], lang, signed=True),
                            prev=prev))
        if euros.min() < 0:
            points.append(t(lang, 'kp_fall',
                            cat=category_name(lang, fall['Category']),
                            amount=money_compact(-euros.min(), lang),
                            pct=pct(fall['Delta_pct'], lang, signed=True),
                            prev=prev))
        biggest_first = year_dev.reindex(
            year_dev['Delta_pct'].abs().sort_values(ascending=False).index)
        flagged = [category_name(lang, c) for c in
                   biggest_first.loc[biggest_first['Flagged'], 'Category']]
        thr = pct(threshold, lang, 0)
        if not flagged:
            points.append(t(lang, 'kp_flagged_none', thr=thr, prev=prev))
        elif len(flagged) == 1:
            points.append(t(lang, 'kp_flagged_one', thr=thr, cats=flagged[0]))
        else:
            shown = ', '.join(flagged[:4])
            if len(flagged) > 4:  # keep the sentence short
                shown += t(lang, 'and_more', n=len(flagged) - 4)
            points.append(t(lang, 'kp_flagged_many', n=len(flagged), thr=thr,
                            cats=shown))

    if inflation is None:
        points.append(t(lang, 'kp_nominal'))
    else:
        points.append(t(lang, 'kp_real', year=year,
                        pi=pct(inflation, lang)))
    return points


def _number(value: float, lang: str) -> str:
    """Share of every €100, rounded to whole euros: '25 €' / '€25'."""
    return money(round(value), lang, 0)


def _per_res(value: float, lang: str) -> str:
    """Whole euros, except for small amounts where cents matter."""
    return money(value, lang, 0 if value >= 10 else 2)


def mayor_point(lang: str, spans: list[dict], year: int,
                stage: str = 'budget') -> str | None:
    """Who held the mayoralty for the year shown, following the rules of
    modules.mayors: the budget belongs to whoever held it on 1 January, the
    outturn to whoever held it for most of the year. None without data."""
    if stage == 'executed':
        holder = mayors.for_outturn(spans, year)
        if holder:
            return t(lang, 'kp_mayor_exec', year=year,
                     who=mayors.label(holder))
        during = mayors.in_year(spans, year)
        if len(during) > 1:
            return t(lang, 'kp_mayor_split', year=year, who=' → '.join(
                mayors.label(s) + t(lang, 'from_day', day=long_date(
                    max(s['start'], date(year, 1, 1)), lang))
                for s in during))
        return None
    holder = mayors.for_budget(spans, year)
    if not holder:
        return None
    key = 'kp_mayor_budget_earlier' if holder.get('earlier') \
        else 'kp_mayor_budget'
    text = t(lang, key, year=year, who=mayors.label(holder),
             since=long_date(holder['start'], lang))
    if mayors.changed(mayors.for_budget(spans, year - 1), holder):
        text += t(lang, 'kp_mayor_first')
    later = [mayors.label(s) + t(lang, 'on_day',
                                 day=long_date(s['start'], lang))
             for s in mayors.in_year(spans, year)
             if s['start'] > date(year, 1, 1)
             and not mayors.same_person(s['name'], holder['name'])]
    if later:
        text += t(lang, 'kp_mayor_during', who=t(lang, 'then').join(later))
    return text


def mayor_change_note(lang: str, spans: list[dict], year: int,
                      stage: str = 'budget') -> str | None:
    """A note for the year-on-year view when the mayor changed between the
    two years compared."""
    rule = mayors.for_outturn if stage == 'executed' else mayors.for_budget
    before, after = rule(spans, year - 1), rule(spans, year)
    if not mayors.changed(before, after):
        return None
    return t(lang, 'change_mayor', prev=year - 1, year=year,
             before=mayors.label(before), after=mayors.label(after))
