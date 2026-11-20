#!/usr/bin/env python3
"""news-image-20261119 — deterministic broadsheet front page for 19 Nov 2026.

Renders at 2048x2048 with Pillow, then downscales (LANCZOS) to 1024x1024.
No network, no timestamps, fixed seed: re-running produces byte-identical
entry.png. Every headline is a verified 19 November 2026 event (see
../dev/STORY-POOL.md); one-party claims stay attributed.
"""
import random
from PIL import Image, ImageDraw, ImageFont

random.seed(19)

S = 2048                      # render size; downscaled to 1024 at the end
M = 36                        # outer margin
G = 28                        # gutter

PAPER = (246, 241, 230)
INK = (24, 24, 30)
NAVY = (18, 38, 74)
NAVY2 = (28, 58, 108)
RED = (178, 34, 34)
DARKRED = (122, 20, 20)
GOLD = (201, 162, 39)
TEAL = (16, 96, 110)
GREEN = (24, 120, 58)
GREY = (110, 110, 116)
LIGHT = (255, 255, 255)
CREAM = (252, 248, 238)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(w, h, top, bottom):
    """Vertical gradient image."""
    import numpy as np
    t = np.linspace(0, 1, h)[:, None, None]
    top_a = np.array(top, dtype=float)[None, None, :]
    bot_a = np.array(bottom, dtype=float)[None, None, :]
    arr = (top_a * (1 - t) + bot_a * t).astype("uint8")
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr, "RGB")


def hgrad(w, h, left, right):
    import numpy as np
    t = np.linspace(0, 1, w)[None, :, None]
    l = np.array(left, dtype=float)[None, None, :]
    r = np.array(right, dtype=float)[None, None, :]
    arr = (l * (1 - t) + r * t).astype("uint8")
    arr = np.repeat(arr, h, axis=0)
    return Image.fromarray(arr, "RGB")


def panel(d, box, fill, outline=INK, width=4, radius=18):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                        width=width)


def shadow(d, box, radius=18, off=10):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 + off, y0 + off, x1 + off, y1 + off],
                        radius=radius, fill=(0, 0, 0, 46))


def kicker(d, x, y, text, color=RED, size=34):
    d.text((x, y), text, font=font(F_SANS, size), fill=color)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, max_w, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def headline(d, x, y, text, size, fill=INK, max_w=None, serif=True):
    fnt = font(F_SERIF if serif else F_SANS, size)
    if max_w is None:
        d.text((x, y), text, font=fnt, fill=fill)
        return y + int(size * 1.15)
    return text_block(d, x, y, text, fnt, fill, max_w)


def rule(d, x0, y, x1, color=INK, width=4):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def draw_flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 34))
    for i in range(7):
        yy = y + i * h / 13 * 2 + (h / 13 if i % 2 == 0 else 0)
        d.rectangle([x, yy, x + w, yy + h / 13], fill=LIGHT)
    d.rectangle([x, y, x + w * 0.4, y + h * 7 / 13], fill=(30, 50, 110))
    for r in range(5):
        for c in range(6):
            sx = x + 8 + c * (w * 0.4 - 14) / 5
            sy = y + 7 + r * (h * 7 / 13 - 12) / 4
            d.ellipse([sx, sy, sx + 5, sy + 5], fill=LIGHT)


def draw_flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.22, y + h * 0.28
    for ang in range(5):
        import math
        a = math.radians(ang * 72 - 90)
        px, py = cx + 13 * math.cos(a), cy + 13 * math.sin(a)
        d.polygon([(cx, cy - 16), (px, py), (cx + 16 * math.cos(a + 2.5),
                    cy + 16 * math.sin(a + 2.5))], fill=(255, 222, 0))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 222, 0))
    for sx, sy in [(0.55, 0.18), (0.68, 0.32), (0.68, 0.52), (0.55, 0.66)]:
        d.ellipse([x + w * sx - 5, y + h * sy - 5, x + w * sx + 5,
                   y + h * sy + 5], fill=(255, 222, 0))


def draw_flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=LIGHT)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def draw_dove(d, cx, cy, s, fill=LIGHT):
    # simple stylised dove: body ellipse, head, beak, swept wings
    d.ellipse([cx - s, cy - s * 0.42, cx + s, cy + s * 0.42], fill=fill)
    d.ellipse([cx + s * 0.62, cy - s * 0.78, cx + s * 1.18, cy - s * 0.18],
              fill=fill)
    d.polygon([(cx + s * 1.1, cy - s * 0.5), (cx + s * 1.55, cy - s * 0.32),
               (cx + s * 1.1, cy - s * 0.28)], fill=GOLD)
    d.polygon([(cx - s * 0.5, cy - s * 0.3), (cx - s * 0.1, cy - s * 1.25),
               (cx + s * 0.35, cy - s * 0.3)], fill=fill)
    d.polygon([(cx - s * 0.7, cy), (cx - s * 1.5, cy - s * 0.55),
               (cx - s * 0.9, cy + s * 0.25)], fill=fill)
    d.ellipse([cx + s * 0.86, cy - s * 0.62, cx + s * 0.94, cy - s * 0.54],
              fill=INK)


def draw_person(d, cx, base_y, suit, skin=(232, 190, 150), hair=(70, 70, 74),
                h=150):
    """Seated figure: head + shoulders + suit torso."""
    d.ellipse([cx - 34, base_y - h, cx + 34, base_y - h + 68], fill=skin)
    d.pieslice([cx - 36, base_y - h - 6, cx + 36, base_y - h + 34], 180, 360,
               fill=hair)
    d.rounded_rectangle([cx - 72, base_y - h + 62, cx + 72, base_y + 26],
                        radius=26, fill=suit)
    d.polygon([(cx - 16, base_y - h + 62), (cx, base_y - h + 96),
               (cx + 16, base_y - h + 62)], fill=LIGHT)
    d.polygon([(cx - 7, base_y - h + 78), (cx + 7, base_y - h + 78),
               (cx, base_y - h + 118)], fill=RED)


def masthead(d, w):
    rule(d, M, 58, w - M, INK, 6)
    d.text((w // 2, 74), "THE WORLD IN ONE PICTURE",
           font=font(F_SERIF, 96), fill=INK, anchor="ma")
    d.text((w // 2, 178), "T H U R S D A Y   1 9   N O V E M B E R   2 0 2 6",
           font=font(F_SANS, 52), fill=RED, anchor="ma")
    rule(d, M, 246, w - M, RED, 5)
    d.text((w // 2, 258), "SHENZHEN  •  THE HAGUE  •  NEW YORK  •  DHAKA  •  ANTALYA",
           font=font(F_SANS, 30), fill=GREY, anchor="ma")


def hero_shenzhen(img, d, box):
    x0, y0, x1, y1 = box
    band_y = y1 - 252
    sky = vgrad(x1 - x0, band_y - y0, (24, 58, 96), (214, 164, 82))
    img.paste(sky, (x0, y0))
    # dusk sun + glow
    d.ellipse([x0 + 520, y0 + 40, x0 + 660, y0 + 180], fill=(255, 214, 120))
    d.ellipse([x0 + 490, y0 + 10, x0 + 690, y0 + 210], outline=(255, 220, 140),
              width=6)
    # distant hills
    d.polygon([(x0, y0 + 420), (x0 + 260, y0 + 320), (x0 + 560, y0 + 420),
               (x0 + 820, y0 + 330), (x0 + 1216, y0 + 420), (x0, y0 + 420)],
              fill=(38, 74, 66))
    d.polygon([(x0, y0 + 450), (x0 + 400, y0 + 380), (x0 + 900, y0 + 450),
               (x0 + 1216, y0 + 400), (x0 + 1216, y0 + 450), (x0, y0 + 450)],
              fill=(28, 58, 52))
    # villa silhouette on the hill
    d.rectangle([x0 + 880, y0 + 330, x0 + 1130, y0 + 420], fill=(20, 30, 44))
    d.polygon([(x0 + 860, y0 + 332), (x0 + 1005, y0 + 280),
               (x0 + 1150, y0 + 332)], fill=(14, 22, 34))
    for wx in range(900, 1120, 44):
        d.rectangle([wx, y0 + 356, wx + 20, y0 + 384], fill=(255, 214, 120))
    # lake with reflections
    d.rectangle([x0, y0 + 450, x1, y0 + 520], fill=(52, 96, 128))
    for i, lx in enumerate(range(x0 + 60, x1 - 120, 90)):
        d.rectangle([lx, y0 + 466 + (i % 3) * 14, lx + 120, y0 + 474 + (i % 3) * 14],
                    fill=(140, 190, 210))
    d.rectangle([x0, y0 + 520, x1, band_y], fill=(16, 26, 40))
    # dove above the table
    draw_dove(d, x0 + 608, y0 + 250, 62)
    # three flags on poles, left to right: US, China, Russia
    for i, fn in enumerate([draw_flag_us, draw_flag_cn, draw_flag_ru]):
        fx = x0 + 150 + i * 330
        d.line([(fx, y0 + 520), (fx, y0 + 660)], fill=(200, 200, 200), width=8)
        d.ellipse([fx - 8, y0 + 512, fx + 8, y0 + 528], fill=GOLD)
        fn(d, fx + 6, y0 + 536, 190, 118)
    # three seated leaders at the summit table
    ty = y0 + 660
    draw_person(d, x0 + 250, ty, (28, 48, 96), h=120)
    draw_person(d, x0 + 608, ty, (122, 20, 20), h=120)
    draw_person(d, x0 + 966, ty, (52, 52, 58), h=120)
    d.rounded_rectangle([x0 + 90, ty + 14, x0 + 1126, ty + 46], radius=12,
                        fill=(96, 62, 32))
    d.rectangle([x0 + 90, ty + 14, x0 + 1126, ty + 28], fill=(150, 100, 52))
    # headline band
    d.rectangle([x0, band_y, x1, y1], fill=(246, 241, 230))
    rule(d, x0, band_y, x1, RED, 6)
    kicker(d, x0 + 36, band_y + 20, "SHENZHEN  —  FIRST TRILATERAL SUMMIT",
           RED, 36)
    headline(d, x0 + 36, band_y + 62, "THREE POWERS, ONE TABLE", 64,
             INK, max_w=x1 - x0 - 72, serif=True)
    text_block(d, x0 + 36, band_y + 150,
               "Trump, Xi & Putin sign a four-point \u201cDeclaration toward "
               "Peace\u201d — silent on Ukraine and Iran.",
               font(F_SANS_R, 36), INK, x1 - x0 - 72)


def panel_icj(img, d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=(232, 226, 208), outline=INK,
                        width=4)
    # Peace Palace: stepped facade + dome
    d.rectangle([x0 + 60, y0 + 120, x0 + 300, y0 + 220], fill=(196, 178, 140))
    d.polygon([(x0 + 50, y0 + 122), (x0 + 180, y0 + 76), (x0 + 310, y0 + 122)],
              fill=(150, 128, 92))
    d.rectangle([x0 + 160, y0 + 168, x0 + 200, y0 + 220], fill=(60, 48, 36))
    for wx in range(80, 290, 40):
        d.rectangle([x0 + wx, y0 + 140, x0 + wx + 18, y0 + 168],
                    fill=(90, 74, 54))
    # scales of justice, right side
    sx, sy = x0 + 560, y0 + 120
    d.line([(sx, sy), (sx, sy + 110)], fill=INK, width=7)
    d.line([(sx - 80, sy + 16), (sx + 80, sy + 16)], fill=INK, width=7)
    d.line([(sx - 80, sy + 16), (sx - 80, sy + 70)], fill=INK, width=4)
    d.line([(sx + 80, sy + 16), (sx + 80, sy + 70)], fill=INK, width=4)
    d.pieslice([sx - 108, sy + 66, sx - 52, sy + 96], 0, 180, fill=GOLD)
    d.pieslice([sx + 52, sy + 66, sx + 108, sy + 96], 0, 180, fill=GOLD)
    d.ellipse([sx - 10, sy - 14, sx + 10, sy + 6], fill=GOLD)
    kicker(d, x0 + 36, y0 + 22, "THE HAGUE  —  WORLD COURT", RED, 34)
    y = headline(d, x0 + 36, y0 + 240, "MYANMAR COMMITTED GENOCIDE", 48,
                 INK, max_w=x1 - x0 - 72)
    text_block(d, x0 + 36, y + 6,
               "ICJ, 9–6: the first state ever found guilty — Rohingya, 2017.",
               font(F_SANS_R, 34), INK, x1 - x0 - 72)


def panel_markets(img, d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=(16, 26, 40), outline=INK, width=4)
    # Nasdaq board, left: ANT ticker
    d.rounded_rectangle([x0 + 30, y0 + 60, x0 + 330, y0 + 180], radius=10,
                        fill=(10, 40, 26), outline=GREEN, width=3)
    d.text((x0 + 52, y0 + 72), "ANT", font=font(F_SANS, 58), fill=(90, 230, 140))
    d.text((x0 + 52, y0 + 136), "$97.17  +17%", font=font(F_SANS, 36),
           fill=(90, 230, 140))
    # red crash chart, right
    pts = [(x0 + 360 + i * 52, y0 + 84 + (i * i) // 7 + i * 6)
           for i in range(7)]
    d.line(pts, fill=RED, width=10, joint="curve")
    d.polygon(pts + [(x0 + 672, y0 + 180), (x0 + 360, y0 + 180)], fill=(120, 20, 20))
    d.text((x0 + 380, y0 + 186), "DOW  −1,101", font=font(F_SANS, 46),
           fill=(255, 90, 90))
    kicker(d, x0 + 36, y0 + 22, "NEW YORK  —  MARKETS", GOLD, 34)
    y = headline(d, x0 + 36, y0 + 240, "RECORD IPO, CRASHING MARKET", 50,
                 LIGHT, max_w=x1 - x0 - 72)
    text_block(d, x0 + 36, y + 6,
               "Biggest IPO ever ($81.3bn) — as the Dow plunges 1,101.",
               font(F_SANS_R, 34), (220, 220, 220), x1 - x0 - 72)


def panel_bangladesh(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 190, (52, 28, 24), (178, 84, 32))
    img.paste(sky, (x0, y0))
    d.rounded_rectangle(box, radius=18, outline=INK, width=4)
    # burning building silhouette
    d.rectangle([x0 + 40, y0 + 86, x0 + 190, y0 + 190], fill=(24, 18, 16))
    for wx in range(56, 180, 34):
        d.rectangle([x0 + wx, y0 + 104, x0 + wx + 16, y0 + 128],
                    fill=(255, 170, 40))
    # flames
    for fx, fh in [(76, 56), (115, 76), (158, 62)]:
        d.polygon([(x0 + fx - 18, y0 + 90), (x0 + fx, y0 + 90 - fh),
                   (x0 + fx + 18, y0 + 90)], fill=(255, 120, 20))
        d.polygon([(x0 + fx - 9, y0 + 90), (x0 + fx, y0 + 90 - fh // 2),
                   (x0 + fx + 9, y0 + 90)], fill=(255, 210, 60))
    # smoke
    for sx, sy, sr in [(240, 110, 26), (285, 88, 32), (330, 112, 26),
                       (380, 92, 30), (420, 116, 22)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(90, 84, 84))
    # street barricade
    d.polygon([(x0 + 220, y0 + 168), (x0 + 440, y0 + 168), (x0 + 420, y0 + 192),
               (x0 + 240, y0 + 192)], fill=(60, 52, 48))
    d.line([(x0 + 230, y0 + 192), (x0 + 430, y0 + 192)], fill=(200, 160, 60),
           width=6)
    kicker(d, x0 + 24, y0 + 14, "DHAKA  —  UNREST", (255, 210, 90), 30)
    d.rectangle([x0, y0 + 200, x1, y1], fill=(246, 241, 230))
    y = headline(d, x0 + 24, y0 + 212, "BANGLADESH BURNS", 40, INK,
                 max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "Lockdown arson in 28 districts; two killed.",
               font(F_SANS_R, 30), INK, x1 - x0 - 48)


def panel_cop31(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 190, (30, 60, 90), (120, 170, 200))
    img.paste(sky, (x0, y0))
    d.rounded_rectangle(box, radius=18, outline=INK, width=4)
    # conference hall + smokestack vs solar panel
    d.rectangle([x0 + 40, y0 + 120, x0 + 200, y0 + 190], fill=(40, 50, 66))
    d.polygon([(x0 + 30, y0 + 122), (x0 + 120, y0 + 78),
               (x0 + 210, y0 + 122)], fill=(28, 36, 50))
    for wx in range(56, 190, 34):
        d.rectangle([x0 + wx, y0 + 140, x0 + wx + 16, y0 + 168],
                    fill=(255, 214, 120))
    # smokestack with grey plume
    d.rectangle([x0 + 250, y0 + 90, x0 + 282, y0 + 190], fill=(70, 70, 76))
    for sx, sy, sr in [(300, 84, 22), (330, 66, 26), (366, 80, 20)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(120, 120, 124))
    # solar panel, gold
    d.polygon([(x0 + 340, y0 + 190), (x0 + 440, y0 + 190), (x0 + 420, y0 + 150),
               (x0 + 360, y0 + 150)], fill=(30, 90, 160))
    d.line([(x0 + 390, y0 + 190), (x0 + 390, y0 + 150)], fill=LIGHT, width=3)
    kicker(d, x0 + 24, y0 + 14, "ANTALYA  —  COP31", (255, 220, 120), 30)
    d.rectangle([x0, y0 + 200, x1, y1], fill=(246, 241, 230))
    y = headline(d, x0 + 24, y0 + 212, "COP31 DRAFT DROPS FOSSIL FUELS", 40,
                 INK, max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "Cover text deletes phase-out; talks deadlocked.",
               font(F_SANS_R, 30), INK, x1 - x0 - 48)


def panel_voyager(img, d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=(8, 12, 30), outline=INK, width=4)
    # stars
    for sx, sy, sr in [(60, 60, 3), (120, 110, 2), (200, 50, 3), (280, 130, 2),
                       (360, 60, 3), (420, 100, 2), (90, 160, 2), (250, 170, 3),
                       (330, 40, 2), (160, 30, 2), (400, 160, 3), (30, 120, 2)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=LIGHT)
    # Voyager probe: bus + dish + boom
    px, py = x0 + 240, y0 + 100
    d.ellipse([px - 46, py - 26, px + 46, py + 26], fill=(200, 200, 210))
    d.polygon([(px - 46, py - 10), (px - 120, py - 52), (px - 120, py + 30)],
              fill=(160, 160, 175))
    d.line([(px + 46, py), (px + 130, py - 40)], fill=(180, 180, 190), width=6)
    d.line([(px, py + 26), (px - 30, py + 80)], fill=(180, 180, 190), width=6)
    d.ellipse([px - 126, py - 58, px - 114, py - 46], fill=GOLD)
    # tiny Earth, far below
    d.ellipse([x0 + 36, y0 + 150, x0 + 64, y0 + 178], fill=(70, 130, 220))
    d.ellipse([x0 + 42, y0 + 154, x0 + 56, y0 + 164], fill=(90, 190, 110))
    d.text((x0 + 76, y0 + 152), "EARTH", font=font(F_SANS, 24),
           fill=(180, 200, 230))
    # signal arc
    d.arc([x0 + 90, y0 + 10, x0 + 420, y0 + 190], 200, 340,
          fill=(120, 200, 255), width=4)
    kicker(d, x0 + 24, y0 + 14, "SPACE  —  NASA", (140, 200, 255), 30)
    d.rectangle([x0, y0 + 200, x1, y1], fill=(246, 241, 230))
    y = headline(d, x0 + 24, y0 + 212, "VOYAGER 1, ONE LIGHT-DAY AWAY", 40,
                 INK, max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "NASA confirms the farthest human object — 25.9bn km.",
               font(F_SANS_R, 30), INK, x1 - x0 - 48)


def panel_hormuz(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 190, (120, 70, 40), (40, 30, 30))
    img.paste(sky, (x0, y0))
    d.rounded_rectangle(box, radius=18, outline=INK, width=4)
    # sea
    d.rectangle([x0, y0 + 130, x1, y0 + 190], fill=(30, 60, 90))
    for lx in range(20, 460, 70):
        d.rectangle([x0 + lx, y0 + 150, x0 + lx + 40, y0 + 156],
                    fill=(110, 160, 200))
    # tanker hull + superstructure, listing
    d.polygon([(x0 + 60, y0 + 110), (x0 + 380, y0 + 110), (x0 + 360, y0 + 150),
               (x0 + 80, y0 + 150)], fill=(140, 30, 30))
    d.rectangle([x0 + 300, y0 + 70, x0 + 360, y0 + 110], fill=(200, 200, 200))
    # flames + smoke column
    for fx, fh in [(130, 60), (180, 84), (235, 66)]:
        d.polygon([(x0 + fx - 18, y0 + 112), (x0 + fx, y0 + 112 - fh),
                   (x0 + fx + 18, y0 + 112)], fill=(255, 120, 20))
        d.polygon([(x0 + fx - 9, y0 + 112), (x0 + fx, y0 + 112 - fh // 2),
                   (x0 + fx + 9, y0 + 112)], fill=(255, 210, 60))
    for sx, sy, sr in [(180, 40, 24), (210, 20, 28), (250, 36, 22)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(60, 56, 56))
    kicker(d, x0 + 24, y0 + 14, "STRAIT OF HORMUZ", (255, 200, 120), 30)
    d.rectangle([x0, y0 + 200, x1, y1], fill=(246, 241, 230))
    y = headline(d, x0 + 24, y0 + 212, "IRGC SAYS TWO TANKERS HIT MINES",
                 40, INK, max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "Iran's navy claims mine blasts in the Strait.",
               font(F_SANS_R, 30), INK, x1 - x0 - 48)


def footer_briefs(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=NAVY, outline=INK, width=4)
    d.text((x0 + 36, y0 + 26), "IN BRIEF", font=font(F_SERIF, 58),
           fill=GOLD)
    rule(d, x0 + 36, y0 + 104, x0 + 300, GOLD, 4)
    briefs = [
        ("SENATE 51–48", "US Senate rejects bid to curb Trump's Iran war "
         "powers."),
        ("SOMALIA", "Expels UAE envoy; Mogadishu calls port deals an "
         "\u201copen invasion\u201d."),
        ("MONGOLIA", "Parliament accepts the president's resignation — a "
         "historic first."),
    ]
    col_w = (x1 - x0 - 72 - 360) // 3
    for i, (head, body) in enumerate(briefs):
        bx = x0 + 400 + i * col_w
        d.text((bx, y0 + 28), head, font=font(F_SANS, 42), fill=LIGHT)
        text_block(d, bx, y0 + 86, body, font(F_SANS_R, 40), (210, 215, 225),
                   col_w - 40)


def main():
    img = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    masthead(d, S)
    # hero + right column
    hero_shenzhen(img, d, (M, 292, 1252, 1268))
    panel_icj(img, d, (1280, 292, 2012, 766))
    panel_markets(img, d, (1280, 794, 2012, 1268))
    # middle row: four panels
    y_mid0, y_mid1 = 1296, 1700
    xs = [36, 536, 1036, 1536]
    xe = [508, 1008, 1508, 2012]
    panel_bangladesh(img, d, (xs[0], y_mid0, xe[0], y_mid1))
    panel_cop31(img, d, (xs[1], y_mid0, xe[1], y_mid1))
    panel_voyager(img, d, (xs[2], y_mid0, xe[2], y_mid1))
    panel_hormuz(img, d, (xs[3], y_mid0, xe[3], y_mid1))
    # footer
    footer_briefs(d, (M, 1728, 2012, 2012))
    small = img.resize((1024, 1024), Image.LANCZOS)
    small.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
