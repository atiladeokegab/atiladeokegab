# Animated PCB header: current enters from an edge connector, draws "ATILADE OKE" in gold
# traces letter by letter. Just the name: less is more. Pure SVG + CSS, no services.
# Regenerate: python3 tools/make_traces.py assets/traces.svg
import sys
from html import escape
W, H = 1040, 292
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
NX, NY, RAIL = (W - name_w) / 2 + 10, 50, 180
CARD_W, CARD_H, CM, CG = 293, 70, 50, 30
ROW_Y = [206, 302]
CARDS = []
_UNUSED = [
    ('DATA & AI', '@ ION'),
    ('ELECTRICAL ENGINEERING', 'University of Manchester'),
    ('#1| WORLDWIDE', 'IBM Z Student Ambassador · 2025–26'),
    ('8×| HACKATHON WINNER', '2× first place, incl. Worlds London'),
    ('AI AGENT TEAMS', 'Agents that plan, build and review'),
    ('IBM Z SOCIETY', 'Co-founded · 0 → 50 members'),
]
css, back, mid, sparks, pads, texts, mask, blue, refl = [], [], [], [], [], [], [], [], []

def dpath(points): return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)

def trace(id_, points, start, dur, width=7, idle=None, in_mask=False, bp=None, reflect=False):
    """Metallic trace (dark edge, gold body, highlight) that draws from its first point,
    with a white-hot spark riding the drawing edge; optionally keeps pulsing afterwards."""
    d = dpath(points)
    css.append(f'.{id_}{{animation:draw {dur:.2f}s ease-in-out {start:.2f}s both}}')
    common = f'class="{id_}" d="{d}" pathLength="100" fill="none" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="100" stroke-dashoffset="100"'
    mid.append(f'<path {common} stroke="{EDGE}" stroke-width="{width + 4}"/>')
    mid.append(f'<path {common} stroke="url(#gold)" stroke-width="{width}"/>')
    if reflect:
        refl.append(f'<path {common} stroke="url(#gold)" stroke-width="{width}"/>')
    if bp is not None:  # blueprint outline: fades in early, fades out once the copper is laid
        css.append(f'#{id_}b{{animation:bpin .45s ease-out {bp:.2f}s both,bpout .5s ease-in {start + dur:.2f}s forwards}}')
        blue.append(f'<path id="{id_}b" d="{d}" fill="none" stroke="{BLUE}" stroke-width="1.3" stroke-dasharray="4 4" stroke-linejoin="round" opacity="0"/>')
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
for k in range(5):  # edge-connector gold fingers
    back.append(f'<rect x="8" y="{RAIL - 39.5 + k * 17}" width="26" height="11" rx="2" fill="url(#gold)"/>')
back.append(f'<text x="10" y="{RAIL - 47}" font-size="9" fill="{MUTED}">J1 PWR</text>')
# --- power rail -----------------------------------------------------------------------------
RAIL_X1 = W - 36
t = 1.5
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
    bp_t = 0.25 + (x - NX) / name_w * 0.8
    trace(f'st{li}', [(ax, RAIL), (ax, ay)], t, 0.16, width=5, bp=bp_t, reflect=True)
    pad(f'sp{li}', ax, RAIL, t, r=5.5)
    for si, s in enumerate(strokes):
        trace(f'L{li}_{si}', s, t + 0.16, 0.55, width=LW, idle=(8.2 + li * 0.34) if si == 0 else None, in_mask=True, bp=bp_t, reflect=True)
    for pi, (px, py) in enumerate(padpts):
        blue.append(f'<path class="gd" d="M{x + px * U - 5:.1f},{NY + py * U:.1f} h10 M{x + px * U:.1f},{NY + py * U - 5:.1f} v10" stroke="{BLUE}" stroke-width="1"/>')
        pad(f'p{li}_{pi}', x + px * U, NY + py * U, t + 0.66)
    letters_done = t + 0.75
    t += 0.3; x += glyph_w(ch) + (gap_after(ch, nxt) if nxt != ' ' else GAP); li += 1
t = letters_done
css.append(f'.gd{{animation:bpin .45s ease-out .2s both,bpout .6s ease-in {t:.2f}s forwards}}'
           '@keyframes bpin{from{opacity:0}to{opacity:.6}}@keyframes bpout{from{opacity:.6}to{opacity:0}}')
t += 0.35
css.append(f'#nameglow{{animation:flash 1.4s ease-out {t:.2f}s both}}'
           '@keyframes flash{from{opacity:0}to{opacity:.38}}')
css.append(f'#sheen{{animation:sheen 1.8s ease-in-out {t:.2f}s 1 both}}'
           f'@keyframes sheen{{0%{{transform:translateX(-260px)}}100%{{transform:translateX({W + 60}px)}}}}')
t += 0.45
pad('railend', RAIL_X1, RAIL, 2.45, r=6.5)

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

css.append('@keyframes draw{to{stroke-dashoffset:0}}'
           '@keyframes spark{0%{stroke-dashoffset:0;opacity:1}90%{opacity:1}100%{stroke-dashoffset:-95;opacity:0}}'
           '@keyframes flow{0%{stroke-dashoffset:0;opacity:.8}100%{stroke-dashoffset:-100;opacity:.8}}'
           '@keyframes pop{0%{transform:scale(0)}65%{transform:scale(1.45)}100%{transform:scale(1)}}'
           '@keyframes show{from{opacity:0}to{opacity:1}}'
           '@keyframes card{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Atilade Oke, spelled out in gold circuit traces">
<defs>
 <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="{DOT}"/></pattern>
 <linearGradient id="gold" x1="0" y1="0" x2="46" y2="92" gradientUnits="userSpaceOnUse" spreadMethod="reflect"><stop offset="0" stop-color="#f6cf75"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="#b47d22"/></linearGradient>
 <linearGradient id="chip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#161d36"/><stop offset="1" stop-color="#0c1122"/></linearGradient>
 <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <radialGradient id="vig" cx="50%" cy="40%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/></radialGradient>
 <filter id="glow" x="-15%" y="-40%" width="130%" height="180%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="big" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="22"/></filter>
 <filter id="soft" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="1.6"/></filter>
 <linearGradient id="reflfade" x1="0" y1="{RAIL}" x2="0" y2="{RAIL + 100}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <mask id="reflmask" maskUnits="userSpaceOnUse" x="0" y="{RAIL}" width="{W}" height="{H - RAIL}"><rect x="0" y="{RAIL + 6}" width="{W}" height="{H - RAIL}" fill="url(#reflfade)"/></mask>
 <mask id="namemask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{''.join(mask)}</mask>
</defs>
<style>text{{font-family:{MONO}}}{''.join(css)}</style>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#vig)"/>
<ellipse id="nameglow" cx="{NX + name_w / 2}" cy="{NY + 3 * U}" rx="{name_w / 2 + 20}" ry="{4 * U}" fill="{GOLD}" filter="url(#big)" style="opacity:0"/>
{''.join(back)}
<g class="gd" stroke="{BLUE}" stroke-width="1" stroke-dasharray="2 6"><path d="M{NX - 26},{NY} H{NX + name_w + 26}"/><path d="M{NX - 26},{NY + 6 * U} H{NX + name_w + 26}"/></g>
<g class="gd" font-size="8" fill="{BLUE}"><text x="{NX - 30}" y="{NY + 3}" text-anchor="end">CAP</text><text x="{NX - 30}" y="{NY + 6 * U + 3}" text-anchor="end">BASE</text></g>
{''.join(blue)}
<g mask="url(#reflmask)"><g transform="translate(0,{2 * RAIL + 6}) scale(1,-1)" opacity=".5" filter="url(#soft)">{''.join(refl)}</g></g>
<g id="lit" filter="url(#glow)">{''.join(mid)}</g>
<g mask="url(#namemask)"><rect id="sheen" x="0" y="{NY - 10}" width="200" height="{6 * U + 20}" fill="url(#shine)" transform="translate(-260 0)"/></g>
<g filter="url(#glow)">{''.join(sparks)}</g>
{''.join(pads)}
{''.join(texts)}
</svg>'''
open(sys.argv[1], 'w').write(svg)
print(f'intro {t:.1f}s, {len(svg) // 1024} KB')
