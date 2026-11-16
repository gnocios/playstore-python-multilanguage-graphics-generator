"""Nachigo Google Play feature graphic (1024x500) generator.
Needs next to this file: nachigo_mascot.png and banner_img.json (texts of all languages).
Run (Windows):   python banner_img.py        -> banner_img/banner_img_<code>.png
Requires:        python -m pip install pillow numpy arabic-reshaper python-bidi"""
import os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
try:
    from bidi import get_display
except ImportError:
    from bidi.algorithm import get_display

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, 'output', os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1024, 500
FONT_CANDIDATES = [
    'C:/Windows/Fonts/arialbd.ttf',
    'C:/Windows/Fonts/segoeuib.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
]
FONT = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT is None:
    raise SystemExit('No bold font found: edit FONT_CANDIDATES in this file with the path of a .ttf bold font.')
WHITE, GREEN, PURPLE, SOFT = (255, 255, 255), (46, 204, 113), (168, 85, 247), (232, 232, 232)

# font per language (Windows). A "font" key inside the JSON entry overrides these.
FONT_BY_LANG = {
    'ja-JP': 'C:/Windows/Fonts/YuGothB.ttc',
    'ko-KR': 'C:/Windows/Fonts/malgunbd.ttf',
    'zh-CN': 'C:/Windows/Fonts/msyhbd.ttc',
    'hi-IN': 'C:/Windows/Fonts/Nirmala.ttc',
    'bn-BD': 'C:/Windows/Fonts/Nirmala.ttc',
    'ar': 'C:/Windows/Fonts/segoeuib.ttf',
    'ur': 'C:/Windows/Fonts/segoeuib.ttf',
}
RTL_LANGS = {'ar', 'ur'}

LANGS = json.load(open(os.path.join(ROOT, 'data', 'banner_img.json'), encoding='utf-8'))

def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.zeros((H, W, 3), np.float32) + 26
    def glow(cx, cy, r, color, k):
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        a = np.clip(1 - d / r, 0, 1) ** 2 * k
        return a[..., None] * (np.array(color, np.float32) - 26)
    bg += glow(850, 60, 520, (30, 80, 50), 1.0)
    bg += glow(130, 470, 480, (70, 40, 90), 1.0)
    return bg


def fit(draw, text_parts, path, size, max_w, min_size=14):
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if sum(draw.textlength(t, font=f) for t in text_parts) <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, min_size)


def build(code, cfg):
    path = cfg.get('font') or FONT_BY_LANG.get(code, FONT)
    if not os.path.exists(path):
        print('font not found for', code, ':', path)
        return
    rtl = code in RTL_LANGS

    mascot = Image.open(os.path.join(ROOT, 'assets', 'nachigo_mascot.png')).convert('RGBA')
    base = Image.fromarray(np.clip(background(), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)

    TEXT_W = 625
    GAP = 6
    CIRCLE_W = 212
    group_w = CIRCLE_W + GAP + 40 + TEXT_W
    left = (W - group_w) // 2
    tx = left + CIRCLE_W + GAP + 40
    if rtl:
        mx = W - left - CIRCLE_W - 44     # mascot mirrored to the right side
        edge = W - tx                      # right edge of the text column
    else:
        mx = left - 44
        edge = None

    base.paste(mascot, (mx, (H - mascot.size[1]) // 2 + 2), mascot)

    # title
    ft = fit(d, ['NACHIGO'], FONT, 112, TEXT_W)
    top = 128
    wn = d.textlength('NACHI', font=ft)
    wg = d.textlength('GO', font=ft)
    if rtl:
        x_n = edge - wg - wn
        d.text((x_n, top), 'NACHI', font=ft, fill=WHITE)
        d.text((x_n + wn, top), 'GO', font=ft, fill=GREEN)
    else:
        d.text((tx, top), 'NACHI', font=ft, fill=WHITE)
        d.text((tx + wn, top), 'GO', font=ft, fill=GREEN)

    # subtitle
    sy = 262
    if rtl:
        p0, p1 = [shape(p.strip()) for p in cfg['sub']]
        fs = fit(d, [p0, ' ', p1], path, 40, TEXT_W)
        w0 = d.textlength(p0, font=fs)
        w1 = d.textlength(p1, font=fs)
        sp = d.textlength(' ', font=fs)
        d.text((edge - 2 - w0, sy), p0, font=fs, fill=SOFT)
        d.text((edge - 2 - w0 - sp - w1, sy), p1, font=fs, fill=PURPLE)
    else:
        fs = fit(d, list(cfg['sub']), path, 40, TEXT_W)
        d.text((tx + 2, sy), cfg['sub'][0], font=fs, fill=SOFT)
        d.text((tx + 2 + d.textlength(cfg['sub'][0], font=fs), sy), cfg['sub'][1], font=fs, fill=PURPLE)

    # chips
    chips = [shape(t) for t in cfg['chips']] if rtl else list(cfg['chips'])
    padx, gap, h, y = 18, 10, 46, 334
    size = 24
    while True:
        fc = ImageFont.truetype(path, size)
        widths = [int(d.textlength(t, font=fc)) + padx * 2 for t in chips]
        if sum(widths) + gap * (len(widths) - 1) <= TEXT_W or size <= 14:
            break
        size -= 1

    if rtl:
        xr = edge - 2
        for t, w in zip(chips, widths):
            d.rounded_rectangle((xr - w, y, xr, y + h), radius=h // 2, fill=(24, 62, 42),
                                outline=(37, 120, 78), width=2)
            d.text((xr - padx, y + h // 2), t, font=fc, fill=GREEN, anchor='rm')
            xr -= w + gap
    else:
        x = tx + 2
        for t, w in zip(chips, widths):
            d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=(24, 62, 42),
                                outline=(37, 120, 78), width=2)
            d.text((x + padx, y + h // 2), t, font=fc, fill=GREEN, anchor='lm')
            x += w + gap

    out = os.path.join(OUT_DIR, f'banner_img_{code}.png')
    base.save(out, optimize=True)
    print('saved', out)


if __name__ == '__main__':
    print('font:', FONT)
    for c, cfg in LANGS.items():
        build(c, cfg)