"""End-to-end checks of the Streamlit app with Streamlit's own test runner."""
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from modules import conprel, mayors

APP = str(Path(__file__).parents[1] / 'app.py')
official = pytest.mark.skipif(not conprel.available(),
                              reason='official dataset not built')


def run(query: dict | None = None, state: dict | None = None) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in (query or {}).items():
        app.query_params[key] = value
    for key, value in (state or {}).items():
        app.session_state[key] = value
    return app.run()


def hero(app: AppTest) -> str:
    return next(m.value for m in app.markdown
                if "class='om-hero'" in m.value
                or "class='om-landing'" in m.value)


@official
def test_landing_shows_only_sentence_and_search():
    app = run({'lang': 'es'})
    assert not app.exception
    assert 'explica en qué gasta su dinero cada ayuntamiento' in hero(app)
    assert len(app.text_input) == 1


@official
def test_municipality_view_in_both_languages():
    app = run({'lang': 'es', 'm': '11012'})
    assert not app.exception
    assert 'Ayuntamiento de Cádiz' in hero(app)
    assert [m.label for m in app.metric][0] == 'Gasto total'
    app = run({'lang': 'en', 'm': '11012'})
    assert not app.exception and 'Cádiz council' in hero(app)


@official
def test_comparison_inflation_and_spending_types():
    app = run({'lang': 'es', 'm': '11012', 'c': '41091'},
              {'real': True, 'group': 'kind'})
    assert not app.exception
    assert 'descontada la inflación' in hero(app)
    points = next(m.value for m in app.markdown if 'om-points' in m.value
                  and '<li>' in m.value)
    assert 'Sevilla gasta' in points and 'inversiones' in points
    # The comparison is announced at the top, with a way to remove it
    assert any('Comparando con **Sevilla' in m.value for m in app.markdown)
    assert 'Quitar la comparación' in [b.label for b in app.button]


@official
def test_municipality_without_data_is_explained():
    app = run({'lang': 'es', 'm': '01006'})  # Armiñón (Álava): never sent
    assert not app.exception
    assert 'No hay datos de Armiñón' in hero(app)
    assert 'régimen foral' in app.info[0].value


@official
def test_side_menu_is_headed_by_the_municipality():
    app = run({'lang': 'es', 'm': '11012'})
    assert not app.exception
    assert [h.value for h in app.sidebar.header] == ['Cádiz']
    assert not app.get('file_uploader')  # official data only


@official
def test_rolled_over_budget_is_flagged():
    # Leganés reported a 2025 budget identical to 2024 in every area
    app = run({'lang': 'es', 'm': '28074'})
    assert not app.exception
    assert any('prorrogado' in w.value for w in app.warning)
    app = run({'lang': 'es', 'm': '11012'})  # Cádiz 2025: a new budget
    assert not any('prorrogado' in w.value for w in app.warning)


@official
def test_outturn_view_compares_planned_and_spent():
    # Stage and year come from the address, so the view can be shared
    app = run({'lang': 'es', 'm': '11012', 's': 'executed', 'y': '2024'},
              {'a11y_tables': True})
    assert not app.exception
    assert 'En 2024, el Ayuntamiento de Cádiz gastó' in hero(app)
    assert '¿Se gastó lo previsto?' in [s.value for s in app.subheader]
    points = next(m.value for m in app.markdown if 'om-points' in m.value
                  and '<li>' in m.value)
    assert 'presupuestó gastar' in points
    # AppTest returns plain strings or one-item lists depending on version
    assert str(app.query_params['s']).strip("[']") == 'executed'
    assert str(app.query_params['y']).strip("[']") == '2024'
    # Accessible table under the chart, with the share spent of the plan
    assert any('Gastado de lo previsto (%)' in str(d.value.columns.tolist())
               or 'Rate' in d.value.columns for d in app.dataframe)


@official
def test_year_in_address_and_missing_outturn_year():
    app = run({'lang': 'en', 'm': '11012', 'y': '2015'})
    assert not app.exception and 'In 2015' in hero(app)
    # 2025 has no outturn yet: the latest outturn year is shown instead
    app = run({'lang': 'en', 'm': '11012', 's': 'executed', 'y': '2025'})
    assert not app.exception and 'In 2024' in hero(app)


# Streamlit 1.51's test runner garbles segmented controls after a click (the
# app itself works there; checked in a browser), so this test needs 1.52+
old_runner = pytest.mark.skipif(
    tuple(int(x) for x in st.__version__.split('.')[:2]) < (1, 52),
    reason='AppTest bug with clicks next to segmented controls in 1.51')


@official
@old_runner
def test_side_menu_search_goes_to_another_municipality():
    app = run({'lang': 'es', 'm': '11012'})
    app.sidebar.text_input(key='sq').input('sevilla').run()
    assert not app.exception
    app.sidebar.button(key='pick_side_41091').click().run()
    assert not app.exception
    assert 'Ayuntamiento de Sevilla' in hero(app)
    assert [h.value for h in app.sidebar.header] == ['Sevilla']


@official
@pytest.mark.skipif(mayors.load() is None, reason="no mayors file")
def test_mayors_are_lined_up_with_the_budget():
    # Madrid 2016: first budget of Manuela Carmena, who took office in 2015
    app = run({'lang': 'es', 'm': '28079', 'y': '2016'}, {'a11y_tables': True})
    assert not app.exception
    assert any('Alcaldía en 2016' in m.value for m in app.sidebar.markdown)
    assert any('Manuela Carmena' in c.value for c in app.sidebar.caption)
    points = next(m.value for m in app.markdown if 'om-points' in m.value
                  and '<li>' in m.value)
    assert 'Manuela Carmena Castrillo (AHORA)' in points
    assert 'primer presupuesto' in points
    assert any('cambió la alcaldía' in i.value for i in app.info)
    # The record of each mayoralty, with the budgets assigned to it
    record = next(d.value for d in app.dataframe if 'mayor' in d.value
                  and 'budgets' in d.value)
    carmena = record[record['mayor'].str.startswith('Manuela')].iloc[0]
    assert carmena['budgets'] == '2016–2019'
    assert 'Descargar la lista de alcaldías (CSV)' in [
        b.proto.label for b in app.get('download_button')]


@official
@pytest.mark.skipif(mayors.load() is None, reason="no mayors file")
def test_years_without_mayor_data_say_so():
    # Dénia: for the current term the Ministry lists only today's mayor,
    # who took office in 2026, so 2023-2026 has a gap that is explained
    app = run({'lang': 'en', 'm': '03063', 'y': '2025'})
    assert not app.exception
    captions = ' '.join(c.value for c in app.sidebar.caption)
    assert 'No mayor data from 17 Jun 2023' in captions
    assert 'only publishes who is mayor today' in captions
