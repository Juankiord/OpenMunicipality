import pandas as pd


def _check_population(population: int) -> None:
    if population is None or population <= 0:
        raise ValueError('Population must be a positive integer.')


def calculate_budget_kpis(df: pd.DataFrame, population: int,
                          selected_year: int) -> dict:
    """Calculates key financial and communication metrics for a given year."""
    _check_population(population)
    df_year = df[df['Year'] == selected_year]

    total_expenditure = df_year[df_year['Type'] == 'Expense']['Amount'].sum()
    total_revenue = df_year[df_year['Type'] == 'Income']['Amount'].sum()

    return {
        'total_expenditure': total_expenditure,
        'total_revenue': total_revenue,
        'net_balance': total_revenue - total_expenditure,
        'per_capita_expenditure': total_expenditure / population,
        'per_capita_revenue': total_revenue / population,
    }


def get_category_breakdown(df: pd.DataFrame, selected_year: int,
                           population: int,
                           budget_type: str = 'Expense') -> pd.DataFrame:
    """Returns totals, allocation share (%) and per-capita value by
    category."""
    _check_population(population)
    filtered = df[(df['Year'] == selected_year) & (df['Type'] == budget_type)]
    grouped = filtered.groupby('Category', as_index=False)['Amount'].sum()
    total = grouped['Amount'].sum()
    grouped['Share_pct'] = grouped['Amount'] / total * 100 if total else 0.0
    grouped['Per_Capita'] = grouped['Amount'] / population
    return grouped.sort_values(by='Amount', ascending=False,
                               ignore_index=True)


def calculate_yoy_deviation(df: pd.DataFrame, budget_type: str = 'Expense',
                            threshold_pct: float = 10.0) -> pd.DataFrame:
    """Computes the year-on-year change (%) of each category with respect
    to the immediately preceding year and flags |Δ%| >= threshold."""
    grouped = (df[df['Type'] == budget_type]
               .groupby(['Category', 'Year'], as_index=False)['Amount'].sum())
    previous = grouped.assign(Year=grouped['Year'] + 1).rename(
        columns={'Amount': 'Previous_Amount'})
    out = grouped.merge(previous, on=['Category', 'Year'], how='left')

    base = out['Previous_Amount'].where(out['Previous_Amount'] > 0)
    out['Delta_pct'] = (out['Amount'] - base) / base * 100  # NaN if undefined
    out['Flagged'] = out['Delta_pct'].abs() >= threshold_pct
    return out.sort_values(['Year', 'Category'], ignore_index=True)
