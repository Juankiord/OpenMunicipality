import importlib.util
from pathlib import Path

import pytest

from modules import conprel
from modules.metrics_engine import calculate_budget_kpis

ROOT = Path(__file__).parents[1]
pytestmark = pytest.mark.skipif(not conprel.available(),
                                reason='official dataset not built')


def _builder():
    spec = importlib.util.spec_from_file_location(
        'build_conprel', ROOT / 'scripts' / 'build_conprel.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_official_names_are_made_readable():
    name = _builder().readable_name
    assert name('Coruña (A)') == 'A Coruña'
    assert name('Palmas, Las') == 'Las Palmas'
    assert name("Hospitalet de Llobregat (L')") == "L'Hospitalet de Llobregat"
    assert name('Cádiz') == 'Cádiz'


def test_search_ignores_accents_and_ranks_exact_names_first():
    meta, _, _ = conprel.load()
    index = conprel.search_index(meta)
    assert conprel.search(index, 'cadiz')['label'].iloc[0] == 'Cádiz (Cádiz)'
    assert conprel.search(index, 'coruña').index[0] == '15030'
    assert conprel.search(index, 'rozas')['name'].iloc[0] == 'Las Rozas de Madrid'
    assert conprel.search(index, 'zzzz').empty


def test_municipality_totals_are_consistent():
    meta, lines, bench = conprel.load()
    df, population, name = conprel.municipality(meta, lines, '11012', 'budget')
    assert name == 'Cádiz' and population[2025] > 100_000
    kpis = calculate_budget_kpis(df, population[2025], 2025)
    # Spanish budgets are approved balanced: spending equals income
    assert kpis['total_expenditure'] == pytest.approx(kpis['total_revenue'])
    band, rows = conprel.benchmark(bench, 2025, 'budget', population[2025])
    assert band == '100000-500000' and not rows.empty


def test_year_on_year_with_two_official_years():
    from modules.metrics_engine import calculate_yoy_deviation
    from modules.narrative import key_points
    from modules.metrics_engine import get_category_breakdown
    meta, lines, _ = conprel.load()
    df, population, _ = conprel.municipality(meta, lines, '11012', 'budget')
    if 2024 not in population:
        pytest.skip('2024 not in the bundled dataset')
    deviation = calculate_yoy_deviation(df, threshold_pct=10)
    assert deviation.loc[deviation['Year'] == 2025, 'Delta_pct'].notna().all()
    points = key_points('es', 2025, get_category_breakdown(
        df, 2025, population[2025]), deviation, 10)
    assert any(' y ' in p and 'más' in p for p in points)  # list was shortened


def test_budgets_and_outturns_load_together():
    meta, lines, _ = conprel.load()
    assert set(lines['Stage'].cat.categories) == {'budget', 'executed'}
    assert lines["ine_code"].dtype == "category"
    planned, spent = conprel.execution(lines, '11012', 2024)
    assert 0.5 < spent / planned < 2
    executed_years = conprel.years_of(meta, 'executed')
    assert executed_years[0] == 2010 and 2024 in executed_years
    assert 2014 in conprel.years_without_data(meta, '11012', 'executed')


def test_execution_far_from_plan_is_flagged():
    kpis = {'total_expenditure': 100.0, 'total_revenue': 100.0,
            'per_capita_expenditure': 1.0}
    keys = [k for k, _ in conprel.data_warnings(kpis, None, 'executed', 100,
                                                None, None, False, 2.5)]
    assert keys == ['warn_execution']
    assert not conprel.data_warnings(kpis, None, 'executed', 100, None, None,
                                     False, 1.1)


def test_programme_names_depend_on_the_year():
    _, names = conprel.load_programs()
    assert conprel.program_names(names, 2012)['134'] == 'Protección civil'
    assert conprel.program_names(names, 2025)['134'] == 'Movilidad urbana'
