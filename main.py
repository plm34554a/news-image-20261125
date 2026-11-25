#!/usr/bin/env python3
"""news-image-20261125: a front-page image summing up the world news of
Wednesday 25 November 2026. Pure Python 3.13 stdlib (zlib/struct for PNG).
Draws a 1024x1024 newspaper front page with a small built-in 5x7 bitmap
font: no external fonts, images or network. Deterministic: two runs write
byte-identical files.

Run:  python3 main.py        (writes $MAKEFUN_OUTPUT_DIR/entry.png,
                              or /output/entry.png when unset)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # warm newsprint
INK = (18, 30, 54)        # deep navy
INK_SOFT = (52, 66, 96)
RED = (178, 34, 27)       # masthead red
GOLD = (198, 158, 44)
DARK = (13, 22, 42)       # lead panel background
DARK2 = (24, 38, 68)
CREAM = (246, 241, 227)
GREY = (120, 122, 118)
LIGHT = (214, 222, 235)   # pale blue-grey text on dark
WHITE = (255, 255, 255)
TEAL = (31, 120, 110)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 bits, '#' = on. Uppercase + digits + punctuation.
# Text is upper-cased before drawing, so only these glyphs are needed.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '\u2022': ("00000", "00100", "01110", "01110", "01110", "00100", "00000"),
}

CHAR_W = 6  # glyph advance in font units (5 px + 1 px gap)


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    return len(text) * CHAR_W * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for deg in range(0, 360):
                import math
                a = math.radians(deg)
                self.put(cx + int(rr * math.cos(a)), cy + int(rr * math.sin(a)), c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT['?'])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def block(self, x, y, s, scale, c, max_w, leading=None):
        """Wrapped paragraph; returns y just below the last line."""
        lh = leading if leading is not None else 7 * scale + 3
        for line in wrap(s, scale, max_w):
            self.text(x, y, line, scale, c)
            y += lh
        return y


# ------------------------------------------------------------- decorations
def draw_globe(cv, cx, cy, r):
    """Wireframe globe: circle, meridians, parallels, gold on dark."""
    import math
    cv.ring(cx, cy, r, GOLD, 3)
    for k in range(-2, 3):
        off = k * r // 3
        half = int((r * r - off * off) ** 0.5)
        cv.hline(cx - half, cy + off, 2 * half, GOLD, 1)
    for k in range(-2, 3):
        rx = abs(k) * r // 3
        ry = r
        for deg in range(0, 360):
            a = math.radians(deg)
            px = cx + int(rx * math.cos(a))
            py = cy + int(ry * math.sin(a))
            if abs(px - cx) <= r:
                cv.put(px, py, GOLD)
    cv.vline(cx, cy - r, 2 * r, GOLD, 1)


def draw_lock(cv, x, y, s, body, metal):
    """Padlock: shackle arc + body + keyhole."""
    import math
    w, h = 34 * s, 30 * s
    for deg in range(180, 361, 2):
        a = math.radians(deg)
        px = x + w // 2 + int(11 * s * math.cos(a))
        py = y + 8 * s + int(11 * s * math.sin(a))
        cv.fill_rect(px - s, py - s, 2 * s, 2 * s, metal)
    cv.fill_rect(x, y + 8 * s, w, h, body)
    cv.rect(x, y + 8 * s, w, h, metal, 2 * s)
    cv.disc(x + w // 2, y + 18 * s, 4 * s, metal)
    cv.fill_rect(x + w // 2 - s, y + 18 * s, 2 * s, 9 * s, metal)


def draw_binary_rain(cv, x, y, w, h, color):
    """Deterministic columns of 0s and 1s (seeded pattern, no randomness)."""
    cols = w // 26
    for col in range(cols):
        n = (col * 7 + 3) % 5 + 2
        for k in range(n):
            ch = '1' if (col * 3 + k * 5) % 2 else '0'
            cv.text(x + col * 26, y + k * 20, ch, 1, color)


def draw_tower(cv, x, y, h, c):
    """Riyadh tower: tall slab with stepped crown and spire."""
    w = 26
    cv.fill_rect(x, y + 30, w, h - 30, c)
    cv.fill_rect(x + 4, y + 18, w - 8, 12, c)
    cv.fill_rect(x + 9, y + 6, w - 18, 12, c)
    cv.vline(x + w // 2, y, 8, c, 2)
    for i in range(4):  # lit windows
        cv.fill_rect(x + 5, y + 44 + i * 18, 4, 8, GOLD)
        cv.fill_rect(x + 17, y + 44 + i * 18, 4, 8, GOLD)
    # impact burst above the crown
    cx, cy = x + w // 2, y - 6
    for dx, dy in ((0, -14), (12, -10), (-12, -10), (16, 0), (-16, 0),
                   (10, 8), (-10, 8)):
        cv.line(cx, cy, cx + dx, cy + dy, RED)


def draw_ship(cv, x, y, w, c):
    """Cargo ship on waves with a small drone above."""
    cv.fill_rect(x, y, w, 14, c)
    cv.fill_rect(x + 8, y - 16, w // 3, 16, c)
    cv.fill_rect(x + w // 2, y - 26, 10, 10, c)
    for i in range(3):
        cv.fill_rect(x + 14 + i * 16, y - 12, 8, 6, GOLD)
    for i in range(4):  # waves
        wx = x + i * (w // 4)
        cv.line(wx, y + 22, wx + 12, y + 18, c)
        cv.line(wx + 12, y + 18, wx + 24, y + 22, c)
    # drone quad
    dx, dy = x + w - 18, y - 52
    cv.fill_rect(dx - 6, dy - 3, 12, 6, RED)
    cv.disc(dx - 10, dy - 6, 4, INK)
    cv.disc(dx + 10, dy - 6, 4, INK)
    cv.disc(dx - 10, dy + 6, 4, INK)
    cv.disc(dx + 10, dy + 6, 4, INK)


def draw_chip(cv, x, y, s, c):
    """Microchip with pins."""
    w = 30 * s
    for i in range(4):
        cv.fill_rect(x - 6 * s, y + (5 + i * 7) * s, 6 * s, 2 * s, c)
        cv.fill_rect(x + w, y + (5 + i * 7) * s, 6 * s, 2 * s, c)
        cv.fill_rect(x + (5 + i * 7) * s, y - 6 * s, 2 * s, 6 * s, c)
        cv.fill_rect(x + (5 + i * 7) * s, y + w, 2 * s, 6 * s, c)
    cv.fill_rect(x, y, w, w, c)
    cv.rect(x + 6 * s, y + 6 * s, w - 12 * s, w - 12 * s, PAPER, 2 * s)
    cv.text(x + 10 * s, y + 12 * s, "IP", 1, PAPER)


def draw_medal(cv, x, y, r, c):
    """Gold medal on ribbons."""
    cv.fill_rect(x - 8, y - r - 26, 7, 26, RED)
    cv.fill_rect(x + 2, y - r - 26, 7, 26, INK)
    cv.disc(x, y, r, c)
    cv.ring(x, y, r - 4, WHITE, 2)
    cv.disc(x, y, 5, RED)


def draw_ballot(cv, x, y, w, c):
    """Ballot box with a check mark."""
    cv.fill_rect(x, y, w, w * 3 // 4, c)
    cv.fill_rect(x + 4, y - 8, w - 8, 8, c)
    cv.line(x + 8, y + w // 3, x + w // 3, y + w // 2, WHITE)
    cv.line(x + w // 3, y + w // 2, x + w - 8, y + 4, WHITE)


def draw_bat_ball(cv, x, y, c):
    """Cricket bat and ball."""
    cv.line(x, y + 44, x + 26, y + 4, c)
    cv.line(x + 6, y + 44, x + 32, y + 4, c)
    cv.line(x, y + 44, x + 6, y + 44, c)
    cv.line(x + 26, y + 4, x + 32, y + 4, c)
    cv.fill_rect(x + 24, y - 6, 12, 16, c)  # handle
    cv.disc(x + 52, y + 34, 11, RED)
    cv.ring(x + 52, y + 34, 6, WHITE, 1)


def draw_cross(cv, x, y, s, c):
    """Medical cross in a ring."""
    cv.disc(x, y, 26 * s, c)
    cv.fill_rect(x - 4 * s, y - 14 * s, 8 * s, 28 * s, WHITE)
    cv.fill_rect(x - 14 * s, y - 4 * s, 28 * s, 8 * s, WHITE)


# ------------------------------------------------------------------- page
def story_panel(cv, x, y, w, h, kicker, headline, deck, motif=None):
    """White panel: red kicker, navy headline, grey deck, optional motif.

    When a motif is drawn in the lower-right corner, the headline and deck
    are wrapped to a narrower width so no text ever runs under the motif.
    """
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 5, RED)
    pad = 16
    text_w = w - 2 * pad - (84 if motif is not None else 0)
    tx = x + pad
    ty = y + 16
    cv.text(tx, ty, kicker, 2, RED)
    ty += 24
    ty = cv.block(tx, ty, headline, 3, INK, text_w, leading=24)
    ty += 4
    cv.block(tx, ty, deck, 2, INK_SOFT, text_w, leading=17)
    if motif is not None:
        motif(x + w - 74, y + h - 78)


def build():
    cv = Canvas(W, H, PAPER)
    # thin double frame around the whole page
    cv.rect(10, 10, W - 20, H - 20, INK, 2)
    cv.rect(16, 16, W - 32, H - 32, INK, 1)

    # ---------------------------------------------------------- masthead
    cv.text_center(W // 2, 34, "THE WORLD TODAY", 7, INK)
    cv.hline(60, 92, W - 120, INK, 2)
    cv.hline(60, 97, W - 120, RED, 3)
    # date band: the day, named loud and clear
    cv.fill_rect(60, 108, W - 120, 44, RED)
    cv.text_center(W // 2, 118, "WEDNESDAY 25 NOVEMBER 2026", 4, WHITE)
    cv.text_center(W // 2, 160, "ONE DAY  *  ONE IMAGE  *  THE WORLD'S NEWS",
                   2, INK_SOFT)

    # ------------------------------------------------------------- lead
    lx, ly, lw, lh = 28, 186, 612, 392
    cv.fill_rect(lx, ly, lw, lh, DARK)
    cv.rect(lx, ly, lw, lh, INK, 2)
    draw_binary_rain(cv, lx + 14, ly + 58, 150, 300, (46, 64, 100))
    draw_globe(cv, lx + 150, ly + 150, 92)
    draw_lock(cv, lx + 430, ly + 84, 2, RED, GOLD)
    cv.fill_rect(lx + 14, ly + 14, 148, 26, RED)
    cv.text(lx + 26, ly + 20, "LEAD STORY", 2, WHITE)
    cv.text(lx + 14, ly + 268, "CIA AND SPY CHIEF", 3, WHITE)
    cv.text(lx + 14, ly + 296, "HIT BY CYBER", 3, WHITE)
    cv.text(lx + 14, ly + 324, "INTRUSION", 3, GOLD)
    cv.block(lx + 14, ly + 356, "Classified data affected, sources say - "
             "latest in a string of US government breaches.", 2, LIGHT,
             lw - 28, leading=17)

    # ------------------------------------------------------- right column
    rx, rw = 656, 340
    story_panel(cv, rx, 186, rw, 188, "TECH / TRADE",
                "HUAWEI FOUND GUILTY",
                "US jury convicts on 10 of 12 counts, incl. trade-secret theft.",
                lambda mx, my: draw_chip(cv, mx, my, 1, INK))
    story_panel(cv, rx, 390, rw, 188, "UKRAINE WAR",
                "WAR AT SEA ESCALATES",
                "Kyiv drone hits Russian ship; Putin vows reply; NATO jets to Poland.",
                lambda mx, my: draw_ship(cv, mx - 30, my + 26, 84, INK))

    # ------------------------------------------------------------- row 2
    y2, h2, w2 = 594, 196, 316
    x0, x1, x2 = 28, 356, 684
    story_panel(cv, x0, y2, w2, h2, "MIDDLE EAST",
                "HOUTHIS STRIKE RIYADH",
                "Drone hits the capital's tallest tower; 11 wounded.",
                lambda mx, my: draw_tower(cv, mx + 16, my + 8, 62, INK))
    story_panel(cv, x1, y2, w2, h2, "WASHINGTON",
                "TRUMP HONOURS GIULIANI",
                "Medal of Freedom on Thanksgiving eve; turkeys pardoned.",
                lambda mx, my: draw_medal(cv, mx + 26, my + 44, 20, GOLD))
    story_panel(cv, x2, y2, w2, h2, "INDIA",
                "BJP-AKALI ALLIANCE BACK",
                "Punjab pact for 2027 after a six-year split; Nepal PM visits.",
                lambda mx, my: draw_ballot(cv, mx + 8, my + 18, 44, INK))

    # ------------------------------------------------------------- row 3
    y3, h3, w3 = 806, 130, 484
    story_panel(cv, 28, y3, w3, h3, "SPORT",
                "ENGLAND LEVEL T20 SERIES",
                "Beat Australia by 8 wickets, chasing 185.",
                lambda mx, my: draw_bat_ball(cv, mx + 6, my + 8, INK))
    story_panel(cv, 512, y3, w3, h3, "AFRICA / HEALTH",
                "DRC: EBOLA AND WAR",
                "WHO pulls staff from Ituri hospital amid fighting.",
                lambda mx, my: draw_cross(cv, mx + 30, my + 40, 1, TEAL))

    # ------------------------------------------------------------ ticker
    ty = 950
    cv.fill_rect(28, ty, 968, 46, INK)
    cv.text(44, ty + 7, "ALSO TODAY: DAY TO END VIOLENCE AGAINST WOMEN  *  "
            "GTA 6 OUT WORLDWIDE", 2, WHITE)
    cv.text(44, ty + 27, "TRUMP TO MEET NATO CHIEF RUTTE  *  "
            "US READIES NEW TARIFFS", 2, GOLD)
    return cv


# -------------------------------------------------------------- PNG write
def png_bytes(cv):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
