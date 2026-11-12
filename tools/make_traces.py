import sys
import math
from html import escape

W, H = 1040, 320
BG = '#070a14'
DOT = '#151c33'
EDGE = '#4a3210'
GOLD = '#dba33f'
HILITE = '#fff1c4'
SPARK = '#fffdf2'
BLUE = '#63c7ff'
LED = '#58f0a0'
SANS = "Inter,'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"

U = 15
LETTERS = {
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
GAP, SPACE, LW = 2 * U, 5 * U, 10

def glyph_w(c): return max(px for st in LETTERS[c][0] for px, _ in st) * U
def gap_after(a, b): return GAP * (0.8 if 'I' in (a, b) else 1)

name_w = 0
for a, b in zip(NAME, NAME[1:] + ' '):
    if a == ' ': name_w += SPACE - GAP; continue
    name_w += glyph_w(a) + (gap_after(a, b) if b != ' ' else GAP)
name_w -= GAP
NX, NY = (W - name_w) / 2 + 10, 75
BASE = NY + 6 * U  # 165
FLOOR = 278        # floor line where minions stand

LXS = []
x = NX
for ci, ch in enumerate(NAME):
    nxt = NAME[ci + 1] if ci + 1 < len(NAME) else ' '
    if ch == ' ': x += SPACE - GAP; continue
    LXS.append(x)
    x += glyph_w(ch) + (gap_after(ch, nxt) if nxt != ' ' else GAP)

SWX = LXS[9] + 2 * U  # ~921.5
CX = NX + 2 * U       # 138.5
CY = NY - 14          # 61 (crown on A)
CLX = NX - 2          # 106.5 (climbing coordinate on A)
CLY = NY + 26         # 101 (perch beside crown)

# Minion positions on floor:
# Switch box centered at SWX = 920
# Minion A (tall, Stuart): x = 952
# Minion B (short, Bob): x = 995
AX = 952
BX = 995

def dpath(points): return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)

css = []
mid, refl, pads, mask = [], [], [], []

for ci, ch in enumerate(NAME):
    if ch == ' ': continue
    x_pos = LXS.pop(0) if LXS else NX
    strokes, padpts = LETTERS[ch]
    strokes = [[(x_pos + px * U, NY + py * U) for px, py in s] for s in strokes]
    for si, s in enumerate(strokes):
        d = dpath(s)
        common = f'd="{d}" fill="none" stroke-linejoin="round" stroke-linecap="round"'
        mid.append(f'<path {common} stroke="{EDGE}" stroke-width="{LW + 4}"/>')
        mid.append(f'<path {common} stroke="url(#gold)" stroke-width="{LW}"/>')
        refl.append(f'<path {common} stroke="url(#gold)" stroke-width="{LW}"/>')
        mid.append(f'<path {common} stroke="{HILITE}" stroke-width="2.2" stroke-opacity=".55" transform="translate(-0.8,-0.8)"/>')
        mask.append(f'<path d="{d}" stroke="#fff" stroke-width="{LW}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    for pi, (px, py) in enumerate(padpts):
        pads.append(f'<g style="transform-origin:{x_pos + px * U:.1f}px {NY + py * U:.1f}px">'
                    f'<circle cx="{x_pos + px * U:.1f}" cy="{NY + py * U:.1f}" r="9.5" fill="{EDGE}"/>'
                    f'<circle cx="{x_pos + px * U:.1f}" cy="{NY + py * U:.1f}" r="8" fill="url(#gold)"/>'
                    f'<circle cx="{x_pos + px * U:.1f}" cy="{NY + py * U:.1f}" r="3.4" fill="{BG}"/></g>')

T_TOTAL = 16.0

def kf(sel, frames, ease='linear'):
    """frames = [(seconds, css_declarations), ...]"""
    end = T_TOTAL
    if frames[0][0] > 0:
        frames = [(0, frames[0][1])] + frames
    if frames[-1][0] < end:
        frames = frames + [(end, frames[0][1])]
    
    kname = f'k{len(css)}'
    body = ''.join(f'{max(0, min(100, ts / end * 100)):.2f}%{{{decl}}}' for ts, decl in frames)
    css.append(f'{sel}{{animation:{kname} {end:.2f}s {ease} infinite}}@keyframes {kname}{{{body}}}')

# 1. Glow, Light, and Reflections
kf('#lit', [(0, 'opacity:0.25'), (8.8, 'opacity:0.25'), (8.9, 'opacity:0.6'), (9.0, 'opacity:1'), (14.6, 'opacity:1'), (15.0, 'opacity:0.25')])
kf('#padsg', [(0, 'opacity:0.25'), (8.8, 'opacity:0.25'), (8.9, 'opacity:0.6'), (9.0, 'opacity:1'), (14.6, 'opacity:1'), (15.0, 'opacity:0.25')])
kf('#reflg', [(0, 'opacity:0.18'), (8.8, 'opacity:0.18'), (9.0, 'opacity:0.6'), (14.6, 'opacity:0.6'), (15.0, 'opacity:0.18')])
kf('#nameglow', [(0, 'opacity:0'), (8.8, 'opacity:0'), (9.0, 'opacity:0.42'), (14.6, 'opacity:0.42'), (15.0, 'opacity:0')])

# Sheen sweep across letters
kf('#sheen', [
    (0, 'transform:translateX(-260px);opacity:0'),
    (9.2, 'transform:translateX(-260px);opacity:0'),
    (9.3, 'transform:translateX(-260px);opacity:1'),
    (10.8, 'transform:translateX(1100px);opacity:1'),
    (10.9, 'transform:translateX(1100px);opacity:0'),
])

# Wire spark pulse from switch/bulb to name (t=8.8 - 9.2s)
kf('#wire_spark', [
    (0, 'stroke-dashoffset:160;opacity:0'),
    (8.8, 'stroke-dashoffset:160;opacity:1'),
    (9.15, 'stroke-dashoffset:-160;opacity:1'),
    (9.2, 'stroke-dashoffset:-160;opacity:0'),
])

# Switch lever handle (rotates down around pivot 925, 245)
kf('#sw_lever', [
    (0, 'transform:rotate(-45deg)'),
    (8.2, 'transform:rotate(-45deg)'),
    (8.4, 'transform:rotate(38deg)'),
    (14.8, 'transform:rotate(38deg)'),
    (15.0, 'transform:rotate(-45deg)'),
])

# Big Visible Lamp / Bulb (on top of switch box at 925, 145)
kf('#lamp_lit', [
    (0, 'opacity:0'),
    (8.75, 'opacity:0'),
    (8.8, 'opacity:1'),
    (14.8, 'opacity:1'),
    (15.0, 'opacity:0'),
])
kf('#lamp_glow', [
    (0, 'opacity:0;transform:scale(0.5)'),
    (8.75, 'opacity:0;transform:scale(0.5)'),
    (8.85, 'opacity:0.95;transform:scale(1.1)'),
    (9.0, 'opacity:0.85;transform:scale(1.0)'),
    (14.8, 'opacity:0.85;transform:scale(1.0)'),
    (15.0, 'opacity:0;transform:scale(0.5)'),
])

# Crown: crooked (-18deg) -> snaps straight at 7.0s
kf('#crownr', [
    (0, 'transform:rotate(-18deg)'),
    (6.8, 'transform:rotate(-18deg)'),
    (7.0, 'transform:rotate(4deg)'),
    (7.2, 'transform:none'),
    (14.8, 'transform:none'),
    (15.2, 'transform:rotate(-18deg)'),
])

# Crown spark burst when straight (7.0s)
kf('#crown_sparks', [
    (0, 'opacity:0;transform:scale(0)'),
    (6.95, 'opacity:0;transform:scale(0)'),
    (7.05, 'opacity:1;transform:scale(1.4)'),
    (7.45, 'opacity:0;transform:scale(2.0)'),
])

# Bonk impact starburst on B's head (2.0s)
kf('#bonk_star', [
    (0, 'opacity:0;transform:scale(0)'),
    (1.95, 'opacity:0;transform:scale(0)'),
    (2.02, 'opacity:1;transform:scale(1.5)'),
    (2.45, 'opacity:0;transform:scale(2.2)'),
])

# Minion A Position (stays at switch, bounces when cheering)
kf('.minion_a', [
    (0, f'transform:translate({AX}px,{FLOOR}px)'),
    (8.8, f'transform:translate({AX}px,{FLOOR}px)'),
    (9.0, f'transform:translate({AX}px,{FLOOR - 12}px)'),
    (9.3, f'transform:translate({AX}px,{FLOOR}px)'),
    (9.6, f'transform:translate({AX}px,{FLOOR - 12}px)'),
    (9.9, f'transform:translate({AX}px,{FLOOR}px)'),
    (10.2, f'transform:translate({AX}px,{FLOOR - 12}px)'),
    (10.5, f'transform:translate({AX}px,{FLOOR}px)'),
    (10.8, f'transform:translate({AX}px,{FLOOR - 12}px)'),
    (11.1, f'transform:translate({AX}px,{FLOOR}px)'),
    (14.6, f'transform:translate({AX}px,{FLOOR}px)'),
])

# Minion A Arms
# Left arm: holds wrench, winds up at 1.7s, bonks B at 2.0s, points left at 2.6s, cheers at 9.0s
kf('.m_a_arm_l', [
    (0, 'transform:rotate(0deg)'),
    (1.5, 'transform:rotate(0deg)'),
    (1.75, 'transform:rotate(-95deg)'), # raises wrench way up!
    (2.0, 'transform:rotate(65deg)'),   # SLAMS DOWN: BONK!
    (2.35, 'transform:rotate(20deg)'),
    (2.6, 'transform:rotate(-125deg)'), # points left across the board to crown!
    (3.5, 'transform:rotate(-125deg)'),
    (3.9, 'transform:rotate(0deg)'),
    (8.8, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-145deg)'), # cheer arms up!
    (14.5, 'transform:rotate(-145deg)'),
    (14.8, 'transform:rotate(0deg)'),
])

# Right arm: reaches to switch lever at 8.0s, pulls down at 8.4s, cheers at 9.0s
kf('.m_a_arm_r', [
    (0, 'transform:rotate(0deg)'),
    (7.8, 'transform:rotate(0deg)'),
    (8.1, 'transform:rotate(-135deg)'), # reaches up to red knob
    (8.4, 'transform:rotate(-60deg)'),  # pulls lever down!
    (8.7, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-145deg)'), # cheer arms up!
    (14.5, 'transform:rotate(-145deg)'),
    (14.8, 'transform:rotate(0deg)'),
])

# Minion A Eye pupil
kf('.m_a_pupil', [
    (0, 'transform:none'),
    (1.4, 'transform:translate(2px, 1px)'),    # looks at B
    (2.6, 'transform:translate(-2.5px, -1px)'), # looks left at crown
    (7.8, 'transform:translate(-2px, -3px)'),   # looks up at switch
    (8.6, 'transform:translate(-2px, -3px)'),
    (9.0, 'transform:none'),
    (14.6, 'transform:none'),
])

# Minion A Eyelid blink
kf('.m_a_lid', [
    (0, 'opacity:0'),
    (0.9, 'opacity:0'),
    (1.0, 'opacity:1'),
    (1.15, 'opacity:0'),
    (12.0, 'opacity:0'),
    (12.1, 'opacity:1'),
    (12.25, 'opacity:0'),
])

# Minion A Body Squash/Stretch
kf('.minion_a_inner', [
    (0, 'transform:none'),
    (1.75, 'transform:scale(0.96, 1.05)'), # stretch on windup
    (2.0, 'transform:scale(1.08, 0.92)'),  # squash on slam
    (2.3, 'transform:none'),
    (8.9, 'transform:none'),
    (9.0, 'transform:scale(0.94, 1.08)'),
    (9.3, 'transform:scale(1.06, 0.94)'),
    (9.6, 'transform:scale(0.94, 1.08)'),
    (9.9, 'transform:scale(1.06, 0.94)'),
    (14.5, 'transform:none'),
])

# Minion B Position
kf('.minion_b', [
    (0, f'transform:translate({BX}px,{FLOOR}px)'),
    (1.95, f'transform:translate({BX}px,{FLOOR}px)'),
    (2.05, f'transform:translate({BX + 12}px,{FLOOR}px)'), # reels back
    (3.2, f'transform:translate({BX}px,{FLOOR}px)'),
    # Run to CLX
    (3.4, f'transform:translate({BX - 60}px,{FLOOR}px) scaleX(-1)'),
    (4.0, f'transform:translate({(BX + CLX)/2}px,{FLOOR}px) scaleX(-1)'),
    (5.4, f'transform:translate({CLX}px,{FLOOR}px) scaleX(-1)'),
    # Climb up A
    (5.5, f'transform:translate({CLX}px,{FLOOR}px) scaleX(1)'),
    (5.8, f'transform:translate({CLX}px,{FLOOR - 55}px) scaleX(1)'),
    (6.2, f'transform:translate({CLX}px,{FLOOR - 120}px) scaleX(1)'),
    (6.6, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Push crown
    (6.8, f'transform:translate({CLX + 8}px,{CLY - 6}px) scaleX(1)'),
    (7.0, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Cheering on A
    (7.2, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (8.8, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (9.0, f'transform:translate({CLX}px,{CLY - 12}px) scaleX(1)'),
    (9.3, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (9.6, f'transform:translate({CLX}px,{CLY - 12}px) scaleX(1)'),
    (9.9, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (14.5, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Slide down
    (15.0, f'transform:translate({CLX}px,{FLOOR}px) scaleX(1)'),
    # Run back to BX
    (15.2, f'transform:translate({(BX + CLX)/2}px,{FLOOR}px) scaleX(1)'),
    (15.8, f'transform:translate({BX}px,{FLOOR}px) scaleX(1)'),
])

# Minion B Body Squash & Stretch
kf('.minion_b_inner', [
    (0, 'transform:none'),
    (1.95, 'transform:none'),
    (2.05, 'transform:scale(1.4, 0.52)'), # massive squash on bonk!
    (2.25, 'transform:scale(0.85, 1.2)'),  # spring back up
    (2.5, 'transform:none'),
    # Running bounce & lean
    (3.4, 'transform:scale(1.1, 0.9) rotate(14deg)'),
    (3.8, 'transform:scale(0.92, 1.08) rotate(18deg)'),
    (4.2, 'transform:scale(1.1, 0.9) rotate(14deg)'),
    (4.6, 'transform:scale(0.92, 1.08) rotate(18deg)'),
    (5.0, 'transform:scale(1.1, 0.9) rotate(14deg)'),
    (5.4, 'transform:none'),
    # Climbing
    (5.8, 'transform:scale(0.92, 1.08)'),
    (6.2, 'transform:scale(1.08, 0.92)'),
    (6.6, 'transform:none'),
    # Cheering on A
    (9.0, 'transform:scale(0.92, 1.1)'),
    (9.3, 'transform:scale(1.08, 0.92)'),
    (9.6, 'transform:scale(0.92, 1.1)'),
    (9.9, 'transform:scale(1.08, 0.92)'),
    (14.5, 'transform:none'),
])

# Minion B Bump on head
kf('.m_b_bump', [
    (0, 'opacity:0;transform:scale(0)'),
    (2.05, 'opacity:0;transform:scale(0)'),
    (2.15, 'opacity:1;transform:scale(1.3)'),
    (2.35, 'opacity:1;transform:scale(1.0)'),
    (3.4, 'opacity:1;transform:scale(1.0)'),
    (3.8, 'opacity:0;transform:scale(0)'),
])

# Minion B Stars circling head
kf('.m_b_stars', [
    (0, 'opacity:0;transform:scale(0) rotate(0deg)'),
    (2.05, 'opacity:0;transform:scale(0) rotate(0deg)'),
    (2.2, 'opacity:1;transform:scale(1.2) rotate(100deg)'),
    (2.6, 'opacity:1;transform:scale(1.0) rotate(240deg)'),
    (3.2, 'opacity:1;transform:scale(0.8) rotate(360deg)'),
    (3.6, 'opacity:0;transform:scale(0) rotate(420deg)'),
])

# Minion B Pupils: look at A, dizzy spin, look forward, cheer
kf('.m_b_pupil', [
    (0, 'transform:none'),
    (1.5, 'transform:translate(-2px, 0px)'), # looks at A
    (2.1, 'transform:translate(2px, -2px)'), # dizzy spin
    (2.4, 'transform:translate(-2px, 2px)'),
    (2.7, 'transform:translate(1px, 1px)'),
    (3.4, 'transform:translate(2.5px, 0px)'), # looks forward in sprint
    (6.6, 'transform:translate(2px, -1px)'), # looks at crown
    (9.0, 'transform:none'),
    (14.5, 'transform:none'),
])

# Minion B Arms
kf('.m_b_arm_l', [
    (0, 'transform:rotate(0deg)'),
    (2.05, 'transform:rotate(-70deg)'), # head clutch
    (2.8, 'transform:rotate(-70deg)'),
    (3.2, 'transform:rotate(0deg)'),
    # Running arms pump
    (3.4, 'transform:rotate(-55deg)'),
    (3.8, 'transform:rotate(55deg)'),
    (4.2, 'transform:rotate(-55deg)'),
    (4.6, 'transform:rotate(55deg)'),
    (5.0, 'transform:rotate(-55deg)'),
    (5.4, 'transform:rotate(-85deg)'), # climb reaching
    (5.8, 'transform:rotate(-35deg)'),
    (6.2, 'transform:rotate(-85deg)'),
    (6.6, 'transform:rotate(105deg)'), # push crown
    (7.0, 'transform:rotate(105deg)'),
    (7.5, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-145deg)'), # cheer
    (14.5, 'transform:rotate(-145deg)'),
    (15.0, 'transform:rotate(0deg)'),
])

kf('.m_b_arm_r', [
    (0, 'transform:rotate(0deg)'),
    (2.05, 'transform:rotate(70deg)'), # head clutch
    (2.8, 'transform:rotate(70deg)'),
    (3.2, 'transform:rotate(0deg)'),
    # Running arms pump
    (3.4, 'transform:rotate(55deg)'),
    (3.8, 'transform:rotate(-55deg)'),
    (4.2, 'transform:rotate(55deg)'),
    (4.6, 'transform:rotate(-55deg)'),
    (5.0, 'transform:rotate(55deg)'),
    (5.4, 'transform:rotate(-35deg)'),
    (5.8, 'transform:rotate(-85deg)'),
    (6.2, 'transform:rotate(-35deg)'),
    (6.6, 'transform:rotate(105deg)'), # push crown
    (7.0, 'transform:rotate(105deg)'),
    (7.5, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-145deg)'), # cheer
    (14.5, 'transform:rotate(-145deg)'),
    (15.0, 'transform:rotate(0deg)'),
])

# Minion B Legs running cycle
kf('.m_b_l1', [
    (0, 'transform:none'),
    (3.2, 'transform:none'),
    (3.4, 'transform:rotate(36deg)'),
    (3.7, 'transform:rotate(-36deg)'),
    (4.0, 'transform:rotate(36deg)'),
    (4.3, 'transform:rotate(-36deg)'),
    (4.6, 'transform:rotate(36deg)'),
    (4.9, 'transform:rotate(-36deg)'),
    (5.2, 'transform:rotate(36deg)'),
    (5.4, 'transform:none'),
    (15.0, 'transform:none'),
    (15.2, 'transform:rotate(36deg)'),
    (15.5, 'transform:rotate(-36deg)'),
    (15.8, 'transform:none'),
])
kf('.m_b_l2', [
    (0, 'transform:none'),
    (3.2, 'transform:none'),
    (3.4, 'transform:rotate(-36deg)'),
    (3.7, 'transform:rotate(36deg)'),
    (4.0, 'transform:rotate(-36deg)'),
    (4.3, 'transform:rotate(36deg)'),
    (4.6, 'transform:rotate(-36deg)'),
    (4.9, 'transform:rotate(36deg)'),
    (5.2, 'transform:rotate(-36deg)'),
    (5.4, 'transform:none'),
    (15.0, 'transform:none'),
    (15.2, 'transform:rotate(-36deg)'),
    (15.5, 'transform:rotate(36deg)'),
    (15.8, 'transform:none'),
])

reduced_css = '''
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-delay: -10s !important;
    animation-play-state: paused !important;
  }
  #lit, #padsg, #reflg { opacity: 1 !important; }
  #nameglow { opacity: 0.42 !important; }
  #lamp_lit { opacity: 1 !important; }
  #lamp_glow { opacity: 0.85 !important; transform: scale(1) !important; }
  #sw_lever { transform: rotate(38deg) !important; }
  #crownr { transform: none !important; }
}
'''

# Minion A SVG (Stuart: 84px tall, width 42px)
minion_a_svg = f'''
<g class="minion_a" transform="translate({AX},{FLOOR})">
  <g class="minion_a_inner">
    <!-- Hair strands -->
    <path d="M-12,-83 C-6,-91 -2,-87 0,-84 C2,-87 6,-91 12,-83" stroke="#15171d" stroke-width="2.6" fill="none" stroke-linecap="round"/>
    <path d="M-7,-85 C-2,-92 2,-92 7,-85" stroke="#15171d" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    
    <!-- Body capsule (84px tall, 42px wide) -->
    <rect x="-21" y="-84" width="42" height="84" rx="21" fill="url(#minion_body_a)"/>
    <!-- 3D Shading & Highlight -->
    <path d="M-17,-78 C-19,-60 -19,-20 -17,-5" stroke="#fff8b0" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.6"/>
    <path d="M17,-78 C19,-60 19,-20 17,-5" stroke="#cc9200" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.45"/>

    <!-- Mouth -->
    <path d="M-8,-30 Q0,-24 8,-30" stroke="#6b3a0a" stroke-width="2.2" stroke-linecap="round" fill="none"/>

    <!-- Goggle strap -->
    <rect x="-22" y="-60" width="44" height="10" rx="2" fill="#1e2026"/>
    <line x1="-22" y1="-55" x2="22" y2="-55" stroke="#111317" stroke-width="1.2" stroke-dasharray="3 2"/>

    <!-- Single Goggle (Stuart) -->
    <g transform="translate(0, -55)">
      <!-- Outer silver frame -->
      <circle cx="0" cy="0" r="15.5" fill="url(#silver_rim)" stroke="#353b49" stroke-width="1.5"/>
      <circle cx="-14.2" cy="0" r="1.4" fill="#222"/>
      <circle cx="14.2" cy="0" r="1.4" fill="#222"/>
      <!-- Inner bevel -->
      <circle cx="0" cy="0" r="11.5" fill="#1b1d22"/>
      <!-- Sclera -->
      <circle cx="0" cy="0" r="10.2" fill="#ffffff"/>
      <!-- Pupil & Iris -->
      <g class="m_a_pupil">
        <circle cx="0" cy="0" r="5.2" fill="#7d4212" stroke="#4a2406" stroke-width="0.8"/>
        <circle cx="0" cy="0" r="3.0" fill="#111111"/>
        <circle cx="1.8" cy="-1.8" r="1.6" fill="#ffffff"/>
        <circle cx="-1.5" cy="2.0" r="0.8" fill="#ffffff" opacity="0.6"/>
      </g>
      <!-- Eyelid for blinks -->
      <path class="m_a_lid" d="M-10.2,-4 Q0,2 10.2,-4 V-11 H-10.2 Z" fill="#ffd426"/>
    </g>

    <!-- Denim Overalls -->
    <path d="M-21,-28 C-21,-12 -16,0 0,0 C16,0 21,-12 21,-28 L21,-8 C21,0 14,0 0,0 C-14,0 -21,0 -21,-8 Z" fill="url(#denim_grad)"/>
    <path d="M-16,-34 H16 V-4 Q16,0 0,0 Q-16,0 -16,-4 Z" fill="url(#denim_grad)"/>
    <path d="M-16,-34 H16 V-4 Q16,0 0,0 Q-16,0 -16,-4 Z" fill="none" stroke="#4377b5" stroke-width="1.2" stroke-dasharray="2.5 2"/>
    <!-- Straps -->
    <path d="M-19,-40 L-12,-30" stroke="#265691" stroke-width="4.8" stroke-linecap="round"/>
    <path d="M19,-40 L12,-30" stroke="#265691" stroke-width="4.8" stroke-linecap="round"/>
    <circle cx="-12.5" cy="-30.5" r="2.2" fill="#141820"/>
    <circle cx="12.5" cy="-30.5" r="2.2" fill="#141820"/>
    <!-- Pocket -->
    <path d="M-9,-22 H9 V-13 Q9,-7 0,-7 Q-9,-7 -9,-13 Z" fill="#1e4475" stroke="#17355c" stroke-width="1.2"/>
    <circle cx="0" cy="-14" r="3.4" fill="#152233"/>
    <circle cx="0" cy="-14" r="2.2" fill="#1e4475"/>
    <path d="M-0.6,-15.5 H0.8 V-12.5 H-0.4" stroke="#152233" stroke-width="0.9" fill="none"/>

    <!-- Legs & Shoes -->
    <g class="m_a_l1">
      <rect x="-15" y="-2" width="10" height="9" rx="2" fill="#1d4373"/>
      <path d="M-18,7 H-4 C-4,4 -7,3 -10,3 C-15,3 -18,4 -18,7 Z" fill="#14161a"/>
      <line x1="-18" y1="7" x2="-4" y2="7" stroke="#2c303a" stroke-width="1.2"/>
    </g>
    <g class="m_a_l2">
      <rect x="5" y="-2" width="10" height="9" rx="2" fill="#1d4373"/>
      <path d="M2,7 H16 C16,4 13,3 10,3 C5,3 2,4 2,7 Z" fill="#14161a"/>
      <line x1="2" y1="7" x2="16" y2="7" stroke="#2c303a" stroke-width="1.2"/>
    </g>

    <!-- Left Arm (with CARTOON WRENCH) -->
    <g class="m_a_arm_l" style="transform-origin: -18px -32px">
      <path d="M-18,-32 Q-28,-22 -26,-10" stroke="#ffd426" stroke-width="6.5" stroke-linecap="round" fill="none"/>
      <!-- Glove -->
      <circle cx="-26" cy="-8" r="5.2" fill="#15171d"/>
      <!-- Heavy Wrench / Mallet -->
      <g transform="translate(-26, -8) rotate(30)">
        <rect x="-2.5" y="-22" width="5" height="28" rx="2" fill="#717a8c" stroke="#353d4c" stroke-width="1"/>
        <!-- Wrench Head -->
        <path d="M-8,-32 H8 V-22 C8,-20 4,-19 0,-19 C-4,-19 -8,-20 -8,-22 Z" fill="#475467" stroke="#1d2939" stroke-width="1.4"/>
        <rect x="-3" y="-32" width="6" height="8" rx="1" fill="#1d2939"/>
      </g>
    </g>

    <!-- Right Arm -->
    <g class="m_a_arm_r" style="transform-origin: 18px -32px">
      <path d="M18,-32 Q28,-22 26,-10" stroke="#ffd426" stroke-width="6.5" stroke-linecap="round" fill="none"/>
      <circle cx="26" cy="-8" r="5.2" fill="#15171d"/>
    </g>
  </g>
</g>
'''

# Minion B SVG (Bob: 68px tall, width 46px, 2 eyes with heterochromia)
minion_b_svg = f'''
<g class="minion_b" transform="translate({BX},{FLOOR})">
  <g class="minion_b_inner">
    <!-- Hair sprouts -->
    <path d="M-4,-67 V-75 M0,-67 V-77 M4,-67 V-75" stroke="#15171d" stroke-width="2.2" stroke-linecap="round"/>

    <!-- Large Bump / Knot on head (bonk reaction) -->
    <g class="m_b_bump" style="transform-origin: 0px -68px">
      <path d="M-9,-68 Q0,-90 9,-68 Z" fill="#ff6b6b" stroke="#d43b3b" stroke-width="1.4"/>
      <line x1="-4" y1="-78" x2="4" y2="-78" stroke="#fff" stroke-width="1.2" opacity="0.85"/>
      <line x1="-3" y1="-73" x2="3" y2="-73" stroke="#fff" stroke-width="1.2" opacity="0.85"/>
    </g>

    <!-- Bold Spinning Comic Stars -->
    <g class="m_b_stars" style="transform-origin: 0px -78px">
      <path d="M0,-12 L3,-3 L12,0 L3,3 L0,12 L-3,3 L-12,0 L-3,-3 Z" fill="#ffd426" stroke="#c99700" stroke-width="1.2" transform="translate(-20,-75) scale(0.9)"/>
      <path d="M0,-12 L3,-3 L12,0 L3,3 L0,12 L-3,3 L-12,0 L-3,-3 Z" fill="#ffd426" stroke="#c99700" stroke-width="1.2" transform="translate(20,-72) scale(1.0)"/>
      <path d="M0,-10 L2.5,-2.5 L10,0 L2.5,2.5 L0,10 L-2.5,2.5 L-10,0 L-2.5,-2.5 Z" fill="#ffffff" stroke="#c99700" stroke-width="1" transform="translate(0,-88) scale(0.8)"/>
    </g>

    <!-- Body capsule (68px tall, 46px wide) -->
    <rect x="-23" y="-68" width="46" height="68" rx="23" fill="url(#minion_body_b)"/>
    <path d="M-18,-62 C-20,-48 -20,-18 -18,-4" stroke="#fff8b0" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.6"/>
    <path d="M18,-62 C20,-48 20,-18 18,-4" stroke="#cc9200" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.45"/>

    <!-- Mouth -->
    <path d="M-8,-24 Q0,-16 8,-24" stroke="#6b3a0a" stroke-width="2.2" stroke-linecap="round" fill="none"/>

    <!-- Goggle strap -->
    <rect x="-24" y="-48" width="48" height="10" rx="2" fill="#1e2026"/>
    <line x1="-24" y1="-43" x2="24" y2="-43" stroke="#111317" stroke-width="1.2" stroke-dasharray="3 2"/>

    <!-- Two Goggles (Bob: Heterochromia) -->
    <!-- Left Goggle (Green Eye) -->
    <g transform="translate(-8.5, -43)">
      <circle cx="0" cy="0" r="10.8" fill="url(#silver_rim)" stroke="#353b49" stroke-width="1.2"/>
      <circle cx="-9.8" cy="0" r="1.2" fill="#222"/>
      <circle cx="0" cy="0" r="8.0" fill="#1b1d22"/>
      <circle cx="0" cy="0" r="7.0" fill="#ffffff"/>
      <g class="m_b_pupil">
        <circle cx="0" cy="0" r="3.6" fill="#2e7d32" stroke="#1b4d1f" stroke-width="0.6"/>
        <circle cx="0" cy="0" r="2.0" fill="#111111"/>
        <circle cx="1.2" cy="-1.2" r="1.1" fill="#ffffff"/>
      </g>
    </g>
    <!-- Right Goggle (Brown Eye) -->
    <g transform="translate(8.5, -43)">
      <circle cx="0" cy="0" r="10.8" fill="url(#silver_rim)" stroke="#353b49" stroke-width="1.2"/>
      <circle cx="9.8" cy="0" r="1.2" fill="#222"/>
      <circle cx="0" cy="0" r="8.0" fill="#1b1d22"/>
      <circle cx="0" cy="0" r="7.0" fill="#ffffff"/>
      <g class="m_b_pupil">
        <circle cx="0" cy="0" r="3.6" fill="#7d4212" stroke="#4a2406" stroke-width="0.6"/>
        <circle cx="0" cy="0" r="2.0" fill="#111111"/>
        <circle cx="1.2" cy="-1.2" r="1.1" fill="#ffffff"/>
      </g>
    </g>

    <!-- Overalls -->
    <path d="M-23,-24 C-23,-10 -18,0 0,0 C18,0 23,-10 23,-24 L23,-6 C23,0 16,0 0,0 C-16,0 -23,0 -23,-6 Z" fill="url(#denim_grad)"/>
    <path d="M-17,-27 H17 V-4 Q17,0 0,0 Q-17,0 -17,-4 Z" fill="url(#denim_grad)"/>
    <path d="M-17,-27 H17 V-4 Q17,0 0,0 Q-17,0 -17,-4 Z" fill="none" stroke="#4377b5" stroke-width="1.2" stroke-dasharray="2.5 2"/>
    <!-- Straps -->
    <path d="M-21,-33 L-13,-24" stroke="#265691" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M21,-33 L13,-24" stroke="#265691" stroke-width="4.5" stroke-linecap="round"/>
    <circle cx="-13.5" cy="-24.5" r="2.0" fill="#141820"/>
    <circle cx="13.5" cy="-24.5" r="2.0" fill="#141820"/>
    <!-- Pocket -->
    <path d="M-8,-18 H8 V-10 Q8,-5 0,-5 Q-8,-5 -8,-10 Z" fill="#1e4475" stroke="#17355c" stroke-width="1.1"/>
    <circle cx="0" cy="-11" r="3.0" fill="#152233"/>
    <circle cx="0" cy="-11" r="1.8" fill="#1e4475"/>

    <!-- Legs & Shoes -->
    <g class="m_b_l1" style="transform-origin: -11px 0px">
      <rect x="-16" y="-2" width="10" height="8" rx="2" fill="#1d4373"/>
      <path d="M-19,6 H-5 C-5,3.5 -8,2.5 -11,2.5 C-16,2.5 -19,3.5 -19,6 Z" fill="#14161a"/>
      <line x1="-19" y1="6" x2="-5" y2="6" stroke="#2c303a" stroke-width="1.2"/>
    </g>
    <g class="m_b_l2" style="transform-origin: 11px 0px">
      <rect x="6" y="-2" width="10" height="8" rx="2" fill="#1d4373"/>
      <path d="M3,6 H17 C17,3.5 14,2.5 11,2.5 C6,2.5 3,3.5 3,6 Z" fill="#14161a"/>
      <line x1="3" y1="6" x2="17" y2="6" stroke="#2c303a" stroke-width="1.2"/>
    </g>

    <!-- Arms -->
    <g class="m_b_arm_l" style="transform-origin: -19px -26px">
      <path d="M-19,-26 Q-28,-16 -24,-4" stroke="#ffd426" stroke-width="5.8" stroke-linecap="round" fill="none"/>
      <circle cx="-24" cy="-2" r="4.6" fill="#15171d"/>
    </g>
    <g class="m_b_arm_r" style="transform-origin: 19px -26px">
      <path d="M19,-26 Q28,-16 24,-4" stroke="#ffd426" stroke-width="5.8" stroke-linecap="round" fill="none"/>
      <circle cx="24" cy="-2" r="4.6" fill="#15171d"/>
    </g>
  </g>
</g>
'''

# Real Lever/Switch Box + Big Industrial Light Bulb
switch_apparatus = f'''
<g id="switch_station">
  <!-- Power conduit from switch to name -->
  <path d="M{SWX},{BASE + 8} V210" stroke="url(#gold)" stroke-width="3.5"/>
  <path id="wire_spark" d="M{SWX},210 V{BASE + 8} H{SWX - 70}" stroke="{SPARK}" stroke-width="4" fill="none" stroke-linecap="round" stroke-dasharray="20 140" pathLength="100"/>

  <!-- Switch Box Casing (heavy industrial enclosure) -->
  <rect x="{SWX - 22}" y="208" width="44" height="68" rx="6" fill="#161c2e" stroke="{GOLD}" stroke-width="2"/>
  <rect x="{SWX - 18}" y="212" width="36" height="60" rx="4" fill="#0d111d"/>
  <!-- Corner bolts -->
  <circle cx="{SWX - 17}" cy="213" r="1.8" fill="{HILITE}"/>
  <circle cx="{SWX + 17}" cy="213" r="1.8" fill="{HILITE}"/>
  <circle cx="{SWX - 17}" cy="271" r="1.8" fill="{HILITE}"/>
  <circle cx="{SWX + 17}" cy="271" r="1.8" fill="{HILITE}"/>

  <!-- Electrical warning badge -->
  <path d="M{SWX - 6},226 L{SWX + 2},220 L{SWX},227 L{SWX + 6},227 L{SWX - 2},235 L{SWX},229 Z" fill="#ffd426"/>

  <!-- Mechanical Lever slot and pivot -->
  <rect x="{SWX - 4}" y="232" width="8" height="30" rx="3" fill="#05070d"/>
  <circle cx="{SWX}" cy="245" r="5" fill="#364057" stroke="#1d2433" stroke-width="1.2"/>
  <circle cx="{SWX}" cy="245" r="2.2" fill="{HILITE}"/>

  <!-- Big Lever Arm + Red Ball Knob -->
  <g id="sw_lever" style="transform-origin: {SWX}px 245px">
    <rect x="{SWX - 2.5}" y="218" width="5" height="28" rx="1.5" fill="url(#silver_rim)" stroke="#222" stroke-width="0.8"/>
    <!-- Big red grip ball knob -->
    <circle cx="{SWX}" cy="216" r="6.8" fill="url(#red_knob)" stroke="#731111" stroke-width="1"/>
    <circle cx="{SWX + 1.8}" cy="214.2" r="1.8" fill="#ffffff" opacity="0.8"/>
  </g>

  <!-- Big Light Bulb / Lamp on top of switch box (center at SWX, 150) -->
  <g id="lamp_fixture">
    <!-- Brass / metallic socket -->
    <rect x="{SWX - 8}" y="174" width="16" height="14" rx="2" fill="#c4932f" stroke="#7a550d" stroke-width="1"/>
    <line x1="{SWX - 8}" y1="178" x2="{SWX + 8}" y2="178" stroke="#523908" stroke-width="1.2"/>
    <line x1="{SWX - 8}" y1="183" x2="{SWX + 8}" y2="183" stroke="#523908" stroke-width="1.2"/>

    <!-- Unlit / Dark bulb glass -->
    <circle cx="{SWX}" cy="150" r="18" fill="#141a29" stroke="#3d4966" stroke-width="1.5" opacity="0.85"/>
    <!-- Filament coils (visible inside) -->
    <path d="M{SWX - 4},170 L{SWX - 4},155 L{SWX},146 L{SWX + 4},155 L{SWX + 4},170" fill="none" stroke="#684a1a" stroke-width="1.2"/>

    <!-- Lit Glow & Lamp Bulb (t=9.0s onwards) -->
    <g id="lamp_lit">
      <!-- Radiant Light Rays -->
      <g stroke="#ffd952" stroke-width="2" stroke-linecap="round" opacity="0.75">
        <line x1="{SWX}" y1="126" x2="{SWX}" y2="114"/>
        <line x1="{SWX + 17}" y1="133" x2="{SWX + 26}" y2="124"/>
        <line x1="{SWX + 24}" y1="150" x2="{SWX + 36}" y2="150"/>
        <line x1="{SWX + 17}" y1="167" x2="{SWX + 26}" y2="176"/>
        <line x1="{SWX - 17}" y1="133" x2="{SWX - 26}" y2="124"/>
        <line x1="{SWX - 24}" y1="150" x2="{SWX - 36}" y2="150"/>
        <line x1="{SWX - 17}" y1="167" x2="{SWX - 26}" y2="176"/>
      </g>
      <!-- Brilliant glass core -->
      <circle cx="{SWX}" cy="150" r="18" fill="url(#lamp_core)" stroke="#fff" stroke-width="1.5"/>
      <circle cx="{SWX - 4}" cy="144" r="5" fill="#ffffff" opacity="0.75"/>
    </g>
    <!-- Giant soft radial bloom flare -->
    <circle id="lamp_glow" cx="{SWX}" cy="150" r="55" fill="#ffcb36" filter="url(#big)" style="transform-origin:{SWX}px 150px"/>
  </g>
</g>
'''

STAR = 'M0,-14 L3.5,-3.5 L14,0 L3.5,3.5 L0,14 L-3.5,3.5 L-14,0 L-3.5,-3.5 Z'
crown = f'''
<g transform="translate({CX:.1f},{CY})">
  <g id="crownr">
    <g id="crown" filter="url(#glow)">
      <path d="M-21,0 L-25,-21 L-11,-10 L0,-26 L11,-10 L25,-21 L21,0 Z" fill="url(#gold)" stroke="{EDGE}" stroke-width="1.8" stroke-linejoin="round"/>
      <path d="M-19,-3.5 H19" stroke="{HILITE}" stroke-width="1.8" stroke-linecap="round" opacity=".8"/>
      <circle cx="-25" cy="-21" r="3.5" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>
      <circle cx="0" cy="-26" r="3.5" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>
      <circle cx="25" cy="-21" r="3.5" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>
    </g>
  </g>
  <!-- Spark burst when crown is pushed straight -->
  <g id="crown_sparks" filter="url(#glow)" transform="translate(0,-12)">
    <path d="{STAR}" fill="{SPARK}" transform="translate(-28,-14) scale(0.65)"/>
    <path d="{STAR}" fill="{SPARK}" transform="translate(0,-24) scale(0.85)"/>
    <path d="{STAR}" fill="{SPARK}" transform="translate(28,-14) scale(0.65)"/>
    <circle cx="-12" cy="-16" r="2.2" fill="{HILITE}"/>
    <circle cx="12" cy="-16" r="2.2" fill="{HILITE}"/>
  </g>
</g>

<!-- Dramatic Bonk Impact Flash Starburst on B's head -->
<g id="bonk_star" filter="url(#glow)" transform="translate({BX - 4},{FLOOR - 74})">
  <path d="{STAR}" fill="#ffffff" transform="scale(2.2)"/>
  <path d="{STAR}" fill="#ffd426" transform="scale(1.5) rotate(22)"/>
  <circle cx="0" cy="0" r="7" fill="#fff"/>
</g>
{switch_apparatus}
'''

# PCB Floor Ground Plane: elegant metallic tracks and dots along the floor line
pcb_floor = f'''
<g id="pcb_ground">
  <!-- Main ground copper bus -->
  <line x1="30" y1="{FLOOR}" x2="{W - 30}" y2="{FLOOR}" stroke="{EDGE}" stroke-width="6"/>
  <line x1="30" y1="{FLOOR}" x2="{W - 30}" y2="{FLOOR}" stroke="url(#gold)" stroke-width="3"/>
  <line x1="30" y1="{FLOOR - 1}" x2="{W - 30}" y2="{FLOOR - 1}" stroke="{HILITE}" stroke-width="0.8" opacity="0.6"/>
  <!-- Floor mounting via pads -->
  ''' + ''.join(f'<circle cx="{vx}" cy="{FLOOR + 18}" r="4" fill="{EDGE}"/><circle cx="{vx}" cy="{FLOOR + 18}" r="2.8" fill="url(#gold)"/><circle cx="{vx}" cy="{FLOOR + 18}" r="1.2" fill="{BG}"/>' for vx in range(80, W - 60, 95)) + f'''
  <line x1="40" y1="{FLOOR + 18}" x2="{W - 40}" y2="{FLOOR + 18}" stroke="{DOT}" stroke-width="1.5" stroke-dasharray="6 8"/>
</g>
'''

minions_markup = f'''
{pcb_floor}
<g mask="url(#botmask)">
  <g transform="translate(0,{2 * FLOOR + 4}) scale(1,-1)" opacity=".3" filter="url(#soft)">
    {minion_a_svg}
    {minion_b_svg}
  </g>
</g>
{minion_a_svg}
{minion_b_svg}
'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Atilade Oke in gold traces: two Minions fix the crooked crown on the first A, flip the switch, and light the name in gold">
<defs>
  <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="{DOT}"/></pattern>
  <linearGradient id="gold" x1="0" y1="0" x2="46" y2="92" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop offset="0" stop-color="#f6cf75"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="#b47d22"/>
  </linearGradient>
  <linearGradient id="minion_body_a" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#fff176"/><stop offset="35%" stop-color="#ffd426"/><stop offset="100%" stop-color="#e0a400"/>
  </linearGradient>
  <linearGradient id="minion_body_b" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#fff176"/><stop offset="35%" stop-color="#ffd426"/><stop offset="100%" stop-color="#e0a400"/>
  </linearGradient>
  <linearGradient id="denim_grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#3b6ca8"/><stop offset="60%" stop-color="#28568e"/><stop offset="100%" stop-color="#1b3d68"/>
  </linearGradient>
  <linearGradient id="silver_rim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ffffff"/><stop offset="30%" stop-color="#cbd3e0"/><stop offset="70%" stop-color="#798294"/><stop offset="100%" stop-color="#4a5263"/>
  </linearGradient>
  <linearGradient id="red_knob" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ff6b6b"/><stop offset="40%" stop-color="#e02424"/><stop offset="100%" stop-color="#800f0f"/>
  </linearGradient>
  <radialGradient id="lamp_core" cx="40%" cy="40%" r="65%">
    <stop offset="0%" stop-color="#ffffff"/><stop offset="30%" stop-color="#fff3a1"/><stop offset="70%" stop-color="#ffb71b"/><stop offset="100%" stop-color="#e08400"/>
  </radialGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="vig" cx="50%" cy="40%" r="75%">
    <stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/>
  </radialGradient>
  <filter id="glow" x="-15%" y="-40%" width="130%" height="180%">
    <feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="big" x="-40%" y="-80%" width="180%" height="260%"><feGaussianBlur stdDeviation="24"/></filter>
  <filter id="soft" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="1.6"/></filter>
  <linearGradient id="reflfade" x1="0" y1="{BASE}" x2="0" y2="{BASE + 100}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff" stop-opacity=".65"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="reflmask" maskUnits="userSpaceOnUse" x="0" y="{BASE}" width="{W}" height="{H - BASE}">
    <rect x="0" y="{BASE + 6}" width="{W}" height="{H - BASE}" fill="url(#reflfade)"/>
  </mask>
  <linearGradient id="botfade" x1="0" y1="{FLOOR}" x2="0" y2="{FLOOR + 38}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="botmask" maskUnits="userSpaceOnUse" x="0" y="{FLOOR}" width="{W}" height="{H - FLOOR}">
    <rect x="0" y="{FLOOR + 2}" width="{W}" height="{H - FLOOR}" fill="url(#botfade)"/>
  </mask>
  <mask id="namemask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{''.join(mask)}</mask>
</defs>
<style>
text{{font-family:{MONO}}}
{''.join(css)}
{reduced_css}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#vig)"/>
<ellipse id="nameglow" cx="{NX + name_w / 2}" cy="{NY + 3 * U}" rx="{name_w / 2 + 20}" ry="{4 * U}" fill="{GOLD}" filter="url(#big)" style="opacity:0"/>
<g id="reflg" mask="url(#reflmask)"><g transform="translate(0,{2 * BASE + 8}) scale(1,-1)" opacity=".5" filter="url(#soft)">{''.join(refl)}</g></g>
<g id="lit" filter="url(#glow)">{''.join(mid)}</g>
<g mask="url(#namemask)"><rect id="sheen" x="0" y="{NY - 10}" width="200" height="{6 * U + 20}" fill="url(#shine)" transform="translate(-260 0)"/></g>
<g id="padsg">{''.join(pads)}</g>
{crown}
{minions_markup}
</svg>'''

target = sys.argv[1] if len(sys.argv) > 1 else 'assets/traces.svg'
open(target, 'w').write(svg)
print(f"Generated {target}: size {len(svg)//1024} KB")
