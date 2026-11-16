"""Nachigo store image #4 (Kanji from day 1) -> store_img_04/store_04_kanji_<code>.png (1080x1920).
Needs: assets/screenshot_kanji.png and store_img_04.json (same name as this file).
Usage: python store_img_04.py            (all locales)
       python store_img_04.py en-US es-419   (only those)
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

W, H = 1080, 1920
GREEN, WHITE, GREY = (46, 204, 113), (255, 255, 255), (190, 190, 190)
BLUE, LABEL_GREY, YELLOW = (52, 152, 219), (136, 136, 136), (233, 190, 16)
MODAL_BG, STATS_BG, CHIP_FILL, CHIP_LINE = (26, 26, 26), (37, 37, 37), (38, 38, 38), (60, 60, 60)


def load(spec, size):
    path, idx = spec
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(path, size)


def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def spaced_width(d, text, font, sp):
    return sum(d.textlength(c, font=font) for c in text) + sp * max(len(text) - 1, 0)


def draw_spaced(d, x, base, text, font, fill, sp):
    if sp == 0:
        d.text((x, base), text, font=font, fill=fill, anchor='ls'); return
    for c in text:
        d.text((x, base), c, font=font, fill=fill, anchor='ls'); x += d.textlength(c, font=font) + sp


def fit_one_line(d, text, spec, size, max_w, sp, floor=18):
    while size > floor and spaced_width(d, text, load(spec, size), sp) > max_w:
        size -= 1
    return load(spec, size)


def wrap_lines(d, text, font, max_w, sp, tx):
    """Wraps logical text; measures each candidate already shaped (tx) for RTL."""
    if ' ' not in text:
        return [text]
    lines, cur = [], ''
    for w in text.split(' '):
        t = (cur + ' ' + w) if cur else w
        if spaced_width(d, tx(t), font, sp) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def patch(shot, cfg, f_reg, f_bold, rtl):
    tx = shape if rtl else (lambda t: t)
    s = shot.copy(); d = ImageDraw.Draw(s)
    sp = 0 if rtl else cfg.get('letter_spacing', 5)
    L = cfg['labels']
    # MEANINGS heading
    d.rectangle((110, 958, 1000, 1004), fill=MODAL_BG)
    t = tx(L['meanings'])
    f = fit_one_line(d, t, f_bold, 33, 1080, sp)
    draw_spaced(d, 123, 993, t, f, BLUE, sp)
    # meaning chips (redrawn, sized to the text)
    d.rectangle((110, 1046, 1240, 1158), fill=MODAL_BG)
    chips = [tx(c) for c in cfg['chips']]
    size = 49
    while True:
        f = load(f_reg, size)
        widths = [int(d.textlength(t, font=f)) + 70 for t in chips]
        if sum(widths) + 24 * (len(widths) - 1) <= 1110 or size <= 24:
            break
        size -= 1
    x = 120
    for t, w in zip(chips, widths):
        d.rounded_rectangle((x, 1057, x + w, 1147), 20, fill=CHIP_FILL, outline=CHIP_LINE, width=2)
        d.text((x + 36, 1122), t, font=f, fill=(238, 238, 238), anchor='ls')
        x += w + 24
    # KUN heading (left column, up to 2 lines) / ON heading (right column, 1 line)
    d.rectangle((110, 1160, 690, 1256), fill=MODAL_BG)
    size = 33
    while True:
        f = load(f_bold, size)
        lines = wrap_lines(d, L['kun'], f, 527, sp, tx)
        if len(lines) <= 2 and all(spaced_width(d, tx(ln), f, sp) <= 527 for ln in lines) or size <= 18:
            break
        size -= 1
    bases = [1240] if len(lines) == 1 else [1194, 1240]
    for ln, b in zip(lines, bases):
        draw_spaced(d, 123, b, tx(ln), f, BLUE, sp)
    d.rectangle((690, 1160, 1250, 1210), fill=MODAL_BG)
    t = tx(L['on'])
    f = fit_one_line(d, t, f_bold, 33, 527, sp)
    draw_spaced(d, 701, 1194, t, f, BLUE, sp)
    # stats labels
    for key, (x0, x1, base) in {'strokes': (696, 1190, 1506), 'grade': (159, 640, 1636),
                                 'frequency': (696, 1190, 1636), 'heisig': (161, 1180, 1792)}.items():
        d.rectangle((x0 - 10, base - 30, x1, base + 8), fill=STATS_BG)
        t = tx(L[key])
        f = fit_one_line(d, t, f_bold, 30, x1 - x0, 0)
        d.text((x0, base), t, font=f, fill=LABEL_GREY, anchor='ls')
    # yellow Heisig keyword
    d.rectangle((150, 1804, 1190, 1852), fill=STATS_BG)
    t = tx(cfg['keyword'])
    f = fit_one_line(d, t, f_reg, 39, 1000, 0)
    d.text((160, 1840), t, font=f, fill=YELLOW, anchor='ls')
    return s


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


def fit_font(d, text, spec, size, max_w):
    while size > 20 and d.textlength(text, font=load(spec, size)) > max_w:
        size -= 2
    return load(spec, size)


def build(code, cfg, shot):
    fonts = FONTS.get(code, {'bold': LATIN_BOLD, 'text': LATIN_TEXT})
    f_bold, f_reg = fonts['bold'], fonts['text']
    if 'font' in cfg:                                  # JSON override
        f_reg = (cfg['font'], 0)
        f_bold = (cfg.get('font_bold', cfg['font']), 0)
    for p, _ in (f_bold, f_reg):
        if not os.path.exists(p):
            print('font not found for', code, ':', p)
            return
    rtl = code in RTL_LANGS
    tx = shape if rtl else (lambda t: t)

    img = background(); d = ImageDraw.Draw(img)
    h1, h2, sub = tx(cfg['headline'][0]), tx(cfg['headline'][1]), tx(cfg['subtitle'])
    f1 = fit_font(d, h1, f_bold, 112, 900); f2 = fit_font(d, h2, f_bold, 150, 900)
    d.text((W/2, 95), h1, font=f1, fill=WHITE, anchor='mt')
    d.text((W/2, 245), h2, font=f2, fill=GREEN, anchor='mt')
    f3 = fit_font(d, sub, f_bold, 38, 940)
    d.text((W/2, 452), sub, font=f3, fill=GREY, anchor='mt')

    px0, px1, ptop, inset = 90, 990, 600, 14
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((px0-10, ptop+14, px1+10, H+300), 100, fill=(0, 0, 0, 170))
    blurred = shadow.filter(ImageFilter.GaussianBlur(28)); img.paste(blurred, (0, 0), blurred)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((px0, ptop, px1, H + 300), 96, fill=(36, 36, 40), outline=(105, 105, 118), width=4)
    sx0, sx1, stop = px0 + inset, px1 - inset, ptop + inset
    sw, sh = sx1 - sx0, H - stop
    patched = patch(shot, cfg, f_reg, f_bold, rtl)
    cx0, cx1, cy0 = 20, 1330, 250
    scale = sw / (cx1 - cx0)
    crop = patched.crop((cx0, cy0, cx1, cy0 + int(sh / scale) + 1)).resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh + 200), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))

    out = os.path.join(OUT_DIR, f'store_04_kanji_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'screenshot_kanji.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg, shot)