# Animated PCB header with Minions:
# Story: (1) dark: name dim, crown crooked on first A, light off;
#        (2) Minion A bonks Minion B on the head (B reels: bump & stars);
#        (3) B runs to the crown, climbs and sets it straight;
#        (4) A has stayed at the switch the whole time; once crown is fixed A flips the switch;
#        (5) the light comes on and the name glows gold; both cheer; pause, loop.
# Regenerate: python3 tools/make_traces.py assets/traces.svg

import sys
from html import escape

W, H = 1040, 270
BG = '#070a14'
DOT = '#151c33'
EDGE = '#4a3210'
GOLD = '#dba33f'
HILITE = '#fff1c4'
SPARK = '#fffdf2'
INK = '#f4f6ff'
SUB = '#f0c877'
MUTED = '#56618a'
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
NX, NY, RAIL = (W - name_w) / 2 + 10, 66, 66 + 6 * U + 8
BASE = NY + 6 * U; FLOOR = BASE + 58
LXS = []
x = NX
for ci, ch in enumerate(NAME):
    nxt = NAME[ci + 1] if ci + 1 < len(NAME) else ' '
    if ch == ' ': x += SPACE - GAP; continue
    LXS.append(x)
    x += glyph_w(ch) + (gap_after(ch, nxt) if nxt != ' ' else GAP)

SWX = LXS[9] + 2 * U
SY = FLOOR - 24
CX = NX + 2 * U
CY = NY - 13
CLX = NX - 5
CLY = NY + 24
AX = SWX + 18
BX = SWX + 48

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

# 1. Lights and Glow
kf('#lit', [(0, 'opacity:0.28'), (8.8, 'opacity:0.28'), (8.9, 'opacity:0.6'), (9.0, 'opacity:1'), (14.6, 'opacity:1'), (15.0, 'opacity:0.28')])
kf('#padsg', [(0, 'opacity:0.28'), (8.8, 'opacity:0.28'), (8.9, 'opacity:0.6'), (9.0, 'opacity:1'), (14.6, 'opacity:1'), (15.0, 'opacity:0.28')])
kf('#reflg', [(0, 'opacity:0.2'), (8.8, 'opacity:0.2'), (9.0, 'opacity:0.65'), (14.6, 'opacity:0.65'), (15.0, 'opacity:0.2')])
kf('#nameglow', [(0, 'opacity:0'), (8.8, 'opacity:0'), (9.0, 'opacity:0.38'), (14.6, 'opacity:0.38'), (15.0, 'opacity:0')])

# Sheen sweep across letters
kf('#sheen', [
    (0, 'transform:translateX(-260px);opacity:0'),
    (9.2, 'transform:translateX(-260px);opacity:0'),
    (9.3, 'transform:translateX(-260px);opacity:1'),
    (10.8, 'transform:translateX(1100px);opacity:1'),
    (10.9, 'transform:translateX(1100px);opacity:0'),
])

# Wire spark pulse from switch to name
kf('#wire_spark', [
    (0, 'stroke-dashoffset:120;opacity:0'),
    (8.8, 'stroke-dashoffset:120;opacity:1'),
    (9.15, 'stroke-dashoffset:-120;opacity:1'),
    (9.2, 'stroke-dashoffset:-120;opacity:0'),
])

# Switch handle and LED
kf('#swk', [
    (0, 'transform:translateY(-4px)'),
    (8.2, 'transform:translateY(-4px)'),
    (8.4, 'transform:translateY(4px)'),
    (14.8, 'transform:translateY(4px)'),
    (15.0, 'transform:translateY(-4px)'),
])
kf('#swled', [
    (0, 'opacity:0.15;fill:#ff5a5a'),
    (8.7, 'opacity:0.15;fill:#ff5a5a'),
    (8.8, 'opacity:1;fill:#58f0a0'),
    (14.8, 'opacity:1;fill:#58f0a0'),
    (15.0, 'opacity:0.15;fill:#ff5a5a'),
])

# Crown: starts crooked (-18deg), B sets it straight at 7.0s
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
    (7.05, 'opacity:1;transform:scale(1.3)'),
    (7.4, 'opacity:0;transform:scale(1.8)'),
])

# Bonk star on B's head (2.0s)
kf('#bonk_star', [
    (0, 'opacity:0;transform:scale(0)'),
    (1.95, 'opacity:0;transform:scale(0)'),
    (2.05, 'opacity:1;transform:scale(1.4)'),
    (2.45, 'opacity:0;transform:scale(2.0)'),
])

# Minion A Position (stays at switch, bounces when cheering)
kf('.minion_a', [
    (0, f'transform:translate({AX}px,{FLOOR}px)'),
    (8.8, f'transform:translate({AX}px,{FLOOR}px)'),
    (9.0, f'transform:translate({AX}px,{FLOOR - 8}px)'),
    (9.3, f'transform:translate({AX}px,{FLOOR}px)'),
    (9.6, f'transform:translate({AX}px,{FLOOR - 8}px)'),
    (9.9, f'transform:translate({AX}px,{FLOOR}px)'),
    (10.2, f'transform:translate({AX}px,{FLOOR - 8}px)'),
    (10.5, f'transform:translate({AX}px,{FLOOR}px)'),
    (10.8, f'transform:translate({AX}px,{FLOOR - 8}px)'),
    (11.1, f'transform:translate({AX}px,{FLOOR}px)'),
    (14.6, f'transform:translate({AX}px,{FLOOR}px)'),
])

# Minion A Pupil: looks at B, looks at crown, looks up at switch, looks forward cheering
kf('.m_a_pupil', [
    (0, 'transform:none'),
    (1.4, 'transform:translate(1px, 0.5px)'), # looks at B
    (2.5, 'transform:translate(-1.2px, -0.5px)'), # looks left at crown
    (7.8, 'transform:translate(-0.8px, -1.5px)'), # looks up at switch
    (8.6, 'transform:translate(-0.8px, -1.5px)'),
    (9.0, 'transform:none'),
    (14.6, 'transform:none'),
])

# Minion A Eyelid blink
kf('.m_a_lid', [
    (0, 'opacity:0'),
    (0.9, 'opacity:0'),
    (1.0, 'opacity:1'),
    (1.1, 'opacity:0'),
    (12.0, 'opacity:0'),
    (12.1, 'opacity:1'),
    (12.2, 'opacity:0'),
])

# Minion A Arms
kf('.m_a_arm_l', [
    (0, 'transform:rotate(0deg)'),
    (1.5, 'transform:rotate(0deg)'),
    (1.75, 'transform:rotate(-75deg)'),
    (2.0, 'transform:rotate(55deg)'),
    (2.3, 'transform:rotate(15deg)'),
    (2.6, 'transform:rotate(-120deg)'), # points left toward crown
    (3.5, 'transform:rotate(-120deg)'),
    (3.8, 'transform:rotate(0deg)'),
    (8.8, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-140deg)'), # cheer
    (14.5, 'transform:rotate(-140deg)'),
    (14.8, 'transform:rotate(0deg)'),
])

kf('.m_a_arm_r', [
    (0, 'transform:rotate(0deg)'),
    (7.8, 'transform:rotate(0deg)'),
    (8.1, 'transform:rotate(-130deg)'),
    (8.4, 'transform:rotate(-65deg)'),
    (8.7, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-140deg)'), # cheer
    (14.5, 'transform:rotate(-140deg)'),
    (14.8, 'transform:rotate(0deg)'),
])

# Minion A Body Squash/Stretch
kf('.minion_a_inner', [
    (0, 'transform:none'),
    (1.9, 'transform:none'),
    (2.0, 'transform:scale(1.05, 0.95)'),
    (2.2, 'transform:none'),
    (8.9, 'transform:none'),
    (9.0, 'transform:scale(0.95, 1.08)'),
    (9.3, 'transform:scale(1.06, 0.94)'),
    (9.6, 'transform:scale(0.95, 1.08)'),
    (9.9, 'transform:scale(1.06, 0.94)'),
    (14.5, 'transform:none'),
])

# Minion B Position
kf('.minion_b', [
    (0, f'transform:translate({BX}px,{FLOOR}px)'),
    (1.95, f'transform:translate({BX}px,{FLOOR}px)'),
    (2.05, f'transform:translate({BX + 6}px,{FLOOR}px)'),
    (3.2, f'transform:translate({BX}px,{FLOOR}px)'),
    # Run to CLX
    (3.4, f'transform:translate({BX - 40}px,{FLOOR}px) scaleX(-1)'),
    (4.0, f'transform:translate({(BX + CLX)/2}px,{FLOOR}px) scaleX(-1)'),
    (5.4, f'transform:translate({CLX}px,{FLOOR}px) scaleX(-1)'),
    # Climb up A
    (5.5, f'transform:translate({CLX}px,{FLOOR}px) scaleX(1)'),
    (5.8, f'transform:translate({CLX}px,{FLOOR - 40}px) scaleX(1)'),
    (6.2, f'transform:translate({CLX}px,{FLOOR - 85}px) scaleX(1)'),
    (6.6, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Push crown
    (6.8, f'transform:translate({CLX + 4}px,{CLY - 4}px) scaleX(1)'),
    (7.0, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Cheering on A
    (7.2, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (8.8, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (9.0, f'transform:translate({CLX}px,{CLY - 8}px) scaleX(1)'),
    (9.3, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (9.6, f'transform:translate({CLX}px,{CLY - 8}px) scaleX(1)'),
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
    (2.05, 'transform:scale(1.3, 0.6)'), # bonked squash
    (2.25, 'transform:scale(0.88, 1.15)'), # spring up
    (2.5, 'transform:none'),
    # Running bounce
    (3.4, 'transform:scale(1.08, 0.92) rotate(8deg)'),
    (3.8, 'transform:scale(0.94, 1.06) rotate(12deg)'),
    (4.2, 'transform:scale(1.08, 0.92) rotate(8deg)'),
    (4.6, 'transform:scale(0.94, 1.06) rotate(12deg)'),
    (5.0, 'transform:scale(1.08, 0.92) rotate(8deg)'),
    (5.4, 'transform:none'),
    # Climbing
    (5.8, 'transform:scale(0.95, 1.05)'),
    (6.2, 'transform:scale(1.05, 0.95)'),
    (6.6, 'transform:none'),
    # Cheering on A
    (9.0, 'transform:scale(0.95, 1.08)'),
    (9.3, 'transform:scale(1.06, 0.94)'),
    (9.6, 'transform:scale(0.95, 1.08)'),
    (9.9, 'transform:scale(1.06, 0.94)'),
    (14.5, 'transform:none'),
])

# Minion B Bump on head
kf('.m_b_bump', [
    (0, 'opacity:0;transform:scale(0)'),
    (2.05, 'opacity:0;transform:scale(0)'),
    (2.15, 'opacity:1;transform:scale(1.2)'),
    (2.3, 'opacity:1;transform:scale(1.0)'),
    (3.4, 'opacity:1;transform:scale(1.0)'),
    (3.8, 'opacity:0;transform:scale(0)'),
])

# Minion B Stars circling head
kf('.m_b_stars', [
    (0, 'opacity:0;transform:scale(0) rotate(0deg)'),
    (2.05, 'opacity:0;transform:scale(0) rotate(0deg)'),
    (2.2, 'opacity:1;transform:scale(1.1) rotate(90deg)'),
    (2.6, 'opacity:1;transform:scale(1.0) rotate(220deg)'),
    (3.2, 'opacity:1;transform:scale(0.8) rotate(360deg)'),
    (3.5, 'opacity:0;transform:scale(0) rotate(420deg)'),
])

# Minion B Pupils: look at A, spin on bonk, look at crown, cheer
kf('.m_b_pupil', [
    (0, 'transform:none'),
    (1.5, 'transform:translate(-1px, 0px)'), # looks at A
    (2.1, 'transform:translate(1px, -1px)'), # dizzy spin
    (2.4, 'transform:translate(-1px, 1px)'),
    (2.7, 'transform:translate(0.5px, 0.5px)'),
    (3.4, 'transform:translate(1.2px, 0px)'), # looks forward in run
    (6.6, 'transform:translate(1px, -0.5px)'), # looks at crown
    (9.0, 'transform:none'),
    (14.5, 'transform:none'),
])

# Minion B Arms
kf('.m_b_arm_l', [
    (0, 'transform:rotate(0deg)'),
    (2.05, 'transform:rotate(-60deg)'), # head clutch
    (2.8, 'transform:rotate(-60deg)'),
    (3.2, 'transform:rotate(0deg)'),
    # Running arms pump
    (3.4, 'transform:rotate(-45deg)'),
    (3.8, 'transform:rotate(45deg)'),
    (4.2, 'transform:rotate(-45deg)'),
    (4.6, 'transform:rotate(45deg)'),
    (5.0, 'transform:rotate(-45deg)'),
    (5.4, 'transform:rotate(-70deg)'), # climb reaching
    (5.8, 'transform:rotate(-30deg)'),
    (6.2, 'transform:rotate(-70deg)'),
    (6.6, 'transform:rotate(90deg)'), # push crown
    (7.0, 'transform:rotate(90deg)'),
    (7.5, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-140deg)'), # cheer
    (14.5, 'transform:rotate(-140deg)'),
    (15.0, 'transform:rotate(0deg)'),
])

kf('.m_b_arm_r', [
    (0, 'transform:rotate(0deg)'),
    (2.05, 'transform:rotate(60deg)'), # head clutch
    (2.8, 'transform:rotate(60deg)'),
    (3.2, 'transform:rotate(0deg)'),
    # Running arms pump
    (3.4, 'transform:rotate(45deg)'),
    (3.8, 'transform:rotate(-45deg)'),
    (4.2, 'transform:rotate(45deg)'),
    (4.6, 'transform:rotate(-45deg)'),
    (5.0, 'transform:rotate(45deg)'),
    (5.4, 'transform:rotate(-30deg)'),
    (5.8, 'transform:rotate(-70deg)'),
    (6.2, 'transform:rotate(-30deg)'),
    (6.6, 'transform:rotate(90deg)'), # push crown
    (7.0, 'transform:rotate(90deg)'),
    (7.5, 'transform:rotate(0deg)'),
    (9.0, 'transform:rotate(-140deg)'), # cheer
    (14.5, 'transform:rotate(-140deg)'),
    (15.0, 'transform:rotate(0deg)'),
])

# Minion B Legs running cycle
kf('.m_b_l1', [
    (0, 'transform:none'),
    (3.2, 'transform:none'),
    (3.4, 'transform:rotate(28deg)'),
    (3.7, 'transform:rotate(-28deg)'),
    (4.0, 'transform:rotate(28deg)'),
    (4.3, 'transform:rotate(-28deg)'),
    (4.6, 'transform:rotate(28deg)'),
    (4.9, 'transform:rotate(-28deg)'),
    (5.2, 'transform:rotate(28deg)'),
    (5.4, 'transform:none'),
    (15.0, 'transform:none'),
    (15.2, 'transform:rotate(28deg)'),
    (15.5, 'transform:rotate(-28deg)'),
    (15.8, 'transform:none'),
])
kf('.m_b_l2', [
    (0, 'transform:none'),
    (3.2, 'transform:none'),
    (3.4, 'transform:rotate(-28deg)'),
    (3.7, 'transform:rotate(28deg)'),
    (4.0, 'transform:rotate(-28deg)'),
    (4.3, 'transform:rotate(28deg)'),
    (4.6, 'transform:rotate(-28deg)'),
    (4.9, 'transform:rotate(28deg)'),
    (5.2, 'transform:rotate(-28deg)'),
    (5.4, 'transform:none'),
    (15.0, 'transform:none'),
    (15.2, 'transform:rotate(-28deg)'),
    (15.5, 'transform:rotate(28deg)'),
    (15.8, 'transform:none'),
])

reduced_css = '''
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-delay: -10s !important;
    animation-play-state: paused !important;
  }
  #lit, #padsg, #reflg { opacity: 1 !important; }
  #nameglow { opacity: 0.38 !important; }
  #swled { opacity: 1 !important; fill: #58f0a0 !important; }
  #swk { transform: translateY(4px) !important; }
  #crownr { transform: none !important; }
}
'''

minion_a_svg = f'''
<g class="minion_a" transform="translate({AX},{FLOOR})">
  <g class="minion_a_inner">
    <!-- Hair strands -->
    <path d="M-6,-42 C-3,-46 -1,-44 0,-42 C1,-44 3,-46 6,-42" stroke="#15171d" stroke-width="1.4" fill="none" stroke-linecap="round"/>
    <path d="M-3,-43 C-1,-46 1,-46 3,-43" stroke="#15171d" stroke-width="1.1" fill="none" stroke-linecap="round"/>
    
    <!-- Body capsule -->
    <rect x="-11" y="-42" width="22" height="42" rx="11" fill="url(#minion_body_a)"/>
    <path d="M8,-38 C9,-30 9,-10 9,-2" stroke="#e0a000" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.4"/>
    <path d="M-8,-38 C-9,-30 -9,-10 -9,-2" stroke="#fff7a8" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.5"/>

    <!-- Mouth -->
    <path d="M-4,-15 Q0,-12 4,-15" stroke="#6b3a0a" stroke-width="1.2" stroke-linecap="round" fill="none"/>

    <!-- Goggle strap -->
    <rect x="-11.5" y="-29" width="23" height="5" rx="1" fill="#1b1d22"/>

    <!-- Single Goggle (Stuart) -->
    <g transform="translate(0, -26.5)">
      <circle cx="0" cy="0" r="7.4" fill="url(#silver_rim)" stroke="#353b49" stroke-width="0.8"/>
      <circle cx="-6.8" cy="0" r="0.7" fill="#222"/>
      <circle cx="6.8" cy="0" r="0.7" fill="#222"/>
      <circle cx="0" cy="0" r="5.6" fill="#1b1d22"/>
      <circle cx="0" cy="0" r="5.0" fill="#ffffff"/>
      <!-- Eye Pupil & Iris -->
      <g class="m_a_pupil">
        <circle cx="0" cy="0" r="2.6" fill="#7d4212" stroke="#4a2406" stroke-width="0.4"/>
        <circle cx="0" cy="0" r="1.5" fill="#111111"/>
        <circle cx="0.9" cy="-0.9" r="0.8" fill="#ffffff"/>
      </g>
      <!-- Eyelid for blinks -->
      <path class="m_a_lid" d="M-5,-2 Q0,1 5,-2 V-5 H-5 Z" fill="#ffd426"/>
    </g>

    <!-- Denim Overalls -->
    <path d="M-11,-14 C-11,-6 -8,0 0,0 C8,0 11,-6 11,-14 L11,-4 C11,0 7,0 0,0 C-7,0 -11,0 -11,-4 Z" fill="url(#denim_grad)"/>
    <path d="M-8,-16 H8 V-2 Q8,0 0,0 Q-8,0 -8,-2 Z" fill="url(#denim_grad)"/>
    <path d="M-8,-16 H8 V-2 Q8,0 0,0 Q-8,0 -8,-2 Z" fill="none" stroke="#1c3b63" stroke-width="0.8"/>
    <!-- Straps -->
    <path d="M-10,-19 L-6,-14" stroke="#224c80" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M10,-19 L6,-14" stroke="#224c80" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="-6.2" cy="-14.2" r="1.2" fill="#13161c"/>
    <circle cx="6.2" cy="-14.2" r="1.2" fill="#13161c"/>
    <!-- Pocket -->
    <path d="M-4.5,-11 H4.5 V-6.5 Q4.5,-3.5 0,-3.5 Q-4.5,-3.5 -4.5,-6.5 Z" fill="#204370" stroke="#162e4f" stroke-width="0.7"/>
    <circle cx="0" cy="-7" r="1.6" fill="#131e2b"/>
    <circle cx="0" cy="-7" r="1.0" fill="#204370"/>

    <!-- Legs & Shoes -->
    <g class="m_a_l1">
      <rect x="-7.5" y="-1" width="5" height="4.5" rx="1" fill="#1e4270"/>
      <path d="M-9,3.5 H-2 C-2,2 -3.5,1.5 -5,1.5 C-7.5,1.5 -9,2 -9,3.5 Z" fill="#14161a"/>
      <line x1="-9" y1="3.5" x2="-2" y2="3.5" stroke="#2c303a" stroke-width="0.8"/>
    </g>
    <g class="m_a_l2">
      <rect x="2.5" y="-1" width="5" height="4.5" rx="1" fill="#1e4270"/>
      <path d="M1,3.5 H8 C8,2 6.5,1.5 5,1.5 C2.5,1.5 1,2 1,3.5 Z" fill="#14161a"/>
      <line x1="1" y1="3.5" x2="8" y2="3.5" stroke="#2c303a" stroke-width="0.8"/>
    </g>

    <!-- Left Arm (with mallet) -->
    <g class="m_a_arm_l" style="transform-origin: -9px -15px">
      <path d="M-9,-15 Q-14,-10 -13,-4" stroke="#ffd426" stroke-width="3.2" stroke-linecap="round" fill="none"/>
      <circle cx="-13" cy="-3.5" r="2.4" fill="#15171d"/>
      <!-- Mallet -->
      <g transform="translate(-13, -3.5) rotate(25)">
        <rect x="-1.2" y="-10" width="2.4" height="13" rx="0.8" fill="#717a8c"/>
        <rect x="-4.5" y="-14" width="9" height="5.5" rx="1.5" fill="#475467" stroke="#1d2939" stroke-width="0.8"/>
      </g>
    </g>

    <!-- Right Arm -->
    <g class="m_a_arm_r" style="transform-origin: 9px -15px">
      <path d="M9,-15 Q14,-10 13,-4" stroke="#ffd426" stroke-width="3.2" stroke-linecap="round" fill="none"/>
      <circle cx="13" cy="-3.5" r="2.4" fill="#15171d"/>
    </g>
  </g>
</g>
'''

minion_b_svg = f'''
<g class="minion_b" transform="translate({BX},{FLOOR})">
  <g class="minion_b_inner">
    <!-- Hair sprouts -->
    <path d="M-2.5,-33 V-37 M0,-33 V-38 M2.5,-33 V-37" stroke="#15171d" stroke-width="1.2" stroke-linecap="round"/>

    <!-- Bump / Knot on head (bonk reaction) -->
    <g class="m_b_bump" style="transform-origin: 0px -33px">
      <path d="M-4,-33 Q0,-42 4,-33 Z" fill="#ff7a7a" stroke="#d94f4f" stroke-width="0.8"/>
      <line x1="-2" y1="-37" x2="2" y2="-37" stroke="#fff" stroke-width="0.7" opacity="0.8"/>
    </g>

    <!-- Circling stars -->
    <g class="m_b_stars" style="transform-origin: 0px -38px">
      <path d="M0,-8 L2,-2 L8,0 L2,2 L0,8 L-2,2 L-8,0 L-2,-2 Z" fill="#ffd426" stroke="#c99700" stroke-width="0.6" transform="translate(-11,-38) scale(0.6)"/>
      <path d="M0,-8 L2,-2 L8,0 L2,2 L0,8 L-2,2 L-8,0 L-2,-2 Z" fill="#ffd426" stroke="#c99700" stroke-width="0.6" transform="translate(11,-36) scale(0.7)"/>
      <circle cx="0" cy="-44" r="1.6" fill="#fff" opacity="0.9"/>
    </g>

    <!-- Body capsule -->
    <rect x="-12" y="-33" width="24" height="33" rx="12" fill="url(#minion_body_b)"/>
    <path d="M9,-30 C10,-20 10,-8 10,-1" stroke="#e0a000" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.4"/>
    <path d="M-9,-30 C-10,-20 -10,-8 -10,-1" stroke="#fff7a8" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.5"/>

    <!-- Mouth -->
    <path d="M-4,-12 Q0,-8 4,-12" stroke="#6b3a0a" stroke-width="1.2" stroke-linecap="round" fill="none"/>

    <!-- Goggle strap -->
    <rect x="-12.5" y="-23.5" width="25" height="5" rx="1" fill="#1b1d22"/>

    <!-- Two Goggles (Bob: heterochromia!) -->
    <!-- Left Eye: Green -->
    <g transform="translate(-4.2, -21)">
      <circle cx="0" cy="0" r="5.2" fill="url(#silver_rim)" stroke="#353b49" stroke-width="0.7"/>
      <circle cx="-4.8" cy="0" r="0.6" fill="#222"/>
      <circle cx="0" cy="0" r="3.9" fill="#1b1d22"/>
      <circle cx="0" cy="0" r="3.4" fill="#ffffff"/>
      <g class="m_b_pupil">
        <circle cx="0" cy="0" r="1.8" fill="#2e7d32" stroke="#1b4d1f" stroke-width="0.3"/>
        <circle cx="0" cy="0" r="1.0" fill="#111111"/>
        <circle cx="0.6" cy="-0.6" r="0.6" fill="#ffffff"/>
      </g>
    </g>
    <!-- Right Eye: Brown -->
    <g transform="translate(4.2, -21)">
      <circle cx="0" cy="0" r="5.2" fill="url(#silver_rim)" stroke="#353b49" stroke-width="0.7"/>
      <circle cx="4.8" cy="0" r="0.6" fill="#222"/>
      <circle cx="0" cy="0" r="3.9" fill="#1b1d22"/>
      <circle cx="0" cy="0" r="3.4" fill="#ffffff"/>
      <g class="m_b_pupil">
        <circle cx="0" cy="0" r="1.8" fill="#7d4212" stroke="#4a2406" stroke-width="0.3"/>
        <circle cx="0" cy="0" r="1.0" fill="#111111"/>
        <circle cx="0.6" cy="-0.6" r="0.6" fill="#ffffff"/>
      </g>
    </g>

    <!-- Overalls -->
    <path d="M-12,-12 C-12,-5 -9,0 0,0 C9,0 12,-5 12,-12 L12,-3 C12,0 8,0 0,0 C-8,0 -12,0 -12,-3 Z" fill="url(#denim_grad)"/>
    <path d="M-8.5,-13.5 H8.5 V-2 Q8.5,0 0,0 Q-8.5,0 -8.5,-2 Z" fill="url(#denim_grad)"/>
    <path d="M-8.5,-13.5 H8.5 V-2 Q8.5,0 0,0 Q-8.5,0 -8.5,-2 Z" fill="none" stroke="#1c3b63" stroke-width="0.8"/>
    <!-- Straps -->
    <path d="M-11,-16 L-7,-12" stroke="#224c80" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M11,-16 L7,-12" stroke="#224c80" stroke-width="2.4" stroke-linecap="round"/>
    <circle cx="-6.8" cy="-12" r="1.1" fill="#13161c"/>
    <circle cx="6.8" cy="-12" r="1.1" fill="#13161c"/>
    <!-- Pocket -->
    <path d="M-4,-9 H4 V-5 Q4,-2.5 0,-2.5 Q-4,-2.5 -4,-5 Z" fill="#204370" stroke="#162e4f" stroke-width="0.6"/>
    <circle cx="0" cy="-5.5" r="1.5" fill="#131e2b"/>
    <circle cx="0" cy="-5.5" r="0.9" fill="#204370"/>

    <!-- Legs & Shoes -->
    <g class="m_b_l1" style="transform-origin: -5.5px 0px">
      <rect x="-8" y="-1" width="5" height="4" rx="1" fill="#1e4270"/>
      <path d="M-9.5,3 H-2.5 C-2.5,1.8 -4,1.2 -5.5,1.2 C-8,1.2 -9.5,1.8 -9.5,3 Z" fill="#14161a"/>
      <line x1="-9.5" y1="3" x2="-2.5" y2="3" stroke="#2c303a" stroke-width="0.8"/>
    </g>
    <g class="m_b_l2" style="transform-origin: 5.5px 0px">
      <rect x="3" y="-1" width="5" height="4" rx="1" fill="#1e4270"/>
      <path d="M1.5,3 H8.5 C8.5,1.8 7,1.2 5.5,1.2 C3,1.2 1.5,1.8 1.5,3 Z" fill="#14161a"/>
      <line x1="1.5" y1="3" x2="8.5" y2="3" stroke="#2c303a" stroke-width="0.8"/>
    </g>

    <!-- Arms -->
    <g class="m_b_arm_l" style="transform-origin: -10px -13px">
      <path d="M-10,-13 Q-14,-8 -12,-2" stroke="#ffd426" stroke-width="2.8" stroke-linecap="round" fill="none"/>
      <circle cx="-12" cy="-1.5" r="2.0" fill="#15171d"/>
    </g>
    <g class="m_b_arm_r" style="transform-origin: 10px -13px">
      <path d="M10,-13 Q14,-8 12,-2" stroke="#ffd426" stroke-width="2.8" stroke-linecap="round" fill="none"/>
      <circle cx="12" cy="-1.5" r="2.0" fill="#15171d"/>
    </g>
  </g>
</g>
'''

switch_wire = f'''
<g id="sw">
  <path d="M{SWX},{BASE + 6} V{SY - 11}" stroke="url(#gold)" stroke-width="2.5"/>
  <path id="wire_spark" d="M{SWX},{SY - 11} V{BASE + 6} H{SWX - 60}" stroke="{SPARK}" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="15 105" pathLength="100"/>
  <rect x="{SWX - 8}" y="{SY - 12}" width="16" height="24" rx="4" fill="#141a30" stroke="{GOLD}" stroke-width="1.5"/>
  <rect x="{SWX - 2.5}" y="{SY - 7}" width="5" height="14" rx="2.5" fill="#05070f"/>
  <circle id="swk" cx="{SWX}" cy="{SY}" r="3.4" fill="{HILITE}"/>
  <circle cx="{SWX + 5}" cy="{SY - 9}" r="1.3" fill="#ff5a5a" opacity=".7"/>
  <circle id="swled" cx="{SWX + 5}" cy="{SY - 9}" r="1.6" fill="{LED}" filter="url(#glow)"/>
</g>
'''

STAR = 'M0,-9 L2.5,-2.5 L9,0 L2.5,2.5 L0,9 L-2.5,2.5 L-9,0 L-2.5,-2.5 Z'
crown = f'''
<g transform="translate({CX:.1f},{CY})">
  <g id="crownr">
    <g id="crown" filter="url(#glow)">
      <path d="M-19,0 L-23,-19 L-10,-9 L0,-24 L10,-9 L23,-19 L19,0 Z" fill="url(#gold)" stroke="{EDGE}" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M-17,-3.5 H17" stroke="{HILITE}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>
      <circle cx="-23" cy="-19" r="3.2" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>
      <circle cx="0" cy="-24" r="3.2" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>
      <circle cx="23" cy="-19" r="3.2" fill="{HILITE}" stroke="{EDGE}" stroke-width="1"/>
    </g>
  </g>
  <g id="crown_sparks" filter="url(#glow)" transform="translate(0,-12)">
    <path d="{STAR}" fill="{SPARK}" transform="translate(-24,-12) scale(0.6)"/>
    <path d="{STAR}" fill="{SPARK}" transform="translate(0,-20) scale(0.8)"/>
    <path d="{STAR}" fill="{SPARK}" transform="translate(24,-12) scale(0.6)"/>
    <circle cx="-10" cy="-15" r="1.8" fill="{HILITE}"/>
    <circle cx="10" cy="-15" r="1.8" fill="{HILITE}"/>
  </g>
</g>
<g id="bonk_star" filter="url(#glow)" transform="translate({BX},{FLOOR - 34})">
  <path d="{STAR}" fill="{HILITE}" transform="scale(1.2)"/>
  <circle cx="0" cy="0" r="3" fill="#fff"/>
</g>
{switch_wire}
'''

minions_markup = f'''
<g mask="url(#botmask)">
  <g transform="translate(0,{2 * FLOOR + 3}) scale(1,-1)" opacity=".35" filter="url(#soft)">
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
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="vig" cx="50%" cy="40%" r="75%">
    <stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".55"/>
  </radialGradient>
  <filter id="glow" x="-15%" y="-40%" width="130%" height="180%">
    <feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="big" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="22"/></filter>
  <filter id="soft" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="1.6"/></filter>
  <linearGradient id="reflfade" x1="0" y1="{RAIL}" x2="0" y2="{RAIL + 100}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="reflmask" maskUnits="userSpaceOnUse" x="0" y="{RAIL}" width="{W}" height="{H - RAIL}">
    <rect x="0" y="{RAIL + 6}" width="{W}" height="{H - RAIL}" fill="url(#reflfade)"/></mask>
  <linearGradient id="botfade" x1="0" y1="{FLOOR}" x2="0" y2="{FLOOR + 48}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="botmask" maskUnits="userSpaceOnUse" x="0" y="{FLOOR}" width="{W}" height="{H - FLOOR}">
    <rect x="0" y="{FLOOR + 2}" width="{W}" height="{H - FLOOR}" fill="url(#botfade)"/></mask>
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
<g id="reflg" mask="url(#reflmask)"><g transform="translate(0,{2 * RAIL + 6}) scale(1,-1)" opacity=".5" filter="url(#soft)">{''.join(refl)}</g></g>
<g id="lit" filter="url(#glow)">{''.join(mid)}</g>
<g mask="url(#namemask)"><rect id="sheen" x="0" y="{NY - 10}" width="200" height="{6 * U + 20}" fill="url(#shine)" transform="translate(-260 0)"/></g>
<g id="padsg">{''.join(pads)}</g>
{crown}
{minions_markup}
</svg>'''

target = sys.argv[1] if len(sys.argv) > 1 else 'assets/traces.svg'
open(target, 'w').write(svg)
print(f"Generated {target}: size {len(svg)//1024} KB")
