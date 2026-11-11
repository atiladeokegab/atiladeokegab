# Animated circuit-board header for the GitHub profile: a chip powers on, traces route out,
# and each achievement "lights up" when current reaches it. Pure SVG + CSS, no external services.
import sys
from html import escape
W, H = 1040, 560
BG, GRID, COPPER, LIVE, HOT, INK, MUTED = '#06100b', '#10261a', '#1c4a31', '#3dffa8', '#eaff7a', '#e8fff1', '#7fbf9a'
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
CX, CY, CHW, CHH = W / 2, H / 2 - 10, 270, 128          # chip centre and size
CL, CR, CT = CX - CHW / 2, CX + CHW / 2, CY - CHH / 2
CARD_W, CARD_H = 290, 64
LEFT_X, RIGHT_X = 24, W - 24 - CARD_W
ROWS = [CY - 160, CY, CY + 160]
PINS = [CY - 36, CY, CY + 36]
CARDS = [  # (side, row, title, subtitle)
    ('L', 0, 'DATA & AI', '@ ION'),
    ('R', 0, '#1 IBM Z STUDENT AMBASSADOR', 'worldwide, 2025-26'),
    ('L', 1, 'ELECTRICAL ENGINEERING', 'University of Manchester'),
    ('R', 1, '8x HACKATHON WINNER', '2x 1st place, incl. Worlds London'),
    ('L', 2, 'AI AGENT TEAMS', 'agents that plan, build and review'),
    ('R', 2, 'IBM Z SOCIETY', 'co-founded: 0 -> 50 members'),
]
css, out = [], []

def typed(id_, x, y, text, size, color, start, per=0.035, weight=700, anchor_w=None):
    """Text revealed left-to-right one character at a time (clip-rect steps)."""
    cw = size * 0.6
    n = len(text); w = (n + 1) * cw * 1.06; dur = max(0.25, n * per)
    css.append(f'#{id_} rect{{animation:{id_} {dur:.2f}s steps({n}) {start:.2f}s both}}'
               f'@keyframes {id_}{{from{{width:0}}to{{width:{w:.0f}px}}}}')
    out.append(f'<clipPath id="{id_}"><rect x="{x}" y="{y - size}" height="{size * 1.5}" width="0"/></clipPath>'
               f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" clip-path="url(#{id_})" xml:space="preserve">{escape(text)}</text>')
    return start + dur

def route(x0, y0, x1, y1, xm, ch=12):
    """PCB-style trace: horizontal, 45-degree chamfer, vertical, chamfer, horizontal."""
    if y0 == y1:
        return f'M{x0},{y0} H{x1}'
    sx = 1 if x1 > x0 else -1; sy = 1 if y1 > y0 else -1
    return (f'M{x0},{y0} H{xm - sx * ch} L{xm},{y0 + sy * ch} V{y1 - sy * ch} '
            f'L{xm + sx * ch},{y1} H{x1}')

# --- board furniture (static) -------------------------------------------------------------
deco = []
for i, (x, y) in enumerate([(22, 22), (W - 22, 22), (22, H - 22), (W - 22, H - 22)]):
    deco.append(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{COPPER}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="3" fill="#020604"/>')
for k in range(9):  # faint background bus lines along the bottom and top
    y = H - 46 + (k % 3) * 6 if k < 3 else (40 + (k % 3) * 6 if k < 6 else None)
    if y: deco.append(f'<path d="M{120 + k * 9},{y} H{W - 120 - k * 9}" stroke="{GRID}" stroke-width="2"/>')
deco.append(f'<text x="{W - 48}" y="{H - 18}" font-size="10" fill="{COPPER}" text-anchor="end">ATILADE-OKE  REV 2026  //  atilade.uk</text>')
deco.append(f'<text x="{CL}" y="{CT - 10}" font-size="10" fill="{MUTED}">U1</text>')

# --- chip ---------------------------------------------------------------------------------
t = 0.4
css.append(f'#chip{{animation:power .9s ease-out {t}s both}}'
           '@keyframes power{0%{opacity:.15;filter:brightness(.4)}55%{opacity:1;filter:brightness(2.2)}100%{opacity:1;filter:none}}')
chip = [f'<rect x="{CL}" y="{CT}" width="{CHW}" height="{CHH}" rx="10" fill="#0b1712" stroke="{LIVE}" stroke-width="1.5"/>',
        f'<circle cx="{CL + 14}" cy="{CT + 14}" r="3.5" fill="{LIVE}"/>']
for i in range(11):  # top/bottom pins
    x = CL + 22 + i * (CHW - 44) / 10
    chip.append(f'<rect x="{x - 3}" y="{CT - 9}" width="6" height="9" fill="{COPPER}"/><rect x="{x - 3}" y="{CT + CHH}" width="6" height="9" fill="{COPPER}"/>')
for y in PINS:
    chip.append(f'<rect x="{CL - 9}" y="{y - 3}" width="9" height="6" fill="{LIVE}"/><rect x="{CR}" y="{y - 3}" width="9" height="6" fill="{LIVE}"/>')
t += 0.9
name = 'ATILADE OKE'; size = 30
t = typed('nm', CX - len(name) * size * 0.6 / 2, CY + 4, name, size, INK, t, per=0.07)
tag = 'I BUILD THE FUTURE'
t = typed('tg', CX - len(tag) * 12 * 0.6 / 2, CY + 34, tag, 12, LIVE, t + 0.1, per=0.03, weight=600)
t += 0.3

# --- traces + cards -----------------------------------------------------------------------
traces, pulses = [], []
for i, (side, row, title, sub) in enumerate(CARDS):
    yc, yp = ROWS[row], PINS[row]
    if side == 'L':
        x0, x1, xm, cx = CL - 9, LEFT_X + CARD_W, CL - 60, LEFT_X
    else:
        x0, x1, xm, cx = CR + 9, RIGHT_X, CR + 60, RIGHT_X
    d = route(x0, yp, x1, yc, xm)
    draw = 0.55
    css.append(f'#tr{i}{{animation:draw {draw}s ease-in {t:.2f}s both}}')
    traces.append(f'<path id="tr{i}" d="{d}" pathLength="100" stroke="{LIVE}" stroke-width="2.5" fill="none" stroke-dasharray="100" stroke-dashoffset="100" stroke-linejoin="round"/>')
    arrive = t + draw
    # endless current pulses after the trace is live
    css.append(f'#pu{i}{{animation:show 0s {arrive:.2f}s both,flow 2.4s linear {arrive + i * 0.37:.2f}s infinite}}')
    pulses.append(f'<path id="pu{i}" d="{d}" pathLength="100" stroke="{HOT}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-dasharray="7 93" opacity="0"/>')
    # pad + card light up on arrival
    px = x1
    css.append(f'#pad{i}{{animation:pad .5s ease-out {arrive:.2f}s both}}#cd{i}{{animation:card .45s ease-out {arrive:.2f}s both}}')
    out.append(f'<g id="cd{i}"><rect x="{cx}" y="{yc - CARD_H / 2}" width="{CARD_W}" height="{CARD_H}" rx="10" fill="#0a1a12" stroke="{LIVE}" stroke-opacity=".55"/></g>')
    out.append(f'<circle id="pad{i}" cx="{px}" cy="{yc}" r="6" fill="{LIVE}"/>')
    tx = cx + 18
    e = typed(f'ti{i}', tx, yc - 4, title, 14, INK, arrive + 0.15, per=0.025)
    typed(f'su{i}', tx, yc + 17, sub, 12, MUTED, e, per=0.018, weight=500)
    t = arrive + 0.35
css.append('@keyframes draw{to{stroke-dashoffset:0}}'
           '@keyframes flow{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}'
           '@keyframes show{from{opacity:0}to{opacity:1}}'
           '@keyframes pad{0%{opacity:0;r:0}60%{opacity:1;r:11}100%{opacity:1;r:6}}'
           '@keyframes card{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}')
# chip heartbeat once everything is live
css.append(f'#beat{{animation:show 0s {t:.2f}s both,beat 2.4s ease-in-out {t:.2f}s infinite}}'
           '@keyframes beat{0%,100%{stroke-opacity:.15}50%{stroke-opacity:.7}}')
beat = f'<rect id="beat" x="{CL - 6}" y="{CT - 6}" width="{CHW + 12}" height="{CHH + 12}" rx="14" fill="none" stroke="{LIVE}" stroke-width="2" opacity="0"/>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Atilade Oke: Data and AI at ION, Electrical Engineering at Manchester, number 1 IBM Z Student Ambassador worldwide, 8x hackathon winner">
<defs>
 <pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="11" cy="11" r="1.1" fill="{GRID}"/></pattern>
 <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <radialGradient id="halo" cx="50%" cy="48%" r="45%"><stop offset="0" stop-color="{LIVE}" stop-opacity=".10"/><stop offset="1" stop-color="{LIVE}" stop-opacity="0"/></radialGradient>
</defs>
<style>text{{font-family:{MONO}}}{''.join(css)}</style>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#halo)"/>
{''.join(deco)}
<g stroke="{COPPER}" stroke-width="2.5" fill="none">{''.join(f'<path d="{route(*a)}"/>' for a in [(CL - 9, PINS[r], (LEFT_X + CARD_W if s == 'L' else RIGHT_X), ROWS[r], (CL - 60 if s == 'L' else CR + 60)) for s, r, *_ in CARDS] for _ in [0])}</g>
<g filter="url(#glow)">{''.join(traces)}{''.join(pulses)}</g>
{beat}
<g id="chip" filter="url(#glow)">{''.join(chip)}</g>
<g filter="url(#glow)">{''.join(o for o in out if o.startswith('<circle'))}</g>
{''.join(o for o in out if not o.startswith('<circle'))}
</svg>'''
open(sys.argv[1], 'w').write(svg)
print('intro', round(t, 1), 's')
