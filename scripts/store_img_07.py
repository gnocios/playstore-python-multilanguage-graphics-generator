"""Nachigo store image #7 (happy path / daily flow) -> store_img_07/store_07_flow_<code>.png (1080x1920).
Needs: assets/happy_path.png and store_img_07.json (same name as this file).
Usage: python store_img_07.py            (all locales)
       python store_img_07.py en-US es-419   (only those)
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
GREEN, VIOLET = (46, 204, 113), (168, 85, 247)
WHITE, GREY, DARK = (255, 255, 255), (190, 190, 190), (26, 26, 26)

# the 10 cards of the screenshot (1350x2400), row by row, 2 columns
ORDER = ['父', '母', '従姉妹', '姉妹', '祖父', '祖母', '妻', '夫', '娘', '息子']
CARD_X = (144, 694)
CARD_Y = (1087, 1363, 1639, 1915, 2191)
CARD_W, CARD_H = 513, 240
CARD_BG = (45, 52, 54)
MEAN_SIZE, MEAN_BASELINE = 35, 185

# layout of the final image
P_X0, P_X1 = 60, 1020
P1_TOP, P1_H = 520, 200
P2_TOP, P2_H = 740, 268
PHONE_TOP = 1040


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


def wrap(d, text, spec, size, max_w, rtl, max_lines=2, min_size=22):
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


def patch_screenshot(shot, meanings, spec, rtl):
    tx = shape if rtl else (lambda t: t)
    shot = shot.copy(); d = ImageDraw.Draw(shot)
    for i, kanji in enumerate(ORDER):
        x, y = CARD_X[i % 2], CARD_Y[i // 2]
        d.rectangle((x + 10, y + 146, x + CARD_W - 10, y + 212), fill=CARD_BG)    # erase old meaning
        text = tx(meanings[kanji])
        f = fit_font(d, text, spec, MEAN_SIZE, CARD_W - 40, 18)
        d.text((x + CARD_W / 2, y + MEAN_BASELINE), text, font=f, fill=WHITE, anchor='ms')
    return shot


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


def draw_lines(d, lines, f, x, y, fill, rtl, lh):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), shape(ln) if rtl else ln, font=f, fill=fill, anchor='ra' if rtl else 'la')


def panel_frame(d, top, h, num, color, num_color, rtl):
    d.rounded_rectangle((P_X0, top, P_X1, top + h), 34, fill=(34, 37, 39), outline=(66, 72, 76), width=3)
    cx = P_X1 - 56 if rtl else P_X0 + 56
    cy = top + 54
    d.ellipse((cx - 32, cy - 32, cx + 32, cy + 32), fill=color)
    d.text((cx, cy + 1), str(num), font=load(LATIN_BOLD, 38), fill=num_color, anchor='mm')


def text_box(rtl):
    if rtl:
        return P_X1 - 112, (P_X1 - 112) - (P_X0 + 36)
    return P_X0 + 112, (P_X1 - 36) - (P_X0 + 112)


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

    img = background(); d = ImageDraw.Draw(img)
    h1, h2, sub = tx(cfg['headline'][0]), tx(cfg['headline'][1]), tx(cfg['subtitle'])
    f1 = fit_font(d, h1, bold, 112, 900)
    f2 = fit_font(d, h2, bold, 150, 900)
    d.text((W/2, 95), h1, font=f1, fill=WHITE, anchor='mt')
    d.text((W/2, 245), h2, font=f2, fill=GREEN, anchor='mt')
    f3 = fit_font(d, sub, bold, 38, 900)
    d.text((W/2, 440), sub, font=f3, fill=GREY, anchor='mt')

    txx, tw = text_box(rtl)
    # panel 1: right order
    panel_frame(d, P1_TOP, P1_H, 1, GREEN, DARK, rtl)
    t1 = tx(cfg['p1_title'])
    ft = fit_font(d, t1, bold, 44, tw, 26)
    d.text((txx, P1_TOP + 26), t1, font=ft, fill=WHITE, anchor=anchor)
    fb, lines = wrap(d, cfg['p1_text'], text, 30, tw, rtl, 2)
    draw_lines(d, lines, fb, txx, P1_TOP + 88, GREY, rtl, 40)

    # panel 2: daily cycle
    panel_frame(d, P2_TOP, P2_H, 2, VIOLET, WHITE, rtl)
    t2 = tx(cfg['p2_title'])
    ft = fit_font(d, t2, bold, 44, tw, 26)
    d.text((txx, P2_TOP + 26), t2, font=ft, fill=WHITE, anchor=anchor)
    fb, lines = wrap(d, cfg['p2_text'], text, 30, tw, rtl, 2)
    draw_lines(d, lines, fb, txx, P2_TOP + 88, GREY, rtl, 40)
    # 3 steps
    gap = 48; cx0, cx1 = P_X0 + 36, P_X1 - 36
    cw = (cx1 - cx0 - 2 * gap) // 3; cy0 = P2_TOP + 176; ch = 66
    styles = [((30, 64, 44), GREEN, WHITE), ((58, 40, 80), VIOLET, WHITE), (GREEN, GREEN, DARK)]
    for i in range(3):
        slot = 2 - i if rtl else i
        x0 = cx0 + slot * (cw + gap)
        fill, outline, tcol = styles[i]
        d.rounded_rectangle((x0, cy0, x0 + cw, cy0 + ch), 22, fill=fill, outline=outline, width=3)
        step = tx(cfg['steps'][i])
        fs = fit_font(d, step, bold, 30, cw - 24, 16)
        d.text((x0 + cw / 2, cy0 + ch / 2), step, font=fs, fill=tcol, anchor='mm')
        if i < 2:   # chevron between chips
            gx = (x0 - gap / 2) if rtl else (x0 + cw + gap / 2)
            gy = cy0 + ch / 2; s = -1 if rtl else 1
            d.line([(gx - 6 * s, gy - 13), (gx + 6 * s, gy), (gx - 6 * s, gy + 13)], fill=GREY, width=5, joint='curve')

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
    patched = patch_screenshot(shot, cfg['meanings'], text, rtl)
    crop_x0, crop_x1, crop_y0 = 90, 1260, 1077
    scale = sw / (crop_x1 - crop_x0)
    crop = patched.crop((crop_x0, crop_y0, crop_x1, crop_y0 + int(sh / scale) + 1))
    crop = crop.resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh + 200), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))  # camera

    out = os.path.join(OUT_DIR, f'store_07_flow_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'happy_path.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg, shot)