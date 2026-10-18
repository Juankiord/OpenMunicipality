# Readability of the generated texts

`scripts/readability.py` builds, for every municipality with a 2025 budget in
the bundled dataset (7,344), the headline and key points the app shows with
default settings, in Spanish and English, and scores them. Figures (amounts,
percentages, years) are replaced by one neutral word before scoring.

| Measure (2025 budgets, n = 7,344) | Mean | Median | P10 | P90 |
|---|---|---|---|---|
| INFLESZ / Szigriszt-Pazos (es) | 69.2 | 69.3 | 65.4 | 72.9 |
| Fernández Huerta, corrected (es) | 73.5 | 73.5 | 69.8 | 77.0 |
| Flesch Reading Ease (en) | 60.2 | 60.2 | 55.9 | 64.4 |

- Median length: 135 words (es), 129 words (en); 15.1 words per sentence (es).
- INFLESZ bands (Barrio-Cantalejo et al., 2008): 92.3 % "bastante fácil"
  (65–80), 7.7 % "normal" (55–65), none "algo difícil" or harder.
- Flesch 60–70 corresponds to plain English (Flesch, 1948).
- The texts describe past years in the past tense ("presupuestó gastar"),
  which is slightly longer than the present ("prevé gastar").

Per-municipality scores: `docs/readability_results.csv`.

## Sensitivity: figures left as they are

`python scripts/readability.py --keep-figures` scores the same texts without
replacing the figures (`docs/readability_results_with_figures.csv`):

| Measure (figures as they are) | Mean | Median | P10 | P90 |
|---|---|---|---|---|
| INFLESZ / Szigriszt-Pazos (es) | 82.8 | 82.9 | 78.4 | 86.9 |
| Fernández Huerta, corrected (es) | 86.8 | 86.8 | 82.6 | 90.7 |
| Flesch Reading Ease (en) | 69.2 | 69.3 | 64.2 | 74.1 |

The scores are higher because the points and commas inside numbers ("1.798",
"18,1") are counted as sentence ends (10.6 words per sentence instead of
15.1). Replacing the figures is therefore the more conservative estimate.

These formulas measure sentence and word length, not comprehension.

References: Barrio-Cantalejo et al. (2008), An Sist Sanit Navar 31(2):135–152;
Fernández Huerta (1959), Consigna 214:29–32, with the sentence term corrected as
discussed by G. Law (LINGUIST List 22.2332, 2011); Flesch (1948), J Appl Psychol
32(3):221–233.
