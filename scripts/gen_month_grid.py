#!/usr/bin/env python3
"""Front-view 3D monthly contribution grid (animated SVG, crimson).
Reads a JSON list of {date, contributionCount, weekday} on stdin (one month)
and writes an animated SVG to the path given as argv[1]."""
import sys, json, datetime

days = json.load(sys.stdin)
if not days:
    sys.exit("no days")
days.sort(key=lambda d: d["date"])
y, m, _ = map(int, days[0]["date"].split("-"))
month_name = datetime.date(y, m, 1).strftime("%B %Y").upper()
total = sum(d["contributionCount"] for d in days)
mx = max((d["contributionCount"] for d in days), default=0)

# crimson palette by level: (top, front)
PAL = [("#1c1116", "#120b0e"),   # 0
       ("#5c0a18", "#3a0610"),   # 1-2
       ("#8b0f20", "#590a15"),   # 3-5
       ("#c01530", "#7c0d1f"),   # 6-9
       ("#ff2d4d", "#b01530")]   # 10+
RAISE = [3, 10, 15, 20, 26]

def level(c):
    if c == 0: return 0
    if c <= 2: return 1
    if c <= 5: return 2
    if c <= 9: return 3
    return 4

# layout
COL, ROW, TILE = 46, 44, 34
ox, oy = 70, 142
W, H = 400, 420
WK = ["S", "M", "T", "W", "T", "F", "S"]

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       'font-family="ui-monospace,\'JetBrains Mono\',Consolas,monospace">']
svg.append('<defs><filter id="g" x="-40%" y="-40%" width="180%" height="180%">'
           '<feGaussianBlur stdDeviation="2.2" result="b"/><feMerge>'
           '<feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
svg.append(f'<rect width="{W}" height="{H}" rx="14" fill="#0a0a0c"/>')
svg.append(f'<rect width="{W}" height="{H}" rx="14" fill="none" stroke="#dc143c" stroke-opacity="0.18"/>')
# header (bright, readable)
svg.append(f'<text x="26" y="46" font-size="22" font-weight="700" fill="#f2f2f4">{month_name}</text>')
svg.append(f'<text x="26" y="70" font-size="13" fill="#dc143c">● {total} contributions this month</text>')
# weekday headers
for c in range(7):
    svg.append(f'<text x="{ox + c*COL + TILE/2}" y="114" font-size="11" fill="#7a7a82" '
               f'text-anchor="middle">{WK[c]}</text>')

# build grid rows
row = 0
first_wd = days[0]["weekday"]
cells = []
for i, d in enumerate(days):
    wd = d["weekday"]
    if i > 0 and wd == 0:
        row += 1
    cells.append((row, wd, d["contributionCount"], int(d["date"][8:10])))

# draw back-to-front (top rows first) for depth
delay = 0.0
for (row, wd, cnt, dom) in cells:
    lv = level(cnt)
    top, front = PAL[lv]
    h = RAISE[lv]
    x = ox + wd * COL
    y = oy + row * ROW
    b = round(delay, 2)
    # front face (grows)
    svg.append(f'<rect x="{x}" y="{y+TILE}" width="{TILE}" height="0" fill="{front}">'
               f'<animate attributeName="height" from="0" to="{h}" begin="{b}s" dur="0.5s" '
               f'fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.3 1"/></rect>')
    # top face (moves up as it grows)
    extra = ' filter="url(#g)"' if lv >= 3 else ''
    svg.append(f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="4" fill="{top}" '
               f'stroke="#000" stroke-opacity="0.25"{extra}>'
               f'<animate attributeName="y" from="{y}" to="{y-h}" begin="{b}s" dur="0.5s" '
               f'fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.3 1"/>')
    if lv >= 2:  # continuous subtle glow pulse on active days
        svg.append(f'<animate attributeName="opacity" values="1;0.72;1" begin="{b+0.6}s" '
                   f'dur="2.6s" repeatCount="indefinite"/>')
    svg.append('</rect>')
    # day number on active tiles
    if cnt > 0:
        svg.append(f'<text x="{x+TILE/2}" y="{y-h+TILE/2+4}" font-size="10" fill="#fff" '
                   f'text-anchor="middle" opacity="0.85"><animate attributeName="y" '
                   f'from="{y+TILE/2+4}" to="{y-h+TILE/2+4}" begin="{b}s" dur="0.5s" fill="freeze"/>{dom}</text>')
    delay += 0.035

svg.append('</svg>')
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(svg))
print(f"wrote {sys.argv[1]} — {month_name}, {total} contributions, {len(cells)} days")
