"""Nachigo store image #5 (Review / Fibonacci spacing) -> store_img_05/store_05_review_<code>.png (1080x1920).
Needs: assets/pantalla_review.png and store_img_05.json (same name as this file).
Usage: python store_img_05.py            (all locales)
       python store_img_05.py en-US es-419   (only those)
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
GREEN, VIOLET, RED = (46, 204, 113), (168, 85, 247), (255, 77, 77)
WHITE, GREY, DARK = (255, 255, 255), (190, 190, 190), (26, 26, 26)

# measured on pantalla_review.png (1350x2400)
PAGE_BG = (26, 26, 26)
MEAN_SIZE, MEAN_BASELINE, MEAN_CX = 61, 384, 675       # meaning (bold, green)
BTN_SIZE, BTN_BASELINE = 46, 768                        # "wrong" / "Right"
BTN_WRONG_CX, BTN_RIGHT_CX, BTN_MAXW = 397, 953, 420
CARD_BOX, CARD_BORDER, CARD_RADIUS = (96, 144, 1254, 1206), (45, 52, 54), 76
HAMBURGER = (44, 44, 170, 158)                          # hamburger menu button, erased
CROP_X0, CROP_X1, CROP_Y0 = 70, 1280, 70                # crop shown inside the phone

# layout of the final image
P_X0, P_X1 = 60, 1020
R_TOP, R_H = 500, 330
W_TOP, W_H = 846, 136
PHONE_TOP = 1010
FIB = [1, 1, 2, 3, 5]


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
    """Wraps logical text; measures each candidate line already shaped when RTL."""
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


def patch_screenshot(shot, cfg, text_spec, card_bold, rtl):
    tx = shape if rtl else (lambda t: t)
    shot = shot.copy()
    # hamburger button: erase it and redraw the corner of the card border that it overlapped
    layer = Image.new('RGB', shot.size, PAGE_BG)
    ImageDraw.Draw(layer).rounded_rectangle(CARD_BOX, CARD_RADIUS, outline=CARD_BORDER, width=5)
    shot.paste(layer.crop(HAMBURGER), HAMBURGER[:2])
    d = ImageDraw.Draw(shot)
    # meaning (bold green)
    meaning = tx(cfg['meaning'])
    d.rectangle((160, 330, 1190, 402), fill=PAGE_BG)
    f = fit_font(d, meaning, card_bold, MEAN_SIZE, 1000, 28)
    d.text((MEAN_CX, MEAN_BASELINE), meaning, font=f, fill=GREEN, anchor='ms')
    # wrong / Right buttons
    wrong, right = tx(cfg['wrong']), tx(cfg['right'])
    d.rectangle((172, 718, 626, 792), fill=PAGE_BG)
    d.rectangle((730, 718, 1176, 792), fill=PAGE_BG)
    fw = fit_font(d, wrong, text_spec, BTN_SIZE, BTN_MAXW, 22)
    fr = fit_font(d, right, text_spec, BTN_SIZE, BTN_MAXW, 22)
    d.text((BTN_WRONG_CX, BTN_BASELINE), wrong, font=fw, fill=RED, anchor='ms')
    d.text((BTN_RIGHT_CX, BTN_BASELINE), right, font=fr, fill=GREEN, anchor='ms')
    return shot


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

    tx_x = P_X1 - 36 if rtl else P_X0 + 36
    tw = (P_X1 - P_X0) - 72
    # panel 1: right answer -> Fibonacci nodes
    d.rounded_rectangle((P_X0, R_TOP, P_X1, R_TOP + R_H), 34, fill=(34, 37, 39), outline=(66, 72, 76), width=3)
    rt = tx(cfg['right_title'])
    ft = fit_font(d, rt, bold, 40, tw, 24)
    d.text((tx_x, R_TOP + 24), rt, font=ft, fill=GREEN, anchor=anchor)
    fb, lines = wrap(d, cfg['right_text'], text, 28, tw, rtl, 2)
    for j, ln in enumerate(lines):
        d.text((tx_x, R_TOP + 80 + j * 36), tx(ln), font=fb, fill=GREY, anchor=anchor)
    radii = [30 + 8 * v for v in FIB]; gap = 70
    total = sum(2 * r for r in radii) + gap * (len(FIB) - 1)
    cy = R_TOP + 236
    slots = list(range(len(FIB)))
    if rtl:
        slots = slots[::-1]                            # visual left-to-right order
    cx_list, xx = [], (W - total) / 2
    for k in slots:
        r = radii[k]
        cx_list.append((xx + r, k, r)); xx += 2 * r + gap
    for i, (cx, k, r) in enumerate(cx_list):
        last = (k == len(FIB) - 1)
        fill, outline, tcol = ((GREEN, GREEN, DARK) if last else ((30, 64, 44), GREEN, WHITE))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=3)
        d.text((cx, cy + 1), str(FIB[k]), font=load(LATIN_BOLD, int(r * 0.9)), fill=tcol, anchor='mm')
        if i < len(cx_list) - 1:
            gx = cx + r + gap / 2; s = -1 if rtl else 1
            d.line([(gx - 6 * s, cy - 14), (gx + 6 * s, cy), (gx - 6 * s, cy + 14)], fill=GREY, width=5, joint='curve')

    # panel 2: wrong answer -> interval steps back
    d.rounded_rectangle((P_X0, W_TOP, P_X1, W_TOP + W_H), 34, fill=(34, 37, 39), outline=(66, 72, 76), width=3)
    ix = P_X1 - 66 if rtl else P_X0 + 66; iy = W_TOP + W_H / 2
    d.ellipse((ix - 34, iy - 34, ix + 34, iy + 34), fill=(70, 32, 36), outline=RED, width=3)
    s = 1 if rtl else -1       # arrow that goes "back" (points left in ltr)
    d.line([(ix - 7 * s, iy - 15), (ix + 7 * s, iy), (ix - 7 * s, iy + 15)], fill=RED, width=6, joint='curve')
    wx = P_X1 - 126 if rtl else P_X0 + 126
    ww = (P_X1 - P_X0) - 126 - 36
    wt = tx(cfg['wrong_title'])
    ft = fit_font(d, wt, bold, 38, ww, 24)
    d.text((wx, W_TOP + 18), wt, font=ft, fill=RED, anchor=anchor)
    fb, lines = wrap(d, cfg['wrong_text'], text, 28, ww, rtl, 2)
    for j, ln in enumerate(lines):
        d.text((wx, W_TOP + 68 + j * 34), tx(ln), font=fb, fill=GREY, anchor=anchor)

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
    patched = patch_screenshot(shot, cfg, text, bold, rtl)
    scale = sw / (CROP_X1 - CROP_X0)
    crop = patched.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y0 + int(sh / scale) + 1)).resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh + 200), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))  # camera

    out = os.path.join(OUT_DIR, f'store_05_review_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'pantalla_review.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg, shot)