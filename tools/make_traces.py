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

# Shift name slightly left (NX=80) so 'E' ends at ~923, giving plenty of room
# for switch box & bulb at SWX=975 (completely right of 'E', zero overlap).
NX, NY = 80, 75
BASE = NY + 6 * U  # 165
FLOOR = 278        # floor line where minions stand

LXS = []
x = NX
for ci, ch in enumerate(NAME):
    nxt = NAME[ci + 1] if ci + 1 < len(NAME) else ' '
    if ch == ' ': x += SPACE - GAP; continue
    LXS.append(x)
    x += glyph_w(ch) + (gap_after(ch, nxt) if nxt != ' ' else GAP)

# Coordinates:
# Crown on first A:
CX = NX + 2 * U       # 110.0
CY = NY - 14          # 61
# Minion B perch beside crown on the left shoulder of A:
# A's left edge is at x=80, so perch at x=52 puts B entirely to the left of A!
CLX = 52.0
CLY = 105.0           # perch platform beside A shoulder

# Switch station on the right wall (SWX = 975):
# Last E of OKE ends at 923.0. SWX=975 is >50px to the right of E!
SWX = 975
# Minion A at the switch: x = 925 (standing under right edge of name, but on floor at y=278)
AX = 925
# Minion B at the start (in front of Minion A): x = 865
BX = 865

def dpath(points): return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)

edge_paths, mid_paths, refl_paths, mask_paths, pads = [], [], [], [], []
for ci, ch in enumerate(NAME.replace(' ', '')):
    ox = LXS[ci]
    for seg in LETTERS[ch][0]:
        pts = [(ox + px * U, NY + py * U) for px, py in seg]
        d = dpath(pts)
        edge_paths.append(f'<path d="{d}" stroke="{EDGE}" stroke-width="{LW}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
        mid_paths.append(f'<path d="{d}" stroke="url(#gold)" stroke-width="{LW - 2}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
        refl_paths.append(f'<path d="{d}" stroke="url(#gold)" stroke-width="{LW - 2}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
        mask_paths.append(f'<path d="{d}" stroke="#fff" stroke-width="{LW}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    for px, py in LETTERS[ch][1]:
        cx, cy = ox + px * U, NY + py * U
        pads.append(f'<circle cx="{cx}" cy="{cy}" r="3.2" fill="{BG}" stroke="{GOLD}" stroke-width="1.2"/>')

T = 16.0
keyframes = {}
def kf(sel, frames):
    keyframes[sel] = sorted(frames, key=lambda f: f[0])

# Global Name Illumination (t=9.0s onwards)
kf('#lit', [
    (0, 'opacity:0.25'),
    (8.8, 'opacity:0.25'),
    (8.9, 'opacity:0.6'),
    (9.0, 'opacity:1'),
    (14.6, 'opacity:1'),
    (15.0, 'opacity:0.25'),
    (T, 'opacity:0.25'),
])
kf('#padsg', [
    (0, 'opacity:0.25'),
    (8.8, 'opacity:0.25'),
    (8.9, 'opacity:0.6'),
    (9.0, 'opacity:1'),
    (14.6, 'opacity:1'),
    (15.0, 'opacity:0.25'),
    (T, 'opacity:0.25'),
])
kf('#reflg', [
    (0, 'opacity:0.18'),
    (8.8, 'opacity:0.18'),
    (9.0, 'opacity:0.6'),
    (14.6, 'opacity:0.6'),
    (15.0, 'opacity:0.18'),
    (T, 'opacity:0.18'),
])
kf('#nameglow', [
    (0, 'opacity:0'),
    (8.8, 'opacity:0'),
    (9.0, 'opacity:0.42'),
    (14.6, 'opacity:0.42'),
    (15.0, 'opacity:0'),
    (T, 'opacity:0'),
])
kf('#sheen', [
    (0, 'transform:translateX(-260px);opacity:0'),
    (9.2, 'transform:translateX(-260px);opacity:0'),
    (9.3, 'transform:translateX(-260px);opacity:1'),
    (10.8, 'transform:translateX(1100px);opacity:1'),
    (10.9, 'transform:translateX(1100px);opacity:0'),
    (T, 'transform:translateX(-260px);opacity:0'),
])
kf('#wire_spark', [
    (0, 'stroke-dashoffset:160;opacity:0'),
    (8.8, 'stroke-dashoffset:160;opacity:1'),
    (9.15, 'stroke-dashoffset:-160;opacity:1'),
    (9.2, 'stroke-dashoffset:-160;opacity:0'),
    (T, 'stroke-dashoffset:160;opacity:0'),
])

# Mechanical Switch Lever: flips down at 8.4s
kf('#sw_lever', [
    (0, 'transform:rotate(-45deg)'),
    (8.2, 'transform:rotate(-45deg)'),
    (8.4, 'transform:rotate(38deg)'),
    (14.8, 'transform:rotate(38deg)'),
    (15.0, 'transform:rotate(-45deg)'),
    (T, 'transform:rotate(-45deg)'),
])

# Lamp Light Bulb above switch box: ignites at 9.0s
kf('#lamp_lit', [
    (0, 'opacity:0'),
    (8.8, 'opacity:0'),
    (8.95, 'opacity:0.7'),
    (9.0, 'opacity:1'),
    (14.6, 'opacity:1'),
    (15.0, 'opacity:0'),
    (T, 'opacity:0'),
])
kf('#lamp_glow', [
    (0, 'opacity:0;transform:scale(0.3)'),
    (8.8, 'opacity:0;transform:scale(0.3)'),
    (9.0, 'opacity:0.85;transform:scale(1.0)'),
    (9.3, 'opacity:0.95;transform:scale(1.1)'),
    (9.6, 'opacity:0.85;transform:scale(1.0)'),
    (14.6, 'opacity:0.85;transform:scale(1.0)'),
    (15.0, 'opacity:0;transform:scale(0.3)'),
    (T, 'opacity:0;transform:scale(0.3)'),
])

# Crown: crooked until fixed by B at 7.0s
kf('#crown_g', [
    (0, 'transform:rotate(24deg)'),
    (6.8, 'transform:rotate(24deg)'),
    (7.0, 'transform:rotate(0deg)'),
    (14.8, 'transform:rotate(0deg)'),
    (15.0, 'transform:rotate(24deg)'),
    (T, 'transform:rotate(24deg)'),
])

# Crown spark burst when straight (7.0s)
kf('#crown_sparks', [
    (0, 'opacity:0;transform:scale(0)'),
    (6.95, 'opacity:0;transform:scale(0)'),
    (7.05, 'opacity:1;transform:scale(1.4)'),
    (7.45, 'opacity:0;transform:scale(2.0)'),
    (T, 'opacity:0;transform:scale(0)'),
])

# Dramatic Bonk Impact Flash Starburst on B's head (2.0s)
# NOTE: translate(BX, FLOOR - 74) included in keyframes so it NEVER renders at (0, 0)!
kf('#bonk_star', [
    (0, f'opacity:0;transform:translate({BX}px,{FLOOR - 74}px) scale(0)'),
    (1.95, f'opacity:0;transform:translate({BX}px,{FLOOR - 74}px) scale(0)'),
    (2.02, f'opacity:1;transform:translate({BX}px,{FLOOR - 74}px) scale(1.6)'),
    (2.45, f'opacity:0;transform:translate({BX}px,{FLOOR - 74}px) scale(2.2)'),
    (T, f'opacity:0;transform:translate({BX}px,{FLOOR - 74}px) scale(0)'),
])

# Minion A Position: stays at AX=925 near switch box
kf('.minion_a', [
    (0, f'transform:translate({AX}px,{FLOOR}px)'),
    (8.8, f'transform:translate({AX}px,{FLOOR}px)'),
    # Cheering bounces during Beat 5
    (9.0, f'transform:translate({AX}px,{FLOOR - 14}px)'),
    (9.3, f'transform:translate({AX}px,{FLOOR}px)'),
    (9.6, f'transform:translate({AX}px,{FLOOR - 14}px)'),
    (9.9, f'transform:translate({AX}px,{FLOOR}px)'),
    (14.5, f'transform:translate({AX}px,{FLOOR}px)'),
    (T, f'transform:translate({AX}px,{FLOOR}px)'),
])

# Minion A Left Arm: holds wrench, winds up at 1.7s, swings LEFT to bonk B at 2.0s
kf('.m_a_arm_l', [
    (0, 'transform:rotate(-15deg)'),
    (1.5, 'transform:rotate(-15deg)'),
    (1.7, 'transform:rotate(75deg)'),   # windup high
    (2.02, 'transform:rotate(-85deg)'), # slam down left onto B's head!
    (2.4, 'transform:rotate(-85deg)'),  # hold impact
    (2.8, 'transform:rotate(-45deg)'),  # point wrench
    (3.5, 'transform:rotate(-15deg)'),  # lower
    (9.0, 'transform:rotate(-155deg)'), # cheer arms up!
    (14.5, 'transform:rotate(-155deg)'),
    (15.0, 'transform:rotate(-15deg)'),
    (T, 'transform:rotate(-15deg)'),
])

# Minion A Right Arm: reaches RIGHT to pull switch lever at SWX=975
kf('.m_a_arm_r', [
    (0, 'transform:rotate(10deg)'),
    (7.8, 'transform:rotate(10deg)'),
    (8.1, 'transform:rotate(-55deg)'),  # reach right towards lever knob
    (8.4, 'transform:rotate(30deg)'),   # pull lever down
    (8.8, 'transform:rotate(30deg)'),
    (9.0, 'transform:rotate(155deg)'),  # cheer arms up!
    (14.5, 'transform:rotate(155deg)'),
    (15.0, 'transform:rotate(10deg)'),
    (T, 'transform:rotate(10deg)'),
])

# Minion A Eye / Pupil: tracks B, tracks switch, celebrates
kf('.m_a_pupil', [
    (0, 'transform:translate(-2px, 0px)'),       # look left at B
    (2.0, 'transform:translate(-3px, 1px)'),      # glaring down-left at B
    (3.5, 'transform:translate(-3px, 0px)'),      # watch B run left
    (6.5, 'transform:translate(-3.5px, -2px)'),   # look up-left at B on crown
    (7.8, 'transform:translate(2px, 0px)'),       # look right at switch
    (8.4, 'transform:translate(2px, 1px)'),       # look at lever
    (9.0, 'transform:translate(0px, -2px)'),      # look up at blazing bulb!
    (14.5, 'transform:translate(0px, -2px)'),
    (15.0, 'transform:translate(-2px, 0px)'),
    (T, 'transform:translate(-2px, 0px)'),
])

# Minion A Body Bounce / Cheer
kf('.minion_a_inner', [
    (0, 'transform:none'),
    (1.7, 'transform:scale(0.96, 1.05)'),
    (2.02, 'transform:scale(1.08, 0.92)'), # slam exertion
    (2.3, 'transform:none'),
    (8.4, 'transform:scale(1.04, 0.96)'), # pull effort
    (9.0, 'transform:scale(0.92, 1.1)'),  # cheer jump
    (9.3, 'transform:scale(1.06, 0.94)'),
    (9.6, 'transform:scale(0.92, 1.1)'),
    (9.9, 'transform:scale(1.06, 0.94)'),
    (14.5, 'transform:none'),
    (T, 'transform:none'),
])

# Minion B Position:
# Starts at BX=865 (plenty of room inside frame, 175px from right wall).
# Runs left to CLX=52 (perch platform beside A shoulder).
kf('.minion_b', [
    (0, f'transform:translate({BX}px,{FLOOR}px)'),
    (1.95, f'transform:translate({BX}px,{FLOOR}px)'),
    (2.05, f'transform:translate({BX - 10}px,{FLOOR}px)'), # reels left from bonk
    (3.2, f'transform:translate({BX}px,{FLOOR}px)'),
    # Run to CLX=52
    (3.4, f'transform:translate({BX - 60}px,{FLOOR}px) scaleX(-1)'),
    (4.0, f'transform:translate({(BX + CLX)/2}px,{FLOOR}px) scaleX(-1)'),
    (5.4, f'transform:translate({CLX}px,{FLOOR}px) scaleX(-1)'),
    # Climb up ladder to perch beside A shoulder (CLX=52, CLY=105)
    (5.5, f'transform:translate({CLX}px,{FLOOR}px) scaleX(1)'),
    (5.8, f'transform:translate({CLX}px,{FLOOR - 55}px) scaleX(1)'),
    (6.2, f'transform:translate({CLX}px,{FLOOR - 120}px) scaleX(1)'),
    (6.6, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Push crown: crown is at CX=110, B reaches arm right to push it straight
    (6.8, f'transform:translate({CLX + 6}px,{CLY - 4}px) scaleX(1)'),
    (7.0, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Cheering on perch beside A (unobscuring A!)
    (7.2, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (8.8, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (9.0, f'transform:translate({CLX}px,{CLY - 14}px) scaleX(1)'),
    (9.3, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (9.6, f'transform:translate({CLX}px,{CLY - 14}px) scaleX(1)'),
    (9.9, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    (14.5, f'transform:translate({CLX}px,{CLY}px) scaleX(1)'),
    # Slide down
    (15.0, f'transform:translate({CLX}px,{FLOOR}px) scaleX(1)'),
    # Run back to BX
    (15.2, f'transform:translate({(BX + CLX)/2}px,{FLOOR}px) scaleX(1)'),
    (15.8, f'transform:translate({BX}px,{FLOOR}px) scaleX(1)'),
    (T, f'transform:translate({BX}px,{FLOOR}px) scaleX(1)'),
])

# Minion B Body Squash & Stretch
kf('.minion_b_inner', [
    (0, 'transform:none'),
    (1.95, 'transform:none'),
    (2.05, 'transform:scale(1.4, 0.52)'), # massive squash on bonk!
    (2.25, 'transform:scale(0.85, 1.2)'),  # spring back up
    (2.5, 'transform:none'),
    # Running squash & stretch cycle
    (3.4, 'transform:scale(1.1, 0.9) rotate(-14deg)'),
    (3.8, 'transform:scale(0.92, 1.08) rotate(-18deg)'),
    (4.2, 'transform:scale(1.1, 0.9) rotate(-14deg)'),
    (4.6, 'transform:scale(0.92, 1.08) rotate(-18deg)'),
    (5.0, 'transform:scale(1.1, 0.9) rotate(-14deg)'),
    (5.4, 'transform:none'),
    # Climbing effort
    (5.8, 'transform:scale(0.92, 1.08)'),
    (6.2, 'transform:scale(1.08, 0.92)'),
    (6.6, 'transform:none'),
    # Cheering bounce
    (9.0, 'transform:scale(0.92, 1.1)'),
    (9.3, 'transform:scale(1.08, 0.92)'),
    (9.6, 'transform:scale(0.92, 1.1)'),
    (9.9, 'transform:scale(1.08, 0.92)'),
    (14.5, 'transform:none'),
    (T, 'transform:none'),
])

# Minion B Bump on head: swells on bonk
kf('.m_b_bump', [
    (0, 'opacity:0;transform:scale(0)'),
    (2.05, 'opacity:0;transform:scale(0)'),
    (2.15, 'opacity:1;transform:scale(1.3)'),
    (2.35, 'opacity:1;transform:scale(1.0)'),
    (3.4, 'opacity:1;transform:scale(1.0)'),
    (3.8, 'opacity:0;transform:scale(0)'),
    (T, 'opacity:0;transform:scale(0)'),
])

# Minion B Orbiting comic stars
kf('.m_b_stars', [
    (0, 'opacity:0;transform:scale(0) rotate(0deg)'),
    (2.05, 'opacity:0;transform:scale(0) rotate(0deg)'),
    (2.2, 'opacity:1;transform:scale(1.2) rotate(100deg)'),
    (2.6, 'opacity:1;transform:scale(1.0) rotate(240deg)'),
    (3.2, 'opacity:1;transform:scale(0.8) rotate(360deg)'),
    (3.6, 'opacity:0;transform:scale(0) rotate(420deg)'),
    (T, 'opacity:0;transform:scale(0) rotate(0deg)'),
])

# Minion B Eyes: dazed on bonk, focused on run, happy when celebrating
kf('.m_b_pupil', [
    (0, 'transform:translate(2px, 0px)'),        # look right at A
    (1.5, 'transform:translate(2px, 0px)'),
    (2.1, 'transform:translate(-2px, -2px)'),    # dazed dizzy roll
    (2.4, 'transform:translate(2px, 2px)'),
    (2.7, 'transform:translate(-1px, 1px)'),
    (3.4, 'transform:translate(-2.5px, 0px)'),   # look ahead (left)
    (6.6, 'transform:translate(2px, -1px)'),     # look at crown
    (9.0, 'transform:translate(0px, -2px)'),     # cheering up
    (14.5, 'transform:translate(0px, -2px)'),
    (T, 'transform:translate(2px, 0px)'),
])

# Minion B Left Arm
kf('.m_b_arm_l', [
    (0, 'transform:rotate(0deg)'),
    (2.05, 'transform:rotate(-70deg)'), # flail on bonk
    (2.8, 'transform:rotate(-70deg)'),
    (3.2, 'transform:rotate(0deg)'),
    # Running arm pump
    (3.4, 'transform:rotate(-55deg)'),
    (3.8, 'transform:rotate(55deg)'),
    (4.2, 'transform:rotate(-55deg)'),
    (4.6, 'transform:rotate(55deg)'),
    (5.0, 'transform:rotate(-55deg)'),
    # Climbing reach
    (5.4, 'transform:rotate(-85deg)'),
    (5.8, 'transform:rotate(-35deg)'),
    (6.2, 'transform:rotate(-85deg)'),
    # Push crown
    (6.6, 'transform:rotate(105deg)'),
    (7.0, 'transform:rotate(105deg)'),
    (7.5, 'transform:rotate(0deg)'),
    # Cheer arms up
    (9.0, 'transform:rotate(-145deg)'),
    (14.5, 'transform:rotate(-145deg)'),
    (15.0, 'transform:rotate(0deg)'),
    (T, 'transform:rotate(0deg)'),
])

# Minion B Right Arm
kf('.m_b_arm_r', [
    (0, 'transform:rotate(0deg)'),
    (2.05, 'transform:rotate(70deg)'), # flail on bonk
    (2.8, 'transform:rotate(70deg)'),
    (3.2, 'transform:rotate(0deg)'),
    # Running arm pump
    (3.4, 'transform:rotate(55deg)'),
    (3.8, 'transform:rotate(-55deg)'),
    (4.2, 'transform:rotate(55deg)'),
    (4.6, 'transform:rotate(-55deg)'),
    (5.0, 'transform:rotate(55deg)'),
    # Climbing reach
    (5.4, 'transform:rotate(-35deg)'),
    (5.8, 'transform:rotate(-85deg)'),
    (6.2, 'transform:rotate(-35deg)'),
    # Push crown straight (reaches right to crown at CX=110)
    (6.6, 'transform:rotate(105deg)'),
    (7.0, 'transform:rotate(105deg)'),
    (7.5, 'transform:rotate(0deg)'),
    # Cheer arms up
    (9.0, 'transform:rotate(-145deg)'),
    (14.5, 'transform:rotate(-145deg)'),
    (15.0, 'transform:rotate(0deg)'),
    (T, 'transform:rotate(0deg)'),
])

# Minion B Legs: running sprint cycle
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
    (T, 'transform:none'),
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
    (T, 'transform:none'),
])

css = []
for sel, frames in keyframes.items():
    idx = len(css)
    name = f'k{idx}'
    css.append(f'{sel}{{animation:{name} {T:.2f}s linear infinite}}')
    body = []
    for t, decl in frames:
        pct = max(0.0, min(100.0, (t / T) * 100))
        body.append(f'{pct:.2f}%{{{decl}}}')
    css.append(f'@keyframes {name}{{{ "".join(body) }}}')

reduced_css = f'''
@media (prefers-reduced-motion: reduce) {{
  *, ::before, ::after {{{{
    animation-delay: -10s !important;
    animation-play-state: paused !important;
  }}
  #lit, #padsg, #reflg {{ opacity: 1 !important; }}
  #nameglow {{ opacity: 0.42 !important; }}
  #lamp_lit {{ opacity: 1 !important; }}
  #lamp_glow {{ opacity: 0.85 !important; transform: scale(1) !important; }}
  #crown_g {{ transform: rotate(0deg) !important; }}
  .minion_a {{ transform: translate({AX}px,{FLOOR}px) !important; }}
  .minion_b {{ transform: translate({CLX}px,{CLY}px) scaleX(1) !important; }}
  .m_a_arm_l, .m_a_arm_r {{ transform: rotate(-155deg) !important; }}
  .m_b_arm_l, .m_b_arm_r {{ transform: rotate(-145deg) !important; }}
  #sw_lever {{ transform: rotate(38deg) !important; }}
}}
'''

STAR = "M0,-14 L3.5,-3.5 L14,0 L3.5,3.5 L0,14 L-3.5,3.5 L-14,0 L-3.5,-3.5 Z"

# Crown at (CX, CY) on top of the first A
crown = f'''
<g id="crown_g" transform-origin="{CX}px {CY + 14}px" style="transform:rotate(24deg)">
  <!-- Golden Crown Base & Jewels -->
  <path d="M{CX - 18},{CY + 13} L{CX - 22},{CY - 5} L{CX - 8},{CY + 3} L{CX},{CY - 12} L{CX + 8},{CY + 3} L{CX + 22},{CY - 5} L{CX + 18},{CY + 13} Z" fill="url(#gold)" stroke="{HILITE}" stroke-width="1.2" stroke-linejoin="round"/>
  <circle cx="{CX - 22}" cy="{CY - 5}" r="2.8" fill="{SPARK}"/>
  <circle cx="{CX}" cy="{CY - 12}" r="3.5" fill="{SPARK}"/>
  <circle cx="{CX + 22}" cy="{CY - 5}" r="2.8" fill="{SPARK}"/>
  <circle cx="{CX - 9}" cy="{CY + 8}" r="1.8" fill="#e03030"/>
  <circle cx="{CX}" cy="{CY + 8}" r="2.2" fill="{BLUE}"/>
  <circle cx="{CX + 9}" cy="{CY + 8}" r="1.8" fill="#e03030"/>
  <rect x="{CX - 17}" y="{CY + 11}" width="34" height="2.5" rx="1.2" fill="{HILITE}" opacity="0.8"/>
  <g id="crown_sparks" filter="url(#glow)" transform="translate({CX},{CY})">
    <path d="{STAR}" fill="{SPARK}" transform="translate(-28,-14) scale(0.65)"/>
    <path d="{STAR}" fill="{SPARK}" transform="translate(0,-24) scale(0.85)"/>
    <path d="{STAR}" fill="{SPARK}" transform="translate(28,-14) scale(0.65)"/>
    <circle cx="-12" cy="-16" r="2.2" fill="{HILITE}"/>
    <circle cx="12" cy="-16" r="2.2" fill="{HILITE}"/>
  </g>
</g>
'''

# Switch Station & Light Bulb at SWX = 975 (well to the right of 'E' at 923):
SW_BOX_Y = 210
switch_apparatus = f'''
<g id="switch_station">
  <!-- Power conduit from switch to name: runs from SWX=975 left to LXS[9] + glyph_w('E')=923 -->
  <path d="M{SWX},{BASE} H{LXS[9] + glyph_w('E')}" stroke="url(#gold)" stroke-width="3.5" fill="none"/>
  <path d="M{SWX},{SW_BOX_Y} V{BASE}" stroke="url(#gold)" stroke-width="3.5" fill="none"/>
  <path id="wire_spark" d="M{SWX},{SW_BOX_Y} V{BASE} H{LXS[9]}" stroke="#fffdf2" stroke-width="4" fill="none" stroke-linecap="round" stroke-dasharray="20 140" pathLength="100"/>

  <!-- Substantial Mechanical Switch Box -->
  <rect x="{SWX - 18}" y="{SW_BOX_Y}" width="36" height="{FLOOR - SW_BOX_Y}" rx="5" fill="#121724" stroke="#2a354d" stroke-width="2"/>
  <rect x="{SWX - 14}" y="{SW_BOX_Y + 4}" width="28" height="{FLOOR - SW_BOX_Y - 8}" rx="3" fill="#182030" stroke="#0e131d" stroke-width="1.2"/>
  <!-- Corner mounting screws -->
  <circle cx="{SWX - 12}" cy="{SW_BOX_Y + 7}" r="1.5" fill="#52607a"/>
  <circle cx="{SWX + 12}" cy="{SW_BOX_Y + 7}" r="1.5" fill="#52607a"/>
  <circle cx="{SWX - 12}" cy="{FLOOR - 7}" r="1.5" fill="#52607a"/>
  <circle cx="{SWX + 12}" cy="{FLOOR - 7}" r="1.5" fill="#52607a"/>

  <!-- Lever slot and pivot -->
  <rect x="{SWX - 4}" y="{SW_BOX_Y + 22}" width="8" height="30" rx="3" fill="#05070d"/>
  <circle cx="{SWX}" cy="{SW_BOX_Y + 35}" r="5" fill="#364057" stroke="#1d2433" stroke-width="1.2"/>
  <circle cx="{SWX}" cy="{SW_BOX_Y + 35}" r="2.2" fill="{HILITE}"/>

  <!-- Big Lever Arm + Red Ball Knob -->
  <g id="sw_lever" style="transform-origin: {SWX}px {SW_BOX_Y + 35}px">
    <rect x="{SWX - 2.5}" y="{SW_BOX_Y + 8}" width="5" height="28" rx="1.5" fill="url(#silver_rim)" stroke="#222" stroke-width="0.8"/>
    <!-- Big red grip ball knob -->
    <circle cx="{SWX}" cy="{SW_BOX_Y + 6}" r="6.8" fill="url(#red_knob)" stroke="#731111" stroke-width="1"/>
    <circle cx="{SWX + 1.8}" cy="{SW_BOX_Y + 4.2}" r="1.8" fill="#ffffff" opacity="0.8"/>
  </g>

  <!-- Big Light Bulb / Lamp on top of switch box (center at SWX, 150) -->
  <g id="lamp_fixture">
    <!-- Brass / metallic socket -->
    <rect x="{SWX - 8}" y="{SW_BOX_Y - 36}" width="16" height="14" rx="2" fill="#c4932f" stroke="#7a550d" stroke-width="1"/>
    <line x1="{SWX - 8}" y1="{SW_BOX_Y - 32}" x2="{SWX + 8}" y2="{SW_BOX_Y - 32}" stroke="#523908" stroke-width="1.2"/>
    <line x1="{SWX - 8}" y1="{SW_BOX_Y - 27}" x2="{SWX + 8}" y2="{SW_BOX_Y - 27}" stroke="#523908" stroke-width="1.2"/>

    <!-- Unlit / Dark bulb glass -->
    <circle cx="{SWX}" cy="{SW_BOX_Y - 60}" r="18" fill="#141a29" stroke="#3d4966" stroke-width="1.5" opacity="0.85"/>
    <!-- Filament coils (visible inside) -->
    <path d="M{SWX - 4},{SW_BOX_Y - 40} L{SWX - 4},{SW_BOX_Y - 55} L{SWX},{SW_BOX_Y - 64} L{SWX + 4},{SW_BOX_Y - 55} L{SWX + 4},{SW_BOX_Y - 40}" fill="none" stroke="#684a1a" stroke-width="1.2"/>

    <!-- Lit Glow & Lamp Bulb (t=9.0s onwards) -->
    <g id="lamp_lit">
      <!-- Radiant Light Rays -->
      <g stroke="#ffd952" stroke-width="2" stroke-linecap="round" opacity="0.75">
        <line x1="{SWX}" y1="{SW_BOX_Y - 84}" x2="{SWX}" y2="{SW_BOX_Y - 96}"/>
        <line x1="{SWX + 18}" y1="{SW_BOX_Y - 77}" x2="{SWX + 27}" y2="{SW_BOX_Y - 86}"/>
        <line x1="{SWX + 24}" y1="{SW_BOX_Y - 60}" x2="{SWX + 36}" y2="{SW_BOX_Y - 60}"/>
        <line x1="{SWX + 18}" y1="{SW_BOX_Y - 43}" x2="{SWX + 27}" y2="{SW_BOX_Y - 34}"/>
        <line x1="{SWX - 18}" y1="{SW_BOX_Y - 77}" x2="{SWX - 27}" y2="{SW_BOX_Y - 86}"/>
        <line x1="{SWX - 24}" y1="{SW_BOX_Y - 60}" x2="{SWX - 36}" y2="{SW_BOX_Y - 60}"/>
        <line x1="{SWX - 18}" y1="{SW_BOX_Y - 43}" x2="{SWX - 27}" y2="{SW_BOX_Y - 34}"/>
      </g>
      <!-- Brilliant Glowing Core -->
      <circle cx="{SWX}" cy="{SW_BOX_Y - 60}" r="18" fill="url(#lamp_core)" stroke="#fffdf0" stroke-width="2"/>
      <circle cx="{SWX - 5}" cy="{SW_BOX_Y - 65}" r="4.5" fill="#ffffff" opacity="0.8"/>
      <!-- Soft Radial Bloom halo -->
      <circle id="lamp_glow" cx="{SWX}" cy="{SW_BOX_Y - 60}" r="48" fill="url(#lamp_bloom)" style="transform-origin:{SWX}px {SW_BOX_Y - 60}px"/>
    </g>
  </g>
</g>
'''

# PCB Floor Ground Plane + Ladder Trace to Perch beside A
pcb_floor = f'''
<g id="pcb_ground">
  <!-- Copper bus bar along floor line -->
  <line x1="0" y1="{FLOOR}" x2="{W}" y2="{FLOOR}" stroke="#523916" stroke-width="4"/>
  <line x1="0" y1="{FLOOR}" x2="{W}" y2="{FLOOR}" stroke="url(#gold)" stroke-width="2"/>
  <!-- Ladder trace rising up to perch beside A (CLX=52, CLY=105) -->
  <line x1="{CLX}" y1="{FLOOR}" x2="{CLX}" y2="{CLY}" stroke="url(#gold)" stroke-width="2.5"/>
  <line x1="{CLX - 10}" y1="{CLY + 30}" x2="{CLX + 10}" y2="{CLY + 30}" stroke="url(#gold)" stroke-width="1.8"/>
  <line x1="{CLX - 10}" y1="{CLY + 65}" x2="{CLX + 10}" y2="{CLY + 65}" stroke="url(#gold)" stroke-width="1.8"/>
  <line x1="{CLX - 10}" y1="{CLY + 100}" x2="{CLX + 10}" y2="{CLY + 100}" stroke="url(#gold)" stroke-width="1.8"/>
  <line x1="{CLX - 10}" y1="{CLY + 135}" x2="{CLX + 10}" y2="{CLY + 135}" stroke="url(#gold)" stroke-width="1.8"/>
  <!-- Perch step platform beside A shoulder -->
  <rect x="{CLX - 16}" y="{CLY}" width="32" height="3.5" rx="1.5" fill="url(#gold)" stroke="{EDGE}" stroke-width="0.8"/>
  <circle cx="{CLX - 10}" cy="{CLY + 1.8}" r="1.5" fill="{HILITE}"/>
  <circle cx="{CLX + 10}" cy="{CLY + 1.8}" r="1.5" fill="{HILITE}"/>
</g>
'''

# Starburst element for bonk impact
bonk_star_markup = f'''
<!-- Dramatic Bonk Impact Flash Starburst on B's head -->
<g id="bonk_star" filter="url(#glow)">
  <path d="{STAR}" fill="#ffffff" transform="scale(2.4)"/>
  <path d="{STAR}" fill="#ffd426" transform="scale(1.6) rotate(22)"/>
  <circle cx="0" cy="0" r="7" fill="#fff"/>
</g>
'''

# Minion A Markup: Stuart (tall, 1 goggle, parting hair, holds wrench)
minion_a_markup = f'''
<g class="minion_a">
  <g class="minion_a_inner" style="transform-origin: 0px 0px">
    <!-- Shadow under feet -->
    <ellipse cx="0" cy="0" rx="22" ry="4.5" fill="#000000" opacity="0.65"/>

    <!-- Black Shoes -->
    <path d="M-13,-2 C-13,-7 -20,-7 -20,-2 C-20,1 -12,1 -13,-2 Z" fill="#11151c"/>
    <path d="M13,-2 C13,-7 20,-7 20,-2 C20,1 12,1 13,-2 Z" fill="#11151c"/>

    <!-- Left Arm & Heavy Wrench (swings left at B) -->
    <g class="m_a_arm_l" style="transform-origin: -21px -50px">
      <!-- Arm -->
      <path d="M-21,-50 Q-32,-42 -30,-28" stroke="#f5c227" stroke-width="8" stroke-linecap="round" fill="none"/>
      <!-- Black Glove -->
      <circle cx="-30" cy="-27" r="5.5" fill="#11151c"/>
      <!-- Heavy Industrial Wrench -->
      <g transform="translate(-30,-27)">
        <rect x="-3" y="-2" width="6" height="30" rx="1.5" fill="url(#silver_rim)" stroke="#333" stroke-width="0.8"/>
        <!-- Wrench Head -->
        <path d="M-9,26 L9,26 L9,38 L3,38 L3,31 L-3,31 L-3,38 L-9,38 Z" fill="url(#silver_rim)" stroke="#333" stroke-width="0.8"/>
      </g>
    </g>

    <!-- Right Arm (pulls switch lever) -->
    <g class="m_a_arm_r" style="transform-origin: 21px -50px">
      <!-- Arm -->
      <path d="M21,-50 Q32,-42 30,-28" stroke="#f5c227" stroke-width="8" stroke-linecap="round" fill="none"/>
      <!-- Black Glove -->
      <circle cx="30" cy="-27" r="5.5" fill="#11151c"/>
    </g>

    <!-- Capsule Yellow Body (Stuart: height=84, width=44) -->
    <rect x="-22" y="-76" width="44" height="66" rx="22" fill="url(#minion_body_a)"/>

    <!-- Blue Denim Overalls -->
    <path d="M-22,-28 Q0,-22 22,-28 L22,-8 C22,0 12,2 0,2 C-12,2 -22,0 -22,-8 Z" fill="url(#overall_blue)"/>
    <!-- Bib front -->
    <rect x="-14" y="-40" width="28" height="18" rx="2" fill="url(#overall_blue)"/>
    <!-- Shoulder Straps with Silver Buttons -->
    <path d="M-20,-48 L-13,-36" stroke="#244d85" stroke-width="4.5" stroke-linecap="round"/>
    <circle cx="-13" cy="-36" r="1.8" fill="#ced8e6"/>
    <circle cx="-13" cy="-36" r="0.8" fill="#111"/>
    <path d="M20,-48 L13,-36" stroke="#244d85" stroke-width="4.5" stroke-linecap="round"/>
    <circle cx="13" cy="-36" r="1.8" fill="#ced8e6"/>
    <circle cx="13" cy="-36" r="0.8" fill="#111"/>
    <!-- Center Pocket with Gru Emblem -->
    <path d="M-7,-30 H7 V-20 Q7,-17 0,-17 Q-7,-17 -7,-20 Z" fill="#1a3d6e" stroke="#142e54" stroke-width="0.8"/>
    <circle cx="0" cy="-24" r="3.2" fill="#11151c"/>
    <polygon points="0,-25.5 1.8,-23 -1.8,-23" fill="#ced8e6"/>

    <!-- Goggle Strap -->
    <rect x="-22.5" y="-64" width="45" height="7.5" fill="#11151c" rx="1.5"/>

    <!-- Single Big Goggle (Stuart) -->
    <g transform="translate(0, -60)">
      <circle cx="0" cy="0" r="15.5" fill="url(#silver_rim)" stroke="#384353" stroke-width="1"/>
      <circle cx="0" cy="0" r="12" fill="#1a222d"/>
      <circle cx="0" cy="0" r="10.5" fill="#f8f9fa"/>
      <!-- Pupil with animation -->
      <g class="m_a_pupil">
        <!-- Brown Iris -->
        <circle cx="0" cy="0" r="5.2" fill="#6d411b"/>
        <!-- Pupil -->
        <circle cx="0" cy="0" r="2.8" fill="#000000"/>
        <!-- Catchlight shine -->
        <circle cx="1.5" cy="-1.5" r="1.4" fill="#ffffff"/>
      </g>
      <!-- Glass reflection highlight -->
      <path d="M-7,-7 A10,10 0 0,1 7,-7" stroke="#ffffff" stroke-width="1.2" fill="none" opacity="0.6"/>
    </g>

    <!-- Parted Strands of Hair -->
    <path d="M-6,-76 Q-4,-83 -8,-86" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    <path d="M-2,-76 Q0,-84 -3,-88" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    <path d="M2,-76 Q0,-84 3,-88" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    <path d="M6,-76 Q4,-83 8,-86" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>

    <!-- Smug / Cheerful Mouth -->
    <path d="M-8,-44 Q0,-38 8,-44" stroke="#4a3000" stroke-width="2" stroke-linecap="round" fill="none"/>
  </g>
</g>
'''

# Minion B Markup: Bob (short, 2 goggles with green & brown heterochromia, sprout hair)
minion_b_markup = f'''
<g class="minion_b">
  <g class="minion_b_inner" style="transform-origin: 0px 0px">
    <!-- Shadow under feet -->
    <ellipse cx="0" cy="0" rx="20" ry="4" fill="#000000" opacity="0.65"/>

    <!-- Running Legs -->
    <g class="m_b_l1" style="transform-origin: -8px -6px">
      <path d="M-8,-4 C-8,-9 -15,-9 -15,-4 C-15,-1 -7,-1 -8,-4 Z" fill="#11151c"/>
    </g>
    <g class="m_b_l2" style="transform-origin: 8px -6px">
      <path d="M8,-4 C8,-9 15,-9 15,-4 C15,-1 7,-1 8,-4 Z" fill="#11151c"/>
    </g>

    <!-- Left Arm -->
    <g class="m_b_arm_l" style="transform-origin: -21px -40px">
      <path d="M-21,-40 Q-30,-32 -26,-18" stroke="#f5c227" stroke-width="7" stroke-linecap="round" fill="none"/>
      <circle cx="-26" cy="-17" r="5" fill="#11151c"/>
    </g>

    <!-- Right Arm -->
    <g class="m_b_arm_r" style="transform-origin: 21px -40px">
      <path d="M21,-40 Q30,-32 26,-18" stroke="#f5c227" stroke-width="7" stroke-linecap="round" fill="none"/>
      <circle cx="26" cy="-17" r="5" fill="#11151c"/>
    </g>

    <!-- Capsule Yellow Body (Bob: height=68, width=44) -->
    <rect x="-22" y="-64" width="44" height="56" rx="22" fill="url(#minion_body_b)"/>

    <!-- Blue Denim Overalls -->
    <path d="M-22,-24 Q0,-18 22,-24 L22,-6 C22,0 12,2 0,2 C-12,2 -22,0 -22,-6 Z" fill="url(#overall_blue)"/>
    <!-- Bib front -->
    <rect x="-13" y="-34" width="26" height="15" rx="2" fill="url(#overall_blue)"/>
    <!-- Straps -->
    <path d="M-19,-40 L-12,-30" stroke="#244d85" stroke-width="4" stroke-linecap="round"/>
    <circle cx="-12" cy="-30" r="1.6" fill="#ced8e6"/>
    <path d="M19,-40 L12,-30" stroke="#244d85" stroke-width="4" stroke-linecap="round"/>
    <circle cx="12" cy="-30" r="1.6" fill="#ced8e6"/>
    <!-- Front Pocket -->
    <path d="M-6,-24 H6 V-16 Q6,-13 0,-13 Q-6,-13 -6,-16 Z" fill="#1a3d6e" stroke="#142e54" stroke-width="0.8"/>
    <circle cx="0" cy="-19" r="2.6" fill="#11151c"/>

    <!-- Goggle Strap -->
    <rect x="-22.5" y="-55" width="45" height="7" fill="#11151c" rx="1.5"/>

    <!-- Dual Goggles (Bob: Heterochromia - Green Left, Brown Right) -->
    <!-- Left Eye (Green iris) -->
    <g transform="translate(-10, -51)">
      <circle cx="0" cy="0" r="11" fill="url(#silver_rim)" stroke="#384353" stroke-width="0.8"/>
      <circle cx="0" cy="0" r="8.5" fill="#1a222d"/>
      <circle cx="0" cy="0" r="7.5" fill="#f8f9fa"/>
      <g class="m_b_pupil">
        <circle cx="0" cy="0" r="3.8" fill="#387a32"/>
        <circle cx="0" cy="0" r="2" fill="#000000"/>
        <circle cx="1" cy="-1" r="1" fill="#ffffff"/>
      </g>
    </g>
    <!-- Right Eye (Brown iris) -->
    <g transform="translate(10, -51)">
      <circle cx="0" cy="0" r="11" fill="url(#silver_rim)" stroke="#384353" stroke-width="0.8"/>
      <circle cx="0" cy="0" r="8.5" fill="#1a222d"/>
      <circle cx="0" cy="0" r="7.5" fill="#f8f9fa"/>
      <g class="m_b_pupil">
        <circle cx="0" cy="0" r="3.8" fill="#6d411b"/>
        <circle cx="0" cy="0" r="2" fill="#000000"/>
        <circle cx="1" cy="-1" r="1" fill="#ffffff"/>
      </g>
    </g>

    <!-- Sprout Hair Strands -->
    <path d="M-2,-64 Q-3,-70 -6,-72" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    <path d="M0,-64 Q0,-71 0,-74" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    <path d="M2,-64 Q3,-70 6,-72" stroke="#1a1c20" stroke-width="1.5" stroke-linecap="round" fill="none"/>

    <!-- Mouth -->
    <path d="M-6,-37 Q0,-32 6,-37" stroke="#4a3000" stroke-width="1.8" stroke-linecap="round" fill="none"/>

    <!-- Large Bump / Knot on head (bonk reaction) -->
    <g class="m_b_bump" style="transform-origin: 0px -64px">
      <ellipse cx="-2" cy="-67" rx="8" ry="6" fill="#f05454" stroke="#991b1b" stroke-width="1"/>
      <path d="M-6,-68 Q-2,-70 2,-68" stroke="#ffe0e0" stroke-width="1" fill="none"/>
      <!-- Band-aid / cross -->
      <line x1="-5" y1="-67" x2="1" y2="-67" stroke="#fff" stroke-width="1.2"/>
      <line x1="-2" y1="-70" x2="-2" y2="-64" stroke="#fff" stroke-width="1.2"/>
    </g>

    <!-- Orbiting Comic Stars (bonk reaction) -->
    <g class="m_b_stars" style="transform-origin: 0px -74px">
      <path d="{STAR}" fill="#ffd426" stroke="#fff" stroke-width="0.8" transform="translate(-18,-74) scale(0.65)"/>
      <path d="{STAR}" fill="#ffd426" stroke="#fff" stroke-width="0.8" transform="translate(18,-74) scale(0.65)"/>
      <path d="{STAR}" fill="#ffec6e" stroke="#fff" stroke-width="0.8" transform="translate(0,-86) scale(0.75)"/>
    </g>
  </g>
</g>
'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
<defs>
  <radialGradient id="vig" cx="50%" cy="45%" r="65%">
    <stop offset="0%" stop-color="#0b1021" stop-opacity="0"/>
    <stop offset="60%" stop-color="#05070f" stop-opacity=".55"/>
    <stop offset="100%" stop-color="#020308" stop-opacity=".95"/>
  </radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="12" cy="12" r="1.1" fill="{DOT}"/>
  </pattern>
  <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{HILITE}"/>
    <stop offset="35%" stop-color="{GOLD}"/>
    <stop offset="100%" stop-color="{EDGE}"/>
  </linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="45%" stop-color="#ffffff" stop-opacity=".15"/>
    <stop offset="50%" stop-color="#ffffff" stop-opacity=".85"/>
    <stop offset="55%" stop-color="#ffffff" stop-opacity=".15"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>

  <!-- Minion Gradients -->
  <linearGradient id="minion_body_a" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ffe24a"/>
    <stop offset="50%" stop-color="#f5c227"/>
    <stop offset="100%" stop-color="#cc9b14"/>
  </linearGradient>
  <linearGradient id="minion_body_b" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#ffe459"/>
    <stop offset="50%" stop-color="#f5c227"/>
    <stop offset="100%" stop-color="#cc9b14"/>
  </linearGradient>
  <linearGradient id="overall_blue" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#3b72bd"/>
    <stop offset="60%" stop-color="#244d85"/>
    <stop offset="100%" stop-color="#17355e"/>
  </linearGradient>
  <linearGradient id="silver_rim" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#ffffff"/>
    <stop offset="30%" stop-color="#ced4da"/>
    <stop offset="70%" stop-color="#868e96"/>
    <stop offset="100%" stop-color="#495057"/>
  </linearGradient>
  <radialGradient id="red_knob" cx="35%" cy="35%" r="65%">
    <stop offset="0%" stop-color="#ff6b6b"/>
    <stop offset="40%" stop-color="#e03131"/>
    <stop offset="100%" stop-color="#731111"/>
  </radialGradient>
  <radialGradient id="lamp_core" cx="40%" cy="40%" r="60%">
    <stop offset="0%" stop-color="#ffffff"/>
    <stop offset="30%" stop-color="#fff8d6"/>
    <stop offset="70%" stop-color="#ffd43b"/>
    <stop offset="100%" stop-color="#f59f00"/>
  </radialGradient>
  <radialGradient id="lamp_bloom" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffd43b" stop-opacity="0.95"/>
    <stop offset="35%" stop-color="#fcc419" stop-opacity="0.45"/>
    <stop offset="70%" stop-color="#fab005" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="#fab005" stop-opacity="0"/>
  </radialGradient>

  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="big" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="16"/>
  </filter>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.5"/>
  </filter>
  <linearGradient id="reflfade" x1="0" y1="{BASE + 6}" x2="0" y2="{FLOOR}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff" stop-opacity=".7"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="reflmask" maskUnits="userSpaceOnUse" x="0" y="{BASE + 6}" width="{W}" height="{FLOOR - BASE}">
    <rect x="0" y="{BASE + 6}" width="{W}" height="{FLOOR - BASE}" fill="url(#reflfade)"/>
  </mask>
  <linearGradient id="botfade" x1="0" y1="{FLOOR}" x2="0" y2="{H - 4}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="botmask" maskUnits="userSpaceOnUse" x="0" y="{FLOOR}" width="{W}" height="{H - FLOOR}">
    <rect x="0" y="{FLOOR + 2}" width="{W}" height="{H - FLOOR}" fill="url(#botfade)"/></mask>
  <mask id="namemask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{''.join(mask_paths)}</mask>
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
<g id="reflg" mask="url(#reflmask)"><g transform="translate(0,{2 * BASE + 8}) scale(1,-1)" opacity=".5" filter="url(#soft)">{''.join(refl_paths)}</g></g>
<g id="lit" filter="url(#glow)">{''.join(mid_paths)}</g>
<g mask="url(#namemask)"><rect id="sheen" x="0" y="{NY - 10}" width="200" height="{6 * U + 20}" fill="url(#shine)" transform="translate(-260 0)"/></g>
<g id="padsg">{''.join(pads)}</g>
{pcb_floor}
{crown}
{switch_apparatus}
{bonk_star_markup}
{minion_a_markup}
{minion_b_markup}
</svg>'''

target = sys.argv[1] if len(sys.argv) > 1 else 'assets/traces.svg'
open(target, 'w').write(svg)
print(f"Generated {target}: size {len(svg)//1024} KB")
