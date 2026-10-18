"""A made-up country in the normalised format: the app's data layer must load
it, name its own categories and compute indicators without Spanish data."""
import pandas as pd

from modules import conprel
from modules.i18n import category_name
from modules.metrics_engine import calculate_budget_kpis, get_category_breakdown


def test_plugged_in_dataset(tmp_path):
    pd.DataFrame({'ine_code': ['X1', 'X1'], 'Year': [2024, 2025],
                  'Stage': ['budget', 'budget'], 'name': ['Ruritania City'] * 2,
                  'province': ['North'] * 2, 'population': [1000, 1000]}
                 ).to_csv(tmp_path / 'municipalities.csv.gz', index=False)
    pd.DataFrame({'ine_code': ['X1'] * 4, 'Year': [2025] * 4,
                  'Stage': ['budget'] * 4,
                  'Type': ['Expense', 'Expense', 'Income', 'ExpenseChapter'],
                  'Category': ['X_TRAMS', 'S_SOCIAL', 'X_TAX', 'E67'],
                  'Amount': [600.0, 400.0, 1000.0, 300.0]}
                 ).to_csv(tmp_path / 'lines.csv.gz', index=False)
    pd.DataFrame({'Year': [2025], 'Stage': ['budget'], 'band': ['1000-5000'],
                  'Type': ['Expense'], 'Category': ['_TOTAL'],
                  'Median_Per_Capita': [0.9], 'Municipalities': [1]}
                 ).to_csv(tmp_path / 'benchmarks.csv.gz', index=False)
    pd.DataFrame({'code': ['X_TRAMS', 'X_TAX'],
                  'name_es': ['Tranvías', 'Impuesto local'],
                  'name_en': ['Trams', 'Local tax']}
                 ).to_csv(tmp_path / 'categories.csv', index=False)

    meta, lines, bench = conprel.load(tmp_path)
    df, population, name = conprel.municipality(meta, lines, 'X1', 'budget')
    assert name == 'Ruritania City' and population[2025] == 1000
    assert category_name('en', 'X_TRAMS') == 'Trams'
    assert category_name('es', 'S_SOCIAL') == 'Servicios sociales'
    kpis = calculate_budget_kpis(df, population[2025], 2025)
    assert kpis['per_capita_expenditure'] == 1.0
    top = get_category_breakdown(df, 2025, 1000).iloc[0]
    assert top['Category'] == 'X_TRAMS' and top['Share_pct'] == 60
    index = conprel.search_index(meta)
    assert conprel.search(index, 'ruritania').index[0] == 'X1'
