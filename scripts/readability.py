"""Measures how easy to read the app's generated texts are, for every
municipality in the official dataset.

For each municipality and language it builds the same headline and key
points the app shows (default settings) and scores them:

- Spanish: INFLESZ scale (Szigriszt-Pazos perspicuity, Barrio-Cantalejo et
  al. 2008) and Fernández Huerta (corrected formulation).
- English: Flesch Reading Ease.

Figures (amounts, percentages, years) are replaced by one neutral word before
scoring, because readability formulas count "1.798" or "18,1" as words with
many syllables and their dots and commas as sentence ends.

    pip install textstat
    python scripts/readability.py [--year 2025] [--keep-figures]

Writes docs/readability_results.csv (or readability_results_with_figures.csv
with --keep-figures, a sensitivity check that scores the texts with their
figures as they are) and prints a summary.
"""
import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import pyphen
import textstat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules import conprel  # noqa: E402
from modules.metrics_engine import (calculate_budget_kpis,  # noqa: E402
                                    calculate_yoy_deviation,
                                    get_category_breakdown)
from modules.narrative import headline, key_points  # noqa: E402

FIGURE = re.compile(r'[−+-]?€?\d(?:[\d.,]*\d)?'
                    r'(?:\s?(?:mil M€|M€|%|€)|(?:\s?(?:million|billion)|bn|M)\b)?')
WORD = {'es': 'cifra', 'en': 'figure'}
INFLESZ = [(0, 40, 'Muy difícil'), (40, 55, 'Algo difícil'), (55, 65, 'Normal'),
           (65, 80, 'Bastante fácil'), (80, 1000, 'Muy fácil')]


HYPHEN_EN = pyphen.Pyphen(lang='en_US')


def flesch_reading_ease(text: str) -> float:
    """Flesch (1948); syllables estimated with the en_US hyphenation
    dictionary, as older textstat versions did (no NLTK download needed)."""
    words = re.findall(r"[A-Za-z']+", text)
    sentences = max(1, len(re.findall(r'[.!?]+(?:\s|$)', text)))
    syllables = sum(max(1, len(HYPHEN_EN.positions(w)) + 1) for w in words)
    return 206.835 - 1.015 * len(words) / sentences - 84.6 * syllables / len(words)


def prepare(text: str, lang: str) -> str:
    return FIGURE.sub(WORD[lang], text)


def inflesz_band(score: float) -> str:
    return next(label for low, high, label in INFLESZ if low <= score < high)


def texts_for(lang, year, meta, lines, bench, code, stage='budget'):
    df, population, name = conprel.municipality(meta, lines, code, stage)
    if year not in population or population[year] <= 0:
        return None
    pop = population[year]
    kpis = calculate_budget_kpis(df, pop, year)
    prev = (calculate_budget_kpis(df, population[year - 1], year - 1)
            if year - 1 in population else None)
    band, rows = conprel.benchmark(bench, year, stage, pop)
    usual = rows[(rows['Type'] == 'Expense') & (rows['Category'] == '_TOTAL')]
    compare = ((band, usual['Median_Per_Capita'].iloc[0],
                kpis['per_capita_expenditure']) if len(usual) else None)
    hero = headline(lang, year, kpis, prev, name, stage)
    points = key_points(lang, year, get_category_breakdown(df, year, pop),
                        calculate_yoy_deviation(df, threshold_pct=10), 10,
                        compare)
    return ' '.join(hero + points)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--year', type=int, default=2025)
    parser.add_argument('--keep-figures', action='store_true',
                        help='score the texts with their figures as they are')
    args = parser.parse_args()
    meta, lines, bench = conprel.load()
    codes = sorted(meta.loc[meta['Year'] == args.year, 'ine_code'].unique())

    rows = []
    for code in codes:
        for lang in ('es', 'en'):
            text = texts_for(lang, args.year, meta, lines, bench, code)
            if text is None:
                continue
            clean = text if args.keep_figures else prepare(text, lang)
            textstat.set_lang(lang)
            row = {'ine_code': code, 'lang': lang,
                   'words': textstat.lexicon_count(clean),
                   'sentences': textstat.sentence_count(clean)}
            if lang == 'es':
                row['inflesz'] = textstat.szigriszt_pazos(clean)
                row['fernandez_huerta'] = textstat.fernandez_huerta(clean)
            else:
                row['flesch'] = flesch_reading_ease(clean)
            rows.append(row)

    out = pd.DataFrame(rows)
    suffix = '_with_figures' if args.keep_figures else ''
    out.to_csv(ROOT / 'docs' / f'readability_results{suffix}.csv', index=False)
    es, en = out[out['lang'] == 'es'], out[out['lang'] == 'en']
    print(f'Municipalities: {es["ine_code"].nunique()} ({args.year})')
    print(f'Words per text: median {es["words"].median():.0f} (es), '
          f'{en["words"].median():.0f} (en)')
    print(f'Words per sentence: median '
          f'{(es["words"] / es["sentences"]).median():.1f} (es)')
    for column in ('inflesz', 'fernandez_huerta'):
        s = es[column]
        print(f'{column}: mean {s.mean():.1f}, median {s.median():.1f}, '
              f'P10 {s.quantile(.1):.1f}, P90 {s.quantile(.9):.1f}')
    print('INFLESZ bands:',
          es['inflesz'].map(inflesz_band).value_counts(normalize=True)
          .mul(100).round(1).to_dict())
    s = en['flesch']
    print(f'Flesch (en): mean {s.mean():.1f}, median {s.median():.1f}, '
          f'P10 {s.quantile(.1):.1f}, P90 {s.quantile(.9):.1f}')


if __name__ == '__main__':
    main()
