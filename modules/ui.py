"""Appearance and accessibility layer: settings, CSS and colour-mode sync."""
import json
from dataclasses import dataclass

TEXT_SCALE = {'m': 1.0, 'l': 1.15, 'xl': 1.3}
THEME_MENU_LABEL = {'auto': 'System', 'light': 'Light', 'dark': 'Dark'}


@dataclass(frozen=True)
class A11y:
    theme: str = 'auto'        # 'auto' | 'light' | 'dark'
    text: str = 'm'            # 'm' | 'l' | 'xl'
    contrast: bool = False     # high contrast
    spacing: bool = False      # WCAG 1.4.12 text spacing
    tables: bool = False       # data table under every chart

    @property
    def scale(self) -> float:
        return TEXT_SCALE.get(self.text, 1.0)


# Short query-string names, so a chosen setup can be bookmarked or shared
QUERY_KEYS = {'theme': 'theme', 'text': 'text', 'contrast': 'hc',
              'spacing': 'sp', 'tables': 'tb'}


def from_query(params) -> A11y:
    defaults = A11y()
    values = {}
    for field, key in QUERY_KEYS.items():
        raw = params.get(key)
        default = getattr(defaults, field)
        if isinstance(default, bool):
            values[field] = raw == '1' if raw is not None else default
        else:
            values[field] = raw if raw is not None else default
    if values['theme'] not in THEME_MENU_LABEL:
        values['theme'] = 'auto'
    if values['text'] not in TEXT_SCALE:
        values['text'] = 'm'
    return A11y(**values)


def to_query(settings: A11y) -> dict:
    """Only non-default values, so the default address stays clean."""
    defaults = A11y()
    out = {}
    for field, key in QUERY_KEYS.items():
        value = getattr(settings, field)
        if value != getattr(defaults, field):
            out[key] = '1' if value is True else str(value)
    return out


BASE_CSS = """
.block-container {padding-top: 3.2rem; max-width: 1180px;}
.om-brand {font-size: .95rem; opacity: .75; margin-bottom: 1.4rem;}
.om-hero {max-width: 34em; margin-bottom: 1.6rem;}
.om-hero h1 {font-size: clamp(1.7rem, 3.4vw, 2.6rem); line-height: 1.18;
              font-weight: 700; letter-spacing: -0.01em; padding: 0;
              margin: 0 0 .7rem 0; color: inherit;}
.om-hero p {font-size: 1.2rem; line-height: 1.5; opacity: .88; margin: 0;}
.om-points li {font-size: 1.05rem; line-height: 1.5; margin-bottom: .35rem;}
[data-testid="stMetricValue"] {font-variant-numeric: tabular-nums;
                               font-weight: 600;}
.stTabs [role="tab"] p {font-size: 1.02rem; font-weight: 600;}
footer {visibility: hidden;}
/* Search results read as a list: text aligned left */
[class*="st-key-pick_"] button,
[class*="st-key-pick_"] button > div {justify-content: flex-start !important;
  text-align: left !important;}
[class*="st-key-pick_"] button > div {width: 100%;}
/* Let metric labels and deltas wrap instead of being cut with "…" */
[data-testid="stMetricLabel"] *, [data-testid="stMetricDelta"] * {
  white-space: normal !important; overflow: visible !important;
  text-overflow: clip !important;}
[data-testid="stMetricValue"] * {overflow: visible !important;
  text-overflow: clip !important;}
/* Always-visible keyboard focus */
.stApp :focus-visible {outline: 3px solid #4d94ff !important;
                       outline-offset: 2px !important;}
/* Segmented controls: when the options do not fit on one line (side menu,
   phones) they wrap, and the joined segments looked cut at the corners. Each
   option is drawn as its own rounded button, with a small gap */
[data-testid="stButtonGroup"] div:has(> button) {gap: 6px !important;}
[data-testid="stButtonGroup"] button {border-radius: 8px !important;
  margin: 0 !important;}
/* Text boxes: the inner input is clipped by its frame, so its outline showed
   only as a blue bar at the start; the whole frame gets the outline instead */
.stApp input:focus-visible, .stApp textarea:focus-visible {
  outline: none !important;}
.stApp [data-baseweb="input"]:focus-within,
.stApp [data-baseweb="textarea"]:focus-within,
.stApp [data-baseweb="select"]:focus-within {
  outline: 3px solid #4d94ff !important; outline-offset: 2px !important;}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {animation-duration: 0s !important;
    transition-duration: 0s !important; scroll-behavior: auto !important;}
}
"""


def build_css(settings: A11y, dark: bool) -> str:
    css = [BASE_CSS]
    if settings.text != 'm':
        css.append(f'html {{font-size: {settings.scale * 100:.1f}% !important;}}')
    if settings.contrast:
        ink = '#ffffff' if dark else '#000000'
        css.append(f"""
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3,
[data-testid="stCaptionContainer"], [data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {{color: {ink} !important; opacity: 1 !important;}}
.om-brand, .om-hero p {{opacity: 1 !important;}}
[data-testid="stMetric"], [data-testid="stExpander"] details,
[data-testid="stVerticalBlockBorderWrapper"],
[data-baseweb="select"] > div, [data-baseweb="input"] {{
  border: 2px solid {ink} !important;}}
.stApp a {{text-decoration: underline !important;}}
.stTabs [aria-selected="true"] p {{text-decoration: underline;
  text-underline-offset: .35em; text-decoration-thickness: 3px;}}
""")
    if settings.spacing:
        css.append("""
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] p, .om-hero p, .om-points li {
  line-height: 1.6 !important; letter-spacing: .12em !important;
  word-spacing: .16em !important;}
[data-testid="stMarkdownContainer"] p {margin-bottom: 1em !important;}
[data-testid="stMetric"] p, [data-testid="stWidgetLabel"] p,
[role="tab"] p, button p {letter-spacing: normal !important;
  word-spacing: normal !important; margin-bottom: 0 !important;}
.om-hero h1 {letter-spacing: .04em !important; word-spacing: .1em !important;
              line-height: 1.35 !important;}
""")
    return '<style>' + '\n'.join(css) + '</style>'


def page_script(lang: str, theme: str) -> str:
    """Sets the page language for screen readers and, when the person picks a
    colour mode, applies it through Streamlit's own theme menu. If that menu
    ever changes, nothing breaks: the menu (⋮) still works by hand."""
    want = THEME_MENU_LABEL[theme]
    return f"""<script>
(function () {{
  const d = window.parent.document, want = {json.dumps(want)};
  d.documentElement.lang = {json.dumps(lang)};
  let stored = null;
  try {{ stored = window.parent.localStorage.getItem('om-colour-mode'); }}
  catch (e) {{}}
  const app = d.querySelector('.stApp');
  const rgb = app ? getComputedStyle(app).backgroundColor.match(/\\d+/g) : null;
  const isDark = rgb ? (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) < 128
                     : null;
  if (want === 'Dark' && isDark === true) return;
  if (want === 'Light' && isDark === false) return;
  if (want === 'System' && stored !== 'Light' && stored !== 'Dark') return;
  const menu = d.querySelector('[data-testid="stMainMenu"] button')
            || d.querySelector('[data-testid="stMainMenu"]');
  if (!menu) return;
  menu.click();
  let tries = 0;
  const pick = setInterval(function () {{
    const item = d.querySelector('[data-testid="stMainMenuItem-theme-'
                                 + want + '"]')
      || Array.from(d.querySelectorAll('[role="menuitemradio"], '
                                       + '[role="option"], [role="menuitem"]'))
           .find(function (el) {{
             return el.innerText
                    && el.innerText.trim().split('\\n').pop() === want;
           }});
    if (item || ++tries > 20) {{
      clearInterval(pick);
      if (item) {{
        item.click();
        setTimeout(function () {{  // close the menu again
          if (menu.getAttribute('aria-expanded') === 'true') menu.click();
        }}, 120);
        try {{ window.parent.localStorage.setItem('om-colour-mode', want); }}
        catch (e) {{}}
      }} else {{
        d.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Escape'}}));
      }}
    }}
  }}, 50);
}})();
</script>"""


# Landing view: only the one-sentence description and the search box, centred.
# The sidebar is hidden until a municipality has been chosen.
LANDING_CSS = """<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {display: none !important;}
.block-container {max-width: 640px !important; padding-top: 24vh !important;}
[data-testid="stMarkdownContainer"] p.om-landing {
              font-size: clamp(1.5rem, 2.8vw, 2.1rem); line-height: 1.28;
              font-weight: 600; letter-spacing: -0.005em; text-align: center;
              margin: 0 0 2rem 0; text-wrap: balance;}
.st-key-q input {font-size: 1.15rem !important; padding-top: .8rem !important;
                 padding-bottom: .8rem !important;}
.st-key-lang_switch {position: fixed; top: .9rem; right: 3.6rem; z-index: 999990;}
.st-key-lang_switch button p {font-size: .9rem; opacity: .7;}
</style>"""

