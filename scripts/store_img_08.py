"""Nachigo store image #8 (full library: kana + kanji + vocabulary) -> store_img_08/store_08_library_<code>.png (1080x1920).
Needs: assets/kanatables.png and store_img_08.json (same name as this file).
Usage: python store_img_08.py            (all locales)
       python store_img_08.py en-US es-419   (only those)
Requires: python -m pip install pillow numpy arabic-reshaper python-bidi"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
try:
    from bidi import get_display
except ImportError:
    from bidi.algorithm import get_display

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = os.path.splitext(os.path.basename(__file__))[0]
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, 'assets')
DATA = os.path.join(ROOT, 'data')
OUT_DIR = os.path.join(ROOT, 'output', NAME)
os.makedirs(OUT_DIR, exist_ok=True)

FD = 'C:/Windows/Fonts/'
LATIN_BOLD = (FD + 'arialbd.ttf', 0)
LATIN_TEXT = (FD + 'arial.ttf', 0)

# (path, collection index) per language. Default: Arial.
FONTS = {
    'ja-JP': {'bold': (FD + 'YuGothB.ttc', 0), 'text': (FD + 'YuGothM.ttc', 0)},
    'ko-KR': {'bold': (FD + 'malgunbd.ttf', 0), 'text': (FD + 'malgun.ttf', 0)},
    'zh-CN': {'bold': (FD + 'msyhbd.ttc', 0), 'text': (FD + 'msyh.ttc', 0)},
    'hi-IN': {'bold': (FD + 'Nirmala.ttc', 1), 'text': (FD + 'Nirmala.ttc', 0)},
    'bn-BD': {'bold': (FD + 'Nirmala.ttc', 1), 'text': (FD + 'Nirmala.ttc', 0)},
    'ar': {'bold': (FD + 'segoeuib.ttf', 0), 'text': (FD + 'segoeui.ttf', 0)},
    'ur': {'bold': (FD + 'segoeuib.ttf', 0), 'text': (FD + 'segoeui.ttf', 0)},
}
RTL_LANGS = {'ar', 'ur'}

# font for the あ / 漢 / 語 icons (first existing one; if none exists the icons fall back to 1/2/3)
FONT_JP_CANDIDATES = [
    (FD + 'YuGothB.ttc', 0), (FD + 'meiryob.ttc', 0), (FD + 'msgothic.ttc', 0),
]

W, H = 1080, 1920
GREEN, VIOLET, BLUE = (46, 204, 113), (168, 85, 247), (21, 101, 192)
WHITE, GREY, DARK = (255, 255, 255), (190, 190, 190), (26, 26, 26)

P_X0, P_X1 = 60, 1020
P_TOP, P_H, P_GAP = 505, 152, 14
PHONE_TOP = 1030
# crop of kanatables.png (1350x2400): kana cards only, centred on the 3 columns (x 108..990)
CROP_X0, CROP_X1, CROP_Y0 = 60, 1038, 440


def load(spec, size):
    path, idx = spec
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(path, size)


def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def fit_font(d, text, spec, size, max_w, min_size=18):
    while size > min_size and d.textlength(text, font=load(spec, size)) > max_w:
        size -= 2
    return load(spec, size)


def wrap(d, text, spec, size, max_w, rtl, max_lines=2, min_size=20):
    """Wraps logical text (char wrap if no spaces); measures each candidate shaped when RTL."""
    spaced = ' ' in text
    tokens = text.split(' ') if spaced else list(text)
    sep = ' ' if spaced else ''
    while True:
        f = load(spec, size)
        meas = (lambda t: d.textlength(shape(t), font=f)) if rtl else (lambda t: d.textlength(t, font=f))
        lines, cur = [], ''
        for t in tokens:
            test = t if not cur else cur + sep + t
            if meas(test) <= max_w or not cur:
                cur = test
            else:
                lines.append(cur); cur = t
        lines.append(cur)
        if len(lines) <= max_lines or size <= min_size:
            return f, lines
        size -= 2


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.zeros((H, W, 3), np.float32) + 26
    def glow(cx, cy, r, c, k):
        a = np.clip(1 - np.sqrt((xx-cx)**2 + (yy-cy)**2) / r, 0, 1) ** 2 * k
        return a[..., None] * (np.array(c, np.float32) - 26)
    bg += glow(900, 120, 900, (30, 80, 50), 1.0)
    bg += glow(120, 1750, 800, (70, 40, 90), 1.0)
    bg += glow(540, 1200, 700, (28, 60, 42), 0.5)
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))


def find_jp_font():
    for spec in FONT_JP_CANDIDATES:
        if os.path.exists(spec[0]):
            return spec
    return None


def build(code, cfg, shot):
    fonts = FONTS.get(code, {'bold': LATIN_BOLD, 'text': LATIN_TEXT})
    bold, text = fonts['bold'], fonts['text']
    if 'font' in cfg:                                  # JSON override
        text = (cfg['font'], 0)
        bold = (cfg.get('font_bold', cfg['font']), 0)
    for p, _ in (bold, text):
        if not os.path.exists(p):
            print('font not found for', code, ':', p)
            return
    rtl = code in RTL_LANGS or bool(cfg.get('rtl'))
    tx = shape if rtl else (lambda t: t)
    anchor = 'ra' if rtl else 'la'
    jp = find_jp_font()

    img = background(); d = ImageDraw.Draw(img)
    h1, h2, sub = tx(cfg['headline'][0]), tx(cfg['headline'][1]), tx(cfg['subtitle'])
    f1 = fit_font(d, h1, bold, 112, 900)
    f2 = fit_font(d, h2, bold, 150, 900)
    d.text((W/2, 95), h1, font=f1, fill=WHITE, anchor='mt')
    d.text((W/2, 245), h2, font=f2, fill=GREEN, anchor='mt')
    f3 = fit_font(d, sub, bold, 38, 900)
    d.text((W/2, 440), sub, font=f3, fill=GREY, anchor='mt')

    # three panels: kana / kanji / vocabulary
    items = [('kana', 'あ', '1', GREEN, DARK), ('kanji', '漢', '2', VIOLET, WHITE), ('vocab', '語', '3', BLUE, WHITE)]
    for i, (key, glyph, digit, col, tcol) in enumerate(items):
        top = P_TOP + i * (P_H + P_GAP)
        d.rounded_rectangle((P_X0, top, P_X1, top + P_H), 34, fill=(34, 37, 39), outline=(66, 72, 76), width=3)
        cx = P_X1 - 70 if rtl else P_X0 + 70
        cy = top + P_H / 2
        d.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=col)
        if jp:
            d.text((cx, cy), glyph, font=load(jp, 50), fill=tcol, anchor='mm')
        else:
            d.text((cx, cy), digit, font=load(LATIN_BOLD, 44), fill=tcol, anchor='mm')
        if rtl:
            txx, tw = P_X1 - 140, (P_X1 - 140) - (P_X0 + 36)
        else:
            txx, tw = P_X0 + 140, (P_X1 - 36) - (P_X0 + 140)
        title = tx(cfg[key + '_title'])
        ft = fit_font(d, title, bold, 42, tw, 24)
        d.text((txx, top + 26), title, font=ft, fill=WHITE, anchor=anchor)
        fb, lines = wrap(d, cfg[key + '_text'], text, 29, tw, rtl, 2)
        for j, ln in enumerate(lines):
            d.text((txx, top + 82 + j * 36), tx(ln), font=fb, fill=GREY, anchor=anchor)

    # phone
    px0, px1, ptop, inset = 90, 990, PHONE_TOP, 14
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((px0-10, ptop+14, px1+10, H+300), 100, fill=(0, 0, 0, 170))
    blurred = shadow.filter(ImageFilter.GaussianBlur(28))
    img.paste(blurred, (0, 0), blurred)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((px0, ptop, px1, H + 300), 96, fill=(36, 36, 40), outline=(105, 105, 118), width=4)
    sx0, sx1, stop = px0 + inset, px1 - inset, ptop + inset
    sw, sh = sx1 - sx0, H - stop
    shot = shot.copy()
    ImageDraw.Draw(shot).rectangle((0, 430, 1350, 500), fill=(26, 26, 26))   # hide the English column headers
    scale = sw / (CROP_X1 - CROP_X0)
    crop = shot.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y0 + int(sh / scale) + 1)).resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh + 200), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))  # camera

    out = os.path.join(OUT_DIR, f'store_08_library_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'kanatables.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg, shot)