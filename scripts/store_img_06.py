"""Nachigo store image #6 (Customize) -> store_img_06/store_06_customize_<code>.png (1080x1920).
Needs: assets/screenshot_customize.png and store_img_06.json (same name as this file).
Usage: python store_img_06.py            (all locales)
       python store_img_06.py en-US es-419   (only those)
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

# --- geometry measured on screenshot_customize.png (1350 x 2400)
BTN = [(1339, 1490), (1521, 1672), (1701, 1852), (1884, 2035), (2064, 2215), (2246, 2397)]  # button y ranges
BTN_X0, BTN_X1 = 256, 1096
BTN_FILL = [(28, 44, 35)] * 3 + [(33, 33, 33)] * 3      # first 3 options are "on" in the screenshot
LABEL_SIZE, LABEL_BASE, LABEL_PAD = 42, 92, 49
MEAN_SIZE, MEAN_BASE, MEAN_CX = 58, 456, 676
BG = (26, 26, 26)


def load(spec, size):
    path, idx = spec
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(path, size)


def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def patch(shot, cfg, text_spec, bold_spec, rtl):
    tx = shape if rtl else (lambda t: t)
    s = shot.copy(); d = ImageDraw.Draw(s)
    d.rectangle((200, 40, 1330, 166), fill=BG)                    # title + subtitle
    d.rectangle((400, 398, 950, 476), fill=BG)                    # meaning text in the card
    meaning = tx(cfg['meaning'])
    size = MEAN_SIZE
    f = load(bold_spec, size)
    while d.textlength(meaning, font=f) > 860 and size > 24:
        size -= 2; f = load(bold_spec, size)
    d.text((MEAN_CX, MEAN_BASE), meaning, font=f, fill=GREEN, anchor='ms')
    for (y0, y1), fill, label in zip(BTN, BTN_FILL, cfg['labels']):
        label = tx(label)
        d.rectangle((BTN_X0 + 8, y0 + 10, BTN_X1 - 8, y1 - 10), fill=fill)
        size = LABEL_SIZE
        f = load(text_spec, size)
        while d.textlength(label, font=f) > (BTN_X1 - BTN_X0) - 2 * LABEL_PAD and size > 20:
            size -= 1; f = load(text_spec, size)
        if rtl:
            d.text((BTN_X1 - LABEL_PAD, y0 + LABEL_BASE), label, font=f, fill=(238, 238, 238), anchor='rs')
        else:
            d.text((BTN_X0 + LABEL_PAD, y0 + LABEL_BASE), label, font=f, fill=(238, 238, 238), anchor='ls')
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

    img = background(); d = ImageDraw.Draw(img)
    h1, h2, sub = tx(cfg['headline'][0]), tx(cfg['headline'][1]), tx(cfg['subtitle'])
    f1 = fit_font(d, h1, bold, 112, 900)
    f2 = fit_font(d, h2, bold, 150, 900)
    d.text((W/2, 95), h1, font=f1, fill=WHITE, anchor='mt')
    d.text((W/2, 245), h2, font=f2, fill=GREEN, anchor='mt')
    f3 = fit_font(d, sub, bold, 38, 940)
    d.text((W/2, 452), sub, font=f3, fill=GREY, anchor='mt')

    # phone
    px0, px1, ptop, inset = 90, 990, 600, 14
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((px0-10, ptop+14, px1+10, H+300), 100, fill=(0, 0, 0, 170))
    blurred = shadow.filter(ImageFilter.GaussianBlur(28)); img.paste(blurred, (0, 0), blurred)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((px0, ptop, px1, H + 300), 96, fill=(36, 36, 40), outline=(105, 105, 118), width=4)
    sx0, sx1, stop = px0 + inset, px1 - inset, ptop + inset
    sw, sh = sx1 - sx0, H - stop
    patched = patch(shot, cfg, text, bold, rtl)
    cx0, cx1, cy0 = 20, 1330, 30
    scale = sw / (cx1 - cx0)
    crop = patched.crop((cx0, cy0, cx1, cy0 + int(sh / scale) + 1)).resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh + 200), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))  # camera

    out = os.path.join(OUT_DIR, f'store_06_customize_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'screenshot_customize.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg, shot)