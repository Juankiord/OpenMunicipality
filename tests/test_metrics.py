import pandas as pd
import pytest

from modules.metrics_engine import (calculate_budget_kpis,
                                    calculate_yoy_deviation,
                                    get_category_breakdown)

# A small made-up budget: five spending areas and two income sources, two years
ROWS = [
    ('Social Services', 'Expense', 25_000_000, 2025),
    ('Education & Culture', 'Expense', 18_000_000, 2025),
    ('Environment & Parks', 'Expense', 14_000_000, 2025),
    ('Urban Infrastructure', 'Expense', 32_000_000, 2025),
    ('Public Safety', 'Expense', 21_000_000, 2025),
    ('Social Services', 'Expense', 28_000_000, 2026),
    ('Education & Culture', 'Expense', 19_500_000, 2026),
    ('Environment & Parks', 'Expense', 15_000_000, 2026),
    ('Urban Infrastructure', 'Expense', 29_000_000, 2026),
    ('Public Safety', 'Expense', 22_500_000, 2026),
    ('Local Taxes', 'Income', 65_000_000, 2025),
    ('State Transfers', 'Income', 50_000_000, 2025),
    ('Local Taxes', 'Income', 68_000_000, 2026),
    ('State Transfers', 'Income', 52_000_000, 2026),
]


def sample() -> pd.DataFrame:
    return pd.DataFrame(ROWS, columns=['Category', 'Type', 'Amount', 'Year'])


def test_kpis_on_sample_dataset():
    df = sample()
    kpis = calculate_budget_kpis(df, 212000, 2026)
    assert kpis['total_expenditure'] == 114_000_000
    assert kpis['net_balance'] == 6_000_000


def test_allocation_share_and_per_capita():
    df = sample()
    out = get_category_breakdown(df, 2026, 212000).set_index('Category')
    assert out['Share_pct'].sum() == pytest.approx(100)
    per_capita = out.loc['Social Services', 'Per_Capita']
    assert per_capita == pytest.approx(132.08, abs=0.01)


def test_yoy_deviation_and_flag():
    df = sample()
    dev = calculate_yoy_deviation(df, threshold_pct=10)
    dev = dev.set_index(['Category', 'Year']).loc['Social Services']
    assert dev.loc[2026, 'Delta_pct'] == pytest.approx(12.0)
    assert bool(dev.loc[2026, 'Flagged'])
    assert not bool(dev.loc[2025, 'Flagged'])  # no t-1 data


def test_plain_language_summary():
    from modules.narrative import headline, key_points
    df = sample()
    kpis = calculate_budget_kpis(df, 212000, 2026)
    prev = calculate_budget_kpis(df, 212000, 2025)
    hero = headline('en', 2026, kpis, prev, current_year=2026)
    assert hero[0] == ('In 2026, the council plans to spend €114 million: '
                       '€538 for every resident.')
    assert hero[1] == "That's 3.6% more than in 2025."
    points = key_points('es', 2026, get_category_breakdown(df, 2026, 212000),
                        calculate_yoy_deviation(df), 10)
    assert 'Servicios sociales' in points[-2]  # the only flagged area


def test_headline_tense_follows_the_calendar():
    from modules.narrative import headline
    kpis = {'total_expenditure': 2e6, 'total_revenue': 2e6,
            'per_capita_expenditure': 1000.0, 'net_balance': 0.0}
    past = headline('es', 2025, kpis, None, 'Cádiz', current_year=2026)
    now = headline('es', 2026, kpis, None, 'Cádiz', current_year=2026)
    assert 'presupuestó gastar' in past[0] and 'estaban equilibrados' in past[2]
    assert 'prevé gastar' in now[0] and 'están equilibrados' in now[2]
    assert 'planned to spend' in headline('en', 2025, kpis, None,
                                          current_year=2026)[0]
    spent = headline('es', 2024, kpis, None, stage='executed',
                     current_year=2026)
    assert 'gastó' in spent[0] and 'quedaron equilibrados' in spent[2]
