# Animated PCB header: current enters from an edge connector, draws "ATILADE OKE" in gold
# traces letter by letter. Just the name: less is more. Pure SVG + CSS, no services.
# Regenerate: python3 tools/make_traces.py assets/traces.svg
import sys
from html import escape
W, H = 1040, 270
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
NX, NY, RAIL = (W - name_w) / 2 + 10, 66, 66 + 6 * U + 8
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
# --- power rail -----------------------------------------------------------------------------
RAIL_X1 = W - 36
t = 1.3

# --- the name, letter by letter ---------------------------------------------------------------
x = NX; li = 0; letters_done = t; LXS = []
for ci, ch in enumerate(NAME):
    nxt = NAME[ci + 1] if ci + 1 < len(NAME) else ' '
    if ch == ' ':
        x += SPACE - GAP; continue
    strokes, padpts = LETTERS[ch]; LXS.append(x)
    strokes = [[(x + px * U, NY + py * U) for px, py in s] for s in strokes]
    ax, ay = strokes[0][0]
    bp_t = 0.25 + (x - NX) / name_w * 0.8
    for si, s in enumerate(strokes):
        trace(f'L{li}_{si}', s, t + 0.16, 0.55, width=LW, in_mask=True, bp=bp_t, reflect=True)
    for pi, (px, py) in enumerate(padpts):
        blue.append(f'<path class="gd" d="M{x + px * U - 5:.1f},{NY + py * U:.1f} h10 M{x + px * U:.1f},{NY + py * U - 5:.1f} v10" stroke="{BLUE}" stroke-width="1"/>')
        pad(f'p{li}_{pi}', x + px * U, NY + py * U, t + 0.66)
    letters_done = t + 0.75
    t += 0.3; x += glyph_w(ch) + (gap_after(ch, nxt) if nxt != ' ' else GAP); li += 1
t = letters_done
css.append(f'.gd{{animation:bpin .45s ease-out .2s both,bpout .6s ease-in {t:.2f}s forwards}}'
           '@keyframes bpin{from{opacity:0}to{opacity:.6}}@keyframes bpout{from{opacity:.6}to{opacity:0}}')
# --- the story: switch fails, flickers, bonk, sprint, crown fixed, light on ---------------
D = t                                   # name fully drawn, still unlit
BASE = NY + 6 * U; FLOOR = BASE + 58
SWX = LXS[9] + 2 * U; TX = LXS[1] + 2 * U
BX, OX = SWX + 19, SWX + 44             # where Bip and Bop stand at the switch
F, LT = D + 3.66, D + 12.0              # flicker, light on

def anim(sel, frames):
    """one absolute-time keyframe track; frames = [(seconds, css)]"""
    if frames[0][0] > 0: frames = [(0, frames[0][1])] + frames
    name = f'k{len(css)}'; end = frames[-1][0]
    body = ''.join(f'{ts / end * 100:.3f}%{{{decl}}}' for ts, decl in frames)
    css.append(f'{sel}{{animation:{name} {end:.2f}s linear both}}@keyframes {name}{{{body}}}')

def at(x, y, ease=''):
    return f'transform:translate({x:.1f}px,{y:.1f}px)' + (f';animation-timing-function:{ease}' if ease else '')

def light(sel, lo, hi):
    m = lo + (hi - lo) * .8
    o = lambda v: f'opacity:{v:.2f}'
    anim(sel, [(F, o(lo)), (F + .02, o(m)), (F + .10, o(m)), (F + .12, o(lo)), (F + .24, o(lo)), (F + .26, o(m)),
               (F + .36, o(m)), (F + .38, o(lo)), (LT, o(lo)), (LT + .3, o(hi))])

for sel, lo, hi in [('#lit', .3, 1), ('#padsg', .3, 1), ('#nameglow', 0, .38), ('#reflg', .2, 1), ('#swled', 0, 1)]:
    light(sel, lo, hi)
css.append(f'#sheen{{animation:sheen 1.8s ease-in-out {LT + .2:.2f}s 1 both}}'
           f'@keyframes sheen{{0%{{transform:translateX(-260px)}}100%{{transform:translateX({W + 60}px)}}}}')

css.append('@keyframes wk1{from{transform:rotate(26deg)}to{transform:rotate(-26deg)}}'
           '@keyframes wk2{from{transform:rotate(-26deg)}to{transform:rotate(26deg)}}'
           '@keyframes poke{50%{transform:rotate(48deg)}}'
           '@keyframes bonk{45%,60%{transform:rotate(78deg)}78%{transform:rotate(-28deg)}}'
           '@keyframes clm{from{transform:rotate(105deg)}to{transform:rotate(40deg)}}'
           '@keyframes push{to{transform:rotate(138deg)}}'
           '@keyframes sit{to{transform:rotate(82deg)}}'
           '@keyframes cheer{to{transform:rotate(98deg)}}'
           '@keyframes sq{30%{transform:scale(1.25,.6)}60%{transform:scale(.9,1.12)}}'
           '@keyframes blip{0%{opacity:0;transform:translateY(5px)}20%,80%{opacity:1;transform:none}100%{opacity:0}}'
           '@keyframes star{0%{opacity:0;transform:scale(0)}30%{opacity:1;transform:scale(1.2)}100%{opacity:0;transform:scale(1.7)}}'
           '@keyframes crown{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:none}}')

def walk(start, dur, half):   # leg cycles for one stretch of walking
    n = max(1, round(dur / half))
    return [f'wk1 {half}s ease-in-out {start:.2f}s {n} alternate', f'wk2 {half}s ease-in-out {start:.2f}s {n} alternate']

def bot(id_, col, shade, line, bubble):
    return (f'<g class="{id_}" transform="translate({W + 40},{FLOOR})">'
            f'<text class="{id_}t" x="0" y="-47" text-anchor="middle" font-size="16" font-weight="800" fill="{HILITE}" style="font-family:{SANS};opacity:0">{bubble}</text>'
            f'<g transform="translate(0,-40)"><path class="{id_}x" d="M0,-9 L2.5,-2.5 L9,0 L2.5,2.5 L0,9 L-2.5,2.5 L-9,0 L-2.5,-2.5 Z" fill="{HILITE}" style="opacity:0"/></g>'
            f'<g class="{id_}q">'
            f'<path class="{id_}l1" d="M-5,-9V-1.5" stroke="{shade}" stroke-width="4.5" stroke-linecap="round" style="transform-origin:-5px -9px"/>'
            f'<path class="{id_}l2" d="M5,-9V-1.5" stroke="{shade}" stroke-width="4.5" stroke-linecap="round" style="transform-origin:5px -9px"/>'
            f'<path d="M0,-34V-40" stroke="{line}" stroke-width="1.6"/><circle cx="0" cy="-41.5" r="2.4" fill="{HILITE}" stroke="{line}" stroke-width="1"/>'
            f'<rect x="-12" y="-34" width="24" height="27" rx="11" fill="{col}" stroke="{line}" stroke-width="1.6"/>'
            f'<path d="M4,-30 Q9,-28 9,-21" stroke="#fff" stroke-width="2" stroke-linecap="round" fill="none" opacity=".45"/>'
            f'<rect x="-10.5" y="-28.5" width="16" height="10" rx="5" fill="#0a0e1a"/>'
            f'<g class="{id_}e"><circle cx="-6.5" cy="-23.5" r="2" fill="#fff"/><circle cx="-0.5" cy="-23.5" r="2" fill="#fff"/></g>'
            f'<path class="{id_}a" d="M-1,-16 L-13,-11" stroke="{shade}" stroke-width="4.5" stroke-linecap="round" style="transform-origin:-1px -16px"/>'
            f'<circle cx="-1" cy="-16" r="2.6" fill="{shade}"/>'
            f'</g></g>')

def multi(sel, anims): css.append(f'{sel}{{animation:{",".join(anims)}}}')

# Bip: flips the switch, gets bonked, sprints off and sits on the T
anim('.bip', [(D + .3, at(W + 40, FLOOR)), (D + 1.7, at(BX, FLOOR)), (D + 5.4, at(BX, FLOOR)),
              (D + 6.9, at(TX + 46, FLOOR)), (D + 7.08, at(TX + 46, FLOOR, 'cubic-bezier(.2,.8,.4,1)')),
              (D + 7.38, at(TX + 14, NY - 22, 'cubic-bezier(.6,0,.9,.4)')), (D + 7.62, at(TX, NY)), (LT + 1, at(TX, NY))])
b1 = walk(D + .3, 1.4, .2); b2 = walk(D + 5.4, 1.5, .075)
for k, leg in enumerate(('.bipl1', '.bipl2')):
    multi(leg, [b1[k], b2[k], f'sit .15s ease-out {D + 7.5:.2f}s forwards'])
multi('.bipa', [f'poke .35s ease-in-out {D + 2.15:.2f}s', f'poke .35s ease-in-out {D + 3.05:.2f}s',
                f'poke .35s ease-in-out {D + 3.45:.2f}s', f'cheer .3s ease-out {LT + .25:.2f}s forwards'])
multi('.bipq', [f'sq .45s ease-out {D + 5.03:.2f}s', f'sq .25s ease-out {D + 6.9:.2f}s', f'sq .3s ease-out {D + 7.62:.2f}s'])
multi('.bipt', [f'blip .7s ease-out {D + 2.6:.2f}s'])
multi('.bipx', [f'star .45s ease-out {D + 5.03:.2f}s'])
# Bop: bonks Bip, spots the crooked crown, climbs the A and straightens it
CLX, CLY = NX - 5, NY + 24
anim('.bop', [(D + 2.6, at(W + 40, FLOOR)), (D + 4.4, at(OX, FLOOR)), (D + 4.85, at(OX, FLOOR)), (D + 5.0, at(OX - 7, FLOOR - 7)),
              (D + 5.15, at(OX, FLOOR)), (D + 6.3, at(OX, FLOOR)), (D + 9.7, at(CLX, FLOOR)), (D + 11.1, at(CLX, CLY)),
              (D + 11.38, at(CLX, CLY)), (D + 11.5, at(CLX, CLY - 5)), (D + 11.65, at(CLX, CLY)), (LT + 1, at(CLX, CLY))])
o1 = walk(D + 2.6, 1.8, .2); o2 = walk(D + 6.3, 3.4, .12); o3 = walk(D + 9.7, 1.4, .2)
for k, leg in enumerate(('.bopl1', '.bopl2')):
    multi(leg, [o1[k], o2[k], o3[k]])
multi('.bopa', [f'bonk .55s ease-in-out {D + 4.6:.2f}s', f'clm .2s ease-in-out {D + 9.7:.2f}s 7 alternate',
                f'push .3s ease-out {D + 11.15:.2f}s forwards'])
multi('.bopt', [f'blip .8s ease-out {D + 5.6:.2f}s'])
anim('.bope', [(D + 5.45, 'transform:none'), (D + 5.6, 'transform:translate(-1.5px,-2.6px)'),
               (D + 6.2, 'transform:translate(-1.5px,-2.6px)'), (D + 6.35, 'transform:none'), (LT, 'transform:none')])
bots = bot('bip', BLUE, '#2f86c4', '#0b2a4a', '?') + bot('bop', LED, '#27b06c', '#0b3a26', '!')

CX, CY = NX + 2 * U, NY - 13
# sparks: kicked off the A while Bop climbs, and a burst when the crown clicks straight
STAR = 'M0,-9 L2.5,-2.5 L9,0 L2.5,2.5 L0,9 L-2.5,2.5 L-9,0 L-2.5,-2.5 Z'
pts = [(CLX + (13 if k % 2 else -13), FLOOR - 12 - k * (FLOOR - CLY) / 7, D + 9.75 + k * .2, .55) for k in range(7)]
pts += [(CX + dx, CY + dy, D + 11.6 + k * .04, .7) for k, (dx, dy) in enumerate([(-30, -8), (-16, -34), (4, -40), (24, -30), (32, -6)])]
fx = '<g filter="url(#glow)">'
for k, (sx, sy, st_, sc) in enumerate(pts):
    css.append(f'#fx{k}{{animation:star .45s ease-out {st_:.2f}s}}')
    fx += f'<g transform="translate({sx:.1f},{sy:.1f}) scale({sc})"><path id="fx{k}" d="{STAR}" fill="{SPARK}" style="opacity:0"/></g>'
fx += '</g>'

# hanging switch wired to the last E
SY = FLOOR - 24
anim('#swk', [(D + 2.30, 'transform:translateY(-4px)'), (D + 2.34, 'transform:translateY(4px)'), (D + 3.20, 'transform:translateY(4px)'),
              (D + 3.24, 'transform:translateY(-4px)'), (D + 3.60, 'transform:translateY(-4px)'), (D + 3.64, 'transform:translateY(4px)'),
              (LT, 'transform:translateY(4px)')])
css.append(f'#sw{{animation:show .5s ease-out {D - .6:.2f}s both}}')
switch = (f'<g id="sw"><path d="M{SWX},{BASE + 6} V{SY - 11}" stroke="url(#gold)" stroke-width="2.5"/>'
          f'<rect x="{SWX - 8}" y="{SY - 12}" width="16" height="24" rx="4" fill="#141a30" stroke="{GOLD}" stroke-width="1.5"/>'
          f'<rect x="{SWX - 2.5}" y="{SY - 7}" width="5" height="14" rx="2.5" fill="#05070f"/>'
          f'<circle id="swk" cx="{SWX}" cy="{SY}" r="3.4" fill="{HILITE}"/>'
          f'<circle cx="{SWX + 5}" cy="{SY - 9}" r="1.3" fill="#ff5a5a" opacity=".7"/><circle id="swled" cx="{SWX + 5}" cy="{SY - 9}" r="1.6" fill="{LED}"/></g>')

# crown lands crooked on the first A; Bop pushes it straight
css.append(f'#crown{{animation:crown .9s cubic-bezier(.2,.9,.3,1) {D:.2f}s both}}')
anim('#crownr', [(D + 11.4, 'transform:rotate(-17deg)'), (D + 11.62, 'transform:rotate(4deg)'), (D + 11.8, 'transform:none'), (LT, 'transform:none')])
crown = (f'<g transform="translate({CX:.1f},{CY})"><g id="crownr"><g id="crown" filter="url(#glow)">'
         f'<path d="M-19,0 L-23,-19 L-10,-9 L0,-24 L10,-9 L23,-19 L19,0 Z" fill="url(#gold)" stroke="{EDGE}" stroke-width="1.5" stroke-linejoin="round"/>'
         f'<path d="M-17,-3.5 H17" stroke="{HILITE}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>'
         + ''.join(f'<circle cx="{a}" cy="{b}" r="3.2" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>' for a, b in [(-23, -19), (0, -24), (23, -19)])
         + f'</g></g></g>{switch}{fx}'
         f'<g mask="url(#botmask)"><g transform="translate(0,{2 * FLOOR + 3}) scale(1,-1)" opacity=".42" filter="url(#soft)">{bots}</g></g>{bots}')
t = LT + 1

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
 <linearGradient id="botfade" x1="0" y1="{FLOOR}" x2="0" y2="{FLOOR + 48}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <mask id="botmask" maskUnits="userSpaceOnUse" x="0" y="{FLOOR}" width="{W}" height="{H - FLOOR}"><rect x="0" y="{FLOOR + 2}" width="{W}" height="{H - FLOOR}" fill="url(#botfade)"/></mask>
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
<g id="reflg" mask="url(#reflmask)"><g transform="translate(0,{2 * RAIL + 6}) scale(1,-1)" opacity=".5" filter="url(#soft)">{''.join(refl)}</g></g>
<g id="lit" filter="url(#glow)">{''.join(mid)}</g>
<g mask="url(#namemask)"><rect id="sheen" x="0" y="{NY - 10}" width="200" height="{6 * U + 20}" fill="url(#shine)" transform="translate(-260 0)"/></g>
<g filter="url(#glow)">{''.join(sparks)}</g>
<g id="padsg">{''.join(pads)}</g>
{crown}
{''.join(texts)}
</svg>'''
open(sys.argv[1], 'w').write(svg)
print(f'intro {t:.1f}s, {len(svg) // 1024} KB')
