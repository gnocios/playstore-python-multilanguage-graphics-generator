"""Nachigo store screenshot #1 (hook) generator -> store_img_01/store_01_hook_<code>.png (1080x1920).
Needs: assets/screenshot_vocab.png and store_img_01.json (same name as this file).
Requires: python -m pip install pillow numpy arabic-reshaper python-bidi"""
import json, os
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

# kanji of the 16 cards in the screenshot, row by row (2 columns)
ORDER = ['父','母','従姉妹','姉妹','祖父','祖母','妻','兄弟','夫','娘','息子','家族','妹','弟','兄','姉']
CARD_X = (144, 694)
CARD_Y = (780, 1078, 1376, 1673, 1971, 2268, 2566, 2864)
CARD_W, CARD_H = 513, 261
CARD_BG = (45, 52, 54)
MEAN_SIZE, MEAN_BASELINE = 35, 228


def load(spec, size):
    path, idx = spec
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(path, size)   # fallback to first font of the file


def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def patch_screenshot(shot, meanings, spec, rtl):
    shot = shot.copy(); d = ImageDraw.Draw(shot)
    for i, kanji in enumerate(ORDER):
        x, y = CARD_X[i % 2], CARD_Y[i // 2]
        d.rectangle((x + 10, y + 186, x + CARD_W - 10, y + 250), fill=CARD_BG)   # erase old meaning
        text = shape(meanings[kanji]) if rtl else meanings[kanji]
        size = MEAN_SIZE
        f = load(spec, size)
        while d.textlength(text, font=f) > CARD_W - 40 and size > 18:
            size -= 1; f = load(spec, size)
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


def fit_font(d, text, spec, size, max_w):
    while size > 20 and d.textlength(text, font=load(spec, size)) > max_w:
        size -= 2
    return load(spec, size)


def build(code, cfg, shot):
    fonts = FONTS.get(code, {'bold': LATIN_BOLD, 'text': LATIN_TEXT})
    bold, text = fonts['bold'], fonts['text']
    if 'font' in cfg:                                  # JSON override
        bold = text = (cfg['font'], 0)
    for p, _ in (bold, text):
        if not os.path.exists(p):
            print('font not found for', code, ':', p)
            return
    rtl = code in RTL_LANGS

    img = background(); d = ImageDraw.Draw(img)

    # headline (line 2 "N5 → N1" is the same in every language: always Latin bold)
    h1 = shape(cfg['headline'][0]) if rtl else cfg['headline'][0]
    sub = shape(cfg['subtitle']) if rtl else cfg['subtitle']
    f1 = fit_font(d, h1, bold, 112, 900)
    f2 = fit_font(d, cfg['headline'][1], LATIN_BOLD, 170, 900)
    d.text((W/2, 95), h1, font=f1, fill=WHITE, anchor='mt')
    d.text((W/2, 245), cfg['headline'][1], font=f2, fill=GREEN, anchor='mt')
    f3 = fit_font(d, sub, bold, 38, 900)
    d.text((W/2, 452), sub, font=f3, fill=GREY, anchor='mt')

    # phone
    px0, px1, ptop, inset = 90, 990, 600, 14
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((px0-10, ptop+14, px1+10, H+300), 100, fill=(0, 0, 0, 170))
    blurred = shadow.filter(ImageFilter.GaussianBlur(28))
    img.paste(blurred, (0, 0), blurred)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((px0, ptop, px1, H + 300), 96, fill=(36, 36, 40), outline=(105, 105, 118), width=4)
    sx0, sx1, stop = px0 + inset, px1 - inset, ptop + inset
    sw, sh = sx1 - sx0, H - stop
    patched = patch_screenshot(shot, cfg['meanings'], text, rtl)
    crop_x0, crop_x1, crop_y0 = 90, 1260, 700
    scale = sw / (crop_x1 - crop_x0)
    crop = patched.crop((crop_x0, crop_y0, crop_x1, crop_y0 + int(sh / scale) + 1))
    crop = crop.resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh + 200), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))  # camera

    out = os.path.join(OUT_DIR, f'store_01_hook_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'screenshot_vocab.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    for code, cfg in data.items():
        build(code, cfg, shot)