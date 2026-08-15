"""
LinkedIn carousel for Nyaysetu — 12 slides, 1080x1350 portrait.

Every figure comes from a verified run against the live deployment, and every
screenshot is a real capture of the running site rather than a mockup. Palette
follows the product: slate ground, amber accent, cream for the light slides.
"""

import os

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

W, H = 1080, 1350
MARGIN = 88
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")

SLATE = HexColor("#0B1220")
SLATE_2 = HexColor("#111C31")
CARD = HexColor("#18243B")
WHITE = HexColor("#FFFFFF")
MUTED = HexColor("#94A3B8")
DIM = HexColor("#64748B")
AMBER = HexColor("#F59E0B")
AMBER_SOFT = HexColor("#FCD34D")
GREEN = HexColor("#34D399")
CREAM = HexColor("#FAF7F0")
INK = HexColor("#0F172A")
INK_SOFT = HexColor("#475569")

BOLD = "Helvetica-Bold"
REG = "Helvetica"
SERIF = "Times-Bold"


# ── primitives ──────────────────────────────────────────────────────────
def wrap(text, font, size, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(c, text, x, y, font, size, colour, leading=None, max_width=None):
    """
    Draw text downward from y, honouring explicit newlines before wrapping.

    `wrap` splits on all whitespace, so a "\\n" passed straight through it is
    lost — which once put "Tamil" and "Telugu" on the same line, reading as one
    language nobody speaks.
    """
    leading = leading or size * 1.26
    max_width = max_width or (W - 2 * MARGIN)
    c.setFont(font, size)
    c.setFillColor(colour)
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            y -= leading
            continue
        for line in wrap(paragraph, font, size, max_width):
            c.drawString(x, y, line)
            y -= leading
    return y


def dark_ground(c):
    """Vertical gradient, so the dark slides have depth rather than flatness."""
    c.saveState()
    c.linearGradient(0, H, 0, 0, [SLATE_2, SLATE], (0, 1), extend=True)
    c.restoreState()


def light_ground(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def glow(c, cx, cy, radius, colour=AMBER):
    """
    Concentric discs, each nearly transparent, largest first.

    Cheaper and more predictable than a radial gradient here: the alpha
    accumulates toward the centre, giving a soft light that never banding-steps
    the way a coarse gradient does at this size.
    """
    steps = 28
    c.saveState()
    c.setFillColor(colour)
    for i in range(steps, 0, -1):
        t = i / steps
        c.setFillAlpha(0.022 * (1 - t) ** 1.4)
        c.circle(cx, cy, radius * t, stroke=0, fill=1)
    c.restoreState()


def rule(c, y, colour=AMBER, width=120, thickness=6):
    c.setFillColor(colour)
    c.rect(MARGIN, y, width, thickness, stroke=0, fill=1)


def eyebrow(c, label, y, colour=AMBER):
    c.setFont(BOLD, 24)
    c.setFillColor(colour)
    c.drawString(MARGIN, y, label.upper())


def shot(c, name, x, y, width, browser_bar=True, max_height=None):
    """
    Place a captured screenshot inside a browser chrome bar.

    Fits within both `width` and `max_height` and re-centres horizontally if the
    height constraint is the binding one. Sizing on width alone let a tall
    capture grow up through the heading above it, which is invisible until you
    render the page and look at it.
    """
    path = os.path.join(SHOTS, f"card_{name}.png")
    if not os.path.exists(path):
        return 0
    reader = ImageReader(path)
    iw, ih = reader.getSize()
    bar = 34 if browser_bar else 0

    height = width * ih / iw
    if max_height and height + bar > max_height:
        height = max_height - bar
        scaled_width = height * iw / ih
        x += (width - scaled_width) / 2
        width = scaled_width
    # Ground plate behind the image so rounded corners read cleanly.
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFillAlpha(0.10)
    c.roundRect(x - 10, y - 10, width + 20, height + bar + 20, 20, stroke=0, fill=1)
    c.setFillAlpha(1)

    if browser_bar:
        c.setFillColor(HexColor("#243349"))
        c.roundRect(x, y, width, height + bar, 16, stroke=0, fill=1)
        for i, dot in enumerate(("#F87171", "#FBBF24", "#34D399")):
            c.setFillColor(HexColor(dot))
            c.circle(x + 26 + i * 26, y + height + bar / 2, 7, stroke=0, fill=1)
        c.setFont(REG, 17)
        c.setFillColor(MUTED)
        c.drawString(x + 120, y + height + bar / 2 - 6, "nyay-setu-sigma.vercel.app")

    c.drawImage(reader, x, y, width=width, height=height, mask="auto")
    return height + bar


def brand(c, dark=True):
    y = 66
    c.setFont(SERIF, 32)
    c.setFillColor(WHITE if dark else INK)
    c.drawString(MARGIN, y, "Nyay")
    c.setFillColor(AMBER)
    c.drawString(MARGIN + stringWidth("Nyay", SERIF, 32), y, "setu")


def footer(c, n, dark=True):
    brand(c, dark)
    c.setFont(REG, 22)
    c.setFillColor(DIM)
    label = f"{n} / 12"
    c.drawString(W - MARGIN - stringWidth(label, REG, 22), 66, label)
    # Swipe nudge on the early slides only.
    if n < 12:
        c.setFont(REG, 22)
        c.setFillColor(AMBER if dark else HexColor("#B45309"))
        hint = "swipe →"
        c.drawString(W / 2 - stringWidth(hint, REG, 22) / 2, 66, hint)
    c.showPage()


# ── slides ──────────────────────────────────────────────────────────────
def build(path):
    c = canvas.Canvas(path, pagesize=(W, H))

    # 1 — hook
    dark_ground(c)
    glow(c, W * 0.78, H * 0.80, 620)
    rule(c, H - 232)
    y = text_block(c, "Most legal chatbots", MARGIN, H - 376, BOLD, 76, WHITE, 90)
    y = text_block(c, "will confidently give", MARGIN, y, BOLD, 76, WHITE, 90)
    y = text_block(c, "you the wrong", MARGIN, y, BOLD, 76, WHITE, 90)
    y = text_block(c, "section number.", MARGIN, y, BOLD, 76, AMBER, 90)
    text_block(c, "So I built one that can't.", MARGIN, y - 60, REG, 38, MUTED)
    footer(c, 1)

    # 2 — the stakes
    light_ground(c)
    rule(c, H - 232, INK)
    y = text_block(c, "A wrong answer isn't", MARGIN, H - 360, BOLD, 64, INK, 78)
    y = text_block(c, "a worse answer.", MARGIN, y, BOLD, 64, INK, 78)
    y = text_block(c, "It's a harmful one.", MARGIN, y - 14, BOLD, 64, HexColor("#B45309"), 78)
    text_block(
        c,
        "Ask whether you can still sue your landlord. If the "
        "limitation period is off by a year, you don't get a "
        "slightly worse answer — you lose the claim entirely.",
        MARGIN,
        y - 76,
        REG,
        37,
        INK_SOFT,
        52,
    )
    footer(c, 2, dark=False)

    # 3 — the inversion
    dark_ground(c)
    glow(c, W * 0.2, H * 0.28, 520)
    eyebrow(c, "the design", H - 250)
    y = text_block(c, "Retrieval produces", MARGIN, H - 350, BOLD, 66, WHITE, 80)
    y = text_block(c, "the law.", MARGIN, y, BOLD, 66, WHITE, 80)
    y = text_block(c, "The model only", MARGIN, y - 10, BOLD, 66, AMBER, 80)
    y = text_block(c, "phrases it.", MARGIN, y, BOLD, 66, AMBER, 80)
    text_block(
        c,
        "Every answer is built from 152 curated passages across "
        "92 Indian Acts, each carrying its section and a source "
        "you can open.\n\n"
        "The model never writes a section number, because it "
        "never gets to invent one.",
        MARGIN,
        y - 70,
        REG,
        36,
        HexColor("#CBD5E1"),
        50,
    )
    footer(c, 3)

    # 4 — the corpus, with a real screenshot
    dark_ground(c)
    eyebrow(c, "cited, not recalled", H - 240)
    text_block(c, "152 passages. 92 Acts.", MARGIN, H - 320, BOLD, 52, WHITE, 64)
    shot(c, "knowledge", MARGIN, 210, W - 2 * MARGIN, max_height=740)
    footer(c, 4)

    # 5 — the numbers
    dark_ground(c)
    glow(c, W * 0.85, H * 0.24, 480, GREEN)
    eyebrow(c, "measured, not asserted", H - 240)
    text_block(c, "The retrieval eval", MARGIN, H - 322, BOLD, 56, WHITE, 68)
    stats = [
        ("131", "test questions, each naming the passage that should come back", AMBER),
        ("92.4%", "hit@1 — the right passage ranked first", AMBER),
        ("100%", "hit@3 — always in the top three", AMBER),
        ("0 / 14", "off-topic questions answered", GREEN),
    ]
    y = H - 470
    for value, label, colour in stats:
        c.setFillColor(CARD)
        c.roundRect(MARGIN, y - 74, W - 2 * MARGIN, 108, 16, stroke=0, fill=1)
        c.setFont(BOLD, 56)
        c.setFillColor(colour)
        c.drawString(MARGIN + 34, y - 42, value)
        c.setFont(REG, 27)
        c.setFillColor(HexColor("#CBD5E1"))
        for i, line in enumerate(wrap(label, REG, 27, W - MARGIN * 2 - 300)):
            c.drawString(MARGIN + 270, y - 28 - i * 34, line)
        y -= 132
    footer(c, 5)

    # 6 — saying I don't know
    light_ground(c)
    rule(c, H - 232, INK)
    y = text_block(c, "It has to be able", MARGIN, H - 356, BOLD, 62, INK, 76)
    y = text_block(c, 'to say "I don\'t know."', MARGIN, y, BOLD, 62, INK, 76)
    y = text_block(
        c,
        "That turned out to be the hardest part — and the part "
        "I could actually measure.",
        MARGIN,
        y - 60,
        REG,
        37,
        INK_SOFT,
        52,
    )
    c.setFillColor(HexColor("#ECFDF5"))
    c.roundRect(MARGIN, y - 220, W - 2 * MARGIN, 180, 18, stroke=0, fill=1)
    text_block(
        c,
        "Several guards have to agree before it answers at all.\n"
        "A tool that guesses about a deadline is worse than no tool.",
        MARGIN + 40,
        y - 90,
        REG,
        32,
        HexColor("#065F46"),
        46,
        W - 2 * MARGIN - 80,
    )
    footer(c, 6, dark=False)

    # 7 — the toolkit, with a real screenshot
    dark_ground(c)
    eyebrow(c, "beyond the assistant", H - 240)
    text_block(c, "Nine tools. No model.", MARGIN, H - 320, BOLD, 52, WHITE, 64)
    shot(c, "toolkit", MARGIN + 90, 190, W - 2 * MARGIN - 180, max_height=790)
    footer(c, 7)

    # 8 — the case plan
    dark_ground(c)
    glow(c, W * 0.18, H * 0.72, 520)
    eyebrow(c, "the whole answer", H - 250)
    y = text_block(c, "One situation.", MARGIN, H - 350, BOLD, 62, WHITE, 76)
    y = text_block(c, "One date.", MARGIN, y, BOLD, 62, AMBER, 76)
    items = [
        "where to file",
        "every deadline, in the order they fall",
        "what it costs",
        "the letter to send first",
        "what happens after you file",
    ]
    y -= 60
    for item in items:
        c.setFillColor(AMBER)
        c.circle(MARGIN + 11, y + 11, 7, stroke=0, fill=1)
        c.setFont(REG, 35)
        c.setFillColor(WHITE)
        c.drawString(MARGIN + 46, y, item)
        y -= 62
    text_block(
        c,
        "Lookup tables and calendar arithmetic — instant, "
        "identical every time, and it works with no network.",
        MARGIN,
        y - 26,
        REG,
        30,
        MUTED,
        44,
    )
    footer(c, 8)

    # 9 — languages
    dark_ground(c)
    eyebrow(c, "eight languages", H - 240)
    y = text_block(
        c,
        "Hindi · Marathi · Gujarati · Tamil\nTelugu · Bengali · Kannada · English",
        MARGIN,
        H - 330,
        BOLD,
        44,
        WHITE,
        62,
    )
    c.setFillColor(CARD)
    c.roundRect(MARGIN, y - 300, W - 2 * MARGIN, 290, 20, stroke=0, fill=1)
    text_block(
        c,
        "Every English metric was green while a Hindi speaker "
        "asking about a withheld deposit got nothing at all. "
        "The aggregate hid it completely.",
        MARGIN + 40,
        y - 70,
        REG,
        32,
        HexColor("#E2E8F0"),
        46,
        W - 2 * MARGIN - 80,
    )
    c.setFont(BOLD, 46)
    c.setFillColor(GREEN)
    c.drawString(MARGIN + 40, y - 250, "0%  →  93%")
    c.setFont(REG, 26)
    c.setFillColor(MUTED)
    c.drawString(MARGIN + 330, y - 245, "once I scored the languages apart")
    footer(c, 9)

    # 10 — the pizza bug
    light_ground(c)
    rule(c, H - 232, INK)
    y = text_block(c, "A bigger knowledge base", MARGIN, H - 350, BOLD, 54, INK, 68)
    y = text_block(c, "makes it easier to be wrong", MARGIN, y, BOLD, 54, INK, 68)
    c.setFillColor(HexColor("#FEF3C7"))
    c.roundRect(MARGIN, y - 218, W - 2 * MARGIN, 186, 18, stroke=0, fill=1)
    text_block(
        c,
        '"the best pizza in town"',
        MARGIN + 40,
        y - 96,
        BOLD,
        38,
        HexColor("#92400E"),
        50,
        W - 2 * MARGIN - 80,
    )
    text_block(
        c,
        "returned street-vending law",
        MARGIN + 40,
        y - 156,
        REG,
        34,
        HexColor("#92400E"),
        46,
        W - 2 * MARGIN - 80,
    )
    text_block(
        c,
        "It matched “Town Vending Committee”. No score threshold "
        "separates that from a real one-word match on “cheque”. "
        "The fix was to ask where the word appears, not how rare "
        "it is.",
        MARGIN,
        y - 280,
        REG,
        34,
        INK_SOFT,
        48,
    )
    footer(c, 10, dark=False)

    # 11 — the invented judges
    dark_ground(c)
    glow(c, W * 0.8, H * 0.3, 500, HexColor("#F87171"))
    eyebrow(c, "the last guard", H - 240, HexColor("#FCA5A5"))
    y = text_block(c, "Asked a question it", MARGIN, H - 330, BOLD, 58, WHITE, 72)
    y = text_block(c, "can't answer, a model", MARGIN, y, BOLD, 58, WHITE, 72)
    y = text_block(c, "will invent one.", MARGIN, y, BOLD, 58, HexColor("#FCA5A5"), 72)
    text_block(
        c,
        "Asked in Hindi who the current Chief Justice is, a local "
        "model replied with a list of judges out of its training "
        "data.\n\n"
        "The corpus names nobody — deliberately. Nothing in it can "
        "keep a name current. That's now a guard, not a hope.",
        MARGIN,
        y - 70,
        REG,
        34,
        HexColor("#CBD5E1"),
        48,
    )
    footer(c, 11)

    # 12 — CTA
    dark_ground(c)
    glow(c, W / 2, H * 0.42, 700, GREEN)
    y = text_block(c, "Free legal aid is a", MARGIN, H - 380, BOLD, 60, WHITE, 74)
    y = text_block(c, "statutory right for", MARGIN, y, BOLD, 60, WHITE, 74)
    y = text_block(c, "most people in India.", MARGIN, y, BOLD, 60, WHITE, 74)
    y = text_block(c, "Very few know it.", MARGIN, y - 16, BOLD, 60, AMBER, 74)

    c.setFillColor(CARD)
    c.roundRect(MARGIN, 290, W - 2 * MARGIN, 230, 20, stroke=0, fill=1)
    text_block(
        c,
        "Try it — no signup to ask a question",
        MARGIN + 40,
        460,
        REG,
        30,
        MUTED,
        42,
        W - 2 * MARGIN - 80,
    )
    text_block(
        c,
        "nyay-setu-sigma.vercel.app",
        MARGIN + 40,
        390,
        BOLD,
        40,
        GREEN,
        52,
        W - 2 * MARGIN - 80,
    )
    text_block(
        c,
        "Next.js · FastAPI · Postgres · open source",
        MARGIN + 40,
        330,
        REG,
        26,
        DIM,
        36,
        W - 2 * MARGIN - 80,
    )
    footer(c, 12)

    c.save()


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "nyaysetu_carousel.pdf"
    build(out)
    print(f"wrote {out}")
