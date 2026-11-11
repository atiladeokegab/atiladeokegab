# Animated PCB header: current enters from an edge connector, draws "ATILADE OKE" in gold
# traces letter by letter, then branches out to achievement chips. Pure SVG + CSS, no services.
# Regenerate: python3 tools/make_traces.py assets/traces.svg
import sys
from html import escape
W, H = 1040, 448
BG, DOT, EDGE, GOLD, HILITE, SPARK, INK, SUB, MUTED, BLUE, LED = (
    '#070a14', '#151c33', '#4a3210', '#dba33f', '#fff1c4', '#fffdf2', '#f4f6ff', '#f0c877', '#56618a', '#63c7ff', '#58f0a0')
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "Inter,'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
U = 15                                   # letter grid unit: letters are 4u wide, 6u tall
LETTERS = {  # (strokes on a 0..4 x 0..6 grid; first point of first stroke is where power enters, pad points)
    'A': ([[(0, 6), (0, 1.5), (1.5, 0), (2.5, 0), (4, 1.5), (4, 6)], [(0, 3.6), (4, 3.6)]], [(4, 6)]),
    'T': ([[(2, 6), (2, 0)], [(2, 0), (0, 0)], [(2, 0), (4, 0)]], [(0, 0), (4, 0)]),
    'I': ([[(0, 6), (0, 0)]], []),
    'L': ([[(1, 6), (0, 5), (0, 0)], [(1, 6), (4, 6)]], [(0, 0), (4, 6)]),
    'D': ([[(0, 6), (0, 0), (3, 0), (4, 1), (4, 5), (3, 6), (0, 6)]], []),
    'E': ([[(1, 6), (0, 5), (0, 1), (1, 0), (4, 0)], [(1, 6), (4, 6)], [(0, 3), (3, 3)]], [(4, 0), (3, 3), (4, 6)]),
    'O': ([[(1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6)]], []),
    'K': ([[(0, 6), (0, 0)], [(0, 3), (1, 3), (4, 0)], [(1, 3), (4, 6)]], [(0, 0), (4, 0), (4, 6)]),
}
NAME = 'ATILADE OKE'
GAP, SPACE, LW = 2 * U, 5 * U, 10            # letter gap, word space, letter stroke width
def glyph_w(c): return max(px for st in LETTERS[c][0] for px, _ in st) * U
def gap_after(a, b):                             # optical spacing: a bare stem needs less air
    return GAP * (0.8 if 'I' in (a, b) else 1)
name_w = 0
for a, b in zip(NAME, NAME[1:] + ' '):
    if a == ' ': name_w += SPACE - GAP; continue
    name_w += glyph_w(a) + (gap_after(a, b) if b != ' ' else GAP)
name_w -= GAP
NX, NY, RAIL = (W - name_w) / 2 + 10, 36, 166
CARD_W, CARD_H, CM, CG = 293, 70, 50, 30
ROW_Y = [206, 302]
CARDS = [
    ('DATA & AI', '@ ION'),
    ('ELECTRICAL ENGINEERING', 'University of Manchester'),
    ('#1| WORLDWIDE', 'IBM Z Student Ambassador · 2025–26'),
    ('8×| HACKATHON WINNER', '2× first place, incl. Worlds London'),
    ('AI AGENT TEAMS', 'Agents that plan, build and review'),
    ('IBM Z SOCIETY', 'Co-founded · 0 → 50 members'),
]
css, back, mid, sparks, pads, texts, mask = [], [], [], [], [], [], []

def dpath(points): return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)

def trace(id_, points, start, dur, width=7, idle=None, in_mask=False):
    """Metallic trace (dark edge, gold body, highlight) that draws from its first point,
    with a white-hot spark riding the drawing edge; optionally keeps pulsing afterwards."""
    d = dpath(points)
    css.append(f'.{id_}{{animation:draw {dur:.2f}s ease-in-out {start:.2f}s both}}')
    common = f'class="{id_}" d="{d}" pathLength="100" fill="none" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="100" stroke-dashoffset="100"'
    mid.append(f'<path {common} stroke="{EDGE}" stroke-width="{width + 4}"/>')
    mid.append(f'<path {common} stroke="url(#gold)" stroke-width="{width}"/>')
    mid.append(f'<path {common} stroke="{HILITE}" stroke-width="{max(1.2, width * 0.22):.1f}" stroke-opacity=".55" transform="translate(-0.8,-0.8)"/>')
    anim = f'spark {dur:.2f}s ease-in-out {start:.2f}s forwards'
    if idle is not None:
        anim += f',flow 3.4s linear {idle:.2f}s infinite'
    css.append(f'#{id_}s{{animation:{anim}}}')
    sparks.append(f'<path id="{id_}s" d="{d}" pathLength="100" stroke="{SPARK}" stroke-width="{width * 0.6:.1f}" fill="none" stroke-linecap="round" stroke-dasharray="5 95" opacity="0"/>')
    if in_mask:
        mask.append(f'<path d="{d}" stroke="#fff" stroke-width="{width}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')

def pad(id_, x, y, start, r=8):
    css.append(f'#{id_}{{animation:pop .45s ease-out {start:.2f}s both}}')
    pads.append(f'<g id="{id_}" style="transform-origin:{x:.1f}px {y:.1f}px"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 1.5}" fill="{EDGE}"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="url(#gold)"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.42:.1f}" fill="{BG}"/></g>')

def typed(id_, x, y, text, size, color, start, per=0.03, weight=700, anchor='start', spacing=0):
    cw = size * 0.6 + spacing; n = len(text); w = (n + 1) * cw * 1.06; dur = max(0.25, n * per)
    x0 = x - n * cw / 2 if anchor == 'middle' else x
    css.append(f'#{id_} rect{{animation:{id_} {dur:.2f}s steps({n}) {start:.2f}s both}}'
               f'@keyframes {id_}{{from{{width:0}}to{{width:{w:.0f}px}}}}')
    ls = f' letter-spacing="{spacing}"' if spacing else ''
    texts.append(f'<clipPath id="{id_}"><rect x="{x0:.1f}" y="{y - size}" height="{size * 1.5}" width="0"/></clipPath>'
                 f'<text x="{x0:.1f}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}"{ls} clip-path="url(#{id_})" xml:space="preserve">{escape(text)}</text>')
    return start + dur, x0 + n * cw

def wiped(id_, x, y, spans, size, start, weight=700, spacing=0.0, dur=0.5):
    """Proportional-font label revealed with a smooth left-to-right wipe. spans: [(text, colour)]."""
    n = sum(len(tx) for tx, _ in spans); w = n * (size * 0.74 + spacing) + 12
    css.append(f'#{id_} rect{{animation:{id_} {dur:.2f}s cubic-bezier(.3,.6,.4,1) {start:.2f}s both}}'
               f'@keyframes {id_}{{from{{width:0}}to{{width:{w:.0f}px}}}}')
    body = ''.join(f'<tspan fill="{c}">{escape(tx)}</tspan>' for tx, c in spans)
    texts.append(f'<clipPath id="{id_}"><rect x="{x:.1f}" y="{y - size}" height="{size * 1.5}" width="0"/></clipPath>'
                 f'<text x="{x:.1f}" y="{y}" style="font-family:{SANS}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" clip-path="url(#{id_})" xml:space="preserve">{body}</text>')
    return start + dur

# --- board furniture (static silkscreen, holes, passives) ----------------------------------
for x, y in [(22, 22), (W - 22, 22), (22, H - 22), (W - 22, H - 22)]:
    back.append(f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-width="3"/><circle cx="{x}" cy="{y}" r="3.5" fill="#02040a"/>')
for k in range(6):  # edge-connector gold fingers
    back.append(f'<rect x="8" y="{RAIL - 47 + k * 17}" width="26" height="11" rx="2" fill="url(#gold)"/>')
back.append(f'<text x="10" y="{RAIL - 55}" font-size="9" fill="{MUTED}">J1 PWR</text>')
for k, (lbl, x) in enumerate([('R1', 70), ('R2', 112), ('C1', 154)]):  # tiny passives, bottom-left
    y = H - 34
    back.append(f'<rect x="{x}" y="{y}" width="7" height="10" fill="{GOLD}" opacity=".7"/><rect x="{x + 7}" y="{y}" width="14" height="10" fill="#1b233d"/>'
                f'<rect x="{x + 21}" y="{y}" width="7" height="10" fill="{GOLD}" opacity=".7"/><text x="{x + 3}" y="{y - 5}" font-size="8" fill="{MUTED}">{lbl}</text>')
back.append(f'<text x="{W - 46}" y="{H - 18}" font-size="10" fill="{MUTED}" text-anchor="end">ATILADE-OKE  REV 2026  //  atilade.uk</text>')
# status LEDs, top right
css.append(f'#pwr{{animation:ledon .3s ease-out .35s both}}#act{{animation:ledon .3s ease-out 1.2s both,blink 1.1s steps(1) 1.5s infinite}}'
           '@keyframes ledon{from{fill-opacity:.12}to{fill-opacity:1}}@keyframes blink{50%{fill-opacity:.2}}')
for k, (lbl, col, id_) in enumerate([('PWR', LED, 'pwr'), ('ACT', BLUE, 'act')]):
    x = 230 + k * 56; ly = H - 29
    back.append(f'<circle id="{id_}" cx="{x}" cy="{ly}" r="4.5" fill="{col}" fill-opacity=".12" filter="url(#glow)"/><text x="{x + 9}" y="{ly + 3.5}" font-size="9" fill="{MUTED}">{lbl}</text>')

# --- power rail -----------------------------------------------------------------------------
RAIL_X1 = CM + 2 * (CARD_W + CG) + CARD_W + CG / 2
t = 0.35
trace('rail', [(34, RAIL), (RAIL_X1, RAIL)], t, 1.0, width=5, idle=7.5)
t += 0.5

# --- the name, letter by letter ---------------------------------------------------------------
x = NX; li = 0; letters_done = t
for ci, ch in enumerate(NAME):
    nxt = NAME[ci + 1] if ci + 1 < len(NAME) else ' '
    if ch == ' ':
        x += SPACE - GAP; continue
    strokes, padpts = LETTERS[ch]
    strokes = [[(x + px * U, NY + py * U) for px, py in s] for s in strokes]
    ax, ay = strokes[0][0]
    trace(f'st{li}', [(ax, RAIL), (ax, ay)], t, 0.16, width=5)
    pad(f'sp{li}', ax, RAIL, t, r=5.5)
    for si, s in enumerate(strokes):
        trace(f'L{li}_{si}', s, t + 0.16, 0.55, width=LW, idle=(6.4 + li * 0.34) if si == 0 else None, in_mask=True)
    for pi, (px, py) in enumerate(padpts):
        pad(f'p{li}_{pi}', x + px * U, NY + py * U, t + 0.66)
    letters_done = t + 0.75
    t += 0.3; x += glyph_w(ch) + (gap_after(ch, nxt) if nxt != ' ' else GAP); li += 1
t = letters_done
css.append(f'#nameglow{{animation:flash 1.4s ease-out {t:.2f}s both}}'
           '@keyframes flash{0%{opacity:0}22%{opacity:.95}100%{opacity:.38}}')
css.append(f'#sheen{{animation:sheen 5.5s ease-in-out {t:.2f}s infinite}}'
           f'@keyframes sheen{{0%{{transform:translateX(-260px)}}28%,100%{{transform:translateX({W + 60}px)}}}}')
t += 0.45

# --- branches to the achievement chips -----------------------------------------------------
for i, (title, sub) in enumerate(CARDS):
    row, col = divmod(i, 3)
    cx = CM + col * (CARD_W + CG); cy = ROW_Y[row]
    if row == 0:
        bx = cx + CARD_W / 2; path = [(bx, RAIL), (bx, cy - 2)]
    else:  # drop down the gap to the chip's right, then turn in
        gx = cx + CARD_W + CG / 2; my = cy + CARD_H / 2
        path = [(gx, RAIL), (gx, my - 10), (gx - 10, my), (cx + CARD_W + 2, my)]
    trace(f'br{i}', path, t, 0.45, width=5, idle=8.0 + i * 0.4)
    pad(f'bp{i}', path[0][0], RAIL, t, r=5.5)
    arrive = t + 0.45
    css.append(f'#cd{i}{{animation:card .5s ease-out {arrive:.2f}s both}}#led{i}{{animation:ledon .25s ease-out {arrive + .15:.2f}s both}}')
    pins = ''.join(f'<rect x="{cx + 14 + k * 13.4:.1f}" y="{cy - 5}" width="6" height="6" fill="url(#gold)" opacity=".8"/>'
                   f'<rect x="{cx + 14 + k * 13.4:.1f}" y="{cy + CARD_H - 1}" width="6" height="6" fill="url(#gold)" opacity=".8"/>' for k in range(20))
    back.append(f'<g id="cd{i}">{pins}<rect x="{cx}" y="{cy}" width="{CARD_W}" height="{CARD_H}" rx="7" fill="url(#chip)" stroke="{GOLD}" stroke-opacity=".5"/>'
                f'<circle cx="{cx + 12}" cy="{cy + 12}" r="3" fill="#0a0e1a" stroke="{MUTED}" stroke-opacity=".6"/>'
                f'<text x="{cx + CARD_W - 12}" y="{cy + CARD_H - 10}" font-size="8" fill="{MUTED}" text-anchor="end">U{i + 1}</text>'
                f'<circle id="led{i}" cx="{cx + CARD_W - 16}" cy="{cy + 16}" r="4" fill="{LED}" fill-opacity=".12" filter="url(#glow)"/></g>')
    lead, _, rest = title.rpartition('|')
    e = wiped(f'ti{i}', cx + 24, cy + 31, [(lead, '#ffd27a'), (rest, INK)], 13.5, arrive + 0.1, weight=700, spacing=1.1)
    wiped(f'su{i}', cx + 24, cy + 52, [(sub, SUB)], 12.5, e - 0.2, weight=400, spacing=0.2, dur=0.45)
    t += 0.28
t += 0.9

# --- closing line + cursor -------------------------------------------------------------------
e, ex = typed('tag', W / 2, H - 28, 'I BUILD THE FUTURE', 16, BLUE, t, per=0.05, anchor='middle', spacing=3)
css.append(f'#cur{{animation:show 0s {e:.2f}s both,cblink 1s steps(1) {e:.2f}s infinite}}@keyframes cblink{{50%{{opacity:0}}}}')
texts.append(f'<rect id="cur" x="{ex + 4:.1f}" y="{H - 42}" width="9" height="17" fill="{BLUE}" opacity="0"/>')

css.append('@keyframes draw{to{stroke-dashoffset:0}}'
           '@keyframes spark{0%{stroke-dashoffset:0;opacity:1}90%{opacity:1}100%{stroke-dashoffset:-95;opacity:0}}'
           '@keyframes flow{0%{stroke-dashoffset:0;opacity:.8}100%{stroke-dashoffset:-100;opacity:.8}}'
           '@keyframes pop{0%{transform:scale(0)}65%{transform:scale(1.45)}100%{transform:scale(1)}}'
           '@keyframes show{from{opacity:0}to{opacity:1}}'
           '@keyframes card{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Atilade Oke, spelled out in gold circuit traces. Data and AI at ION. Electrical Engineering at Manchester. Number 1 IBM Z Student Ambassador worldwide. 8x hackathon winner. I build the future.">
<defs>
 <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="{DOT}"/></pattern>
 <linearGradient id="gold" x1="0" y1="0" x2="46" y2="92" gradientUnits="userSpaceOnUse" spreadMethod="reflect"><stop offset="0" stop-color="#f6cf75"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="#b47d22"/></linearGradient>
 <linearGradient id="chip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#161d36"/><stop offset="1" stop-color="#0c1122"/></linearGradient>
 <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <radialGradient id="vig" cx="50%" cy="40%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/></radialGradient>
 <filter id="glow" x="-15%" y="-40%" width="130%" height="180%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="big" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="22"/></filter>
 <mask id="namemask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{''.join(mask)}</mask>
</defs>
<style>text{{font-family:{MONO}}}{''.join(css)}</style>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#vig)"/>
<ellipse id="nameglow" cx="{NX + name_w / 2}" cy="{NY + 3 * U}" rx="{name_w / 2 + 20}" ry="{4 * U}" fill="{GOLD}" filter="url(#big)" style="opacity:0"/>
{''.join(back)}
<g filter="url(#glow)">{''.join(mid)}</g>
<g mask="url(#namemask)"><rect id="sheen" x="0" y="{NY - 10}" width="200" height="{6 * U + 20}" fill="url(#shine)" transform="translate(-260 0)"/></g>
<g filter="url(#glow)">{''.join(sparks)}</g>
{''.join(pads)}
{''.join(texts)}
</svg>'''
open(sys.argv[1], 'w').write(svg)
print(f'intro {e:.1f}s, {len(svg) // 1024} KB')
