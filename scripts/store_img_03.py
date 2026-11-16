"""Nachigo store image #3 (Learn mode / SLP) -> store_img_03/store_03_learn_<code>.png (1080x1920).
Needs: assets/screenshot_learn.png and store_img_03.json (same name as this file).
Usage: python store_img_03.py            (all locales)
       python store_img_03.py en-US es-419   (only those)
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
BG, PILL = (26, 26, 26), (42, 48, 50)
DIGIT = (87, 97, 100)
DEMO = dict(ok=6, bad=1, pos=8, total=10)     # numbers shown in the counters


def load(spec, size):
    path, idx = spec
    try:
        return ImageFont.truetype(path, size, index=idx)
    except OSError:
        return ImageFont.truetype(path, size)


def shape(t):
    return get_display(arabic_reshaper.reshape(t))


def patch(shot, cfg, f_reg, f_bold, rtl):
    s = shot.copy(); d = ImageDraw.Draw(s)
    icons = {'check': shot.crop((173, 1008, 216, 1044)), 'x': shot.crop((244, 1008, 279, 1044)),
             'copy': shot.crop((620, 995, 674, 1055))}
    meaning = shape(cfg['meaning']) if rtl else cfg['meaning']
    show = shape(cfg['show_answer']) if rtl else cfg['show_answer']
    # 1) meaning in place of the first eye
    d.rectangle((630, 322, 722, 396), fill=BG)
    size = 58; f = load(f_bold, size)
    while d.textlength(meaning, font=f) > 900 and size > 24:
        size -= 2; f = load(f_bold, size)
    d.text((675.5, 378), meaning, font=f, fill=GREEN, anchor='ms')
    # 2) "Show answer"
    d.rectangle((200, 676, 1150, 744), fill=BG)
    size = 48; f = load(f_reg, size)
    while d.textlength(show, font=f) > 900 and size > 22:
        size -= 1; f = load(f_reg, size)
    d.text((676.5, 726), show, font=f, fill=GREEN, anchor='ms')
    # 3) counters (digits only: always Latin font)
    fd = load(LATIN_TEXT, 38)
    d.rectangle((126, 962, 352, 1094), fill=BG); d.rectangle((570, 962, 780, 1094), fill=BG)
    w1, w2 = d.textlength(str(DEMO['ok']), font=fd), d.textlength(str(DEMO['bad']), font=fd)
    width = int(39 + 38 + 6 + w1 + 10 + 31 + 12 + w2 + 35)
    x0 = 136
    d.rounded_rectangle((x0, 972, x0 + width, 1084), 30, fill=PILL)
    x = x0 + 39
    s.paste(icons['check'], (x - 2, 1008)); x += 38 + 6
    d.text((x, 1038), str(DEMO['ok']), font=fd, fill=DIGIT, anchor='ls'); x += w1 + 10
    s.paste(icons['x'], (int(x) - 2, 1008)); x += 31 + 12
    d.text((x, 1038), str(DEMO['bad']), font=fd, fill=DIGIT, anchor='ls')
    txt = f"{DEMO['pos']}/{DEMO['total']}"; wt = d.textlength(txt, font=fd)
    width = int(36 + 45 + 10 + wt + 39); px = 675 - width / 2
    d.rounded_rectangle((px, 972, px + width, 1084), 30, fill=PILL)
    s.paste(icons['copy'], (int(px + 36 - 6), 995)); d.text((px + 36 + 45 + 10, 1038), txt, font=fd, fill=DIGIT, anchor='ls')
    return s


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.zeros((H, W, 3), np.float32) + 26
    def glow(cx, cy, r, c, k):
        a = np.clip(1 - np.sqrt((xx-cx)**2 + (yy-cy)**2) / r, 0, 1) ** 2 * k
        return a[..., None] * (np.array(c, np.float32) - 26)
    bg += glow(900, 120, 900, (30, 80, 50), 1.0)
    bg += glow(120, 1750, 800, (70, 40, 90), 1.0)
    bg += glow(540, 1100, 700, (28, 60, 42), 0.5)
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))


def fit_font(d, text, spec, size, max_w):
    while size > 20 and d.textlength(text, font=load(spec, size)) > max_w:
        size -= 2
    return load(spec, size)


def wrap(d, text, font, max_w, rtl):
    """Wraps the logical text; measures each candidate line already shaped when RTL."""
    meas = (lambda t: d.textlength(shape(t), font=font)) if rtl else (lambda t: d.textlength(t, font=font))
    sep = ' ' if ' ' in text else ''
    words = text.split(' ') if sep else list(text)
    lines, cur = [], ''
    for w in words:
        t = (cur + sep + w) if cur else w
        if meas(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


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
    rtl = code in RTL_LANGS

    img = background(); d = ImageDraw.Draw(img)
    h1 = shape(cfg['headline'][0]) if rtl else cfg['headline'][0]
    h2 = shape(cfg['headline'][1]) if rtl else cfg['headline'][1]
    sub = shape(cfg['subtitle']) if rtl else cfg['subtitle']
    f1 = fit_font(d, h1, bold, 112, 900); f2 = fit_font(d, h2, bold, 150, 900)
    d.text((W/2, 95), h1, font=f1, fill=WHITE, anchor='mt')
    d.text((W/2, 245), h2, font=f2, fill=GREEN, anchor='mt')
    f3 = fit_font(d, sub, bold, 38, 940)
    d.text((W/2, 452), sub, font=f3, fill=GREY, anchor='mt')

    # phone
    px0, px1, ptop, inset, sh = 90, 990, 560, 14, 840
    pbot = ptop + inset * 2 + sh
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((px0-10, ptop+14, px1+10, pbot+14), 100, fill=(0, 0, 0, 170))
    blurred = shadow.filter(ImageFilter.GaussianBlur(28)); img.paste(blurred, (0, 0), blurred)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((px0, ptop, px1, pbot), 96, fill=(36, 36, 40), outline=(105, 105, 118), width=4)
    sx0, sx1, stop = px0 + inset, px1 - inset, ptop + inset
    sw = sx1 - sx0
    patched = patch(shot, cfg, text, bold, rtl)
    cx0, cx1, cy0 = 40, 1310, 20
    scale = sw / (cx1 - cx0)
    crop = patched.crop((cx0, cy0, cx1, cy0 + int(sh / scale) + 1)).resize((sw, sh), Image.LANCZOS)
    m = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh), 82, fill=255)
    img.paste(crop, (sx0, stop), m)
    d = ImageDraw.Draw(img)
    d.ellipse((W/2 - 13, stop + 18, W/2 + 13, stop + 44), fill=(12, 12, 14), outline=(60, 60, 66))

    # caption card
    top, bottom, cx0_, cx1_, pad = pbot + 52, H - 44, 64, 1016, 44
    inner = cx1_ - cx0_ - 2 * pad
    s1, s2 = 40, 33
    while True:
        fa, fb = load(text, s1), load(text, s2)
        la, lb = wrap(d, cfg['caption'], fa, inner, rtl), wrap(d, cfg['caption2'], fb, inner, rtl)
        need = int(s1 * 1.35) * len(la) + 16 + int(s2 * 1.35) * len(lb) + 2 * 36
        if need <= bottom - top or s1 <= 22:
            break
        s1 -= 2; s2 = max(s2 - 1, 20)
    h = need
    ty = top + ((bottom - top) - h) / 2
    d.rounded_rectangle((cx0_, ty, cx1_, ty + h), 34, fill=(26, 66, 46), outline=GREEN, width=3)
    y = ty + 36
    for ln in la:
        if rtl:
            d.text((cx1_ - pad, y), shape(ln), font=fa, fill=(240, 246, 242), anchor='ra')
        else:
            d.text((cx0_ + pad, y), ln, font=fa, fill=(240, 246, 242))
        y += int(s1 * 1.35)
    y += 16
    for ln in lb:
        if rtl:
            d.text((cx1_ - pad, y), shape(ln), font=fb, fill=(160, 214, 184), anchor='ra')
        else:
            d.text((cx0_ + pad, y), ln, font=fb, fill=(160, 214, 184))
        y += int(s2 * 1.35)

    out = os.path.join(OUT_DIR, f'store_03_learn_{code}.png')
    img.save(out, optimize=True); print('saved', out)


if __name__ == '__main__':
    shot = Image.open(os.path.join(ASSETS, 'screenshot_learn.png')).convert('RGB')
    data = json.load(open(os.path.join(DATA, NAME + '.json'), encoding='utf-8'))
    only = sys.argv[1:]
    for code, cfg in data.items():
        if only and code not in only:
            continue
        build(code, cfg, shot)