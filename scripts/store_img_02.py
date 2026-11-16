"""Nachigo store image #2 (clean features list) -> store_img_02/store_02_features_<code>.png (1080x1920).
Needs: assets/nachigo_logo.png and store_img_02.json (same name as this file).
Usage: python store_img_02.py            (all locales in the JSON)
       python store_img_02.py en-US      (only the ones you name)
Requires: python -m pip install pillow numpy arabic-reshaper python-bidi"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
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

W, H = 1080, 1920
GREEN, WHITE, GREY, PURPLE = (46, 204, 113), (255, 255, 255), (178, 186, 182), (168, 85, 247)
HIGHLIGHT = {2, 3}     # rows (0-based) drawn as accent cards: SLP and FSRS


def load(spec, size):
    path, idx = spec
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(path, size)


def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.zeros((H, W, 3), np.float32) + 26
    def glow(cx, cy, r, c, k):
        a = np.clip(1 - np.sqrt((xx-cx)**2 + (yy-cy)**2) / r, 0, 1) ** 2 * k
        return a[..., None] * (np.array(c, np.float32) - 26)
    bg += glow(900, 100, 900, (30, 80, 50), 1.0)
    bg += glow(100, 1800, 800, (70, 40, 90), 1.0)
    bg += glow(540, 260, 520, (28, 62, 44), 0.6)
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))


def fit(d, text, spec, size, max_w, floor=20):
    while size > floor and d.textlength(text, font=load(spec, size)) > max_w:
        size -= 2
    return load(spec, size)


def wrap(d, text, font, max_w, rtl):
    """Wraps the logical (unshaped) text; measures each candidate line already shaped."""
    meas = (lambda t: d.textlength(shape(t), font=font)) if rtl else (lambda t: d.textlength(t, font=font))
    cjk = ' ' not in text
    words = list(text) if cjk else text.split(' ')
    sep = '' if cjk else ' '
    lines, cur = [], ''
    for w in words:
        t = (cur + sep + w) if cur else w
        if meas(t) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def check(d, cx, cy, r):
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=GREEN)
    k = r / 42.0
    d.line([(cx-17*k, cy+1*k), (cx-5*k, cy+14*k), (cx+19*k, cy-13*k)], fill=(18, 40, 28),
           width=max(6, int(9*k)), joint='curve')


def build(code, cfg):
    fonts = FONTS.get(code, {'bold': LATIN_BOLD, 'text': LATIN_TEXT})
    bold, text = fonts['bold'], fonts['text']
    if 'font' in cfg:                                  # JSON override
        text = (cfg['font'], 0)
        bold = (cfg.get('font_bold', cfg['font']), 0)
    for p, _ in (bold, text):
        if not os.path.exists(p):
            print('font not found for', code, ':', p)
            return
    rtl = code in RTL_LANGS

    img = background(); d = ImageDraw.Draw(img)

    # logo + brand (brand name is always Latin bold)
    m = Image.open(os.path.join(ASSETS, 'nachigo_mascot.png')).convert('RGBA')
    ms = 1.3; m = m.resize((int(m.width*ms), int(m.height*ms)), Image.LANCZOS)
    img.paste(m, ((W - m.width)//2, 70), m); d = ImageDraw.Draw(img)
    fb = load(LATIN_BOLD, 124)
    wn = d.textlength('NACHI', font=fb); wg = d.textlength('GO', font=fb)
    x0 = (W - (wn + wg)) / 2
    d.text((x0, 400), 'NACHI', font=fb, fill=WHITE); d.text((x0 + wn, 400), 'GO', font=fb, fill=GREEN)

    # tagline (white part + purple part)
    a, b = cfg['tagline']
    if rtl:
        pa, pb = shape(a.strip()), shape(b.strip())
        ft = fit(d, pa + ' ' + pb, bold, 42, 900)
        wa, wb = d.textlength(pa, font=ft), d.textlength(pb, font=ft)
        sp = d.textlength(' ', font=ft)
        total = wa + sp + wb
        right = (W + total) / 2
        d.text((right - wa, 560), pa, font=ft, fill=(232, 232, 232))
        d.text((right - wa - sp - wb, 560), pb, font=ft, fill=PURPLE)
    else:
        ft = fit(d, a + b, bold, 42, 900)
        tw = d.textlength(a, font=ft) + d.textlength(b, font=ft)
        tx = (W - tw) / 2
        d.text((tx, 560), a, font=ft, fill=(232, 232, 232))
        d.text((tx + d.textlength(a, font=ft), 560), b, font=ft, fill=PURPLE)

    # feature cards
    top, ch, gap, cx0, cx1 = 665, 214, 24, 64, 1016
    icon_r, pad = 42, 38
    tx0 = cx0 + pad + icon_r*2 + 30
    avail = cx1 - 34 - tx0
    for i, f in enumerate(cfg['features']):
        y = top + i * (ch + gap)
        hi = i in HIGHLIGHT
        d.rounded_rectangle((cx0, y, cx1, y + ch), 34, fill=(26, 66, 46) if hi else (37, 43, 41),
                            outline=GREEN if hi else (62, 72, 68), width=3 if hi else 2)
        title = shape(f['title']) if rtl else f['title']
        ftit = fit(d, title, bold, 46, avail, 26)
        size = 31
        while True:
            fd = load(text, size)
            lines = wrap(d, f['desc'], fd, avail, rtl)
            if len(lines) <= 3 or size <= 20:
                break
            size -= 1
        lh = int(size * 1.35); th = 46 + 14 + lh * len(lines)
        ty = y + (ch - th) / 2
        col = (205, 232, 216) if hi else GREY
        if rtl:
            check(d, cx1 - pad - icon_r, y + ch/2, icon_r)
            rx = cx1 - pad - icon_r*2 - 30
            d.text((rx, ty), title, font=ftit, fill=WHITE, anchor='ra')
            for j, ln in enumerate(lines):
                d.text((rx, ty + 46 + 14 + j*lh), shape(ln), font=fd, fill=col, anchor='ra')
        else:
            check(d, cx0 + pad + icon_r, y + ch/2, icon_r)
            d.text((tx0, ty), title, font=ftit, fill=WHITE)
            for j, ln in enumerate(lines):
                d.text((tx0, ty + 46 + 14 + j*lh), ln, font=fd, fill=col)

    out = os.path.join(OUT_DIR, f'store_02_features_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg)