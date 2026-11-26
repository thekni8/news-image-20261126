#!/usr/bin/env python3
"""Draw the 26 November 2026 front page as entry.png.

Everything on the page is drawn here in code: flat vector panels plus real
rendered type (PIL + TrueType fonts), so every headline stays crisp.
The canvas is rendered at twice the final size and downscaled once,
which keeps edges smooth without blurring the lettering.
"""

from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersampling factor
W = H = 1024 * S
M = 34 * S                 # page margin
RIGHT = W - M
PAGE_W = RIGHT - M

PAPER = (247, 243, 234)
INK = (22, 20, 18)
SOFT = (74, 70, 64)
RED = (163, 22, 33)
NAVY = (16, 24, 48)
RULE = (22, 20, 18)

SERIF_XB = "/usr/share/fonts/truetype/noto/NotoSerif-ExtraBold.ttf"
SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS_CB = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS_SB = "/usr/share/fonts/truetype/noto/NotoSans-SemiBold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def tw(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def fit(draw, text, path, size, max_w):
    """Largest size at or below `size` whose text fits max_w (in 1x px)."""
    while size > 8 and tw(draw, text, font(path, size)) > max_w * S:
        size -= 1
    return font(path, size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if tw(draw, trial, fnt) <= max_w * S or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, path, size, max_w, fill=INK, leading=1.18):
    fnt = font(path, size)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x * S, y * S), line, font=fnt, fill=fill)
        y += size * leading
    return y


def centred(draw, y, text, path, size, fill=INK, tracking=0):
    fnt = font(path, size)
    if tracking:
        widths = [tw(draw, ch, fnt) for ch in text]
        total = sum(widths) + tracking * S * (len(text) - 1)
        x = (W - total) / 2
        for ch, w in zip(text, widths):
            draw.text((x, y * S), ch, font=fnt, fill=fill)
            x += w + tracking * S
    else:
        draw.text(((W - tw(draw, text, fnt)) / 2, y * S), text, font=fnt, fill=fill)


def rule(draw, y, weight=2, x0=None, x1=None, fill=RULE):
    draw.rectangle([(x0 or M), y * S, (x1 or RIGHT), y * S + weight * S], fill=fill)


def kicker(draw, x, y, text, size=19):
    fnt = font(SANS_CB, size)
    draw.rectangle([x * S, y * S + 3 * S, x * S + 10 * S, y * S + (size - 2) * S], fill=RED)
    draw.text(((x + 16) * S, y * S), text, font=fnt, fill=RED)


# ---------------------------------------------------------------- panels

def space_panel(draw, x, y, w, h):
    draw.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=10 * S, fill=NAVY)
    # deterministic star field
    seed = 260112026
    for _ in range(90):
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sx = x + 8 + seed % (w - 16)
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sy = y + 8 + seed % (h - 16)
        r = 1.6 if seed % 5 else 2.6
        draw.ellipse([(sx - r) * S, (sy - r) * S, (sx + r) * S, (sy + r) * S], fill=(210, 220, 240))
    # Mercury
    cx, cy, r = x + w * 0.40, y + h * 0.58, h * 0.30
    draw.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(196, 138, 92))
    draw.ellipse([(cx - r) * S, (cy - r) * S, (cx + r * 0.35) * S, (cy + r) * S], fill=(214, 158, 108))
    for dx, dy, cr in [(-0.35, -0.3, 0.16), (0.25, 0.15, 0.20), (-0.05, 0.45, 0.13), (0.45, -0.4, 0.11)]:
        draw.ellipse([(cx + dx * r - cr * r) * S, (cy + dy * r - cr * r) * S,
                      (cx + dx * r + cr * r) * S, (cy + dy * r + cr * r) * S], fill=(168, 112, 70))
    # orbit path
    draw.ellipse([(cx - r * 1.7) * S, (cy - r * 0.62) * S, (cx + r * 1.7) * S, (cy + r * 0.62) * S],
                 outline=(150, 175, 220), width=2 * S)
    # probe on the orbit, clear of the planet's edge
    px, py = cx + r * 1.62, cy - r * 0.52
    draw.rectangle([(px - 9) * S, (py - 7) * S, (px + 9) * S, (py + 7) * S], fill=(235, 238, 245))
    draw.rectangle([(px - 34) * S, (py - 4) * S, (px - 11) * S, (py + 4) * S], fill=(70, 120, 200))
    draw.rectangle([(px + 11) * S, (py - 4) * S, (px + 34) * S, (py + 4) * S], fill=(70, 120, 200))
    draw.line([px * S, (py - 7) * S, px * S, (py - 16) * S], fill=(235, 238, 245), width=2 * S)
    # station silhouette, top right
    sx, sy = x + w * 0.78, y + h * 0.20
    draw.rectangle([(sx - 46) * S, (sy - 4) * S, (sx + 46) * S, (sy + 4) * S], fill=(220, 226, 238))
    draw.rectangle([(sx - 10) * S, (sy - 14) * S, (sx + 10) * S, (sy + 14) * S], fill=(220, 226, 238))
    draw.rectangle([(sx - 62) * S, (sy - 10) * S, (sx - 48) * S, (sy + 10) * S], fill=(90, 140, 210))
    draw.rectangle([(sx + 48) * S, (sy - 10) * S, (sx + 62) * S, (sy + 10) * S], fill=(90, 140, 210))


def colombia_panel(draw, x, y, w, h):
    draw.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(198, 222, 214))
    base = y + h
    draw.polygon([(x * S, base * S), ((x + w * 0.28) * S, (y + h * 0.48) * S),
                  ((x + w * 0.55) * S, base * S)], fill=(96, 140, 110))
    draw.polygon([((x + w * 0.40) * S, base * S), ((x + w * 0.72) * S, (y + h * 0.38) * S),
                  ((x + w) * S, base * S)], fill=(70, 118, 92))
    # dove, large enough to read at thumbnail size
    dx, dy = x + w * 0.52, y + h * 0.34
    edge = (70, 80, 84)
    draw.polygon([((dx - 30) * S, (dy + 2) * S), ((dx - 58) * S, (dy - 14) * S),
                  ((dx - 52) * S, (dy + 12) * S)], fill=(255, 255, 255), outline=edge)
    draw.ellipse([(dx - 34) * S, (dy - 12) * S, (dx + 30) * S, (dy + 14) * S],
                 fill=(255, 255, 255), outline=edge, width=2 * S)
    draw.ellipse([(dx + 18) * S, (dy - 22) * S, (dx + 40) * S, (dy - 2) * S],
                 fill=(255, 255, 255), outline=edge, width=2 * S)
    draw.polygon([(dx - 6) * S, (dy - 8) * S, ((dx - 30) * S, (dy - 40) * S),
                  ((dx + 16) * S, (dy - 20) * S)], fill=(246, 249, 252), outline=edge)
    draw.ellipse([((dx + 31) * S), ((dy - 16) * S), ((dx + 35) * S), ((dy - 12) * S)], fill=edge)
    draw.polygon([((dx + 39) * S, (dy - 13) * S), ((dx + 48) * S, (dy - 10) * S),
                  ((dx + 39) * S, (dy - 7) * S)], fill=(232, 160, 60))
    draw.line([((dx + 44) * S, (dy - 8) * S), ((dx + 58) * S, (dy + 8) * S)], fill=(80, 124, 74), width=3 * S)
    for ox, oy in [(50, 0), (56, 5), (47, 7)]:
        draw.ellipse([((dx + ox - 4) * S), ((dy + oy - 4) * S), ((dx + ox + 4) * S), ((dy + oy + 4) * S)],
                     fill=(104, 146, 86))


def cairo_panel(draw, x, y, w, h):
    draw.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(112, 108, 110))
    # smoke drifting above the fire
    for sx, sy, r in [(0.30, 0.24, 26), (0.47, 0.14, 34), (0.64, 0.22, 26), (0.78, 0.30, 18)]:
        draw.ellipse([((x + w * sx - r) * S), ((y + h * sy - r * 0.55) * S),
                      ((x + w * sx + r) * S), ((y + h * sy + r * 0.55) * S)], fill=(74, 70, 72))
    # road
    draw.rectangle([x * S, (y + h * 0.80) * S, (x + w) * S, (y + h) * S], fill=(38, 37, 39))
    for i in range(6):
        rx = x + 14 + i * (w - 28) / 5
        draw.rectangle([rx * S, (y + h * 0.89) * S, (rx + 26) * S, (y + h * 0.92) * S], fill=(205, 200, 185))
    # flames behind the tanker: layered teardrops, not cones
    def flame(bx, top, half, col):
        base_y = y + h * 0.82
        draw.polygon([(bx - half) * S, base_y * S, (bx - half * 0.35) * S, ((top + base_y) / 2) * S,
                      bx * S, top * S, (bx + half * 0.45) * S, ((top + base_y) / 2) * S,
                      (bx + half) * S, base_y * S], fill=col)
    flame(x + w * 0.40, y + h * 0.10, 30, (222, 96, 24))
    flame(x + w * 0.55, y + h * 0.04, 34, (238, 128, 32))
    flame(x + w * 0.68, y + h * 0.16, 26, (222, 96, 24))
    flame(x + w * 0.55, y + h * 0.30, 18, (250, 196, 80))
    # tanker, light enough to read against the fire
    tx, ty = x + w * 0.28, y + h * 0.58
    draw.rounded_rectangle([tx * S, ty * S, (tx + w * 0.36) * S, (ty + h * 0.18) * S],
                           radius=9 * S, fill=(196, 198, 200), outline=(40, 39, 41), width=2 * S)
    draw.rectangle([((tx + w * 0.37) * S), (ty + h * 0.05) * S, ((tx + w * 0.47) * S), (ty + h * 0.18) * S],
                   fill=(170, 174, 178), outline=(40, 39, 41), width=2 * S)
    for wx in (0.08, 0.26, 0.42):
        draw.ellipse([((tx + w * wx - 7) * S), ((ty + h * 0.17) * S),
                      ((tx + w * wx + 7) * S), ((ty + h * 0.17 + 14) * S)], fill=(30, 29, 31))


def markets_icon(draw, x, y, w, h):
    draw.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(233, 238, 244))
    pts = [(0.08, 0.62), (0.30, 0.78), (0.48, 0.40), (0.66, 0.58), (0.90, 0.22)]
    coords = [((x + w * px) * S, (y + h * py) * S) for px, py in pts]
    draw.line(coords, fill=(38, 110, 70), width=4 * S)
    for cx, cy in coords:
        draw.ellipse([cx - 4 * S, cy - 4 * S, cx + 4 * S, cy + 4 * S], fill=(38, 110, 70))
    draw.line([((x + w * 0.66) * S, (y + h * 0.58) * S), ((x + w * 0.90) * S, (y + h * 0.22) * S)],
              fill=(38, 110, 70), width=4 * S)


def india_icon(draw, x, y, w, h):
    draw.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(244, 238, 226))
    # three bands across the top, then a columned public building below
    for i, col in enumerate([(232, 128, 52), (250, 248, 242), (52, 140, 82)]):
        draw.rectangle([(x + 12) * S, (y + 7 + i * 8) * S, (x + w - 12) * S, (y + 14 + i * 8) * S], fill=col)
    draw.polygon([((x + w * 0.12) * S, (y + h * 0.52) * S), ((x + w * 0.50) * S, (y + h * 0.36) * S),
                  ((x + w * 0.88) * S, (y + h * 0.52) * S)], fill=(90, 80, 70))
    for i in range(5):
        cx = x + w * (0.22 + i * 0.14)
        draw.rectangle([(cx - 4) * S, (y + h * 0.56) * S, (cx + 4) * S, (y + h * 0.88) * S], fill=(90, 80, 70))
    draw.rectangle([(x + w * 0.14) * S, (y + h * 0.88) * S, (x + w * 0.86) * S, (y + h * 0.95) * S], fill=(90, 80, 70))


def chess_icon(draw, x, y, w, h):
    cell = min(w, h) / 4
    ox, oy = x + (w - cell * 4) / 2, y + (h - cell * 4) / 2
    for r in range(4):
        for c in range(4):
            col = (238, 232, 218) if (r + c) % 2 == 0 else (70, 60, 52)
            draw.rectangle([((ox + c * cell) * S), ((oy + r * cell) * S),
                            ((ox + (c + 1) * cell) * S), ((oy + (r + 1) * cell) * S)], fill=col)
    # pawn, sized to survive the thumbnail
    px, py = ox + cell * 2.5, oy + cell * 1.45
    draw.ellipse([(px - 11) * S, (py - 11) * S, (px + 11) * S, (py + 11) * S], fill=(250, 250, 250), outline=INK, width=2 * S)
    draw.polygon([(px - 14) * S, (py + 32) * S, (px + 14) * S, (py + 32) * S, (px + 6) * S, (py + 9) * S,
                  (px - 6) * S, (py + 9) * S], fill=(250, 250, 250), outline=INK)


def nk_icon(draw, x, y, w, h):
    draw.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(238, 234, 228))
    # closed office door with a bar across it
    dx, dy, dw, dh = x + w * 0.34, y + h * 0.14, w * 0.32, h * 0.74
    draw.rectangle([dx * S, dy * S, (dx + dw) * S, (dy + dh) * S], fill=(120, 96, 74), outline=INK, width=2 * S)
    draw.ellipse([((dx + dw - 12) * S), ((dy + dh * 0.5) * S), ((dx + dw - 5) * S), ((dy + dh * 0.5 + 7) * S)], fill=INK)
    draw.line([((x + w * 0.24) * S, (dy + dh * 0.42) * S), ((x + w * 0.76) * S, (dy + dh * 0.42) * S)],
              fill=RED, width=6 * S)
    draw.line([((x + w * 0.24) * S, (dy + dh * 0.58) * S), ((x + w * 0.76) * S, (dy + dh * 0.58) * S)],
              fill=RED, width=6 * S)


# ---------------------------------------------------------------- page

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    rule(d, 24, 3)
    centred(d, 36, "THE WORLD", SERIF_XB, 96)
    centred(d, 148, "THURSDAY 26 NOVEMBER 2026 — ONE DAY IN ONE IMAGE", SANS_CB, 25, tracking=1)
    rule(d, 188, 4)
    rule(d, 196, 1)

    # lead
    kicker(d, 34, 208, "SPACE — TWO FIRSTS", 21)
    d.text((34 * S, 232 * S), "EIGHT YEARS", font=font(SERIF_XB, 56), fill=INK)
    d.text((34 * S, 292 * S), "TO MERCURY", font=font(SERIF_XB, 56), fill=INK)
    y = text_block(d, 34, 356,
                   "Europe–Japan probe reaches Mercury orbit; first Pakistani astronaut heads to China's Tiangong.",
                   SANS_SB, 21, 500, fill=SOFT)
    y += 4
    for fact in ("BepiColombo arrives after an 8-year journey",
                 "Muhammad Zeeshan Ali selected for Shenzhou-24"):
        d.rectangle([34 * S, (y + 5) * S, 42 * S, (y + 13) * S], fill=RED)
        y = text_block(d, 50, y, fact, SANS_B, 18, 484) + 1
    space_panel(d, 562, 210, 428, 240)

    rule(d, 466, 2)

    # second row
    colombia_panel(d, 34, 480, 462, 96)
    kicker(d, 34, 588, "COLOMBIA", 18)
    d.text((34 * S, 612 * S), "TEN YEARS OF PEACE", font=fit(d, "TEN YEARS OF PEACE", SERIF_B, 33, 462), fill=INK)
    text_block(d, 34, 654, "UN warns peace promises remain unfinished, ten years after the historic deal.",
               SANS_SB, 20, 462, fill=SOFT)

    cairo_panel(d, 528, 480, 462, 96)
    kicker(d, 528, 588, "EGYPT", 18)
    d.text((528 * S, 612 * S), "TANKER FIRE KILLS 30", font=fit(d, "TANKER FIRE KILLS 30", SERIF_B, 33, 462), fill=INK)
    text_block(d, 528, 654, "Fuel tanker crash ignites a massive highway fire near Cairo.",
               SANS_SB, 20, 462, fill=SOFT)
    d.line([512 * S, 480 * S, 512 * S, 700 * S], fill=RULE, width=1 * S)

    rule(d, 706, 2)

    # third row
    panels = [
        ("MARKETS", markets_icon, "AI STOCKS BOUNCE", "Nasdaq & S&P pare losses. Nvidia down 5%."),
        ("INDIA", india_icon, "CONSTITUTION DAY", "6,000 new IIT seats in AI, robotics & space."),
        ("CHESS — GENEVA", chess_icon, "GAME 2 DRAWN", "20 moves. Gukesh defends title vs Sindarov."),
        ("NORTH KOREA", nk_icon, "SWISS OFFICE ORDERED CLOSED", "Pyongyang expels Swiss diplomat in sanctions row."),
    ]
    pw = (956 - 3 * 16) / 4
    for i, (kick, icon, head, sub) in enumerate(panels):
        x = 34 + i * (pw + 16)
        icon(d, x, 718, pw, 66)
        kicker(d, x, 792, kick, 16)
        y = 816
        for line in wrap(d, head, font(SANS_CB, 25), pw):
            d.text((x * S, y * S), line, font=font(SANS_CB, 25), fill=INK)
            y += 29
        text_block(d, x, y + 2, sub, SANS_SB, 18, pw, fill=SOFT)
        if i:
            d.line([(x - 8) * S, 718 * S, (x - 8) * S, 936 * S], fill=RULE, width=1 * S)

    rule(d, 946, 2)
    centred(d, 956, "US confidence near 2-year high · Petrobras $122bn plan", SANS_B, 18, fill=SOFT)
    centred(d, 980, "Bangladesh garment wage +36% · Australia–Solomon Islands security pact", SANS_B, 18, fill=SOFT)
    rule(d, 1006, 1)

    img = img.resize((1024, 1024), Image.LANCZOS)
    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
