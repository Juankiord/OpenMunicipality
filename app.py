import inspect
from html import escape
from urllib.parse import urlsplit

import pandas as pd

import streamlit as st
import streamlit.components.v1 as components

from modules import conprel, mayors, share, ui, visualizer as viz
from modules.i18n import (LANGUAGES, category_name, integer, long_date,
                          money, money_compact, money_words, pct,
                          short_date, t)
from modules.metrics_engine import (calculate_budget_kpis,
                                    calculate_yoy_deviation,
                                    get_category_breakdown)
from modules.narrative import (change_pct, headline, key_points,
                               mayor_change_note, mayor_point)

st.set_page_config(page_title='OpenMunicipality', page_icon='🏛️',
                   layout='wide')


def and_list(items) -> str:
    """'2024 y 2025' / '2024 and 2025'."""
    items = [str(i) for i in items]
    joiner = ' y ' if lang == 'es' else ' and '
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + joiner + items[-1]


def year_ranges(years) -> str:
    """[2010, 2011, 2012, 2016] -> '2010-2012 y 2016' (short for long lists)."""
    years = sorted(int(y) for y in years)
    groups, start = [], years[0]
    for previous, current in zip(years, years[1:] + [None]):
        if current != previous + 1 if current else True:
            groups.append(str(start) if start == previous
                          else f'{start}–{previous}')
            start = current
    return and_list(groups)


# Streamlit >= 1.6x can update a text box while the user types; older
# versions update it on Enter, and the box then says so
LIVE_SEARCH = 'live' in inspect.signature(st.text_input).parameters


def search_box(label: str, key: str, placeholder: str, on_change=None,
               show_label: bool = False) -> str:
    """Municipality search box: results appear while typing when supported."""
    options = {'live': True} if LIVE_SEARCH else {}
    if on_change is not None:
        options['on_change'] = on_change
    hint = '' if LIVE_SEARCH else t(lang, 'press_enter')
    return st.text_input(label, key=key, placeholder=placeholder + hint,
                         icon=':material/search:',
                         label_visibility='visible' if show_label
                         else 'collapsed', **options)


def minus_ascii(text: str) -> str:
    """st.metric reads the arrow direction from a leading ASCII '-'."""
    return text.replace('−', '-')


# ---------------------------------------------------------------- language
lang = st.query_params.get('lang', 'es')
lang = lang if lang in LANGUAGES else 'es'
choice = st.sidebar.segmented_control(
    'Idioma / Language', options=list(LANGUAGES), default=lang,
    format_func=LANGUAGES.get)
if choice and choice != lang:
    st.query_params['lang'] = choice
    st.rerun()

# ---------------------------------------------------- appearance & access
saved = ui.from_query(st.query_params)
for field in ui.QUERY_KEYS:
    st.session_state.setdefault(f'a11y_{field}', getattr(saved, field))

with st.sidebar.expander(t(lang, 'a11y_title'),
                         icon=':material/accessibility_new:'):
    st.segmented_control(
        t(lang, 'a11y_theme'), ['auto', 'light', 'dark'], key='a11y_theme',
        format_func=lambda v: t(lang, f'theme_{v}'),
        help=t(lang, 'a11y_theme_help'))
    st.segmented_control(
        t(lang, 'a11y_text'), ['m', 'l', 'xl'], key='a11y_text',
        format_func=lambda v: t(lang, f'text_{v}'))
    st.toggle(t(lang, 'a11y_contrast'), key='a11y_contrast',
              help=t(lang, 'a11y_contrast_help'))
    st.toggle(t(lang, 'a11y_spacing'), key='a11y_spacing',
              help=t(lang, 'a11y_spacing_help'))
    st.toggle(t(lang, 'a11y_tables'), key='a11y_tables',
              help=t(lang, 'a11y_tables_help'))
    st.caption(t(lang, 'a11y_saved'))

settings = ui.A11y(
    theme=st.session_state.a11y_theme or 'auto',
    text=st.session_state.a11y_text or 'm',
    **{f: bool(st.session_state[f'a11y_{f}']) for f in
       ('contrast', 'spacing', 'tables')})


def view_params(municipality: str | None = None,
                compare: str | None = None) -> dict:
    """Municipality, comparison, stage (?s=executed) and year (?y=)."""
    if not municipality:
        return {}
    params = {'m': municipality}
    if compare:
        params['c'] = compare
    if st.session_state.get('stage') == 'executed':
        params['s'] = 'executed'
    if st.session_state.get('year'):
        params['y'] = str(st.session_state.year)
    return params


def sync_query(municipality: str | None = None,
               compare: str | None = None) -> None:
    """Language, accessibility choices and the view (municipality, stage,
    year, comparison) live in the address, so it can be bookmarked or
    shared."""
    wanted = {'lang': lang, **ui.to_query(settings),
              **view_params(municipality, compare)}
    if st.query_params.to_dict() != wanted:
        st.query_params.from_dict(wanted)


dark = (settings.theme == 'dark' or
        (settings.theme == 'auto' and st.context.theme.type == 'dark'))
chart_style = viz.ChartStyle(dark=dark, scale=settings.scale,
                             contrast=settings.contrast)
st.markdown(ui.build_css(settings, dark), unsafe_allow_html=True)

# Page language for screen readers + colour mode chosen in the sidebar
with st.sidebar:
    script = ui.page_script(lang, settings.theme)  # static, no user input
    if hasattr(st, 'iframe'):  # Streamlit >= 1.52
        st.iframe(script, height=1)
    else:
        components.html(script, height=0)

# ---------------------------------------------------------------- data
# Read-only tables shared by every visitor: cache_resource keeps one copy in
# memory instead of copying them on each interaction (nothing modifies them)


@st.cache_resource(show_spinner=False)
def official_data():
    meta, lines, bench = conprel.load()
    everyone = conprel.load_all_municipalities()
    return meta, lines, bench, conprel.search_index(meta, everyone)


@st.cache_resource(show_spinner=False)
def programme_data():
    return conprel.load_programs()


@st.cache_resource(show_spinner=False)
def mayor_data():
    return mayors.load()


@st.cache_data(show_spinner=False, max_entries=64)
def council_years(ine_code: str):
    meta, lines, _, _ = official_data()
    return conprel.yearly_totals(meta, lines, ine_code)


@st.cache_data(show_spinner=False)
def summary_image(*args) -> bytes:
    return share.summary_card(*args)


cpi = conprel.load_cpi()


# Without a dataset (data/conprel or OPENMUNICIPALITY_DATA_DIR) there is
# nothing to show
if not conprel.available():
    st.error(t(lang, 'no_dataset'), icon=':material/error:')
    st.stop()

stage, bench = 'budget', None
BRAND = (f"<div class='om-brand'><b>OpenMunicipality</b><br>"
         f"{t(lang, 'app_tagline')}</div>")
meta, lines_all, bench_all, index = official_data()
st.session_state.setdefault('muni', st.query_params.get('m'))
if st.session_state.muni not in index.index:
    st.session_state.muni = None


def choose(code: str) -> None:
    st.session_state.muni = code
    st.session_state.q = ''


def choose_exact() -> None:
    """Enter on an exact name goes straight to that municipality."""
    found = conprel.search(index, st.session_state.q, 1)
    if len(found) and found['tier'].iloc[0] == 0:
        choose(found.index[0])


def clear() -> None:
    st.session_state.muni = None
    st.session_state.cmp_open = False

code = st.session_state.muni
if code is None:  # landing: one sentence and the search box
    sync_query()
    st.markdown(ui.LANDING_CSS, unsafe_allow_html=True)
    other = 'en' if lang == 'es' else 'es'
    if st.button(LANGUAGES[other], key='lang_switch', type='tertiary'):
        st.query_params['lang'] = other
        st.rerun()
    st.markdown(f"<p class='om-landing'>{t(lang, 'landing_sentence')}</p>",
                unsafe_allow_html=True)
    # Enter on an exact name opens it; with live search the results
    # list (exact name first) is used instead, so typing never jumps away
    query = search_box(t(lang, 'search_label'), 'q', t(lang, 'search_ph'),
                       None if LIVE_SEARCH else choose_exact)
    results = conprel.search(index, query)
    if query and results.empty:
        st.info(t(lang, 'search_none'), icon=':material/info:')
    for found_code, row in results.iterrows():
        st.button(t(lang, 'search_result', label=row['label'],
                    pop=integer(row['population'], lang))
                  if row['has_data'] else
                  t(lang, 'search_nodata', label=row['label']),
                  key=f'pick_{found_code}', on_click=choose,
                  args=(found_code,), width='stretch')
    st.stop()

st.session_state.setdefault('cmp', st.query_params.get('c'))
st.session_state.setdefault('stage', st.query_params.get('s', 'budget'))
if 'year' not in st.session_state:
    wanted_year = st.query_params.get('y', '')
    st.session_state.year = int(wanted_year) if wanted_year.isdigit() \
        else None
has_data = bool(index.loc[code, 'has_data'])
cmp_code = st.session_state.cmp
if (cmp_code not in index.index or cmp_code == code
        or not index.loc[cmp_code, 'has_data']):
    st.session_state.cmp = None
sync_query(code, st.session_state.cmp)
st.markdown(BRAND, unsafe_allow_html=True)


def open_comparison() -> None:
    st.session_state.cmp_open = True

# Comparing changes the whole page, so it sits next to "Change
# municipality", above the headline
with st.container(horizontal=True, gap='medium'):
    st.button(t(lang, 'change_muni'), on_click=clear,
              icon=':material/search:', type='tertiary')
    if has_data and not st.session_state.cmp:
        st.button(t(lang, 'cmp_title'), on_click=open_comparison,
                  icon=':material/compare_arrows:', type='tertiary',
                  key='cmp_open_button')


@st.fragment
def comparison_box() -> None:
    """While comparing: who with, and how to stop. While choosing: a
    search box (typing reruns only this box; choosing reruns the page)."""
    def pick(found: str) -> None:
        st.session_state.cmp = found
        st.session_state.cmp_open = False
        st.session_state.cq = ''
        st.session_state.cmp_changed = True

    def close() -> None:
        st.session_state.cmp = None
        st.session_state.cmp_open = False
        st.session_state.cmp_changed = True

    if st.session_state.pop('cmp_changed', False):
        st.rerun()
    if st.session_state.cmp:
        with st.container(border=True, horizontal=True,
                          vertical_alignment='center', key='cmp_banner'):
            st.markdown(t(lang, 'cmp_active', other=index.loc[
                st.session_state.cmp, 'label']))
            st.button(t(lang, 'cmp_clear'), on_click=close,
                      icon=':material/close:', key='cmp_clear')
    elif st.session_state.get('cmp_open'):
        with st.container(border=True):
            st.markdown(f"**{t(lang, 'cmp_title')}**")
            query = search_box(t(lang, 'cmp_title'), 'cq',
                               t(lang, 'cmp_ph'))
            found = conprel.search(index[index['has_data']], query, 5)
            for found_code, row in found.drop(code,
                                              errors='ignore').iterrows():
                st.button(t(lang, 'search_result', label=row['label'],
                            pop=integer(row['population'], lang)),
                          key=f'pick_cmp_{found_code}', on_click=pick,
                          args=(found_code,), width='stretch')
            st.button(t(lang, 'cmp_cancel'), on_click=close,
                      type='tertiary', key='cmp_cancel')

if has_data:
    comparison_box()


@st.fragment
def sidebar_search() -> None:
    """Search box in the side menu to go straight to another municipality.
    Typing reruns only this box; choosing one reloads the page."""
    def go_to(found: str) -> None:
        st.session_state.muni = found
        st.session_state.sq = ''
        st.session_state.cmp_open = False
        st.session_state.side_changed = True

    if st.session_state.pop('side_changed', False):
        st.rerun()
    query = search_box(t(lang, 'side_search'), 'sq', t(lang, 'side_search_ph'),
                       show_label=True)
    found = conprel.search(index, query, 5).drop(code, errors='ignore')
    if query and found.empty:
        st.caption(t(lang, 'side_search_none'))
    for found_code, row in found.iterrows():
        st.button(t(lang, 'search_result', label=row['label'],
                    pop=integer(row['population'], lang))
                  if row['has_data'] else
                  t(lang, 'search_nodata', label=row['label']),
                  key=f'pick_side_{found_code}', on_click=go_to,
                  args=(found_code,), width='stretch')


with st.sidebar:
    sidebar_search()

if not index.loc[code, 'has_data']:  # in the INE list, not in CONPREL
    missing = sorted(set(meta['Year']))
    st.markdown(f"<div class='om-hero'><h1>"
                f"{escape(t(lang, 'nodata_title', name=index.loc[code, 'name']))}"
                f"</h1><p>{escape(t(lang, 'nodata_text', years=year_ranges(missing)))}"
                "</p></div>", unsafe_allow_html=True)
    if code[:2] in conprel.FORAL_PROVINCES:
        st.info(t(lang, 'nodata_foral'), icon=':material/info:')
    st.caption(t(lang, 'footer'))
    st.stop()

st.sidebar.header(index.loc[code, 'name'])
stages = conprel.stages(lines_all, code)
if st.session_state.stage not in stages:
    st.session_state.stage = stages[0]
if len(stages) > 1:
    stage = st.sidebar.segmented_control(
        t(lang, 'stage_label'), stages, key='stage',
        format_func=lambda v: t(lang, f'stage_{v}')) or stages[0]
else:
    stage = stages[0]
# The outturns live in their own file (lines_executed.csv.gz); say so when
# the dataset lists outturn years but that file is missing
if 'executed' in set(meta['Stage']) and \
        'executed' not in set(lines_all['Stage'].astype(str)):
    st.sidebar.warning(t(lang, 'executed_missing'), icon=':material/error:')
df, population_by_year, name = conprel.municipality(meta, lines_all, code,
                                                    stage)
years = sorted((int(y) for y in df['Year'].unique()), reverse=True)
if st.session_state.year not in years:  # e.g. no outturn for that year
    st.session_state.year = years[0]
year = int(st.sidebar.selectbox(t(lang, 'sb_year'), years, key='year'))
population = population_by_year[year]
st.sidebar.caption(t(lang, 'sb_population_official',
                     pop=integer(population, lang)))
if stage == 'executed':
    st.sidebar.caption(t(lang, 'coverage_executed', years=year_ranges(
        conprel.years_of(meta, 'executed'))))
missing_years = conprel.years_without_data(meta, code, stage)
if missing_years:
    st.sidebar.caption(
        t(lang, 'missing_years' if stage == 'budget'
          else 'missing_years_executed', years=year_ranges(missing_years))
        + (' ' + t(lang, 'nodata_foral')
           if code[:2] in conprel.FORAL_PROVINCES else ''))
# Who held the mayoralty (Ministry of Territorial Policy), when available
mayor_table = mayor_data()
spans = mayors.periods(mayor_table, code)
mayor_cover = mayors.coverage(mayor_table)
if mayor_cover:
    st.sidebar.markdown(f"**{t(lang, 'mayor_side_title', year=year)}**")
    in_office = mayors.in_year(spans, year)
    year_gaps = mayors.gaps(spans, *mayor_cover, year=year)
    if in_office:
        st.sidebar.caption('  \n'.join(
            t(lang, 'mayor_side_open', who=mayors.label(s),
              start=mayors.since(s, lang, long=False))
            if s['end'] >= mayor_cover[1] else
            t(lang, 'mayor_side_row', who=mayors.label(s),
              start=mayors.since(s, lang, long=False),
              end=short_date(s['end'], lang))
            for s in in_office))
    elif not year_gaps:  # outside the register (a gap says so itself)
        st.sidebar.caption(t(lang, 'mayor_side_none', year=year,
                             first=long_date(mayor_cover[0], lang),
                             last=long_date(mayor_cover[1], lang)))
    current_from = mayors.current_term_start(mayor_table)
    for gap_from, gap_to in year_gaps:
        st.sidebar.caption(
            t(lang, 'mayor_side_gap', start=short_date(gap_from, lang),
              end=short_date(gap_to, lang))
            + (' ' + t(lang, 'mayor_current_only')
               if current_from and gap_from >= current_from else ''))
band, bench_rows = conprel.benchmark(bench_all, year, stage, population)
bench = {kind: dict(zip(rows['Category'], rows['Median_Per_Capita']))
         for kind, rows in bench_rows.groupby('Type')}
real_terms = st.sidebar.toggle(t(lang, 'sb_real'), key='real',
                               help=t(lang, 'sb_real_help'))
with st.sidebar.expander(t(lang, 'sb_advanced')):
    threshold = st.slider(t(lang, 'sb_threshold'), 1, 50, 10,
                          help=t(lang, 'sb_threshold_help'))


def pop(y: int) -> int:
    """Registered population of a given year, else the selected year's."""
    return population_by_year.get(y, population)


# ---------------------------------------------------------------- figures
prev = year - 1
has_prev = prev in df['Year'].values
kpis = calculate_budget_kpis(df, population, year)
prev_kpis = calculate_budget_kpis(df, pop(prev), prev) if has_prev else None
spend = get_category_breakdown(df, year, population, 'Expense')
income = get_category_breakdown(df, year, population, 'Income')
deviation = calculate_yoy_deviation(df, 'Expense', threshold)
inflation = cpi.get(year) if real_terms and has_prev else None
if inflation is not None:  # every change is shown after removing inflation
    rate = deviation['Year'].map(cpi)
    adjusted = deviation['Delta_pct'].notna() & rate.notna()
    deviation.loc[adjusted, 'Delta_pct'] = [
        conprel.real_change(d, r) for d, r in
        zip(deviation.loc[adjusted, 'Delta_pct'], rate[adjusted])]
    deviation['Flagged'] = deviation['Delta_pct'].abs() >= threshold
year_dev = deviation[deviation['Year'] == year]

# ---------------------------------------------------------------- hero
lines = [escape(s) for s in headline(lang, year, kpis, prev_kpis, name, stage,
                                     inflation)]
st.markdown(f"<div class='om-hero'><h1>{lines[0]}</h1>"
            f"<p>{' '.join(lines[1:])}</p></div>", unsafe_allow_html=True)
if real_terms and has_prev and inflation is None:
    st.caption(t(lang, 'real_unavailable', year=year))


def delta(key: str, money_fmt) -> str | None:
    if not prev_kpis:
        return None
    if key == 'net_balance':
        diff = kpis[key] - prev_kpis[key]
        if abs(diff) < max(1_000, 0.0005 * kpis['total_expenditure']):
            return None  # rounding differences in balanced budgets
        text = ('+' if diff > 0 else '') + money_fmt(diff, lang)
    else:
        change = change_pct(kpis[key], prev_kpis[key])
        if change is None:
            return None
        if inflation is not None:
            change = conprel.real_change(change, inflation)
        text = pct(change, lang, signed=True)
    return minus_ascii(f"{text} {t(lang, 'kpi_vs', prev=prev)}")


def history(key: str) -> list[float] | None:
    if len(years) < 3:  # a trend needs at least three points
        return None
    return [calculate_budget_kpis(df, pop(y), y)[key] for y in sorted(years)]


tiles = [
    ('kpi_spend', 'total_expenditure', money_compact),
    ('kpi_income', 'total_revenue', money_compact),
    ('kpi_per_res', 'per_capita_expenditure', money),
    ('kpi_balance', 'net_balance', money_compact),
]
for column, (label, key, fmt) in zip(st.columns(4), tiles):
    column.metric(t(lang, label), fmt(kpis[key], lang),
                  delta=delta(key, fmt), delta_color='off', border=True,
                  chart_data=history(key), chart_type='line')

# ------------------------------------------- official data: extra figures
usual = (bench or {}).get('Expense', {}).get('_TOTAL')
other, extra = None, {}
executed = conprel.execution(lines_all, code, year)
if executed and executed[0] <= 0:  # no usable plan to compare with
    executed = None
if executed:
    planned, spent = executed
    extra['execution'] = t(lang, 'kp_execution', year=year,
                           planned=money_words(planned, lang),
                           spent=money_words(spent, lang),
                           rate=pct(spent / planned * 100, lang, 0))
kinds_df = get_category_breakdown(
    conprel.kinds(lines_all, code, stage, year).assign(Year=year), year,
    population)
invest = kinds_df.set_index('Category').loc['K_INVEST']
if kinds_df['Amount'].sum() > 0:
    text = t(lang, 'kp_invest', share=money(round(invest['Share_pct']),
                                            lang, 0),
             per_res=money(invest['Per_Capita'], lang, 0))
    median = (bench or {}).get('ExpenseChapter', {}).get('E67')
    if median is not None:
        text += t(lang, 'kp_invest_bench', median=money(median, lang, 0))
    extra['invest'] = text

# Comparison with a second municipality (kept in the address as ?c=)
if (st.session_state.cmp not in index.index or st.session_state.cmp == code
        or not index.loc[st.session_state.cmp, 'has_data']):
    st.session_state.cmp = None
sync_query(code, st.session_state.cmp)
if st.session_state.cmp:
    df_o, pop_o, name_o = conprel.municipality(
        meta, lines_all, st.session_state.cmp, stage)
    if year in pop_o:
        other_spend = get_category_breakdown(df_o, year, pop_o[year])
        other_kinds = get_category_breakdown(
            conprel.kinds(lines_all, st.session_state.cmp, stage,
                          year).assign(Year=year), year, pop_o[year])
        other = (name_o, other_spend, other_kinds)
        value = calculate_budget_kpis(df_o, pop_o[year], year)[
            'per_capita_expenditure']
        extra['compare'] = t(lang, 'kp_compare', other=name_o,
                             value=money(value, lang, 0),
                             mine=money(kpis['per_capita_expenditure'],
                                        lang, 0))
    else:
        extra['compare'] = t(lang, 'cmp_no_year', other=name_o, year=year)

warnings = conprel.data_warnings(
    kpis, prev_kpis, stage, population, pop(prev) if has_prev else None,
    usual, conprel.same_as_previous(
        calculate_yoy_deviation(df, 'Expense', threshold).query(
            'Year == @year')),
    spent / planned if executed else None)
if warnings:
    items = [t(lang, key, pct=pct(v.get('pct', 0), lang,
                                  1 if key != 'warn_execution' else 0,
                                  signed=key != 'warn_execution'))
             for key, v in warnings]
    st.warning(f"**{t(lang, 'warn_title')}**\n\n- " + '\n- '.join(items)
               + f"\n\n{t(lang, 'warn_source')}", icon=':material/warning:')

with st.container(border=True):
    st.subheader(t(lang, 'kp_title'))
    compare = ((band, usual, kpis['per_capita_expenditure'])
               if usual is not None else None)
    points = key_points(lang, year, spend, deviation, threshold, compare,
                        inflation)
    position = 1 if compare else 0
    if 'compare' in extra:
        points.insert(position, extra['compare'])
    if 'invest' in extra:
        points.insert(position + 1 + ('compare' in extra), extra['invest'])
    if 'execution' in extra:
        points.insert(0, extra['execution'])
    mayor_text = mayor_point(lang, spans, year, stage)
    if mayor_text:
        points.append(mayor_text)
    items = ''.join(f'<li>{escape(p)}</li>' for p in points)
    st.markdown(f"<ul class='om-points'>{items}</ul>", unsafe_allow_html=True)

# ---------------------------------------------------------------- tabs
VIEWS = {'per_res': 'view_per_res', 'total': 'view_total',
         'share': 'view_share'}
tab_spend, tab_income, tab_change, tab_mayors, tab_data = st.tabs(
    [t(lang, 'tab_spend'), t(lang, 'tab_income'), t(lang, 'tab_change'),
     t(lang, 'tab_mayors'), t(lang, 'tab_data')])


def area_panel(data, intro_key: str, kind_key: str, widget_key: str,
               reference: dict | None = None,
               compare_with: tuple[str, dict] | None = None):
    if data.empty:
        st.info(t(lang, 'no_rows', kind=t(lang, kind_key), year=year))
        return
    st.caption(t(lang, intro_key))
    view = st.segmented_control(
        t(lang, 'view_label'), options=list(VIEWS), default='per_res',
        format_func=lambda v: t(lang, VIEWS[v]), key=widget_key,
        label_visibility='collapsed') or 'per_res'
    if compare_with and view != 'per_res':
        st.caption(t(lang, 'cmp_per_res_only', other=compare_with[0],
                     view=t(lang, 'view_per_res')))
    st.plotly_chart(viz.area_bars(data, view, lang, chart_style, reference,
                                  compare_with),
                    width='stretch',
                    config=viz.chart_config(f'{widget_key}_{year}'))
    if settings.tables:
        table = data[['Category', 'Amount', 'Share_pct', 'Per_Capita']]
        columns = {'Amount': 'col_total', 'Share_pct': 'col_share',
                   'Per_Capita': 'col_per_res'}
        if compare_with:
            table = table.assign(Other=[compare_with[1].get(c, 0.0)
                                        for c in table['Category']])
            columns['Other'] = 'col_other'
        elif reference:
            table = table.assign(Usual=[reference.get(c, 0.0)
                                        for c in table['Category']])
            columns['Usual'] = 'col_bench'
        chart_table(table, columns)


def chart_table(data, columns: dict):
    """Accessible text alternative: the numbers behind a chart."""
    table = data.copy()
    table['Category'] = [category_name(lang, c) for c in table['Category']]
    config = {'Category': t(lang, 'col_category')}
    for column, key in columns.items():
        label = t(lang, key, year=column if str(column).isdigit() else year,
                  prev=prev)
        if table[column].dtype == bool:
            table[column] = ['⚑' if v else '' for v in table[column]]
            config[column] = label
        else:
            config[column] = st.column_config.NumberColumn(label,
                                                           format='%.2f')
    st.caption(t(lang, 'chart_table'))
    st.dataframe(table, hide_index=True, width='stretch',
                 column_config=config)


def top_areas(data, keep: int = 6):
    """At most `keep` lines plus 'Other areas', so colours never repeat."""
    if data['Category'].nunique() <= keep + 1:
        return data, False
    latest = data[data['Year'] == data['Year'].max()]
    top = latest.nlargest(keep, 'Amount')['Category']
    data = data.assign(Category=data['Category'].where(
        data['Category'].isin(top), 'OTHER'))
    return data.groupby(['Category', 'Year'], as_index=False)['Amount'].sum(), True


def per_res(data) -> dict:
    return dict(zip(data['Category'], data['Per_Capita']))


def plan_vs_spent(group: str) -> None:
    """Budget against outturn for the same year, by area or by type."""
    if 'execution' not in extra:
        return

    def breakdown(which: str):
        if group == 'kind':
            data = conprel.kinds(lines_all, code, which, year).assign(Year=year)
        else:
            data = conprel.municipality(meta, lines_all, code, which)[0]
        # Same population for both, so the bars differ only by the money
        return get_category_breakdown(data, year, population)

    planned, spent = breakdown('budget'), breakdown('executed')
    # Main bars: the plan; second bars: what was spent (Amount_spent)
    both = planned.merge(spent[['Category', 'Amount', 'Per_Capita']],
                         on='Category', how='outer',
                         suffixes=('', '_spent')).fillna(0)
    both = both[(both['Amount'] > 0) | (both['Amount_spent'] > 0)]
    if both.empty:
        return
    st.subheader(t(lang, 'plan_title'))
    st.caption(t(lang, 'plan_intro', year=year))
    gaps = (both['Amount'] - both['Amount_spent']).abs()
    if gaps.max() >= 1:
        gap = both.loc[gaps.idxmax()]
        st.markdown(t(lang, 'plan_gap',
                      area=category_name(lang, gap['Category']),
                      planned=money_words(gap['Amount'], lang),
                      spent=money_words(gap['Amount_spent'], lang)))
    st.plotly_chart(
        viz.area_bars(both, 'per_res', lang, chart_style,
                      compare=(t(lang, 'plan_spent'),
                               dict(zip(both['Category'],
                                        both['Per_Capita_spent']))),
                      own_name=t(lang, 'plan_planned')),
        width='stretch', config=viz.chart_config(f'plan_{group}_{year}'))
    if settings.tables:
        rate = (both['Amount_spent'] / both['Amount'].where(both['Amount'] > 0)
                * 100).round(1)
        chart_table(both.assign(Rate=rate),
                    {'Per_Capita': 'col_planned',
                     'Per_Capita_spent': 'col_spent', 'Rate': 'col_rate'})


def programme_detail() -> None:
    """Spending programmes (official 3-digit level) inside one area."""
    loaded = programme_data()
    if loaded is None:  # programme files not in the data folder
        st.caption(t(lang, 'detail_unavailable'))
        return
    programs, all_names = loaded
    names = conprel.program_names(all_names, year)
    area = st.selectbox(t(lang, 'detail_label'), list(spend['Category']),
                        index=None, placeholder=t(lang, 'detail_ph'),
                        format_func=lambda c: category_name(lang, c),
                        key='detail')
    if not area:
        return
    rows = conprel.programs_of(programs, code, stage, year, area)
    if rows.empty:
        st.info(t(lang, 'detail_missing'), icon=':material/info:')
        return
    detail = pd.DataFrame({
        'Category': [names.get(p, p).rstrip('.') for p in rows['Program']],
        'Amount': rows['Amount'].to_numpy()})
    detail['Share_pct'] = detail['Amount'] / detail['Amount'].sum() * 100
    detail['Per_Capita'] = detail['Amount'] / population
    st.caption(t(lang, 'detail_caption'))
    st.plotly_chart(viz.area_bars(detail, 'per_res', lang, chart_style),
                    width='stretch', config=viz.chart_config(f'detail_{area}'))
    if settings.tables:
        chart_table(detail, {'Amount': 'col_total', 'Share_pct': 'col_share',
                             'Per_Capita': 'col_per_res'})


with tab_spend:
    group = st.segmented_control(
        t(lang, 'view_by'), ['area', 'kind'], default='area', key='group',
        format_func=lambda v: t(lang, f'by_{v}')) or 'area'
    if group == 'kind':
        chapters = (bench or {}).get('ExpenseChapter', {})
        reference = {k: chapters[c] for k, c in conprel.KIND_BENCH.items()
                     if c in chapters}
        area_panel(kinds_df, 'kind_intro', 'kind_spend', 'view_kind',
                   reference, (other[0], per_res(other[2])) if other else None)
    else:
        area_panel(spend, 'spend_intro', 'kind_spend', 'view_spend',
                   (bench or {}).get('Expense'),
                   (other[0], per_res(other[1])) if other else None)
        programme_detail()
    plan_vs_spent(group)

with tab_income:
    area_panel(income, 'income_intro', 'kind_income', 'view_income',
               (bench or {}).get('Income'))

with tab_change:
    change_note = mayor_change_note(lang, spans, year, stage)
    if change_note and has_prev:
        st.info(change_note, icon=':material/how_to_vote:')
    if year_dev['Delta_pct'].notna().any():
        st.caption(t(lang, 'change_intro', prev=prev,
                     thr=pct(threshold, lang, 0)))
        st.plotly_chart(
            viz.change_bars(year_dev, threshold, lang, prev, chart_style),
            width='stretch', config=viz.chart_config(f'change_{year}'))
        if settings.tables:
            chart_table(
                year_dev.dropna(subset=['Delta_pct'])[
                    ['Category', 'Previous_Amount', 'Amount', 'Delta_pct',
                     'Flagged']],
                {'Previous_Amount': 'col_prev', 'Amount': 'col_now',
                 'Delta_pct': 'col_change', 'Flagged': 'col_flag'})
    else:
        st.info(t(lang, 'change_none', prev=prev), icon=':material/info:')
    if len(years) >= 2:
        st.subheader(t(lang, 'trend_title'))
        lines_df, folded = top_areas(deviation)
        if folded:
            st.caption(t(lang, 'trend_note'))
        st.plotly_chart(viz.trend_lines(lines_df, lang, chart_style),
                        width='stretch', config=viz.chart_config('trend'))
        if settings.tables:
            trend = lines_df.pivot_table(index='Category', columns='Year',
                                         values='Amount').reset_index()
            trend.columns = [str(c) for c in trend.columns]
            chart_table(trend, {c: 'col_now' for c in trend.columns
                                if c != 'Category'})


def share_section() -> None:
    """Summary image for social media and an embed snippet."""
    st.subheader(t(lang, 'share_title'))
    top = spend.head(4)
    biggest = top['Per_Capita'].max() or 1
    stage_word = t(lang, f'card_stage_{stage}')
    image = summary_image(
        t(lang, 'card_title', name=name, stage=stage_word, year=year),
        headline(lang, year, kpis, prev_kpis, name, stage, inflation)[1],
        money(kpis['per_capita_expenditure'], lang, 0), t(lang, 'card_label'),
        tuple((category_name(lang, c), money(v, lang, 0), v / biggest)
              for c, v in zip(top['Category'], top['Per_Capita'])),
        source_note)
    st.image(image, width=600)
    st.download_button(t(lang, 'share_image'), image,
                       file_name=f'openmunicipality_{code}_{year}.png',
                       mime='image/png', icon=':material/image:')
    parts = urlsplit(st.context.url or '')
    base = f'{parts.scheme}://{parts.netloc}{parts.path}' if parts.netloc \
        else 'https://YOUR-APP-ADDRESS'
    params = {'lang': lang, **view_params(code, st.session_state.cmp)}
    st.markdown(f"**{t(lang, 'share_embed')}**")
    st.caption(t(lang, 'share_embed_help'))
    st.code(share.embed_code(base, params, name), language='html')


source_note = t(lang, 'source_conprel', year=year,
                stage=t(lang, f'source_{stage}'))

def mayors_tab() -> None:
    """Spending per resident over time against who held the mayoralty, and
    the record of each mayoralty (budgets assigned by the rules in
    modules.mayors)."""
    if not spans:
        st.info(t(lang, 'mayors_none'), icon=':material/info:')
        return
    st.caption(t(lang, 'mayors_intro'))
    yearly = council_years(code)
    st.plotly_chart(
        viz.mayor_timeline(yearly, spans, lang, chart_style, mayors.ELECTIONS),
        width='stretch', config=viz.chart_config(f'mayors_{code}'))
    first, last = mayor_cover
    if yearly['Year'].min() < first.year or yearly['Year'].max() > last.year:
        st.caption(t(lang, 'mayors_gap', first=long_date(first, lang),
                     last=long_date(last, lang)))
    record = mayors.balance(
        spans, dict(zip(yearly['Year'], yearly['budget_per_res'])),
        dict(zip(yearly['Year'], yearly['invest_per_res'])),
        set(yearly.loc[yearly['rolled_over'], 'Year']),
        dict(zip(yearly['Year'], yearly['spent_vs_plan'])),
        cpi if real_terms else None)

    # The mayoralty of the budget shown, in one sentence
    holder = mayors.for_budget(spans, year)
    row = next((r for r, s in zip(record.itertuples(), spans)
                if s is holder), None)
    if row is not None and row.budgets:
        who = mayors.label(holder)
        if len(row.budgets) == 1:
            st.markdown(t(lang, 'mayors_now_one', who=who, y0=row.budgets[0],
                          first=money(row.first, lang, 0)))
        else:
            nominal = (row.last / row.first - 1) * 100 if row.first else None
            text = t(lang, 'mayors_now', who=who, y0=row.budgets[0],
                     y1=row.budgets[-1], first=money(row.first, lang, 0),
                     last=money(row.last, lang, 0),
                     change=pct(nominal, lang, 1, signed=True)
                     if nominal is not None else '—')
            if real_terms and pd.notna(row.change_pct):
                text += t(lang, 'mayors_now_real',
                          change=pct(row.change_pct, lang, 1, signed=True))
            st.markdown(text.replace(' %', '\u00a0%'))

    st.subheader(t(lang, 'mayors_table'))
    st.caption(t(lang, 'mayors_table_intro'))
    open_end = record['end'] >= last
    table = pd.DataFrame({
        'mayor': record['name'], 'lists': record['lists'],
        'from': [mayors.since(span, lang, long=False) for span in spans],
        'to': [short_date(d, lang) + ('*' if o else '')
               for d, o in zip(record['end'], open_end)],
        'budgets': [year_ranges(b) if b else '—' for b in record['budgets']],
        'first': record['first'], 'last': record['last'],
        'change': record['change_pct'], 'invest': record['invest'],
        'rolled': record['rolled_over'], 'spent': record['spent_pct']})
    euros = '%.0f'
    st.dataframe(table, hide_index=True, width='stretch', column_config={
        'mayor': t(lang, 'col_mayor'), 'lists': t(lang, 'col_lists'),
        'from': t(lang, 'col_from'), 'to': t(lang, 'col_to'),
        'budgets': t(lang, 'col_budgets'),
        'first': st.column_config.NumberColumn(t(lang, 'col_first'),
                                               format=euros),
        'last': st.column_config.NumberColumn(t(lang, 'col_last'),
                                              format=euros),
        'change': st.column_config.NumberColumn(
            t(lang, 'col_change_term_real' if real_terms
              else 'col_change_term'), format='%+.1f'),
        'invest': st.column_config.NumberColumn(t(lang, 'col_invest'),
                                                format=euros),
        'rolled': st.column_config.NumberColumn(t(lang, 'col_rolled'),
                                                format='%d'),
        'spent': st.column_config.NumberColumn(t(lang, 'col_spent_pct'),
                                               format='%.0f')})
    if open_end.any():
        st.caption(t(lang, 'mayors_open_end'))
    if settings.tables:  # the numbers behind the chart
        st.caption(t(lang, 'chart_table'))
        st.dataframe(pd.DataFrame({
            'Year': yearly['Year'],
            'budget': yearly['budget_per_res'],
            'spent': yearly['executed_per_res'],
            'mayor_budget': [mayors.label(m) if m else '—' for m in
                             (mayors.for_budget(spans, int(y))
                              for y in yearly['Year'])],
            'mayor_spent': [mayors.label(m) if m else '—' for m in
                            (mayors.for_outturn(spans, int(y))
                             for y in yearly['Year'])]}),
            hide_index=True, width='stretch', column_config={
                'Year': st.column_config.NumberColumn(t(lang, 'col_year'),
                                                      format='plain'),
                'budget': st.column_config.NumberColumn(
                    t(lang, 'col_planned'), format='%.2f'),
                'spent': st.column_config.NumberColumn(
                    t(lang, 'col_spent'), format='%.2f'),
                'mayor_budget': f"{t(lang, 'col_mayor')} "
                                f"({t(lang, 'legend_budget').lower()})",
                'mayor_spent': f"{t(lang, 'col_mayor')} "
                               f"({t(lang, 'legend_spent').lower()})"})
    st.caption(t(lang, 'mayors_rules'))
    st.caption(t(lang, 'source_mayors') + ' ' + source_note)


with tab_mayors:
    mayors_tab()

with tab_data:
    st.caption(t(lang, 'data_intro', year=year))
    table = df[df['Year'] == year].copy()
    table['Category'] = [category_name(lang, c) for c in table['Category']]
    table['Type'] = [t(lang, f'type_{v}') for v in table['Type']]
    st.dataframe(
        table, width='stretch', hide_index=True,
        column_config={
            'Category': t(lang, 'col_category'), 'Type': t(lang, 'col_type'),
            'Amount': st.column_config.NumberColumn(t(lang, 'col_amount'),
                                                    format='localized'),
            'Year': st.column_config.NumberColumn(t(lang, 'col_year'),
                                                  format='plain')})
    export = df[df['Year'] == year].assign(
        Category=lambda d: [category_name(lang, c) for c in d['Category']])
    st.download_button(t(lang, 'download', year=year),
                       export.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f'openmunicipality_{year}.csv', mime='text/csv',
                       icon=':material/download:')
    if spans:
        own = mayor_table[mayor_table['ine_code'] == code]
        st.download_button(t(lang, 'download_mayors'),
                           own.to_csv(index=False).encode('utf-8-sig'),
                           file_name=f'openmunicipality_{code}_mayors.csv',
                           mime='text/csv', icon=':material/download:',
                           key='download_mayors')
    st.caption(source_note)
    share_section()

with st.expander(t(lang, 'glossary_title'), icon=':material/menu_book:'):
    st.markdown(t(lang, 'glossary') + t(lang, 'glossary_extra')
                + t(lang, 'glossary_kinds')
                + (t(lang, 'glossary_mayors') if mayor_cover else ''))
st.caption(source_note)
st.caption(t(lang, 'footer'))
