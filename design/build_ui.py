# -*- coding: utf-8 -*-
"""
Generator desain UI/UX FigCraft untuk aplikasi Streamlit
"Favorita Store Sales Forecasting" (Mini Project Kelompok 7).

Jalankan:  python build_ui.py
Hasil   :  Favorita_Forecast_Streamlit_UI.figcraft + PNG preview di folder exports/
"""
import json, math, os, subprocess, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
FC = r"C:\Program Files\ArtCraft\FigCraft\figcraft-cli.exe"
OUT = os.path.join(HERE, "Favorita_Forecast_Streamlit_UI.figcraft")
SCRIPT = os.path.join(HERE, "_build_script.json")

# ------------------------------------------------------------------ tokens
C = dict(
    bg="#0B1120", side="#0E1528", card="#131C31", card2="#1A2440", inp="#0D1426",
    border="#25314D", border2="#33415F", text="#F1F5F9", muted="#94A3B8", dim="#64748B",
    primary="#6366F1", violet="#8B5CF6", cyan="#22D3EE", green="#10B981", amber="#F59E0B",
    red="#F43F5E", pink="#EC4899", white="#FFFFFF", sky="#38BDF8",
)
GRAD = {"type": "linearGradient", "stops": ["#6366F1", "#8B5CF6"]}
GRAD_HERO = {"type": "linearGradient", "stops": ["#4338CA", "#7C3AED", "#DB2777"]}
GRAD_CYAN = {"type": "linearGradient", "stops": ["#0EA5E9", "#22D3EE"]}
GRAD_GREEN = {"type": "linearGradient", "stops": ["#059669", "#34D399"]}
SHADOW = [{"type": "dropShadow", "color": "#00000059", "offset": [0, 12], "radius": 32}]
GLOW = [{"type": "dropShadow", "color": "#6366F155", "offset": [0, 8], "radius": 28}]


def fmt(n, d=0):
    s = f"{n:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


HARI = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
HARI_FULL = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def dlabel(d):
    return f"{d.day} {BULAN[d.month - 1]}"


# ------------------------------------------------------------------ builder
class B:
    def __init__(self):
        self.steps, self.nid = [], 2

    def _add(self, cmd, params, creates=True):
        self.steps.append({"command": cmd, "params": params})
        if creates:
            i = self.nid
            self.nid += 1
            return i

    def page(self, name):
        return self._add("page.add", {"name": name})

    def rename_page(self, name):
        self._add("page.rename", {"name": name}, creates=False)

    def frame(self, x, y, w, h, parent=None, name=None, **props):
        if "fill" not in props and "fills" not in props:
            props["fill"] = "none"
        p = {"x": round(x, 1), "y": round(y, 1), "width": round(w, 1), "height": round(h, 1),
             "props": props, "select": False}
        if parent is not None:
            p["parent"] = parent
        if name:
            p["name"] = name
        return self._add("frame.create", p)

    def rect(self, x, y, w, h, parent, name=None, **props):
        p = {"x": round(x, 1), "y": round(y, 1), "width": round(max(w, 0.5), 1),
             "height": round(max(h, 0.5), 1), "parent": parent, "props": props, "select": False}
        if name:
            p["name"] = name
        return self._add("shape.rectangle", p)

    def ellipse(self, x, y, w, h, parent, **props):
        return self._add("shape.ellipse", {"x": round(x, 1), "y": round(y, 1), "width": w, "height": h,
                                           "parent": parent, "props": props, "select": False})

    def text(self, t, x, y, parent, size=14, weight="Regular", color=None, width=None,
             align=None, lh=None, family="Inter", **props):
        pr = {"fontSize": size, "fontFamily": family, "fontStyle": weight, "fill": color or C["text"]}
        if align:
            pr["textAlign"] = align
        if lh:
            pr["lineHeight"] = lh
        pr.update(props)
        p = {"text": t, "x": round(x, 1), "y": round(y, 1), "parent": parent, "props": pr, "select": False}
        if width:
            p["width"] = round(width, 1)
        return self._add("text.create", p)

    def poly(self, pts, parent, stroke=None, sw=2, fill="none", closed=False, **props):
        pr = {"fill": fill}
        if stroke:
            pr.update(stroke=stroke, strokeWeight=sw, strokeJoin="round", strokeCap="round")
        else:
            pr["stroke"] = "none"
        pr.update(props)
        return self._add("vector.create", {"points": [[round(a, 1), round(c, 1)] for a, c in pts],
                                           "closed": closed, "x": 0, "y": 0, "parent": parent,
                                           "props": pr, "select": False})

    def arrow(self, x, y, length, parent, rot=0, color=None):
        return self._add("shape.arrow", {"x": x, "y": y, "width": length, "parent": parent,
                                         "props": {"rotation": rot, "stroke": color or C["muted"],
                                                   "strokeWeight": 2}, "select": False})


b = B()

# ------------------------------------------------------------------ components


def card(p, x, y, w, h, title=None, sub=None, fill=None, radius=16, name=None, shadow=False, stroke=None):
    pr = dict(fill=fill or C["card"], cornerRadius=radius, stroke=stroke or C["border"], strokeWeight=1, clip=True)
    if shadow:
        pr["effects"] = SHADOW
    f = b.frame(x, y, w, h, p, name or (title or "Card"), **pr)
    if title:
        b.text(title, 20, 18, f, 15, "Bold")
    if sub:
        b.text(sub, 20, 41, f, 12, color=C["muted"], width=w - 40)
    return f


def button(p, x, y, label, kind="primary", w=None, h=40, size=13):
    w = w or int(len(label) * size * 0.56 + 36)
    pr = {"cornerRadius": 10}
    col = C["white"]
    if kind == "primary":
        pr["fills"] = [GRAD]
        pr["effects"] = GLOW
    elif kind == "secondary":
        pr.update(fill=C["card2"], stroke=C["border2"], strokeWeight=1)
    elif kind == "ghost":
        pr.update(fill="none", stroke=C["border2"], strokeWeight=1)
        col = C["muted"]
    elif kind == "success":
        pr["fills"] = [GRAD_GREEN]
    elif kind == "danger":
        pr.update(fill=C["red"] + "22", stroke=C["red"], strokeWeight=1)
        col = C["red"]
    elif kind == "white":
        pr.update(fill=C["white"])
        col = "#312E81"
    f = b.frame(x, y, w, h, p, "Button/" + label, **pr)
    b.text(label, 0, (h - size * 1.21) / 2, f, size, "Bold" if kind in ("primary", "white") else "Medium",
           col, width=w, align="center")
    return w


def badge(p, x, y, label, color, size=11, h=24, solid=False):
    w = int(len(label) * size * 0.6 + 20)
    f = b.frame(x, y, w, h, p, "Badge/" + label, fill=(color if solid else color + "24"), cornerRadius=h / 2)
    b.text(label, 0, (h - size * 1.21) / 2, f, size, "Bold", C["white"] if solid else color, width=w, align="center")
    return w


def select(p, x, y, w, label, value, icon="▾", help_=False):
    b.text(label, x, y, p, 12, "Medium", C["muted"])
    if help_:
        b.text("ⓘ", x + len(label) * 6.9 + 6, y - 1, p, 12, color=C["dim"])
    f = b.frame(x, y + 20, w, 40, p, "Select/" + label, fill=C["inp"], stroke=C["border2"], strokeWeight=1,
                cornerRadius=10)
    b.text(value, 14, 11, f, 13, "Medium", width=w - 44)
    b.text(icon, w - 30, 10, f, 14, color=C["muted"])
    return f


def slider(p, x, y, w, label, val, frac, lo="", hi="", color=None):
    color = color or C["primary"]
    b.text(label, x, y, p, 12, "Medium", C["muted"])
    b.text(val, x + w - 160, y - 1, p, 13, "Bold", C["text"], width=160, align="right")
    b.rect(x, y + 30, w, 6, p, fill=C["border"], cornerRadius=3)
    b.rect(x, y + 30, w * frac, 6, p, fills=[{"type": "linearGradient", "stops": [color, C["violet"]]}],
           cornerRadius=3)
    b.ellipse(x + w * frac - 9, y + 24, 18, 18, p, fill=C["white"], stroke=color, strokeWeight=3,
              effects=GLOW)
    if lo:
        b.text(lo, x, y + 46, p, 11, color=C["dim"])
    if hi:
        b.text(hi, x + w - 80, y + 46, p, 11, color=C["dim"], width=80, align="right")


def toggle(p, x, y, label, on=True, sub=None):
    b.rect(x, y, 40, 22, p, fills=[GRAD] if on else [C["border2"]], cornerRadius=11)
    b.ellipse(x + (20 if on else 2), y + 2, 18, 18, p, fill=C["white"])
    b.text(label, x + 52, y + 2, p, 13, "Medium")
    if sub:
        b.text(sub, x + 52, y + 21, p, 11, color=C["dim"])


def checkbox(p, x, y, label, on=True):
    if on:
        b.rect(x, y, 18, 18, p, fills=[GRAD], cornerRadius=5)
        b.text("✓", x + 3, y - 1, p, 13, "Bold", C["white"])
    else:
        b.rect(x, y, 18, 18, p, fill=C["inp"], stroke=C["border2"], strokeWeight=1.5, cornerRadius=5)
    b.text(label, x + 28, y, p, 13)


def radio(p, x, y, label, on=False):
    b.ellipse(x, y, 18, 18, p, fill=C["inp"], stroke=C["primary"] if on else C["border2"], strokeWeight=2)
    if on:
        b.ellipse(x + 5, y + 5, 8, 8, p, fill=C["primary"])
    b.text(label, x + 28, y, p, 13)


def tabs(p, x, y, items, active=0, w_total=None):
    cx = x
    for i, t in enumerate(items):
        tw = len(t) * 7.4 + 28
        on = i == active
        b.text(t, cx, y, p, 13, "Bold" if on else "Medium", C["text"] if on else C["muted"], width=tw, align="center")
        if on:
            b.rect(cx, y + 28, tw, 3, p, fills=[GRAD], cornerRadius=2)
        cx += tw + 6
    b.rect(x, y + 31, (w_total or (cx - x)), 1, p, fill=C["border"])


def segmented(p, x, y, items, active=0, item_w=70, h=34):
    w = item_w * len(items) + 8
    f = b.frame(x, y, w, h, p, "Segmented", fill=C["inp"], stroke=C["border2"], strokeWeight=1, cornerRadius=10)
    for i, t in enumerate(items):
        if i == active:
            b.rect(4 + i * item_w, 4, item_w, h - 8, f, fills=[GRAD], cornerRadius=7)
        b.text(t, 4 + i * item_w, (h - 15) / 2, f, 12, "Bold" if i == active else "Medium",
               C["white"] if i == active else C["muted"], width=item_w, align="center")
    return w


def progress(p, x, y, w, frac, color=None, h=8, bg=None):
    b.rect(x, y, w, h, p, fill=bg or C["border"], cornerRadius=h / 2)
    b.rect(x, y, max(w * frac, h), h, p, fill=color or C["primary"], cornerRadius=h / 2)


def alert(p, x, y, w, h, kind, title, body):
    col = {"info": C["sky"], "success": C["green"], "warning": C["amber"], "error": C["red"], "tip": C["violet"]}[kind]
    ico = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "⛔", "tip": "💡"}[kind]
    f = b.frame(x, y, w, h, p, "Alert/" + kind, fill=col + "14", stroke=col + "55", strokeWeight=1, cornerRadius=12,
                clip=True)
    b.rect(0, 0, 4, h, f, fill=col)
    b.text(ico, 16, 13, f, 16)
    b.text(title, 46, 13, f, 13, "Bold", col, width=w - 60)
    b.text(body, 46, 33, f, 12, color=C["muted"], width=w - 62, lh="150%")
    return f


def icon_tile(p, x, y, emoji, color, s=40):
    b.rect(x, y, s, s, p, fill=color + "26", cornerRadius=s * 0.3)
    b.text(emoji, x, y + (s - s * 0.5 * 1.25) / 2, p, s * 0.48, width=s, align="center")


def kpi(p, x, y, w, h, emoji, color, label, value, delta=None, delta_col=None, foot=None, spark=None):
    f = card(p, x, y, w, h, name="KPI/" + label)
    narrow = w < 200
    s_ = 34 if narrow else 40
    icon_tile(f, 16 if narrow else 20, 18 if narrow else 20, emoji, color, s_)
    lx = 58 if narrow else 72
    b.text(label, lx, 22, f, 12, "Medium", C["muted"], width=w - lx - 12)
    if foot and not narrow:
        b.text(foot, lx, 40, f, 11, color=C["dim"], width=w - lx - 14)
    b.text(value, 16 if narrow else 20, 68 if narrow else 76, f, 24 if narrow else 26, "Bold")
    if delta:
        badge(f, 16 if narrow else 20, h - 36, delta, delta_col or C["green"])
    if spark:
        sx, sy, sw_, sh = w - 120, h - 52, 100, 32
        lo, hi = min(spark), max(spark)
        pts = [(sx + sw_ * i / (len(spark) - 1), sy + sh - sh * (v - lo) / ((hi - lo) or 1)) for i, v in enumerate(spark)]
        b.poly(pts + [(sx + sw_, sy + sh), (sx, sy + sh)], f, fill=color + "22", closed=True)
        b.poly(pts, f, stroke=color, sw=2)
    return f


def table(p, x, y, w, cols, rows, row_h=40, head_h=38, zebra=True, cell_fn=None):
    """cols: list of (label, width, align)"""
    b.rect(x, y, w, head_h, p, fill=C["card2"], cornerRadius=8)
    cx = x
    for (lab, cw, al) in cols:
        b.text(lab, cx + 12, y + 11, p, 11, "Bold", C["muted"], width=cw - 24, align=al, textCase="upper",
               letterSpacing="4%")
        cx += cw
    for r, row in enumerate(rows):
        ry = y + head_h + r * row_h
        if zebra and r % 2 == 1:
            b.rect(x, ry, w, row_h, p, fill="#FFFFFF06")
        b.rect(x, ry + row_h - 1, w, 1, p, fill=C["border"])
        cx = x
        for c, (lab, cw, al) in enumerate(cols):
            val = row[c]
            if cell_fn and cell_fn(p, r, c, val, cx, ry, cw, row_h):
                pass
            else:
                b.text(str(val), cx + 12, ry + (row_h - 16) / 2, p, 13, "Medium" if c == 0 else "Regular",
                       C["text"] if c == 0 else "#CBD5E1", width=cw - 24, align=al)
            cx += cw


def line_chart(p, x, y, w, h, n, vmin, vmax, series, xlabels=(), ygrid=4, yfmt=None, divider=None):
    for i in range(ygrid + 1):
        gy = y + h - h * i / ygrid
        b.rect(x, gy, w, 1, p, fill=C["border"] if i else C["border2"])
        if yfmt:
            b.text(yfmt(vmin + (vmax - vmin) * i / ygrid), x - 58, gy - 8, p, 10, color=C["dim"], width=50,
                   align="right")

    def pt(i, v):
        return (x + w * i / (n - 1), y + h - h * (v - vmin) / (vmax - vmin))

    if divider is not None:
        dx = pt(divider[0], vmin)[0]
        b.rect(dx, y, w - (dx - x), h, p, fill=C["cyan"] + "0D")
        b.rect(dx, y - 6, 1.5, h + 6, p, fill=C["cyan"] + "99")
        b.text(divider[1], dx + 8, y - 4, p, 11, "Bold", C["cyan"])
    for s in series:
        st = s.get("start", 0)
        vals = s["values"]
        if "band" in s:
            lo_, hi_ = s["band"]
            up = [pt(st + i, v) for i, v in enumerate(hi_)]
            dn = [pt(st + i, v) for i, v in enumerate(lo_)][::-1]
            b.poly(up + dn, p, fill=s["color"] + "2B", closed=True, name="Interval")
        pts = [pt(st + i, v) for i, v in enumerate(vals)]
        if s.get("area"):
            b.poly(pts + [(pts[-1][0], y + h), (pts[0][0], y + h)], p, fill=s["color"] + "1A", closed=True)
        extra = {"dashes": [7, 5]} if s.get("dash") else {}
        b.poly(pts, p, stroke=s["color"], sw=s.get("sw", 2.5), name=s.get("name", "Series"), **extra)
        if s.get("dots"):
            for (px, py) in pts:
                b.ellipse(px - 3.5, py - 3.5, 7, 7, p, fill=C["bg"], stroke=s["color"], strokeWeight=2)
    for (i, lab) in xlabels:
        px = x + w * i / (n - 1)
        b.text(lab, px - 30, y + h + 10, p, 10, color=C["dim"], width=60, align="center")


def legend(p, x, y, items):
    cx = x
    for lab, col, dash in items:
        if dash:
            for k in range(3):
                b.rect(cx + k * 7, y + 6, 5, 3, p, fill=col, cornerRadius=1)
        else:
            b.rect(cx, y + 5, 18, 4, p, fill=col, cornerRadius=2)
        b.text(lab, cx + 26, y, p, 12, color=C["muted"])
        cx += 26 + len(lab) * 6.6 + 22


def hbars(p, x, y, w, items, color=None, row_h=34, label_w=150, vfmt=None, maxv=None, colors=None):
    maxv = maxv or max(v for _, v in items)
    for i, (lab, v) in enumerate(items):
        ry = y + i * row_h
        b.text(lab, x, ry + 2, p, 12, "Medium", C["text"], width=label_w - 10)
        bw = (w - label_w - 70) * v / maxv
        b.rect(x + label_w, ry + 3, w - label_w - 70, 14, p, fill=C["border"] + "88", cornerRadius=7)
        col = (colors[i] if colors else None) or color or C["primary"]
        b.rect(x + label_w, ry + 3, max(bw, 6), 14, p,
               fills=[{"type": "linearGradient", "stops": [col, col + "AA"]}], cornerRadius=7)
        b.text(vfmt(v) if vfmt else fmt(v), x + w - 64, ry + 1, p, 12, "Bold", C["text"], width=64, align="right")


def vbars(p, x, y, w, h, items, color=None, highlight=None, vfmt=None, maxv=None, gap=0.35, colors=None):
    n = len(items)
    maxv = maxv or max(v for _, v in items)
    slot = w / n
    bw = slot * (1 - gap)
    for i in range(5):
        b.rect(x, y + h * i / 4, w, 1, p, fill=C["border"])
    for i, (lab, v) in enumerate(items):
        bh = h * v / maxv
        bx = x + i * slot + (slot - bw) / 2
        col = (colors[i] if colors else None) or (C["pink"] if highlight is not None and i in highlight else (color or C["primary"]))
        b.rect(bx, y + h - bh, bw, bh, p, fills=[{"type": "linearGradient", "stops": [col, col + "66"],
                                                  "from": [0.5, 0], "to": [0.5, 1]}], cornerRadius=[6, 6, 0, 0])
        if vfmt:
            b.text(vfmt(v), bx - 10, y + h - bh - 18, p, 10, "Bold", C["muted"], width=bw + 20, align="center")
        b.text(lab, bx - 14, y + h + 8, p, 11, color=C["dim"], width=bw + 28, align="center")


# ------------------------------------------------------------------ data
def lcg(seed):
    s = seed
    while True:
        s = (1103515245 * s + 12345) % 2 ** 31
        yield s / 2 ** 31


rnd = lcg(7)
WEEK = [0.93, 0.90, 0.95, 0.86, 0.99, 1.18, 1.21]
LAST = dt.date(2017, 8, 15)
HIST = [LAST - dt.timedelta(days=89 - i) for i in range(90)]
FCD = [dt.date(2017, 8, 16) + dt.timedelta(days=i) for i in range(16)]


def payday(d):
    nxt = d + dt.timedelta(days=1)
    return d.day in (15, 16, 1, 2) or nxt.month != d.month


def nat(d, i, noise=True):
    v = 742 * WEEK[d.weekday()] * (1.09 if payday(d) else 1) * (1 + 0.025 * math.sin(i / 7.3)) + i * 0.25
    if noise:
        v *= 0.95 + 0.1 * next(rnd)
    return v


hist_nat = [nat(d, i) for i, d in enumerate(HIST)]
fc_nat = [nat(d, 90 + i, noise=False) for i, d in enumerate(FCD)]
FC_TOTAL = sum(fc_nat)
PREV_TOTAL = sum(hist_nat[-16:])

store_hist = [6400 * WEEK[d.weekday()] * (1.07 if payday(d) else 1) * (0.93 + 0.14 * next(rnd)) for d in HIST]
store_fc = [6480 * WEEK[d.weekday()] * (1.07 if payday(d) else 1) for d in FCD]
store_lo = [v * (0.86 - 0.004 * i) for i, v in enumerate(store_fc)]
store_hi = [v * (1.14 + 0.004 * i) for i, v in enumerate(store_fc)]

# ==================================================================== SIDEBAR / HEADER
NAV = [("🏠", "Beranda"), ("📈", "Forecast Explorer"), ("🧪", "Simulasi What-If"), ("📊", "Insight EDA"),
       ("⚙️", "Performa Model"), ("📘", "Panduan & Bantuan")]
W = 1440
MX = 320          # main content left
MW = W - MX - 40  # main content width = 1080


def sidebar(f, H, active):
    s = b.frame(0, 0, 280, H, f, "Sidebar", fill=C["side"], strokeRightWeight=1, stroke=C["border"])
    b.rect(24, 26, 42, 42, s, fills=[GRAD], cornerRadius=12, effects=GLOW)
    b.text("📈", 24, 34, s, 20, width=42, align="center")
    b.text("Favorita Forecast", 78, 26, s, 16, "Bold")
    b.text("Store Sales AI · v1.0", 78, 48, s, 12, color=C["dim"])
    b.text("NAVIGASI", 24, 100, s, 11, "Bold", C["dim"], letterSpacing="8%")
    for i, (e, lab) in enumerate(NAV):
        ny = 122 + i * 44
        on = i == active
        if on:
            b.rect(14, ny, 252, 38, s, fill=C["primary"] + "26", cornerRadius=10)
            b.rect(14, ny + 9, 3, 20, s, fill=C["primary"], cornerRadius=2)
        b.text(e, 30, ny + 9, s, 15)
        b.text(lab, 60, ny + 10, s, 14, "Bold" if on else "Medium", C["text"] if on else C["muted"])
        if i == 5:
            badge(s, 214, ny + 7, "BARU", C["green"], size=9, h=22)
    b.rect(24, 400, 232, 1, s, fill=C["border"])
    b.text("FILTER GLOBAL", 24, 420, s, 11, "Bold", C["dim"], letterSpacing="8%")
    select(s, 24, 446, 232, "Periode forecast", "16 – 31 Agu 2017", "📅")
    b.text("Tipe toko", 24, 520, s, 12, "Medium", C["muted"])
    cx = 24
    for t, on in [("A", 1), ("B", 1), ("C", 1), ("D", 1), ("E", 0)]:
        b.rect(cx, 540, 38, 30, s, fill=(C["primary"] + "33") if on else C["inp"],
               stroke=C["primary"] if on else C["border2"], strokeWeight=1, cornerRadius=8)
        b.text(t, cx, 547, s, 13, "Bold", C["text"] if on else C["dim"], width=38, align="center")
        cx += 46
    select(s, 24, 584, 232, "Provinsi", "Semua provinsi (16)")
    select(s, 24, 656, 232, "Klaster toko", "Semua klaster (1–17)")
    hc = b.frame(16, H - 210, 248, 140, s, "Help Card", fills=[GRAD_HERO], cornerRadius=16, clip=True)
    b.ellipse(170, -30, 120, 120, hc, fill="#FFFFFF1A")
    b.text("💡 Butuh bantuan?", 16, 16, hc, 14, "Bold", C["white"])
    b.text("Ikuti panduan langkah demi langkah untuk memahami setiap fitur.", 16, 40, hc, 12,
           color="#E0E7FF", width=210, lh="145%")
    button(hc, 16, 90, "📘 Buka Panduan", "white", w=150, h=34, size=12)
    b.ellipse(24, H - 48, 8, 8, s, fill=C["green"])
    b.text("Data s/d 15 Agu 2017 · LightGBM (tuned)", 40, H - 52, s, 11, color=C["dim"])
    return s


def header(f, crumb, title, sub, actions=(("📥 Unduh Laporan", "secondary"), ("🎯 Tur Halaman", "primary"))):
    b.text("Deploy", W - 120, 18, f, 13, "Medium", C["muted"])
    b.text("⋮", W - 56, 14, f, 18, "Bold", C["muted"])
    b.text(crumb, MX, 30, f, 12, "Medium", C["dim"])
    b.text(title, MX, 52, f, 30, "Bold")
    b.text(sub, MX, 96, f, 14, color=C["muted"], width=640, lh="150%")
    ax = W - 40
    for lab, kind in reversed(actions):
        w = int(len(lab) * 13 * 0.56 + 36)
        ax -= w
        button(f, ax, 60, lab, kind, w=w)
        ax -= 12


def screen(i, name, H):
    return b.frame(i * (W + 160), 0, W, H, None, name, fill=C["bg"], clip=True)


# ==================================================================== PAGE 1: COVER & PANDUAN
b.rename_page("📘 Cover & Panduan")

# ---- Cover
cv = b.frame(0, 0, 1440, 900, None, "00 · Cover", fills=[{"type": "linearGradient",
                                                          "stops": ["#0B1120", "#1E1B4B", "#312E81"],
                                                          "from": [0, 0], "to": [1, 1]}], clip=True)
b.ellipse(900, -200, 700, 700, cv, fill="#8B5CF61F")
b.ellipse(1100, 400, 600, 600, cv, fill="#22D3EE14")
b.ellipse(-200, 600, 500, 500, cv, fill="#EC489914")
badge(cv, 100, 120, "MINI PROJECT · DATA SCIENCE & GENERATIVE AI", C["cyan"], size=12, h=30)
b.text("Favorita Store Sales", 100, 175, cv, 64, "Bold")
b.text("Forecasting App", 100, 250, cv, 64, "Bold", "#A5B4FC")
b.text("Desain UI/UX aplikasi Streamlit untuk meramal penjualan harian 54 toko × 33 kategori produk "
       "Corporación Favorita (Ekuador) — dibangun di atas model LightGBM (tuned) dengan RMSLE 0,4045.",
       100, 345, cv, 18, color="#C7D2FE", width=620, lh="155%")
cx = 100
for lab, col in [("🏠 6 Halaman", C["primary"]), ("📈 Forecast 16 hari", C["cyan"]), ("🧪 Simulasi What-If", C["pink"]),
                 ("📘 Panduan lengkap", C["green"])]:
    cx += badge(cv, cx, 470, lab, col, size=13, h=34) + 10
b.text("Kelompok 7 · Celerates Independent Study", 100, 560, cv, 15, "Bold", C["white"])
for k, nm in enumerate(["Samudra Tsalasa Putra", "Dwi Aura Ningrum", "Anavalis Ridho Abdee Nugroho",
                        "Hany Nadya Fairuz", "Eka Lidya Rahmadini", "Selsa Trikartika"]):
    b.text("• " + nm, 100 + (k % 2) * 280, 592 + (k // 2) * 26, cv, 14, color="#C7D2FE")
b.text("Isi file: 📘 Cover & Panduan  ·  🎨 Design System  ·  🖥️ App Screens", 100, 800, cv, 13, color=C["muted"])
# mini preview mock
mk = b.frame(820, 170, 540, 400, cv, "Preview Mock", fill=C["bg"], cornerRadius=20, stroke="#FFFFFF22",
             strokeWeight=1, effects=SHADOW, clip=True)
b.rect(0, 0, 120, 400, mk, fill=C["side"])
for k in range(6):
    b.rect(16, 60 + k * 30, 88 if k else 88, 18, mk, fill=(C["primary"] + "55") if k == 0 else "#FFFFFF10", cornerRadius=6)
b.rect(16, 18, 26, 26, mk, fills=[GRAD], cornerRadius=8)
b.rect(140, 20, 200, 16, mk, fill="#FFFFFF22", cornerRadius=6)
for k in range(4):
    b.rect(140 + k * 98, 52, 88, 66, mk, fill=C["card"], stroke=C["border"], strokeWeight=1, cornerRadius=10)
    b.rect(150 + k * 98, 64, 22, 22, mk, fill=[C["primary"], C["cyan"], C["green"], C["amber"]][k] + "44", cornerRadius=6)
    b.rect(150 + k * 98, 94, 50, 10, mk, fill="#FFFFFF33", cornerRadius=4)
cc = b.frame(140, 132, 382, 170, mk, "mini chart", fill=C["card"], cornerRadius=12, stroke=C["border"], strokeWeight=1)
vals = hist_nat[-40:]
pts = [(14 + 280 * i / 39, 140 - 100 * (v - 600) / 400) for i, v in enumerate(vals)]
b.poly(pts, cc, stroke=C["primary"], sw=2)
fpts = [(294 + 76 * i / 15, 140 - 100 * (v - 600) / 400) for i, v in enumerate(fc_nat)]
b.poly([pts[-1]] + fpts, cc, stroke=C["cyan"], sw=2, dashes=[5, 4])
for k in range(2):
    b.rect(140 + k * 196, 316, 186, 70, mk, fill=C["card"], stroke=C["border"], strokeWeight=1, cornerRadius=10)
    for j in range(3):
        b.rect(152 + k * 196, 330 + j * 16, 120 - j * 25, 8, mk, fill=[C["primary"], C["pink"], C["cyan"]][j] + "88",
               cornerRadius=4)

# ---- User Flow
uf = b.frame(1600, 0, 1440, 900, None, "01 · Peta Aplikasi & Alur Pengguna", fill=C["bg"], clip=True)
b.text("PETA APLIKASI", 80, 70, uf, 12, "Bold", C["cyan"], letterSpacing="10%")
b.text("Alur Pengguna (User Flow)", 80, 92, uf, 36, "Bold")
b.text("Bagaimana pengguna bergerak dari halaman pembuka hingga mengambil keputusan stok. Panah menunjukkan "
       "alur utama; setiap halaman tetap bisa diakses langsung dari sidebar.", 80, 145, uf, 15, color=C["muted"],
       width=760, lh="150%")


def flow_node(p, x, y, w, h, emoji, title, desc, col, who):
    f = b.frame(x, y, w, h, p, "Flow/" + title, fill=C["card"], stroke=col + "88", strokeWeight=1.5,
                cornerRadius=16, effects=SHADOW)
    b.rect(0, 0, w, 5, f, fill=col)
    icon_tile(f, 18, 22, emoji, col, 38)
    b.text(title, 66, 24, f, 15, "Bold", width=w - 80)
    b.text(who, 66, 44, f, 11, "Medium", col, width=w - 80)
    b.text(desc, 18, 76, f, 12, color=C["muted"], width=w - 36, lh="150%")


flow_node(uf, 80, 240, 240, 170, "👋", "Onboarding", "Layar sambutan + tur singkat 5 langkah untuk pengguna baru.", C["green"], "Semua pengguna")
flow_node(uf, 400, 240, 240, 170, "🏠", "Beranda", "KPI nasional, tren 90 hari + forecast, top kategori & toko, insight otomatis.", C["primary"], "Direktur · Regional Mgr")
flow_node(uf, 720, 140, 260, 170, "📈", "Forecast Explorer", "Pilih toko & kategori → grafik histori vs forecast, interval, tabel harian, unduh CSV.", C["cyan"], "Manajer toko · Logistik")
flow_node(uf, 720, 360, 260, 170, "🧪", "Simulasi What-If", "Ubah promo, lead time & service level → lift penjualan & safety stock.", C["pink"], "Demand planner")
flow_node(uf, 1060, 140, 280, 170, "📊", "Insight EDA", "Pola mingguan, efek gajian, libur, gempa 2016, harga minyak, Pareto.", C["amber"], "Analis · Merchandising")
flow_node(uf, 1060, 360, 280, 170, "⚙️", "Performa Model", "Leaderboard 6 model, feature importance, error per kategori.", C["violet"], "Data scientist · Dosen")
flow_node(uf, 400, 600, 580, 150, "📘", "Panduan & Bantuan", "Selalu tersedia: quick start, FAQ, glosarium metrik (RMSLE, WAPE, MAE), cara membaca grafik & kontak tim.", C["sky"], "Bisa dibuka dari setiap halaman (tombol ❓ / kartu bantuan di sidebar)")
b.arrow(326, 324, 66, uf, color=C["muted"])
b.arrow(648, 300, 64, uf, rot=-25, color=C["muted"])
b.arrow(648, 350, 64, uf, rot=25, color=C["muted"])
b.arrow(988, 224, 64, uf, color=C["muted"])
b.arrow(988, 444, 64, uf, color=C["muted"])
b.arrow(848, 316, 38, uf, rot=90, color=C["pink"])
b.text("hasil forecast → skenario", 862, 322, uf, 11, "Medium", C["pink"])
b.rect(80, 790, 1280, 1, uf, fill=C["border"])
legend(uf, 80, 815, [("Alur utama", C["muted"], False), ("Alur lanjutan", C["pink"], False)])
b.text("Prinsip UX: 1) Overview dulu, detail kemudian  2) Setiap grafik punya penjelasan singkat  3) Satu klik ke panduan",
       560, 815, uf, 12, "Medium", C["dim"])

# ---- Panduan langkah demi langkah
pg = b.frame(3200, 0, 1440, 1500, None, "02 · Panduan Penggunaan (Langkah demi Langkah)", fill=C["bg"], clip=True)
b.text("TATA CARA PENGGUNAAN", 80, 70, pg, 12, "Bold", C["green"], letterSpacing="10%")
b.text("Panduan Langkah demi Langkah", 80, 92, pg, 36, "Bold")
b.text("Ikuti 6 langkah berikut untuk mendapatkan forecast dan rekomendasi stok. Setiap langkah dilengkapi "
       "contoh komponen yang akan Anda temui di aplikasi.", 80, 145, pg, 15, color=C["muted"], width=760, lh="150%")
STEPS = [
    ("Buka aplikasi & ikuti tur", "👋",
     ["Jalankan `streamlit run streamlit_app/app.py`.", "Pada kunjungan pertama, layar Onboarding muncul.",
      "Klik “Mulai Tur” untuk 5 coach-mark singkat, atau “Lewati”."], C["green"]),
    ("Atur filter global di sidebar", "🎛️",
     ["Pilih periode forecast (default 16–31 Agu 2017).", "Pilih tipe toko A–E, provinsi, dan klaster.",
      "Semua halaman otomatis mengikuti filter ini."], C["primary"]),
    ("Baca ringkasan di Beranda", "🏠",
     ["Lihat 4 KPI: total forecast, rata-rata harian, akurasi, cakupan.", "Garis ungu = histori, garis cyan putus-putus = forecast.",
      "Baca kartu “Insight Otomatis” untuk hari-hari penting."], C["sky"]),
    ("Telusuri forecast per toko", "📈",
     ["Buka Forecast Explorer → pilih Toko & Kategori.", "Atur rentang histori 30/60/90 hari & tampilkan pita interval.",
      "Unduh tabel harian dalam format CSV/Excel."], C["cyan"]),
    ("Simulasikan skenario stok", "🧪",
     ["Geser slider promo, lead time, dan service level.", "Bandingkan baseline vs skenario pada grafik.",
      "Gunakan rekomendasi Safety Stock & Reorder Point."], C["pink"]),
    ("Pahami data & model", "📊",
     ["Insight EDA: pola mingguan, gajian, libur, gempa, minyak.", "Performa Model: leaderboard & feature importance.",
      "Butuh istilah? Buka Panduan → Glosarium."], C["amber"]),
]
for k, (tt, em, pts_, col) in enumerate(STEPS):
    cx_, cy_ = 80 + (k % 3) * 436, 230 + (k // 3) * 420
    f = b.frame(cx_, cy_, 412, 390, pg, f"Step {k + 1}", fill=C["card"], stroke=C["border"], strokeWeight=1,
                cornerRadius=20, clip=True)
    b.rect(0, 0, 412, 150, f, fill=col + "14")
    b.ellipse(300, -60, 180, 180, f, fill=col + "1A")
    b.ellipse(24, 24, 44, 44, f, fills=[{"type": "linearGradient", "stops": [col, col + "AA"]}])
    b.text(str(k + 1), 24, 34, f, 20, "Bold", C["white"], width=44, align="center")
    b.text(em, 330, 40, f, 44)
    b.text(f"LANGKAH {k + 1}", 84, 26, f, 11, "Bold", col, letterSpacing="8%")
    b.text(tt, 84, 44, f, 18, "Bold", width=230)
    # illustration
    if k == 0:
        button(f, 24, 96, "🚀 Mulai Tur", "primary", w=130, h=36, size=12)
        button(f, 166, 96, "Lewati", "ghost", w=90, h=36, size=12)
    elif k == 1:
        for j, t in enumerate(["A", "B", "C", "D", "E"]):
            b.rect(24 + j * 44, 100, 36, 30, f, fill=(C["primary"] + "33") if j < 4 else C["inp"],
                   stroke=C["primary"] if j < 4 else C["border2"], strokeWeight=1, cornerRadius=8)
            b.text(t, 24 + j * 44, 107, f, 13, "Bold", width=36, align="center")
    elif k == 2:
        b.poly([(24, 130), (70, 112), (110, 120), (150, 98), (190, 106)], f, stroke=C["primary"], sw=3)
        b.poly([(190, 106), (230, 92), (270, 100), (310, 84)], f, stroke=C["cyan"], sw=3, dashes=[6, 4])
    elif k == 3:
        sf = b.frame(24, 92, 230, 40, f, "sel", fill=C["inp"], stroke=C["border2"], strokeWeight=1, cornerRadius=10)
        b.text("Toko 44 · GROCERY I", 12, 11, sf, 13, "Medium")
        b.text("▾", 206, 10, sf, 14, color=C["muted"])
    elif k == 4:
        slider(f, 24, 92, 260, "Item promo", "30", 0.6)
    elif k == 5:
        for j, (bh, cl) in enumerate([(30, C["amber"]), (42, C["amber"]), (24, C["amber"]), (50, C["pink"]), (36, C["amber"])]):
            b.rect(24 + j * 28, 132 - bh, 18, bh, f, fill=cl, cornerRadius=[4, 4, 0, 0])
    for j, line in enumerate(pts_):
        ly = 176 + j * 62
        b.ellipse(24, ly + 3, 20, 20, f, fill=col + "26")
        b.text("✓", 24, ly + 4, f, 12, "Bold", col, width=20, align="center")
        b.text(line, 56, ly, f, 13, color="#CBD5E1", width=330, lh="150%")
alert(pg, 80, 1100, 1280, 84, "tip", "Tips cepat",
      "Arahkan kursor ke ikon ⓘ di samping judul grafik untuk penjelasan singkat. Semua grafik interaktif (Plotly): "
      "drag untuk zoom, klik dua kali untuk reset, klik legenda untuk menyembunyikan seri.")
b.text("Cara Membaca Grafik Forecast", 80, 1220, pg, 20, "Bold")
lg = card(pg, 80, 1260, 1280, 180)
legend(lg, 24, 24, [("Histori aktual", C["primary"], False), ("Forecast", C["cyan"], True)])
b.rect(320, 22, 26, 16, lg, fill=C["cyan"] + "2B", cornerRadius=4)
b.text("Pita interval (perkiraan rentang wajar)", 354, 23, lg, 12, color=C["muted"])
b.rect(650, 18, 2, 24, lg, fill=C["cyan"])
b.text("Garis batas: hari terakhir data (15 Agu 2017)", 662, 23, lg, 12, color=C["muted"])
for j, (t, d) in enumerate([("1. Bandingkan level", "Apakah forecast sejalan dengan level histori 2–4 minggu terakhir?"),
                            ("2. Perhatikan pola", "Puncak berulang tiap Sabtu–Minggu & tanggal gajian (15 / akhir bulan)."),
                            ("3. Gunakan interval", "Rencanakan stok di dekat batas atas untuk barang yang mudah habis."),
                            ("4. Cek kategori sulit", "Kategori sporadis (mis. School & Office) punya error lebih besar.")]):
    b.text(t, 24 + j * 312, 70, lg, 14, "Bold")
    b.text(d, 24 + j * 312, 94, lg, 12, color=C["muted"], width=280, lh="150%")

# ---- Cara menjalankan & Handoff
rn = b.frame(4800, 0, 1440, 1100, None, "03 · Cara Menjalankan & Handoff Developer", fill=C["bg"], clip=True)
b.text("UNTUK DEVELOPER", 80, 70, rn, 12, "Bold", C["violet"], letterSpacing="10%")
b.text("Cara Menjalankan & Pemetaan Komponen", 80, 92, rn, 36, "Bold")
term = b.frame(80, 170, 620, 380, rn, "Terminal", fill="#050816", stroke=C["border"], strokeWeight=1,
               cornerRadius=16, clip=True, effects=SHADOW)
b.rect(0, 0, 620, 40, term, fill="#0F172A")
for j, col in enumerate([C["red"], C["amber"], C["green"]]):
    b.ellipse(16 + j * 20, 14, 12, 12, term, fill=col)
b.text("PowerShell — mini-project", 0, 12, term, 12, "Medium", C["dim"], width=620, align="center")
LINES = [("# 1. Siapkan environment", C["dim"]), ("python -m venv .venv ; .venv\\Scripts\\activate", C["text"]),
         ("pip install -r requirements.txt", C["text"]), ("", C["dim"]),
         ("# 2. Ekspor artefak dari notebook (sekali saja)", C["dim"]), ("python scripts/export_artifacts.py", C["text"]),
         ("", C["dim"]), ("# 3. Jalankan aplikasi", C["dim"]), ("streamlit run streamlit_app/app.py", C["cyan"]),
         ("", C["dim"]), ("  Local URL: http://localhost:8501  ✓", C["green"])]
for j, (ln, col) in enumerate(LINES):
    b.text(("$ " if col in (C["text"], C["cyan"]) else "") + ln, 24, 60 + j * 27, term, 13, "Medium", col,
           family="Consolas")
st_ = card(rn, 740, 170, 620, 380, "📁 Struktur Folder", "Artefak dibaca dengan @st.cache_data agar halaman terbuka < 2 detik.")
TREE = ["mini-project/", "├── artifacts/  (forecast_16d.parquet, histori_90d.parquet,", "│              metrics.json, feature_importance.csv, model.joblib)",
        "├── scripts/export_artifacts.py", "├── streamlit_app/", "│   ├── app.py                 → 🏠 Beranda",
        "│   ├── pages/1_📈_Forecast_Explorer.py", "│   ├── pages/2_🧪_What_If_Simulator.py", "│   ├── pages/3_📊_EDA_Insights.py",
        "│   ├── pages/4_⚙️_Model_Performance.py", "│   ├── pages/5_📘_Panduan.py", "│   └── .streamlit/config.toml  (tema gelap)"]
for j, ln in enumerate(TREE):
    b.text(ln, 24, 80 + j * 23, st_, 12, color="#CBD5E1", family="Consolas")
b.text("Pemetaan Komponen Desain → Widget Streamlit", 80, 590, rn, 20, "Bold")
tb = card(rn, 80, 630, 1280, 420)
MAP = [("Selectbox (Toko, Kategori, Provinsi)", "st.selectbox / st.multiselect", "Sidebar & Forecast Explorer"),
       ("Chip tipe toko A–E", "st.pills / st.multiselect", "Sidebar"),
       ("Segmented 30/60/90 hari", "st.segmented_control", "Forecast Explorer"),
       ("Slider promo, lead time", "st.slider", "Simulasi What-If"),
       ("Toggle pita interval / hari gajian", "st.toggle", "Explorer & Simulasi"),
       ("Kartu KPI + delta", "st.metric(border=True)", "Semua halaman"),
       ("Grafik garis / batang / scatter", "st.plotly_chart(use_container_width=True)", "Semua halaman"),
       ("Tab (Pola Musiman, Gajian, …)", "st.tabs", "Insight EDA, Explorer"),
       ("Callout info/tips/peringatan", "st.info / st.success / st.warning", "Semua halaman"),
       ("Tombol unduh CSV/Excel", "st.download_button", "Explorer & Simulasi")]
table(tb, 20, 20, 1240, [("Komponen desain", 440, "left"), ("Widget Streamlit", 460, "left"), ("Dipakai di", 340, "left")],
      MAP, row_h=36)

# ==================================================================== PAGE 2: DESIGN SYSTEM
b.page("🎨 Design System")
ds = b.frame(0, 0, 1440, 1900, None, "Design System", fill=C["bg"], clip=True)
b.text("DESIGN SYSTEM", 80, 70, ds, 12, "Bold", C["primary"], letterSpacing="10%")
b.text("Favorita UI Kit — Dark Analytics", 80, 92, ds, 36, "Bold")
b.text("Token warna, tipografi, dan komponen yang dipakai di seluruh layar. Tema gelap dipilih agar grafik "
       "berwarna menonjol dan nyaman untuk dashboard yang dipantau lama.", 80, 145, ds, 15, color=C["muted"],
       width=760, lh="150%")
b.text("Warna", 80, 220, ds, 20, "Bold")
SW = [("Background", C["bg"]), ("Sidebar", C["side"]), ("Card", C["card"]), ("Card 2", C["card2"]), ("Border", C["border"]),
      ("Text", C["text"]), ("Muted", C["muted"]), ("Primary", C["primary"]), ("Violet", C["violet"]), ("Forecast · Cyan", C["cyan"]),
      ("Success", C["green"]), ("Warning", C["amber"]), ("Danger", C["red"]), ("Highlight · Pink", C["pink"])]
for k, (nm, hx) in enumerate(SW):
    x_, y_ = 80 + (k % 7) * 184, 260 + (k // 7) * 150
    b.rect(x_, y_, 168, 86, ds, fill=hx, cornerRadius=14, stroke=C["border2"], strokeWeight=1)
    b.text(nm, x_, y_ + 96, ds, 13, "Bold")
    b.text(hx, x_, y_ + 116, ds, 12, color=C["muted"], family="Consolas")
b.rect(80, 570, 400, 60, ds, fills=[GRAD], cornerRadius=14)
b.text("Gradient Primary", 96, 590, ds, 14, "Bold", C["white"])
b.rect(500, 570, 400, 60, ds, fills=[GRAD_HERO], cornerRadius=14)
b.text("Gradient Hero", 516, 590, ds, 14, "Bold", C["white"])
b.rect(920, 570, 440, 60, ds, fills=[GRAD_CYAN], cornerRadius=14)
b.text("Gradient Forecast", 936, 590, ds, 14, "Bold", C["white"])

b.text("Tipografi · Inter", 80, 680, ds, 20, "Bold")
for k, (nm, sz, wt, sample) in enumerate([("Display", 36, "Bold", "Forecast Penjualan"), ("H1 · Judul halaman", 30, "Bold", "Forecast Explorer"),
                                          ("H2 · Judul kartu", 15, "Bold", "Histori vs Forecast"), ("Body", 14, "Regular", "Pilih toko dan kategori untuk melihat ramalan."),
                                          ("Caption", 12, "Medium", "Data s/d 15 Agu 2017"), ("KPI Value", 26, "Bold", "12,84 Jt")]):
    y_ = 720 + k * 56
    b.text(nm, 80, y_ + 6, ds, 12, "Medium", C["dim"], width=180)
    b.text(f"{sz}px · {wt}", 260, y_ + 6, ds, 12, color=C["dim"], family="Consolas")
    b.text(sample, 420, y_, ds, sz if sz < 30 else sz - 4, wt)

b.text("Komponen", 80, 1080, ds, 20, "Bold")
cp = card(ds, 80, 1120, 620, 360, "Tombol & Badge")
bx = 20
for lab, kind in [("Primary", "primary"), ("Secondary", "secondary"), ("Ghost", "ghost"), ("Success", "success"), ("Danger", "danger")]:
    bx += button(cp, bx, 64, lab, kind) + 12
bx = 20
for lab, col in [("Naik +4,2%", C["green"]), ("Turun −3,1%", C["red"]), ("Gajian", C["amber"]), ("Akhir pekan", C["violet"]),
                 ("Promo", C["pink"]), ("Champion", C["cyan"])]:
    bx += badge(cp, bx, 124, lab, col) + 8
segmented(cp, 20, 170, ["30 hari", "60 hari", "90 hari"], 1, 90)
tabs(cp, 20, 230, ["Tabel Harian", "Pola Mingguan", "Bandingkan"], 0, 580)
progress(cp, 20, 290, 280, 0.72)
progress(cp, 320, 290, 280, 0.35, C["amber"])
b.text("Progress / risiko", 20, 310, cp, 11, color=C["dim"])
ip = card(ds, 740, 1120, 620, 360, "Input & Kontrol")
select(ip, 20, 60, 270, "Toko", "Toko 44 · Quito · A")
select(ip, 320, 60, 270, "Kategori", "GROCERY I")
slider(ip, 20, 150, 570, "Jumlah item promo", "30 item", 0.6, "0", "60")
toggle(ip, 20, 240, "Tampilkan pita interval", True)
toggle(ip, 320, 240, "Hari gajian", False)
checkbox(ip, 20, 290, "Bandingkan dengan tahun lalu", True)
radio(ip, 320, 290, "Service level 95%", True)
kpi(ds, 80, 1520, 300, 150, "💰", C["primary"], "Total forecast 16 hari", "12,84 Jt", "▲ 4,2%", foot="unit terjual", spark=hist_nat[-20:])
alert(ds, 410, 1520, 460, 72, "info", "Info", "Forecast diperbarui setiap kali artefak diekspor ulang.")
alert(ds, 410, 1600, 460, 72, "warning", "Perhatian", "Simulasi promo bersifat asosiatif, bukan sebab-akibat.")
alert(ds, 900, 1520, 460, 72, "success", "Berhasil", "File forecast_toko44.csv berhasil diunduh.")
alert(ds, 900, 1600, 460, 72, "error", "Data tidak ditemukan", "Kombinasi toko/kategori tidak tersedia.")
# states
b.text("State: Loading · Kosong · Toast", 80, 1710, ds, 20, "Bold")
sk = card(ds, 80, 1750, 420, 120)
for j, wv in enumerate([300, 220, 360]):
    b.rect(20, 22 + j * 30, wv, 14, sk, fill="#FFFFFF12", cornerRadius=7)
b.text("⏳ Memuat data… (st.spinner)", 20, 92, sk, 11, color=C["dim"])
em_ = card(ds, 520, 1750, 420, 120)
b.text("🗂️", 20, 30, em_, 36)
b.text("Belum ada data untuk filter ini", 80, 34, em_, 14, "Bold")
b.text("Coba ubah tipe toko atau provinsi di sidebar.", 80, 58, em_, 12, color=C["muted"])
ts = b.frame(960, 1770, 400, 64, ds, "Toast", fill=C["card2"], stroke=C["green"] + "66", strokeWeight=1, cornerRadius=14,
             effects=SHADOW)
b.text("✅", 16, 20, ts, 18)
b.text("Skenario disimpan", 52, 14, ts, 13, "Bold")
b.text("st.toast · hilang otomatis 4 detik", 52, 34, ts, 11, color=C["muted"])

# ==================================================================== PAGE 3: APP SCREENS
b.page("🖥️ App Screens")

# ---------------- 00 Onboarding
H0 = 1024
s0 = screen(0, "00 · Onboarding / Welcome", H0)
b.ellipse(-200, -300, 900, 900, s0, fill="#6366F11A")
b.ellipse(900, 500, 800, 800, s0, fill="#EC489912")
b.rect(560, 90, 64, 64, s0, fills=[GRAD], cornerRadius=18, effects=GLOW)
b.text("📈", 560, 104, s0, 30, width=64, align="center")
b.text("Selamat datang di Favorita Forecast 👋", 0, 190, s0, 40, "Bold", width=1440 - 260, align="center")
b.text("Ramal penjualan harian 54 toko × 33 kategori untuk 16 hari ke depan, simulasikan promo, dan rencanakan stok — "
       "tanpa menulis satu baris kode pun.", 300, 252, s0, 17, color=C["muted"], width=580, align="center", lh="155%")
for k, (em, tt, dd, col) in enumerate([("📈", "Forecast akurat", "LightGBM (tuned): WAPE 13,6%, 26,9% lebih baik dari baseline.", C["cyan"]),
                                       ("🧪", "Simulasi What-If", "Uji dampak promo & hitung safety stock dalam hitungan detik.", C["pink"]),
                                       ("📘", "Panduan lengkap", "Tur interaktif, FAQ, dan glosarium metrik siap membantu.", C["green"])]):
    f = card(s0, 170 + k * 290, 370, 270, 200, shadow=True)
    icon_tile(f, 22, 24, em, col, 48)
    b.text(tt, 22, 92, f, 17, "Bold")
    b.text(dd, 22, 120, f, 13, color=C["muted"], width=226, lh="150%")
button(s0, 420, 620, "🚀 Mulai Tur (5 langkah)", "primary", w=220, h=50, size=15)
button(s0, 656, 620, "Langsung ke Beranda →", "secondary", w=200, h=50, size=15)
checkbox(s0, 498, 700, "Jangan tampilkan lagi (simpan di st.session_state)", False)
pc = card(s0, 170, 780, 850, 170, "🧭 Apa yang bisa Anda lakukan?")
for k, (n_, t_) in enumerate([("1", "Atur filter di sidebar"), ("2", "Baca KPI di Beranda"), ("3", "Telusuri per toko"), ("4", "Simulasikan stok")]):
    b.ellipse(24 + k * 206, 68, 34, 34, pc, fills=[GRAD])
    b.text(n_, 24 + k * 206, 75, pc, 15, "Bold", C["white"], width=34, align="center")
    b.text(t_, 68 + k * 206, 75, pc, 13, "Medium", width=140)
    if k < 3:
        b.text("→", 190 + k * 206, 72, pc, 18, color=C["dim"])
b.text("Rata-rata waktu: ± 2 menit untuk menyelesaikan tur.", 24, 126, pc, 12, color=C["dim"])
b.text("Model terakhir dilatih: 1.703.592 baris · 54 toko · 33 kategori", 0, 980, s0, 12, color=C["dim"], width=1180, align="center")
b.rect(1180, 0, 260, H0, s0, fill=C["side"])
b.text("SIDEBAR (disembunyikan saat onboarding)", 1196, 30, s0, 10, "Bold", C["dim"], width=230)

# ---------------- 01 Beranda
H1 = 1240
s1 = screen(1, "01 · Beranda (Executive Dashboard)", H1)
sidebar(s1, H1, 0)
header(s1, "Beranda", "Ringkasan Eksekutif",
       "Gambaran penjualan nasional dan proyeksi 16 hari ke depan (16–31 Agustus 2017) untuk seluruh toko Favorita.")
hero = b.frame(MX, 150, MW, 120, s1, "Hero Banner", fills=[GRAD_HERO], cornerRadius=20, clip=True, effects=GLOW)
b.ellipse(820, -80, 260, 260, hero, fill="#FFFFFF14")
b.ellipse(960, 40, 200, 200, hero, fill="#FFFFFF0F")
b.text("Selamat datang kembali, Manajer 👋", 28, 24, hero, 20, "Bold", C["white"])
b.text(f"Total penjualan 16 hari ke depan diperkirakan {fmt(FC_TOTAL / 1000, 2)} juta unit — naik "
       f"{fmt((FC_TOTAL / PREV_TOTAL - 1) * 100, 1)}% dibanding 16 hari terakhir. Puncak terjadi pada akhir pekan & tanggal gajian 31 Agu.",
       28, 56, hero, 13, color="#E0E7FF", width=720, lh="150%")
button(hero, MW - 200, 40, "Lihat detail forecast →", "white", w=172, h=40)
KW = (MW - 3 * 20) / 4
kpi(s1, MX, 290, KW, 150, "💰", C["primary"], "Total forecast 16 hari", f"{fmt(FC_TOTAL / 1000, 2)} Jt",
    f"▲ {fmt((FC_TOTAL / PREV_TOTAL - 1) * 100, 1)}%", foot="unit · vs 16 hari lalu", spark=fc_nat)
kpi(s1, MX + (KW + 20), 290, KW, 150, "📅", C["cyan"], "Rata-rata harian", f"{fmt(FC_TOTAL / 16)} rb", "▲ 2,8%", foot="unit per hari",
    spark=hist_nat[-16:])
kpi(s1, MX + 2 * (KW + 20), 290, KW, 150, "🎯", C["green"], "Akurasi model (WAPE)", "13,6%", "RMSLE 0,4045", C["cyan"],
    foot="validasi 15 hari terakhir")
kpi(s1, MX + 3 * (KW + 20), 290, KW, 150, "🏪", C["amber"], "Cakupan", "1.782 seri", "54 toko · 33 kategori", C["amber"],
    foot="kombinasi toko × kategori")
ch = card(s1, MX, 460, 700, 380, "Tren Penjualan Nasional — Histori 90 Hari & Forecast 16 Hari",
          "Total unit terjual per hari (ribu). Arsir cyan = periode forecast.")
b.text("ⓘ", 640, 18, ch, 14, color=C["dim"])
segmented(ch, 470, 64, ["30H", "60H", "90H"], 2, 70, 30)
legend(ch, 20, 72, [("Histori", C["primary"], False), ("Forecast", C["cyan"], True)])
N1 = 106
line_chart(ch, 74, 120, 600, 210, N1, 500, 1000,
           [dict(values=hist_nat, color=C["primary"], area=True, name="Histori"),
            dict(values=[hist_nat[-1]] + fc_nat, start=89, color=C["cyan"], dash=True, name="Forecast", sw=3)],
           xlabels=[(0, "18 Mei"), (30, "17 Jun"), (60, "17 Jul"), (89, "15 Agu"), (105, "31 Agu")], yfmt=lambda v: fmt(v),
           divider=(89, "Forecast →"))
tk = card(s1, MX + 720, 460, MW - 720, 380, "Top 5 Kategori", "Kontribusi forecast 16 hari (juta unit)")
CATS = [("GROCERY I", 4.11), ("BEVERAGES", 2.61), ("PRODUCE", 1.52), ("CLEANING", 1.16), ("DAIRY", 0.82)]
hbars(tk, 20, 86, MW - 760, CATS, colors=[C["primary"], C["violet"], C["cyan"], C["green"], C["amber"]], row_h=48, label_w=110,
      vfmt=lambda v: fmt(v, 2))
b.text("Lihat semua 33 kategori →", 20, 340, tk, 12, "Bold", C["primary"])
st1 = card(s1, MX, 860, 640, 340, "🏆 Top 5 Toko", "Berdasarkan total forecast 16 hari")
STORES = [("#44", "Quito", "A", "5", "612.410", "▲ 3,9%"), ("#45", "Quito", "A", "11", "548.902", "▲ 4,4%"),
          ("#47", "Quito", "A", "14", "521.377", "▲ 2,1%"), ("#3", "Quito", "D", "8", "498.115", "▼ 0,8%"),
          ("#49", "Quito", "A", "11", "455.630", "▲ 5,2%")]


def store_cell(p, r, c, val, cx, ry, cw, rh):
    if c == 2:
        badge(p, cx + 12, ry + 9, "Tipe " + val, C["violet"])
        return True
    if c == 5:
        badge(p, cx + 12, ry + 9, val, C["green"] if "▲" in val else C["red"])
        return True
    return False


table(st1, 20, 74, 600, [("Toko", 80, "left"), ("Kota", 110, "left"), ("Tipe", 100, "left"), ("Klaster", 90, "left"),
                         ("Forecast", 120, "right"), ("Δ", 100, "left")], STORES, row_h=44, cell_fn=store_cell)
ins = card(s1, MX + 660, 860, MW - 660, 340, "✨ Insight Otomatis", "Dirangkum dari hasil forecast & EDA")
for k, (em, tt, dd, col) in enumerate([("💸", "Hari gajian 31 Agu", "Forecast +9% di atas rata-rata hari biasa. Siapkan stok GROCERY I & BEVERAGES.", C["amber"]),
                                       ("📆", "Akhir pekan 19–20 & 26–27 Agu", "Penjualan Sabtu–Minggu ±20% lebih tinggi dari hari kerja.", C["violet"]),
                                       ("⚠️", "Kategori berisiko", "SCHOOL & OFFICE SUPPLIES sulit diprediksi (musim ajaran baru). Tambah buffer.", C["red"])]):
    yy = 76 + k * 86
    b.rect(20, yy, MW - 700, 76, ins, fill=col + "12", cornerRadius=12)
    b.text(em, 34, yy + 22, ins, 22)
    b.text(tt, 74, yy + 14, ins, 13, "Bold", col)
    b.text(dd, 74, yy + 34, ins, 12, color=C["muted"], width=MW - 780, lh="145%")

# ---------------- 02 Forecast Explorer
H2 = 1380
s2 = screen(2, "02 · Forecast Explorer", H2)
sidebar(s2, H2, 1)
header(s2, "Beranda / Forecast Explorer", "Forecast Explorer",
       "Telusuri ramalan penjualan per toko dan kategori produk, lengkap dengan pita interval dan tabel harian yang bisa diunduh.")
fb = card(s2, MX, 150, MW, 110, name="Filter Bar")
select(fb, 20, 18, 280, "🏪 Toko", "Toko 44 · Quito · Tipe A", help_=True)
select(fb, 320, 18, 240, "🛒 Kategori produk", "GROCERY I")
b.text("Rentang histori", 580, 18, fb, 12, "Medium", C["muted"])
segmented(fb, 580, 40, ["30H", "60H", "90H"], 1, 60, 38)
toggle(fb, 790, 48, "Pita interval", True)
button(fb, MW - 140, 38, "🔄 Terapkan", "primary", w=120, h=40)
SK = (MW - 60) / 4
s_tot = sum(store_fc)
peak_i = max(range(16), key=lambda i: store_fc[i])
kpi(s2, MX, 280, SK, 140, "📦", C["cyan"], "Total forecast 16 hari", fmt(s_tot), "▲ 3,9%", foot="unit · Toko 44 · GROCERY I")
kpi(s2, MX + SK + 20, 280, SK, 140, "📊", C["primary"], "Rata-rata per hari", fmt(s_tot / 16), "± 12% interval", C["violet"], foot="unit per hari")
kpi(s2, MX + 2 * (SK + 20), 280, SK, 140, "🔝", C["pink"], "Hari puncak", f"{HARI_FULL[FCD[peak_i].weekday()]}, {dlabel(FCD[peak_i])}",
    fmt(store_fc[peak_i]) + " unit", C["pink"], foot="perkiraan tertinggi")
kpi(s2, MX + 3 * (SK + 20), 280, SK, 140, "🎯", C["green"], "Error kategori ini", "RMSLE 0,21", "Mudah diprediksi", C["green"], foot="kategori stabil, volume tinggi")
ch2 = card(s2, MX, 440, MW, 420, "Histori vs Forecast — Toko 44 · GROCERY I",
           "Unit terjual per hari. Garis putus-putus cyan = forecast; arsiran = rentang perkiraan wajar (±).")
legend(ch2, MW - 470, 22, [("Histori", C["primary"], False), ("Forecast", C["cyan"], True), ("Interval", C["cyan"] + "77", False)])
hs = store_hist[-60:]
line_chart(ch2, 84, 100, MW - 120, 260, 76, 3500, 10000,
           [dict(values=hs, color=C["primary"], area=True, dots=False),
            dict(values=[hs[-1]] + store_fc, start=59, color=C["cyan"], dash=True, sw=3, dots=True,
                 band=([hs[-1]] + store_lo, [hs[-1]] + store_hi))],
           xlabels=[(0, "17 Jun"), (15, "2 Jul"), (30, "17 Jul"), (45, "1 Agu"), (59, "15 Agu"), (67, "23 Agu"), (75, "31 Agu")],
           yfmt=lambda v: fmt(v), divider=(59, "Hari ini · 15 Agu"))
# tooltip
tt_x = 84 + (MW - 120) * 75 / 75 - 210
tp = b.frame(tt_x, 120, 190, 96, ch2, "Tooltip", fill=C["card2"], stroke=C["border2"], strokeWeight=1, cornerRadius=10, effects=SHADOW)
b.text("Kamis, 31 Agu 2017", 12, 10, tp, 12, "Bold")
b.text("● Forecast", 12, 32, tp, 12, color=C["cyan"])
b.text(fmt(store_fc[-1]), 100, 32, tp, 12, "Bold", width=78, align="right")
b.text("Rentang", 12, 52, tp, 12, color=C["muted"])
b.text(f"{fmt(store_lo[-1])}–{fmt(store_hi[-1])}", 70, 52, tp, 11, "Medium", width=108, align="right")
badge(tp, 12, 70, "💸 Gajian", C["amber"], size=10, h=20)
tb2 = card(s2, MX, 880, 720, 460)
tabs(tb2, 20, 18, ["📋 Tabel Harian", "📆 Pola Mingguan", "🏪 Bandingkan Toko"], 0, 680)
ROWS = []
for i in range(8):
    d = FCD[i]
    ROWS.append((f"{HARI[d.weekday()]}, {dlabel(d)}", fmt(store_fc[i]), fmt(store_lo[i]), fmt(store_hi[i]),
                 str([12, 14, 9, 22, 30, 28, 11, 10][i]), d))


def day_cell(p, r, c, val, cx, ry, cw, rh):
    if c == 5:
        d = val
        xx = cx + 12
        if d.weekday() >= 5:
            xx += badge(p, xx, ry + 9, "Akhir pekan", C["violet"], size=10, h=22) + 6
        if payday(d):
            badge(p, xx, ry + 9, "Gajian", C["amber"], size=10, h=22)
        if d.weekday() < 5 and not payday(d):
            b.text("—", xx, ry + 12, p, 12, color=C["dim"])
        return True
    if c == 1:
        b.text(val, cx + 12, ry + 12, p, 13, "Bold", C["cyan"], width=cw - 24, align="right")
        return True
    return False


table(tb2, 20, 66, 680, [("Tanggal", 120, "left"), ("Forecast", 100, "right"), ("Bawah", 90, "right"), ("Atas", 90, "right"),
                         ("Promo", 80, "right"), ("Penanda", 200, "left")], ROWS, row_h=40, cell_fn=day_cell)
b.text("Menampilkan 8 dari 16 hari", 20, 430, tb2, 12, color=C["dim"])
b.text("‹  1  2  ›", 600, 428, tb2, 13, "Bold", C["muted"])
ex = card(s2, MX + 740, 880, MW - 740, 460, "📥 Ekspor & Catatan")
button(ex, 20, 60, "⬇️ Unduh CSV", "primary", w=MW - 780, h=44)
button(ex, 20, 116, "📊 Unduh Excel (.xlsx)", "secondary", w=MW - 780, h=44)
button(ex, 20, 172, "🖼️ Simpan grafik (PNG)", "ghost", w=MW - 780, h=44)
alert(ex, 20, 236, MW - 780, 108, "tip", "Cara membaca",
      "Rencanakan stok mendekati batas atas untuk hari bertanda Gajian / Akhir pekan agar terhindar dari stockout.")
alert(ex, 20, 356, MW - 780, 84, "info", "Sumber data", "forecast_16d.parquet · diperbarui 15 Agu 2017")

# ---------------- 03 What-If Simulator
H3 = 1300
s3 = screen(3, "03 · Simulasi What-If & Safety Stock", H3)
sidebar(s3, H3, 2)
header(s3, "Beranda / Simulasi What-If", "Simulasi What-If & Safety Stock",
       "Uji skenario promosi dan hitung persediaan pengaman yang direkomendasikan sebelum membuat pesanan ke pemasok.",
       actions=(("💾 Simpan Skenario", "secondary"), ("🔁 Reset", "ghost")))
ctl = card(s3, MX, 150, 360, 760, "🎛️ Parameter Skenario", "Ubah nilai lalu lihat dampaknya secara langsung.")
select(ctl, 20, 76, 320, "Toko & kategori", "Toko 44 · GROCERY I")
slider(ctl, 20, 160, 320, "Jumlah item promo / hari", "30 item  (baseline 12)", 0.5, "0", "60")
slider(ctl, 20, 240, 320, "Lead time pemasok", "3 hari", 0.2, "1 hari", "14 hari", C["cyan"])
b.text("Service level (tingkat layanan)", 20, 322, ctl, 12, "Medium", C["muted"])
segmented(ctl, 20, 344, ["90%", "95%", "99%"], 1, 104, 36)
b.text("Z = 1,65 → peluang tidak kehabisan stok 95%", 20, 390, ctl, 11, color=C["dim"])
b.text("Kondisi kalender", 20, 424, ctl, 12, "Medium", C["muted"])
toggle(ctl, 20, 450, "Termasuk hari gajian", True, "15 & akhir bulan")
toggle(ctl, 20, 500, "Libur nasional", False, "tidak ada di 16–31 Agu")
toggle(ctl, 20, 550, "Bandingkan dengan baseline", True)
button(ctl, 20, 610, "▶ Jalankan Simulasi", "primary", w=320, h=46, size=14)
b.text("Terakhir dijalankan: 19:12 · 0,4 detik", 20, 672, ctl, 11, color=C["dim"], width=320, align="center")
b.text("ⓘ Simulasi memakai elastisitas promo per kategori dari data historis 2015–2017.", 20, 700, ctl, 11,
       color=C["dim"], width=320, lh="145%")
RX = MX + 380
RW = MW - 380
QK = (RW - 3 * 16) / 4
kpi(s3, RX, 150, QK, 140, "🚀", C["pink"], "Lift penjualan", "+8,7%", "+9.320 unit", C["pink"], foot="vs baseline 16 hari")
kpi(s3, RX + QK + 16, 150, QK, 140, "🛡️", C["cyan"], "Safety stock", "1.240", "unit", C["cyan"], foot="direkomendasikan")
kpi(s3, RX + 2 * (QK + 16), 150, QK, 140, "📍", C["primary"], "Reorder point", "21.860", "unit", C["violet"], foot="pesan ulang saat stok ≤")
kpi(s3, RX + 3 * (QK + 16), 150, QK, 140, "🟢", C["green"], "Risiko stockout", "Rendah", "4,8%", C["green"], foot="peluang kehabisan")
sc = card(s3, RX, 310, RW, 380, "Baseline vs Skenario — 16 Hari", "Unit per hari. Batang ungu = baseline, pink = dengan promo tambahan.")
legend(sc, RW - 280, 22, [("Baseline", C["primary"], False), ("Skenario", C["pink"], False)])
gx, gy, gw, gh = 70, 100, RW - 100, 220
for i in range(5):
    b.rect(gx, gy + gh * i / 4, gw, 1, sc, fill=C["border"])
    b.text(fmt(10000 - 2500 * i), gx - 58, gy + gh * i / 4 - 8, sc, 10, color=C["dim"], width=50, align="right")
slot = gw / 16
for i in range(16):
    v0 = store_fc[i]
    v1 = v0 * (1.087 + 0.02 * math.sin(i))
    for j, (v, col) in enumerate([(v0, C["primary"]), (v1, C["pink"])]):
        bh = gh * v / 10000
        b.rect(gx + i * slot + 4 + j * (slot / 2 - 3), gy + gh - bh, slot / 2 - 5, bh, sc, fill=col, cornerRadius=[3, 3, 0, 0])
    if i % 2 == 0:
        b.text(dlabel(FCD[i]).replace(" Agu", ""), gx + i * slot, gy + gh + 8, sc, 10, color=C["dim"], width=slot, align="center")
b.text("Agustus 2017", gx, gy + gh + 30, sc, 10, "Medium", C["dim"])
fm = card(s3, RX, 710, 420, 200, "🧮 Rumus Safety Stock")
fx = b.frame(20, 56, 380, 56, fm, "formula", fill=C["inp"], stroke=C["border2"], strokeWeight=1, cornerRadius=10)
b.text("SS = Z × σ × √L", 0, 14, fx, 22, "Bold", C["cyan"], width=380, align="center", family="Consolas")
b.text("Z = 1,65 (service level 95%) · σ = simpangan baku error harian (459 unit) · L = lead time 3 hari  →  1,65 × 459 × √3 ≈ 1.240 unit",
       20, 124, fm, 12, color=C["muted"], width=380, lh="150%")
rk = card(s3, RX + 440, 710, RW - 440, 200, "🧯 Buffer per Kategori", "Rekomendasi berdasarkan volatilitas")
for k, (cat, frac, lab, col) in enumerate([("PRODUCE (segar)", 0.55, "Sedang · +15%", C["amber"]),
                                           ("DAIRY (segar)", 0.35, "Rendah · +10%", C["green"]),
                                           ("SCHOOL & OFFICE", 0.92, "Tinggi · +40%", C["red"])]):
    yy = 70 + k * 42
    b.text(cat, 20, yy, rk, 12, "Medium", width=130)
    b.text(lab, 20, yy, rk, 11, "Bold", col, width=RW - 480, align="right")
    progress(rk, 20, yy + 20, RW - 480, frac, col, 6)
alert(s3, MX, 930, MW, 72, "warning", "Catatan penting",
      "Efek promosi pada model bersifat asosiatif (bukan sebab-akibat murni). Gunakan hasil simulasi sebagai panduan arah, "
      "lalu validasi dengan data penjualan aktual setelah promo berjalan.")
sv = card(s3, MX, 1022, MW, 238, "💾 Skenario Tersimpan", "Bandingkan beberapa skenario sebelum memutuskan")
SROWS = [("Baseline", "12", "3 hari", "95%", "107.420", "1.240", "Aktif"),
         ("Promo agresif", "30", "3 hari", "95%", "116.740", "1.310", "Dipilih"),
         ("Lead time panjang", "12", "7 hari", "99%", "107.420", "2.660", "Draft")]


def sc_cell(p, r, c, val, cx, ry, cw, rh):
    if c == 6:
        badge(p, cx + 12, ry + 8, val, {"Aktif": C["primary"], "Dipilih": C["green"], "Draft": C["dim"]}[val])
        return True
    return False


table(sv, 20, 72, MW - 40, [("Skenario", 220, "left"), ("Promo", 110, "right"), ("Lead time", 130, "right"), ("Service", 120, "right"),
                            ("Total forecast", 170, "right"), ("Safety stock", 160, "right"), ("Status", 130, "left")], SROWS, row_h=40,
      cell_fn=sc_cell)

# ---------------- 04 EDA Insights
H4 = 1420
s4 = screen(4, "04 · Insight EDA (Pola Bisnis)", H4)
sidebar(s4, H4, 3)
header(s4, "Beranda / Insight EDA", "Insight Data & Pola Bisnis",
       "Temuan utama dari analisis data 2013–2017: pola musiman, efek gajian, hari libur, gempa 2016, harga minyak, dan konsentrasi kategori.")
tabs(s4, MX, 150, ["📆 Pola Musiman", "💸 Hari Gajian", "🎉 Libur & Event", "🌋 Gempa 2016", "🛢️ Harga Minyak", "📦 Pareto"], 0, MW)
w1 = card(s4, MX, 210, 530, 360, "Rata-rata Penjualan per Hari dalam Seminggu", "Indeks (Senin = 100)")
vbars(w1, 30, 90, 470, 200, [(h, round(WEEK[i] / WEEK[0] * 100)) for i, h in enumerate(HARI)], C["primary"], highlight={5, 6},
      vfmt=lambda v: str(v), maxv=140)
w2 = card(s4, MX + 550, 210, MW - 550, 360, "Tren Total Penjualan Bulanan 2013–2017", "Juta unit per bulan · tren naik stabil")
mon = []
for m in range(56):
    yr, mo = 2013 + m // 12, m % 12
    mon.append(14 + m * 0.21 + (3.5 if mo == 11 else 0) + 0.8 * math.sin(m / 1.9))
line_chart(w2, 60, 100, MW - 550 - 90, 200, 56, 10, 32, [dict(values=mon, color=C["violet"], area=True, sw=2.5)],
           xlabels=[(0, "2013"), (12, "2014"), (24, "2015"), (36, "2016"), (48, "2017")], yfmt=lambda v: fmt(v), ygrid=4)
for m in [11, 23, 35, 47]:
    px = 60 + (MW - 640) * m / 55
    b.text("🎄", px - 8, 96 + 200 - 200 * (mon[m] - 10) / 22 - 26, w2, 13)
for k, (em, tt, dd, col) in enumerate([("📆", "Pola mingguan kuat", "Sabtu & Minggu ±20% di atas hari kerja; Kamis paling sepi.", C["primary"]),
                                       ("🎄", "Puncak Desember", "Setiap Desember penjualan melonjak ±25% (belanja akhir tahun).", C["violet"]),
                                       ("💸", "Efek gajian", "Tgl 15 & akhir bulan +9% vs hari biasa (gaji sektor publik).", C["amber"]),
                                       ("📈", "Lag paling informatif", "Rata-rata 7 & 14 hari terakhir menyumbang 84% gain model.", C["cyan"])]):
    f = card(s4, MX + k * (MW + 20) / 4, 590, (MW - 60) / 4, 150)
    icon_tile(f, 18, 18, em, col, 36)
    b.text(tt, 64, 26, f, 14, "Bold", width=(MW - 60) / 4 - 80)
    b.text(dd, 18, 70, f, 12, color=C["muted"], width=(MW - 60) / 4 - 36, lh="150%")
eq = card(s4, MX, 760, 530, 330, "🌋 Dampak Gempa 16 April 2016", "Total penjualan harian (ribu) · Mar–Mei 2016")
eqv = [620 + 40 * math.sin(i / 1.1) + (230 * math.exp(-(i - 46) / 6) if i >= 46 else 0) for i in range(90)]
line_chart(eq, 60, 96, 440, 180, 90, 500, 950, [dict(values=eqv, color=C["red"], sw=2)],
           xlabels=[(0, "1 Mar"), (46, "16 Apr"), (89, "29 Mei")], yfmt=lambda v: fmt(v), ygrid=3)
ex_ = 60 + 440 * 46 / 89
b.rect(ex_, 92, 1.5, 184, eq, fill=C["red"])
badge(eq, ex_ + 8, 100, "Gempa M7,8 · lonjakan donasi", C["red"], size=10, h=22)
oil = card(s4, MX + 550, 760, MW - 550, 330, "🛢️ Harga Minyak vs Penjualan", "Harga WTI (USD) turun, penjualan tetap naik → korelasi lemah")
oilv = [95 + 8 * math.sin(m / 2) if m < 20 else (95 - (m - 20) * 9 if m < 26 else 42 + 8 * math.sin(m / 3) - (12 if 36 <= m <= 38 else 0)) for m in range(56)]
legend(oil, MW - 550 - 260, 22, [("Minyak", C["amber"], False), ("Penjualan", C["violet"], True)])
line_chart(oil, 60, 96, MW - 550 - 90, 180, 56, 20, 110, [dict(values=oilv, color=C["amber"], sw=2.5),
                                                        dict(values=[20 + (v - 10) * 3.6 for v in mon], color=C["violet"], dash=True, sw=2)],
           xlabels=[(0, "2013"), (24, "2015"), (48, "2017")], yfmt=lambda v: fmt(v), ygrid=3)
pr_ = card(s4, MX, 1110, MW, 270, "📦 Pareto Kategori — 5 kategori menyumbang ±80% penjualan",
           "Batang = pangsa per kategori, garis = kumulatif")
PAR = [("GROCERY I", 32.0), ("BEVERAGES", 20.3), ("PRODUCE", 11.8), ("CLEANING", 9.0), ("DAIRY", 6.4), ("BREAD/BAK.", 3.9),
       ("POULTRY", 3.1), ("MEATS", 2.9), ("PERSONAL", 2.5), ("DELI", 2.3), ("Lainnya (23)", 5.8)]
px0, py0, pw, ph = 40, 86, MW - 80, 130
slot = pw / len(PAR)
cum, cpts = 0, []
for i, (lab, v) in enumerate(PAR):
    bh = ph * v / 35
    col = C["primary"] if i < 5 else C["border2"]
    b.rect(px0 + i * slot + 10, py0 + ph - bh, slot - 20, bh, pr_, fill=col, cornerRadius=[5, 5, 0, 0])
    b.text(f"{fmt(v, 1)}%", px0 + i * slot, py0 + ph - bh - 16, pr_, 10, "Bold", C["muted"], width=slot, align="center")
    b.text(lab, px0 + i * slot, py0 + ph + 8, pr_, 10, color=C["dim"], width=slot, align="center")
    cum += v
    cpts.append((px0 + i * slot + slot / 2, py0 + ph - ph * cum / 100))
b.poly(cpts, pr_, stroke=C["cyan"], sw=2.5)
for (a_, c_) in cpts:
    b.ellipse(a_ - 3.5, c_ - 3.5, 7, 7, pr_, fill=C["bg"], stroke=C["cyan"], strokeWeight=2)

# ---------------- 05 Model Performance
H5 = 1400
s5 = screen(5, "05 · Performa & Transparansi Model", H5)
sidebar(s5, H5, 4)
header(s5, "Beranda / Performa Model", "Performa & Transparansi Model",
       "Perbandingan 6 pendekatan pada validasi 15 hari terakhir (1–15 Agu 2017), faktor pendorong prediksi, dan di mana model masih kesulitan.",
       actions=(("📄 Unduh Ringkasan", "secondary"), ("📘 Arti Metrik", "primary")))
champ = b.frame(MX, 150, MW, 110, s5, "Champion", fills=[{"type": "linearGradient", "stops": ["#064E3B", "#0E7490"]}],
                cornerRadius=20, clip=True, stroke=C["green"] + "55", strokeWeight=1)
b.ellipse(MW - 200, -60, 240, 240, champ, fill="#FFFFFF10")
b.text("🏆", 28, 30, champ, 40)
b.text("Model terpilih: LightGBM (tuned)", 96, 26, champ, 22, "Bold", C["white"])
b.text("RMSLE 0,4045 · 26,9% lebih rendah dari baseline terbaik · konsisten pada time-series cross-validation (3 lipatan).", 96, 60,
       champ, 13, color="#A7F3D0", width=610)
for k, (lab, val) in enumerate([("R²", "0,970"), ("MAE", "63,5"), ("Latih", "117 dtk")]):
    b.text(val, MW - 330 + k * 105, 30, champ, 22, "Bold", C["white"], width=95, align="center")
    b.text(lab, MW - 330 + k * 105, 62, champ, 12, color="#A7F3D0", width=95, align="center")
lb = card(s5, MX, 280, MW, 360, "📋 Leaderboard Model", "Diurutkan dari RMSLE terendah (semakin kecil semakin baik)")
LB = [("🥇 LightGBM (tuned)", "0,4045", "214,9", "63,45", "0,9702", "13,6%", "117 dtk"),
      ("🥈 LightGBM", "0,4105", "216,6", "63,68", "0,9697", "13,7%", "99 dtk"),
      ("🥉 Random Forest", "0,4616", "235,4", "67,15", "0,9642", "14,4%", "124 dtk"),
      ("Ridge Regression", "0,5443", "312,4", "88,64", "0,9370", "19,1%", "19 dtk"),
      ("Baseline · Rata-rata 28 hari", "0,5536", "323,2", "96,74", "0,9325", "20,8%", "—"),
      ("Baseline · Seasonal naive", "0,6371", "334,5", "93,32", "0,9277", "20,1%", "—")]


def lb_cell(p, r, c, val, cx, ry, cw, rh):
    if c == 1:
        frac = 1 - (float(val.replace(",", ".")) - 0.38) / 0.3
        col = C["green"] if r == 0 else (C["cyan"] if r < 3 else C["dim"])
        b.text(val, cx + 12, ry + 11, p, 13, "Bold", col, width=60)
        progress(p, cx + 78, ry + 17, cw - 100, frac, col, 6)
        return True
    if c == 0 and r == 0:
        b.text(val, cx + 12, ry + 11, p, 13, "Bold", C["green"], width=cw - 24)
        return True
    return False


table(lb, 20, 72, MW - 40, [("Model", 270, "left"), ("RMSLE ↓", 230, "left"), ("RMSE", 100, "right"), ("MAE", 100, "right"),
                            ("R²", 100, "right"), ("WAPE", 100, "right"), ("Waktu", 140, "right")], LB, row_h=42, cell_fn=lb_cell)
fi = card(s5, MX, 660, 600, 440, "🔍 Feature Importance (gain) — Top 10", "Seberapa besar setiap fitur membantu model")
FI = [("roll_mean_7", 63.17), ("roll_mean_14", 20.60), ("lag_21", 3.95), ("dow_mean_3", 3.52), ("roll_mean_28", 2.02),
      ("lag_28", 1.00), ("family", 0.84), ("onpromotion", 0.69), ("lag_16", 0.67), ("hari", 0.53)]
hbars(fi, 20, 84, 560, FI, row_h=34, label_w=130, vfmt=lambda v: fmt(v, 2) + "%",
      colors=[C["primary"], C["primary"], C["violet"], C["violet"], C["violet"], C["cyan"], C["cyan"], C["pink"], C["cyan"], C["amber"]])
b.text("💡 roll_mean_7 = rata-rata penjualan 7 hari (digeser 16 hari) → level penjualan terbaru.", 20, 410, fi, 11, color=C["dim"], width=560)
gp = card(s5, MX + 620, 660, MW - 620, 210, "🧩 Kontribusi per Kelompok Fitur")
GPS = [("Lag & rolling penjualan", 96.31, C["primary"]), ("Kalender & gajian", 1.34, C["amber"]), ("Identitas toko/kategori", 1.11, C["violet"]),
       ("Promosi", 0.69, C["pink"]), ("Ekonomi & transaksi", 0.48, C["cyan"]), ("Libur & gempa", 0.07, C["green"])]
sx_ = 20
for lab, v, col in GPS:
    w_ = max((MW - 660) * v / 100, 6)
    b.rect(sx_, 60, w_, 28, gp, fill=col, cornerRadius=4)
    sx_ += w_ + 2
for k, (lab, v, col) in enumerate(GPS):
    xx, yy = 20 + (k % 2) * 220, 106 + (k // 2) * 30
    b.rect(xx, yy + 3, 10, 10, gp, fill=col, cornerRadius=3)
    b.text(f"{lab} · {fmt(v, 2)}%", xx + 18, yy, gp, 12, color=C["muted"], width=200)
hd = card(s5, MX + 620, 890, MW - 620, 210, "🎯 Sulit vs Mudah Diprediksi", "Per kategori produk (RMSLE validasi)")
for k, (lab, z) in enumerate([("SCHOOL & OFFICE", "74% hari nol"), ("LINGERIE", "16% hari nol"), ("GROCERY II", "12% hari nol")]):
    yy = 72 + k * 44
    b.text("🔴 " + lab, 20, yy, hd, 12, "Bold", width=190)
    b.text(z, 40, yy + 17, hd, 11, color=C["dim"], width=170)
for k, (lab, z) in enumerate([("BOOKS", "97% hari nol"), ("GROCERY I", "volume tinggi"), ("DAIRY", "pola stabil")]):
    yy = 72 + k * 44
    b.text("🟢 " + lab, 240, yy, hd, 12, "Bold", width=190)
    b.text(z, 260, yy + 17, hd, 11, color=C["dim"], width=170)
sp = card(s5, MX, 1120, 520, 250, "📍 Aktual vs Prediksi", "log1p(sales) · titik dekat garis = akurat")
r2 = lcg(11)
b.poly([(40, 220), (490, 70)], sp, stroke=C["red"], sw=1.5, dashes=[5, 4])
for i in range(120):
    t_ = next(r2)
    xx = 40 + 450 * t_
    yy = 220 - 150 * t_ + (next(r2) - 0.5) * 50 * (1.2 - t_)
    b.ellipse(xx, max(min(yy, 230), 70), 5, 5, sp, fill=C["cyan"] + "99")
of = card(s5, MX + 540, 1120, MW - 540, 250, "🧪 Cek Overfitting", "RMSLE train vs validasi (selisih kecil = sehat)")
for k, (lab, tr, va) in enumerate([("LightGBM (tuned)", 0.3997, 0.4045), ("LightGBM", 0.398, 0.4105), ("Random Forest", 0.36, 0.4616), ("Ridge", 0.54, 0.5443)]):
    yy = 80 + k * 40
    b.text(lab, 20, yy, of, 12, "Medium", width=140)
    progress(of, 160, yy + 2, MW - 540 - 280, tr / 0.6, C["violet"], 6)
    progress(of, 160, yy + 12, MW - 540 - 280, va / 0.6, C["cyan"], 6)
    b.text(f"{fmt(tr, 3)} / {fmt(va, 3)}", MW - 540 - 110, yy, of, 11, "Bold", C["muted"], width=90, align="right")
legend(of, 20, 226, [("Train", C["violet"], False), ("Validasi", C["cyan"], False)])

# ---------------- 06 Panduan & Bantuan (in-app)
H6 = 1360
s6 = screen(6, "06 · Panduan & Bantuan (In-App)", H6)
sidebar(s6, H6, 5)
header(s6, "Beranda / Panduan & Bantuan", "Panduan & Bantuan",
       "Semua yang perlu Anda ketahui untuk memakai aplikasi: mulai cepat, cara membaca grafik, glosarium metrik, dan FAQ.",
       actions=(("🎯 Ulangi Tur", "secondary"), ("✉️ Hubungi Tim", "primary")))
srch = b.frame(MX, 150, MW, 56, s6, "Search", fill=C["inp"], stroke=C["border2"], strokeWeight=1, cornerRadius=14)
b.text("🔍", 18, 16, srch, 18)
b.text("Cari panduan… mis. “cara unduh CSV”, “apa itu RMSLE”", 52, 18, srch, 14, color=C["dim"])
b.text("Ctrl + K", MW - 90, 18, srch, 12, "Bold", C["dim"])
b.text("🚀 Mulai Cepat — 5 Langkah", MX, 236, s6, 20, "Bold")
QS = [("1", "Atur filter", "Pilih periode, tipe toko & provinsi di sidebar.", C["primary"]),
      ("2", "Baca Beranda", "Pahami KPI & tren nasional dalam 30 detik.", C["sky"]),
      ("3", "Pilih toko", "Forecast Explorer → toko & kategori.", C["cyan"]),
      ("4", "Simulasikan", "Atur promo & lead time → safety stock.", C["pink"]),
      ("5", "Unduh", "Ekspor CSV/Excel untuk tim pengadaan.", C["green"])]
QW = (MW - 4 * 16) / 5
for k, (n_, t_, d_, col) in enumerate(QS):
    f = card(s6, MX + k * (QW + 16), 276, QW, 170)
    b.rect(0, 0, QW, 4, f, fill=col)
    b.ellipse(18, 22, 36, 36, f, fills=[{"type": "linearGradient", "stops": [col, col + "99"]}])
    b.text(n_, 18, 30, f, 15, "Bold", C["white"], width=36, align="center")
    b.text(t_, 18, 74, f, 15, "Bold")
    b.text(d_, 18, 100, f, 12, color=C["muted"], width=QW - 36, lh="150%")
    if k < 4:
        b.text("→", MX + k * (QW + 16) + QW - 2, 350, s6, 16, "Bold", C["dim"])
gl = card(s6, MX, 470, 520, 440, "📖 Glosarium Metrik", "Istilah yang muncul di aplikasi")
GL = [("RMSLE", "Error pada skala logaritmik → menilai selisih relatif. Metrik utama (makin kecil makin baik).", C["primary"]),
      ("WAPE", "Total error absolut ÷ total penjualan. 13,6% = rata-rata meleset 13,6%.", C["cyan"]),
      ("MAE", "Rata-rata selisih absolut dalam unit asli (±63 unit per toko-kategori-hari).", C["green"]),
      ("R²", "Porsi variasi penjualan yang dijelaskan model (0,97 = 97%).", C["amber"]),
      ("Safety stock", "Stok cadangan untuk meredam ketidakpastian permintaan & lead time.", C["pink"]),
      ("Lag / Rolling", "Penjualan di masa lalu (mis. 16 hari lalu) / rata-rata bergerak.", C["violet"])]
for k, (t_, d_, col) in enumerate(GL):
    yy = 74 + k * 60
    badge(gl, 20, yy, t_, col, size=11, h=24)
    b.text(d_, 140, yy + 2, gl, 12, color="#CBD5E1", width=360, lh="145%")
fq = card(s6, MX + 540, 470, MW - 540, 440, "❓ Pertanyaan yang Sering Diajukan")
FAQ = [("Mengapa horizon forecast 16 hari?", "Mengikuti periode test Kaggle (16–31 Agu 2017). Semua fitur lag ≥ 16 hari agar tidak terjadi kebocoran data.", True),
       ("Seberapa bisa dipercaya forecast-nya?", None, False),
       ("Kenapa ada kategori dengan error besar?", None, False),
       ("Bagaimana cara memperbarui data?", None, False),
       ("Apakah promo pasti menaikkan penjualan?", None, False),
       ("Bisakah saya mengunduh semua toko sekaligus?", None, False)]
yy = 62
for q, a_, open_ in FAQ:
    h_ = 104 if open_ else 42
    f = b.frame(20, yy, MW - 580, h_, fq, "FAQ/" + q, fill=C["card2"] if open_ else C["inp"],
                stroke=(C["primary"] + "77") if open_ else C["border"], strokeWeight=1, cornerRadius=12)
    b.text(q, 16, 12, f, 13, "Bold" if open_ else "Medium", width=MW - 660)
    b.text("−" if open_ else "+", MW - 610, 9, f, 18, "Bold", C["primary"] if open_ else C["muted"])
    if a_:
        b.text(a_, 16, 40, f, 12, color=C["muted"], width=MW - 640, lh="150%")
    yy += h_ + 8
tm = card(s6, MX, 930, 660, 390, "🎬 Video Tutorial", "Durasi 3:24 · Bahasa Indonesia")
vid = b.frame(20, 70, 620, 250, tm, "Video", fills=[GRAD_HERO], cornerRadius=14, clip=True)
b.ellipse(-60, 120, 260, 260, vid, fill="#FFFFFF12")
b.ellipse(280, 95, 60, 60, vid, fill="#FFFFFFE6", effects=SHADOW)
b.text("▶", 280, 108, vid, 26, "Bold", "#4338CA", width=64, align="center")
b.text("Tur lengkap Favorita Forecast", 20, 210, vid, 14, "Bold", C["white"])
progress(tm, 20, 340, 620, 0.32, C["pink"], 5)
b.text("1:05 / 3:24", 20, 356, tm, 11, color=C["dim"])
ct = card(s6, MX + 680, 930, MW - 680, 390, "👥 Tim Pengembang · Kelompok 7")
for k, (nm, rl) in enumerate([("Samudra Tsalasa Putra", "Business & Integrasi"), ("Dwi Aura Ningrum", "EDA & Preprocessing"),
                              ("Anavalis Ridho A. N.", "Modeling & Tuning"), ("Hany Nadya Fairuz", "Evaluasi & Interpretasi"),
                              ("Eka Lidya Rahmadini", "Data & Feature Eng."), ("Selsa Trikartika", "Forecast & Streamlit")]):
    yy = 64 + k * 50
    col = [C["primary"], C["pink"], C["cyan"], C["green"], C["amber"], C["violet"]][k]
    b.ellipse(20, yy, 36, 36, ct, fill=col + "33")
    b.text("".join(w[0] for w in nm.split()[:2]), 20, yy + 10, ct, 12, "Bold", col, width=36, align="center")
    b.text(nm, 68, yy + 2, ct, 13, "Bold", width=230)
    b.text(rl, 68, yy + 20, ct, 11, color=C["dim"], width=230)

# ---------------- 07 Coach-mark tour overlay
H7 = 1240
s7 = screen(7, "07 · Tur Interaktif (Coach-mark 2/5)", H7)
sidebar(s7, H7, 0)
header(s7, "Beranda", "Ringkasan Eksekutif", "Gambaran penjualan nasional dan proyeksi 16 hari ke depan.")
for k in range(4):
    kpi(s7, MX + k * (KW + 20), 150, KW, 150, ["💰", "📅", "🎯", "🏪"][k], [C["primary"], C["cyan"], C["green"], C["amber"]][k],
        ["Total forecast 16 hari", "Rata-rata harian", "Akurasi model (WAPE)", "Cakupan"][k],
        [f"{fmt(FC_TOTAL / 1000, 2)} Jt", f"{fmt(FC_TOTAL / 16)} rb", "13,6%", "1.782 seri"][k])
card(s7, MX, 320, MW, 400, "Tren Penjualan Nasional")
b.rect(0, 0, W, H7, s7, fill="#020617C7", name="Overlay")
# highlight sidebar filter
b.rect(10, 410, 260, 340, s7, fill="none", stroke=C["cyan"], strokeWeight=3, cornerRadius=16, dashes=[8, 6],
       effects=[{"type": "dropShadow", "color": "#22D3EE88", "offset": [0, 0], "radius": 24}])
fsc = b.frame(16, 416, 248, 328, s7, "Spotlight", fill=C["side"], cornerRadius=12, clip=True)
b.text("FILTER GLOBAL", 8, 4, fsc, 11, "Bold", C["dim"], letterSpacing="8%")
select(fsc, 8, 30, 232, "Periode forecast", "16 – 31 Agu 2017", "📅")
b.text("Tipe toko", 8, 104, fsc, 12, "Medium", C["muted"])
for j, t in enumerate("ABCDE"):
    b.rect(8 + j * 46, 124, 38, 30, fsc, fill=(C["primary"] + "33") if j < 4 else C["inp"],
           stroke=C["primary"] if j < 4 else C["border2"], strokeWeight=1, cornerRadius=8)
    b.text(t, 8 + j * 46, 131, fsc, 13, "Bold", width=38, align="center")
select(fsc, 8, 168, 232, "Provinsi", "Semua provinsi (16)")
select(fsc, 8, 240, 232, "Klaster toko", "Semua klaster (1–17)")
b.poly([(276, 520), (300, 508), (300, 532)], s7, fill=C["white"], closed=True)
pop = b.frame(300, 440, 420, 270, s7, "Coach-mark Popover", fill=C["white"], cornerRadius=18, effects=SHADOW)
badge(pop, 24, 22, "LANGKAH 2 DARI 5", C["primary"], size=11, h=26)
b.text("🎛️ Atur Filter Global", 24, 62, pop, 20, "Bold", "#0F172A")
b.text("Pilih periode, tipe toko, provinsi, dan klaster di sini. Semua halaman — Beranda, Explorer, Simulasi — otomatis "
       "menyesuaikan dengan pilihan Anda.", 24, 96, pop, 13, color="#475569", width=372, lh="155%")
for j in range(5):
    b.rect(24 + j * 22, 194, 16 if j != 1 else 28, 6, pop, fill=C["primary"] if j <= 1 else "#CBD5E1", cornerRadius=3)
b.text("Lewati tur", 24, 222, pop, 13, "Medium", "#64748B")
ghost_w = 96
f_ = b.frame(200, 212, ghost_w, 40, pop, "Btn back", fill="#F1F5F9", cornerRadius=10)
b.text("← Kembali", 0, 11, f_, 13, "Medium", "#334155", width=ghost_w, align="center")
button(pop, 306, 212, "Lanjut →", "primary", w=90)
b.text("Tekan Esc untuk menutup · → untuk lanjut", 300, 724, s7, 12, "Medium", "#94A3B8")

# ==================================================================== RUN
with open(SCRIPT, "w", encoding="utf-8") as fh:
    json.dump(b.steps, fh, ensure_ascii=False)
print(f"{len(b.steps)} langkah, id terakhir yang diprediksi = {b.nid - 1}")
res = subprocess.run([FC, "run", SCRIPT, "--out", OUT], capture_output=True, text=True, encoding="utf-8")
lines = [l for l in res.stdout.splitlines() if l.strip()]
bad = [l for l in lines if '"ok":false' in l]
print("\n".join(bad[:5]) if bad else "Semua langkah OK")
print(res.stderr[-1500:] if res.returncode else lines[-1])
# validasi id prediksi
ids = [json.loads(l).get("result", {}).get("id") for l in lines if l.startswith("{")]
creates = [s for s in b.steps if s["command"] != "page.rename"]
if ids and len(ids) == len(b.steps):
    exp = 2
    mism = 0
    for s, i in zip(b.steps, ids):
        if s["command"] == "page.rename":
            continue
        if i != exp:
            mism += 1
            if mism < 4:
                print("ID mismatch:", s["command"], "dapat", i, "harap", exp)
            exp = i
        exp += 1
    print("Validasi ID:", "cocok" if mism == 0 else f"{mism} selisih")
sys.exit(res.returncode)
