"""Tests for scripts/build_conprel.py with small in-memory CONPREL tables, so
the Access files and mdbtools are not needed."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parents[1]


@pytest.fixture()
def builder():
    spec = importlib.util.spec_from_file_location(
        'build_conprel', ROOT / 'scripts' / 'build_conprel.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_tables(liquidation: bool) -> dict:
    def rows(base, values):
        # planned, recognised, paid, closed years: only 'importer' is used
        extra = ({'imported': [str(v * 2) for v in values],
                  'importer': [str(v) for v in values],
                  'importel': ['0'] * len(values), 'importec': ['0'] * len(values)}
                 if liquidation else {'importe': [str(v) for v in values]})
        return pd.DataFrame({**base, **extra})

    return {
        'tb_inventario': pd.DataFrame({
            'id': ['1', '1', '2'], 'idente': ['1', '9', '2'],
            'codbdgel': ['11012AA000', '11012AA000', '15030AA000'],
            'codente': ['11012AA000', '11012AO001', '15030AA000'],
            'nombreppal': ['Cádiz', 'Cádiz', 'Coruña (A)'],
            'nombreente': ['Cádiz', 'Fundación', 'Coruña (A)'],
            'nsec': ['1', '1', '1'], 'poblacion': ['100', '100', '200'],
            'estado': ['C', 'C', 'C']}),
        'tb_Provincias': pd.DataFrame({'provincia': ['11', '15'],
                                       'nombre': ['Cádiz', 'Coruña, A'],
                                       'ccaa': ['01', '12']}),
        'tb_economica_cons': rows(
            {'id': ['1', '1', '1', '2', '2'],
             'tipreig': ['I', 'G', 'G', 'I', 'G'],
             'cdcta': ['1', '1', '6', '4', '2']},
            [300, 200, 100, 50, 50]),
        'tb_funcional_cons': rows(
            {'id': ['1', '1', '1', '1', '2', '2'],
             'cdcta': ['1', '6', '1', '6', '2', '2'],
             'cdfgr': ['23', '45', '231', '453', '16', '162']},
            [200, 100, 200, 100, 50, 50]),
        'tb_cuentasProgramas': pd.DataFrame({
            'cdfgr': ['231', '453', '162', '23'],
            'nombre': ['Asistencia social primaria', 'Carreteras',
                       'Recogida de residuos', 'Servicios sociales']}),
    }


@pytest.mark.parametrize('liquidation', [False, True])
def test_process_budget_and_liquidation(builder, monkeypatch, liquidation):
    tables = fake_tables(liquidation)
    monkeypatch.setattr(builder, 'export_table', lambda db, name: tables[name])
    monkeypatch.setattr(builder, 'tables_in',
                        lambda db: {name.lower(): name for name in tables})
    stage = 'executed' if liquidation else 'budget'
    meta, lines, programs, names = builder.process(Path('x'), 2024, stage)

    assert sorted(meta['name']) == ['A Coruña', 'Cádiz']
    cadiz = lines[lines['ine_code'] == '11012'].set_index(['Type', 'Category'])
    # Liquidations use recognised obligations (importer), not the planned
    # figure (imported), which is twice as large in the fake data
    assert cadiz.loc[('Expense', 'S_SOCIAL'), 'Amount'] == 200
    assert cadiz.loc[('Expense', 'S_INFRA'), 'Amount'] == 100
    assert cadiz.loc[('ExpenseChapter', 'E67'), 'Amount'] == 100
    assert cadiz.loc[('Income', 'I1'), 'Amount'] == 300
    assert (lines['Stage'] == stage).all()
    assert set(programs['Program']) == {'231', '453', '162'}
    assert 'Carreteras' in set(names['Name'])


def test_year_and_stage_from_file_name(builder):
    assert builder.year_and_stage(Path('Presupuestos2025.zip')) == (2025, 'budget')
    assert builder.year_and_stage(Path('Liquidaciones2024.zip')) == (2024,
                                                                     'executed')


def test_incomplete_programmes_allowed_only_before_2014(builder, monkeypatch):
    tables = fake_tables(False)
    fun = tables['tb_funcional_cons']
    # A Coruña reports areas but no programmes, as small towns could pre-2014
    tables['tb_funcional_cons'] = fun[~((fun['id'] == '2')
                                        & (fun['cdfgr'].str.len() == 3))]
    monkeypatch.setattr(builder, 'export_table', lambda db, name: tables[name])
    monkeypatch.setattr(builder, 'tables_in',
                        lambda db: {name.lower(): name for name in tables})
    _, lines, programs, _ = builder.process(Path('x'), 2012, 'budget')
    assert set(programs['ine_code']) == {'11012'}
    assert lines.loc[lines['ine_code'] == '15030', 'Amount'].sum() > 0
    with pytest.raises(SystemExit):
        builder.process(Path('x'), 2016, 'budget')


def test_missing_province_table_uses_built_in_names(builder, monkeypatch):
    tables = fake_tables(False)
    del tables['tb_Provincias']  # as in the 2018 database
    monkeypatch.setattr(builder, 'export_table', lambda db, name: tables[name])
    monkeypatch.setattr(builder, 'tables_in',
                        lambda db: {name.lower(): name for name in tables})
    meta, _, _, _ = builder.process(Path('x'), 2018, 'budget')
    assert set(meta['province']) == {'Cádiz', 'A Coruña'}


def test_tables_are_written_by_stage_and_read_back(builder, monkeypatch,
                                                   tmp_path):
    from modules import conprel
    monkeypatch.setattr(builder, 'OUT', tmp_path)
    lines = pd.DataFrame({'ine_code': ['11012', '15030', '11012'],
                          'Year': [2024, 2024, 2024],
                          'Stage': ['budget', 'budget', 'executed'],
                          'Type': 'Expense',
                          'Category': ['S_SOCIAL', 'S_GOV', 'S_DEBT'],
                          'Amount': [1.0, 2.0, 3.0]})
    builder.write_by_stage('lines', lines)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        'lines_budget.csv.gz', 'lines_executed.csv.gz']
    back = conprel.read_table(tmp_path, 'lines')
    assert len(back) == 3 and back['Amount'].sum() == 6
    # Categories from both files survive the join
    assert set(back['Category'].cat.categories) == {'S_SOCIAL', 'S_GOV',
                                                    'S_DEBT'}
    merged = builder.merge_existing('lines', lines.iloc[[2]].assign(Amount=9.0))
    assert sorted(merged['Amount']) == [1.0, 2.0, 9.0]


def test_programme_names_follow_the_2014_reform(builder):
    from modules import conprel
    names = pd.DataFrame({
        'Year': [2012, 2013, 2015, 2016, 2012, 2016],
        'Program': ['134', '134', '134', '134', '920', '920'],
        'Name': ['Protección civil', 'Protección civil', 'Movilidad urbana',
                 'Movilidad urbana', 'Administración general',
                 'Administración general ']})
    periods = builder.name_periods(names)
    assert periods.values.tolist() == [
        ['134', 2012, 'Protección civil'], ['134', 2015, 'Movilidad urbana'],
        ['920', 2012, 'Administración general']]
    periods = periods.astype({'Since': str})  # as read back from the file
    assert conprel.program_names(periods, 2014)['134'] == 'Protección civil'
    assert conprel.program_names(periods, 2024)['134'] == 'Movilidad urbana'


def test_missing_programme_files_do_not_break_loading(tmp_path):
    from modules import conprel
    assert conprel.load_programs(tmp_path) is None
    with pytest.raises(FileNotFoundError):
        conprel.read_table(tmp_path, 'lines')
