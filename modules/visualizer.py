"""Plotly chart builders with a shared, accessible visual style.

Every colour depends on the active mode (light/dark, normal/high contrast);
data colours come from palettes validated for colour-vision deficiency on
each background.
"""
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go

from modules.i18n import category_name, money, money_compact, pct, t

FONT = ('"Atkinson Hyperlegible Next", "Atkinson Hyperlegible", system-ui, '
        '-apple-system, "Segoe UI", sans-serif')
MID_GREY = '#8a8f98'  # reference lines, readable on both backgrounds

PALETTES = {
    # mode: (single-series / "goes up", "goes down", categorical order)
    'light': ('#2a78d6', '#e34948',
              ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4',
               '#008300', '#6250d6', '#e34948']),
    'dark': ('#3987e5', '#e66767',
             ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181',
              '#008300', '#9085e9', '#e66767']),
    # High contrast: darker validated ramp steps on light; dark mode already
    # clears 3:1, so it gains outlines and thicker lines instead.
    'light_hc': ('#1c5cab', '#d03b3b',
                 ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4',
                  '#008300', '#6250d6', '#e34948']),
    'dark_hc': ('#3987e5', '#e66767',
                ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181',
                 '#008300', '#9085e9', '#e66767']),
}


@dataclass(frozen=True)
class ChartStyle:
    dark: bool = False
    scale: float = 1.0
    contrast: bool = False

    @property
    def palette(self):
        return PALETTES[('dark' if self.dark else 'light')
                        + ('_hc' if self.contrast else '')]

    def size(self, base: float) -> int:
        return round(base * self.scale)

    @property
    def ink(self) -> str:
        if self.contrast:
            return '#ffffff' if self.dark else '#000000'
        return '#e9ebef' if self.dark else '#1d2433'

    @property
    def ink_2(self) -> str:
        if self.contrast:
            return self.ink
        return '#b4b9c2' if self.dark else '#52514e'

    @property
    def grid(self) -> str:
        return '#2c323d' if self.dark else '#e4e5e1'

    @property
    def outline(self) -> dict:
        """Bar outline in the text colour when high contrast is on."""
        if not self.contrast:
            return dict(width=0)
        return dict(width=2, color='#ffffff' if self.dark else '#000000')


def _style(fig: go.Figure, height: int, style: ChartStyle) -> go.Figure:
    fig.update_layout(
        height=round(height * style.scale), margin=dict(l=8, r=24, t=8, b=8),
        font=dict(family=FONT, size=style.size(15), color=style.ink),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor='#1e232c' if style.dark else '#ffffff',
                        bordercolor=style.grid,
                        font=dict(family=FONT, size=style.size(14),
                                  color=style.ink)),
        barcornerradius=4, showlegend=False)
    fig.update_xaxes(zeroline=False, gridcolor=style.grid,
                     tickfont=dict(size=style.size(13), color=style.ink_2))
    fig.update_yaxes(zeroline=False, gridcolor=style.grid,
                     tickfont=dict(size=style.size(15), color=style.ink))
    return fig


def chart_config(filename: str) -> dict:
    """Plotly toolbar reduced to the 'download as PNG' button."""
    return {'displaylogo': False, 'modeBarButtons': [['toImage']],
            'toImageButtonOptions': {'filename': filename, 'scale': 2}}


def area_bars(breakdown: pd.DataFrame, view: str, lang: str,
              style: ChartStyle = ChartStyle(),
              benchmark: dict | None = None,
              compare: tuple[str, dict] | None = None,
              own_name: str | None = None) -> go.Figure:
    """Horizontal bars, largest on top. view: 'per_res' | 'total' | 'share'.
    benchmark: Category -> usual euros per resident in municipalities of a
    similar size, drawn as a reference tick in the per-resident view.
    compare: (name, Category -> euros per resident) drawn as a second bar;
    own_name labels the main bars (default: 'This council')."""
    data = breakdown.sort_values('Amount')
    names = [category_name(lang, c) for c in data['Category']]
    if view == 'per_res':
        x = data['Per_Capita']
        labels = [money(v, lang, 0) for v in x]
    elif view == 'share':
        x = data['Share_pct']
        labels = [money(round(v), lang, 0) for v in x]
    else:
        x = data['Amount']
        labels = [money_compact(v, lang) for v in x]
    hover = [[money_compact(a, lang), money(round(s), lang, 0),
              money(p, lang)] for a, s, p in
             zip(data['Amount'], data['Share_pct'], data['Per_Capita'])]

    fig = go.Figure(go.Bar(
        x=x, y=names, orientation='h',
        marker=dict(color=style.palette[0], line=style.outline),
        text=labels, textposition='outside', cliponaxis=False,
        textfont=dict(color=style.ink), customdata=hover,
        hovertemplate=(f'<b>%{{y}}</b><br>{t(lang, "hover_total")}: '
                       f'%{{customdata[0]}}<br>{t(lang, "hover_share")}: '
                       f'%{{customdata[1]}}<br>{t(lang, "hover_per_res")}: '
                       '%{customdata[2]}<extra></extra>')))
    fig = _style(fig, 70 + 46 * len(data), style)
    top = x.max() if len(x) else 1
    if compare and view == 'per_res':
        # Second municipality as a second bar in each area (validated
        # categorical slots 1 and 2), both labelled and in the legend
        other_name, other = compare
        values = [other.get(c, 0.0) for c in data['Category']]
        fig.data[0].name = own_name or t(lang, 'this_council')
        fig.add_trace(go.Bar(
            x=values, y=names, orientation='h', name=other_name,
            marker=dict(color=style.palette[2][1], line=style.outline),
            text=[money(v, lang, 0) for v in values], textposition='outside',
            cliponaxis=False, textfont=dict(color=style.ink),
            hovertemplate=(f'<b>%{{y}}</b><br>{other_name}: %{{x:,.0f}} €'
                           '<extra></extra>')))
        # Horizontal groups draw the first trace lowest: put this council on
        # top of each pair and keep it first in the legend
        fig.data = (fig.data[1], fig.data[0])
        fig.update_layout(barmode='group', showlegend=True,
                          height=round((70 + 74 * len(data)) * style.scale),
                          margin=dict(t=style.size(44)),
                          legend=dict(orientation='h', x=0, y=1,
                                      yanchor='bottom', traceorder='reversed',
                                      font=dict(size=style.size(13),
                                                color=style.ink_2)))
        top = max(top, max(values, default=0))
        benchmark = None
    if benchmark and view == 'per_res':
        ref = [benchmark.get(c, 0.0) for c in data['Category']]
        fig.data[0].name = t(lang, 'this_council')
        fig.add_trace(go.Scatter(
            x=ref, y=names, mode='markers', name=t(lang, 'bench_legend'),
            marker=dict(symbol='line-ns', size=style.size(24), color=style.ink,
                        line=dict(width=3, color=style.ink)),
            customdata=[money(v, lang, 0) for v in ref],
            hovertemplate=(f'<b>%{{y}}</b><br>{t(lang, "bench_legend")}: '
                           '%{customdata}<extra></extra>')))
        # Value labels move past the reference tick so the two never overlap
        fig.data[0].text = None
        fig.add_trace(go.Scatter(
            x=[max(v, r) for v, r in zip(x, ref)], y=names, mode='text',
            text=['  ' + label for label in labels], textposition='middle right',
            textfont=dict(color=style.ink, size=style.size(15)),
            showlegend=False, hoverinfo='skip', cliponaxis=False))
        fig.update_layout(showlegend=True, margin=dict(t=style.size(44)),
                          legend=dict(orientation='h', x=0, y=1, yanchor='bottom',
                                      font=dict(size=style.size(13),
                                                color=style.ink_2)))
        top = max(top, max(ref, default=0))
    fig.update_xaxes(showticklabels=False, showgrid=False,
                     range=[0, top * 1.22])
    return fig.update_layout(bargap=0.32)


def change_bars(year_dev: pd.DataFrame, threshold: float, lang: str,
                prev: int, style: ChartStyle = ChartStyle()) -> go.Figure:
    """Diverging bars of year-on-year change (%) with the flag threshold.
    Rises and falls also differ in direction and sign, not only in colour."""
    up, down, _ = style.palette
    data = year_dev.dropna(subset=['Delta_pct']).sort_values('Delta_pct')
    names = [category_name(lang, c) for c in data['Category']]
    labels = [pct(v, lang, signed=True) + ('  ⚑' if f else '')
              for v, f in zip(data['Delta_pct'], data['Flagged'])]
    hover = [[money_compact(p, lang), money_compact(a, lang)]
             for p, a in zip(data['Previous_Amount'], data['Amount'])]
    marker = dict(color=[up if v >= 0 else down for v in data['Delta_pct']],
                  line=style.outline)
    fig = go.Figure(go.Bar(
        x=data['Delta_pct'], y=names, orientation='h', marker=marker,
        text=labels, textposition='outside', cliponaxis=False,
        textfont=dict(color=style.ink), customdata=hover,
        hovertemplate=(f'<b>%{{y}}</b><br>{prev}: %{{customdata[0]}}<br>'
                       '→ %{customdata[1]}<extra></extra>')))
    fig = _style(fig, 90 + 52 * len(data), style)
    limit = max(data['Delta_pct'].abs().max(), threshold) * 1.4
    for x in (-threshold, threshold):
        fig.add_vline(x=x, line=dict(color=MID_GREY, width=1, dash='dot'))
    fig.add_vline(x=0, line=dict(color=MID_GREY, width=1.5))
    fig.update_layout(separators=',.' if lang == 'es' else '.,')
    fig.update_xaxes(range=[-limit, limit],
                     ticksuffix='%' if lang == 'en' else ' %',
                     title=dict(text=t(lang, 'axis_change', prev=prev),
                                font=dict(size=style.size(13),
                                          color=style.ink_2)))
    return fig.update_layout(bargap=0.35)


def trend_lines(deviation: pd.DataFrame, lang: str,
                style: ChartStyle = ChartStyle()) -> go.Figure:
    """One line per area over the years, colour fixed per area and labelled
    directly at its last point."""
    series = style.palette[2]
    fig = go.Figure()
    categories = sorted(c for c in deviation['Category'].unique()
                        if c != 'OTHER')
    if 'OTHER' in set(deviation['Category']):
        categories.append('OTHER')  # folded areas: last and in grey
    ends = []
    first, last = int(deviation['Year'].min()), int(deviation['Year'].max())
    all_years = pd.Index(range(first, last + 1), name='Year')
    for i, cat in enumerate(categories):
        # Years without data stay empty, so the line breaks instead of
        # drawing a straight segment over the gap
        rows = (deviation[deviation['Category'] == cat]
                .groupby('Year')['Amount'].sum().reindex(all_years)
                .reset_index())
        color = MID_GREY if cat == 'OTHER' else series[i % len(series)]
        name = category_name(lang, cat)
        fig.add_trace(go.Scatter(
            x=rows['Year'], y=rows['Amount'], name=name, mode='lines+markers',
            line=dict(color=color, width=3 if style.contrast else 2),
            marker=dict(size=style.size(10), color=color,
                        line=style.outline),
            connectgaps=False,
            customdata=[money_compact(v, lang) if pd.notna(v) else ''
                        for v in rows['Amount']],
            hovertemplate=f'<b>{name}</b> %{{x}}: %{{customdata}}<extra></extra>'))
        known = rows.dropna(subset=['Amount'])
        ends.append([known['Amount'].iloc[-1], known['Year'].iloc[-1], name])

    # Direct labels at the last point, nudged apart so they never overlap
    span = deviation['Amount'].max() - deviation['Amount'].min() or 1
    gap = span * 0.07 * style.scale
    ends.sort()
    for k in range(1, len(ends)):
        ends[k][0] = max(ends[k][0], ends[k - 1][0] + gap)
    for y, x, name in ends:
        fig.add_annotation(x=x, y=y, text=name, xanchor='left', xshift=12,
                           showarrow=False,
                           font=dict(size=style.size(13), color=style.ink))
    fig = _style(fig, 440, style)
    fig.update_layout(showlegend=True,
                      separators=',.' if lang == 'es' else '.,',
                      margin=dict(r=round((24 + 7.6 * max(len(e[2]) for e in ends))
                                          * style.scale), t=10))
    # Legend below the year labels, with room for every row of entries
    rows = (len(categories) + 1) // 2
    bottom = round((90 + 26 * rows) * style.scale)
    height = round(380 * style.scale) + bottom
    plot_height = height - bottom - 10
    fig.update_layout(height=height, margin=dict(b=bottom),
                      legend=dict(orientation='h', x=0, yanchor='top',
                                  y=-round(70 * style.scale) / plot_height,
                                  font=dict(size=style.size(13))))
    span = last - first
    fig.update_xaxes(range=[first - 0.4, last + 0.4], tickangle=0,
                     dtick=1 if span <= 8 else 2 if span <= 16 else 5,
                     showgrid=False)
    return fig.update_yaxes(title=dict(text=t(lang, 'axis_eur'),
                                       font=dict(size=style.size(13),
                                                 color=style.ink_2)))


def mayor_timeline(years: pd.DataFrame, spans: list[dict], lang: str,
                   style: ChartStyle = ChartStyle(),
                   elections: dict | None = None) -> go.Figure:
    """Planned (and spent) spending per resident over time on top of who
    held the mayoralty. Each mayoralty is a band in alternating neutral
    greys, so no party gets a colour; the budget point sits on 1 January
    (the rule that assigns it) and the outturn point in mid-year."""
    from datetime import date
    from modules.mayors import label, short_name
    from modules.mayors import for_budget, for_outturn

    planned, spent_color = style.palette[0], style.palette[2][1]
    first, last = int(years['Year'].min()), int(years['Year'].max())
    x_min, x_max = date(first, 1, 1), date(last, 12, 31)
    fig = go.Figure()
    shade = ('rgba(255,255,255,{a})' if style.dark else 'rgba(29,36,51,{a})')
    shown = [s for s in spans if s['end'] >= x_min and s['start'] <= x_max]
    for i, span in enumerate(shown):
        x0, x1 = max(span['start'], x_min), min(span['end'], x_max)
        fig.add_vrect(x0=x0, x1=x1, layer='below', line_width=0,
                      fillcolor=shade.format(a=0.10 if i % 2 else 0.04))
        if i:  # a thin edge where one mayoralty follows another
            fig.add_vline(x=x0, layer='below',
                          line=dict(color=shade.format(a=0.35), width=1))
        if (x1 - x0).days >= 2.5 * 365:  # room for a label
            words = short_name(span['name']).split()
            middle = (len(words) + 1) // 2
            fig.add_annotation(
                x=x0 + (x1 - x0) / 2, y=1, yref='paper', yanchor='bottom',
                text=(' '.join(words[:middle]) + '<br>'
                      + ' '.join(words[middle:])),
                showarrow=False,
                font=dict(size=style.size(12), color=style.ink_2))
    for year, day in (elections or {}).items():
        if x_min <= day <= x_max:
            fig.add_vline(x=day, line=dict(color=MID_GREY, width=1,
                                           dash='dot'))
            # Upright along the line, so labels never collide on phones
            fig.add_annotation(x=day, y=0.02, yref='paper', yanchor='bottom',
                               xanchor='left', xshift=2, textangle=-90,
                               text=t(lang, 'election', year=year),
                               showarrow=False,
                               font=dict(size=style.size(11),
                                         color=style.ink_2))

    def who(span) -> str:
        return label(span) if span else '—'

    series = [('budget_per_res', 'legend_budget', planned, 'solid',
               lambda y: date(y, 1, 1), for_budget),
              ('executed_per_res', 'legend_spent', spent_color, 'dash',
               lambda y: date(y, 7, 1), for_outturn)]
    for column, name_key, color, dash, place, rule in series:
        rows = years.dropna(subset=[column])
        if rows.empty:
            continue
        name = t(lang, name_key)
        # Gaps break the line instead of joining distant years
        xs, ys, hover = [], [], []
        previous = None
        for year, value in zip(rows['Year'], rows[column]):
            if previous is not None and year - previous > 1:
                xs.append(None)
                ys.append(None)
                hover.append(['', ''])
            xs.append(place(int(year)))
            ys.append(value)
            hover.append([f'{name} {year}: {money(value, lang, 0)}',
                          who(rule(spans, int(year)))])
            previous = year
        fig.add_trace(go.Scatter(
            x=xs, y=ys, name=name, mode='lines+markers',
            line=dict(color=color, width=3 if style.contrast else 2,
                      dash=dash),
            marker=dict(size=style.size(9), color=color, line=style.outline,
                        symbol='circle' if dash == 'solid' else 'diamond'),
            customdata=hover,
            hovertemplate=('%{customdata[0]}<br>'
                           f"{t(lang, 'hover_mayor')}: %{{customdata[1]}}"
                           '<extra></extra>')))
    fig = _style(fig, 420, style)
    fig.update_layout(showlegend=True, separators=',.' if lang == 'es'
                      else '.,', margin=dict(t=round(44 * style.scale)),
                      legend=dict(orientation='h', x=0, y=-0.12,
                                  yanchor='top',
                                  font=dict(size=style.size(13))))
    fig.update_xaxes(range=[x_min, x_max], showgrid=False, dtick='M24',
                     tickformat='%Y')
    return fig.update_yaxes(rangemode='tozero', title=dict(
        text=t(lang, 'axis_per_res'),
        font=dict(size=style.size(13), color=style.ink_2)))
