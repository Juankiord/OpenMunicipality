"""Shareable outputs: a summary image for social media and an embed snippet."""
import io
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).resolve().parents[1] / 'static' / 'fonts'
INK, INK_2, BLUE, TRACK = '#1d2433', '#52514e', '#2a78d6', '#e4e5e1'


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    weight = 700 if bold else 400
    path = FONTS / f'atkinson-hyperlegible-next-latin-{weight}-normal.ttf'
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:  # font missing: still produce a readable image
        return ImageFont.load_default(size)


def _fit(draw, text: str, font, width: int) -> str:
    """Shortens text with an ellipsis so it fits in `width` pixels."""
    if draw.textlength(text, font=font) <= width:
        return text
    while text and draw.textlength(text + '…', font=font) > width:
        text = text[:-1]
    return text.rstrip() + '…'


def summary_card(title: str, headline: str, big_value: str, big_label: str,
                 areas: list[tuple[str, str, float]], source: str) -> bytes:
    """PNG (1200×675) with the key figures. areas: (name, value text, share
    0-1 of the largest) for up to four areas."""
    width, height, pad = 1200, 675, 64
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    draw.text((pad, pad), 'OpenMunicipality', font=_font(24, True),
              fill=INK_2)
    draw.text((pad, pad + 44), _fit(draw, title, _font(46, True), width - 2 * pad),
              font=_font(46, True), fill=INK)
    draw.text((pad, pad + 110), _fit(draw, headline, _font(26), width - 2 * pad),
              font=_font(26), fill=INK_2)

    draw.text((pad, 250), big_value, font=_font(96, True), fill=INK)
    draw.text((pad, 362), big_label, font=_font(28), fill=INK_2)

    left, right, top = 560, width - pad, 250
    name_font, value_font = _font(24), _font(24, True)
    for i, (name, value, share) in enumerate(areas[:4]):
        y = top + i * 72
        draw.text((left, y), _fit(draw, name, name_font, right - left - 120),
                  font=name_font, fill=INK)
        draw.text((right, y), value, font=value_font, fill=INK, anchor='ra')
        draw.rounded_rectangle((left, y + 36, right, y + 48), 6, fill=TRACK)
        draw.rounded_rectangle(
            (left, y + 36, left + max(12, (right - left) * share), y + 48), 6,
            fill=BLUE)

    draw.line((pad, height - 92, width - pad, height - 92), fill=TRACK, width=2)
    draw.text((pad, height - 70), _fit(draw, source, _font(20), width - 2 * pad),
              font=_font(20), fill=INK_2)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()


def embed_code(base_url: str, params: dict, title: str) -> str:
    """<iframe> snippet that shows the same view without Streamlit's chrome."""
    query = '&'.join(f'{k}={v}' for k, v in {**params, 'embed': 'true'}.items())
    url = f"{base_url.rstrip('/')}/?{query}"
    return (f'<iframe src="{escape(url)}" title="{escape(title)}" '
            'width="100%" height="900" style="border:0" loading="lazy">'
            '</iframe>')
