"""Mayors: reading the Ministry lists and lining them up with budgets."""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from modules import mayors
from modules.narrative import mayor_change_note, mayor_point

ROOT = Path(__file__).parents[1]


def table(rows):
    return pd.DataFrame(rows, columns=['ine_code', 'term', 'name', 'list',
                                       'start', 'end'])


# A council where A governs, B replaces A mid-term on 10 March 2017 and is
# re-elected under a coalition label
SAMPLE = table([
    ('99001', 2015, 'Ana Pérez López', 'P1', date(2015, 6, 13),
     date(2017, 3, 1)),
    ('99001', 2015, 'Benito Ruiz Gil', 'P2', date(2017, 3, 10),
     date(2019, 6, 14)),
    ('99001', 2019, 'BENITO RUIZ GIL', 'C. ELECTORAL', date(2019, 6, 15),
     date(2023, 6, 16)),
])


def test_same_person_ignores_case_accents_and_extra_words():
    assert mayors.same_person('JOSE MARIA GONZALEZ SANTOS',
                              'José María González Santos Kichi')
    assert not mayors.same_person('Ana Pérez López', 'Ana Ruiz López')
    # Spelling variants of a word, but not a different first name
    assert mayors.same_person('Vicent Grimalt Boronat',
                              'Vicente Grimalt Boronat')
    assert not mayors.same_person('Francisco Ruiz Gil', 'Francisca Ruiz Gil')
    assert not mayors.same_person('Juan García López', 'Juana García López')


def test_periods_join_terms_of_the_same_person():
    spans = mayors.periods(SAMPLE, '99001')
    assert [s['name'] for s in spans] == ['Ana Pérez López', 'BENITO RUIZ GIL']
    assert spans[1]['lists'] == ['P2', 'C. ELECTORAL']
    assert spans[1]['start'] == date(2017, 3, 10)
    assert mayors.label(spans[1]) == 'BENITO RUIZ GIL (P2, C. ELECTORAL)'


def test_gaps_and_mayors_already_in_office_when_data_start():
    spans = mayors.periods(SAMPLE, '99001')
    assert spans[0]['earlier'] and not spans[1]['earlier']
    assert mayors.since(spans[0], 'es', long=False) == '13/06/2015 o antes'
    assert mayors.gaps(spans, date(2015, 6, 13), date(2023, 6, 16)) == []
    # Ana left on 1 March, Benito arrived on 10 March: too short to report
    assert mayors.gaps(spans, date(2015, 1, 1), date(2024, 6, 30)) == [
        (date(2015, 1, 1), date(2015, 6, 12)),
        (date(2023, 6, 17), date(2024, 6, 30))]
    assert mayors.gaps(spans, date(2015, 1, 1), date(2024, 6, 30),
                       year=2020) == []


def test_budget_and_outturn_attribution_rules():
    spans = mayors.periods(SAMPLE, '99001')
    # Budget: whoever held the office on 1 January
    assert mayors.for_budget(spans, 2017)['name'] == 'Ana Pérez López'
    assert mayors.for_budget(spans, 2018)['name'] == 'BENITO RUIZ GIL'
    assert mayors.for_budget(spans, 2015) is None  # before the data
    # Outturn: whoever held it for more than half the year
    assert mayors.for_outturn(spans, 2017)['name'] == 'BENITO RUIZ GIL'
    assert mayors.for_outturn(spans, 2015) is not None  # from 13 June
    assert mayors.for_outturn(spans, 2023) is None  # data end in June


def test_sentences_name_the_mayor_and_the_change():
    spans = mayors.periods(SAMPLE, '99001')
    text = mayor_point('es', spans, 2017)
    assert 'ocupaba la alcaldía Ana Pérez López (P1), en el cargo al menos ' \
        'desde el 13 de junio de 2015' in text
    assert 'pasó a BENITO RUIZ GIL (P2, C. ELECTORAL) el 10 de marzo' in text
    assert 'primer presupuesto' in mayor_point('es', spans, 2018)
    assert 'primer presupuesto' not in mayor_point('es', spans, 2020)
    assert mayor_change_note('en', spans, 2018).startswith(
        'Between 2017 and 2018 the mayor changed')
    # A new list for the same person is not a change of mayor
    assert mayor_change_note('es', spans, 2020) is None
    assert mayor_point('es', spans, 2025) is None


def test_balance_per_mayoralty():
    spans = mayors.periods(SAMPLE, '99001')
    per_res = {2016: 1000.0, 2017: 1100.0, 2018: 1200.0, 2019: float('nan'),
               2020: 1500.0}
    record = mayors.balance(spans, per_res, {2018: 50.0, 2020: 70.0}, {2020},
                            {2017: 0.9, 2018: 1.1}, cpi={2017: 0, 2018: 0,
                                                         2019: 0, 2020: 25})
    a, b = record.to_dict('records')
    assert a['budgets'] == [2016, 2017]
    assert a['change_pct'] == pytest.approx(10)
    assert b['budgets'] == [2018, 2020]  # 2019 has no data
    assert b['change_pct'] == pytest.approx(0)  # +25 % minus 25 % prices
    assert b['invest'] == pytest.approx(60) and b['rolled_over'] == 1
    assert b['spent_pct'] == pytest.approx(100)  # median of 2017 and 2018


def test_build_mayors_reads_the_ministry_spreadsheet(tmp_path, monkeypatch):
    pytest.importorskip('openpyxl')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import build_mayors
    sheet = pd.DataFrame([
        ['Relación de alcaldes del mandato de 2.019 a 2.023', None, None,
         None, None, None],
        [None] * 6,
        ['CÓDIGO INE', 'MUNICIPIO', 'NOMBRE', 'LISTA', 'FECHA POSESIÓN',
         'FECHA BAJA'],
        ['280796', 'Madrid', 'JOSE LUIS MARTINEZ-ALMEIDA NAVASQÜES', 'PP',
         '15/06/2019', None],
        [170792.0, 'Girona', 'MARTA MADRENAS I MIR', "C's", 'SIN FECHA',
         '01/02/2020'],
        ['170792', 'Girona', 'Lluc Salellas', 'CUP', '02/02/2020', None],
        # 6-digit code that lost its leading zero (Alegría-Dulantzi, 01001)
        ['10014', 'Alegría-Dulantzi', 'ANA LOPEZ', 'IND.', '15/06/2019', None],
    ])
    source = tmp_path / 'Alcaldes_Mandato_2019_2023.xlsx'
    sheet.to_excel(source, header=False, index=False)
    out = tmp_path / 'mayors.csv.gz'
    monkeypatch.setattr(build_mayors, 'OUT', out)
    monkeypatch.setattr(sys, 'argv', ['build_mayors.py', str(source)])
    build_mayors.main()
    built = mayors.load(tmp_path)
    assert sorted(set(built['ine_code'])) == ['01001', '17079', '28079']
    assert built.loc[built['ine_code'] == '01001', 'list'].item() == 'IND'
    madrid = built[built['ine_code'] == '28079'].iloc[0]
    assert madrid['name'] == 'Jose Luis Martinez-Almeida Navasqües'
    assert madrid['end'] == date(2023, 6, 16)  # filled with the term end
    girona = built[built['name'].str.startswith('Marta')].iloc[0]
    assert girona['list'] == 'Cs' and girona['name'] == 'Marta Madrenas i Mir'
    assert girona['start'] == date(2019, 6, 15)  # filled with the term start
    assert girona['end'] == date(2020, 2, 1)


def test_build_mayors_current_term_export_and_since(tmp_path, monkeypatch):
    """The current-term export (one row per council, names split in three
    columns, no end dates) ends on its export date; --since drops mayors
    who had left before that date; 5-digit codes of the 2007 list are kept."""
    pytest.importorskip('openpyxl')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import build_mayors
    current = pd.DataFrame([
        [None] * 10,
        [None, None, None, None, None, None,
         'Ficha de Alcaldes de la Legislatura 2023', None, None, None],
        ['Código INE', 'Municipio', 'Provincia', 'Comunidad Autónoma',
         'Nombre', '1er Apellido', '2º Apellido', 'Cargo',
         'Fecha de Posesión', 'Partido'],
        ['280796', 'Madrid', 'Madrid', 'Madrid', 'JOSÉ LUIS',
         'MARTÍNEZ-ALMEIDA', 'NAVASQÜÉS', 'Alcalde', '17/06/2023', 'PP'],
    ])
    old = pd.DataFrame([
        ['Alcaldes del mandato de 2.007 a 2.011', None, None, None, None,
         None],
        ['CÓDIGO INE', 'MUNICIPIO', 'NOMBRE', 'LISTA', 'FECHA POSESIÓN',
         'FECHA BAJA'],
        ['04001', 'Abla', 'JOSÉ MANUEL ORTIZ BONO', 'PSOE', '16/06/2007',
         '11/12/2010'],
        ['04001', 'Abla', 'ANTONIO MANUEL ORTIZ OLIVA', 'PSOE', '18/12/2010',
         None],
        ['04002', 'Abrucena', 'ANA RUIZ', 'PP', '16/06/2007', '01/05/2009'],
        ['04002', 'Abrucena', 'LUIS GIL', 'PP', '02/05/2009', None],
    ])
    files = [tmp_path / 'Alcaldes_Mandato_2007_2011.xlsx',
             tmp_path / 'ficha_alcaldes_2023_17-10-2026_18_36_29.xlsx']
    old.to_excel(files[0], header=False, index=False)
    current.to_excel(files[1], header=False, index=False)
    monkeypatch.setattr(build_mayors, 'OUT', tmp_path / 'mayors.csv.gz')
    monkeypatch.setattr(sys, 'argv', ['build_mayors.py', '--since',
                                      '2010-01-01', *map(str, files)])
    build_mayors.main()
    built = mayors.load(tmp_path)
    madrid = built[built['ine_code'] == '28079'].iloc[0]
    assert madrid['term'] == 2023
    assert madrid['name'] == 'José Luis Martínez-Almeida Navasqüés'
    assert madrid['end'] == date(2026, 10, 17)  # the export date
    abla = built[built['ine_code'] == '04001']
    assert list(abla['end']) == [date(2010, 12, 11), date(2011, 6, 10)]
    # Ana Ruiz left in 2009, before the data start
    assert list(built.loc[built['ine_code'] == '04002', 'name']) == [
        'Luis Gil']
    assert mayors.coverage(built) == (date(2010, 1, 1), date(2026, 10, 17))
