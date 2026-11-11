# Generates an animated IBM 3270-style green-screen SVG for the GitHub profile.
import sys
from html import escape
W, FS, CW, LH, X0 = 860, 15, 9.0, 24, 28
BAN = [l.rstrip() for l in open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'banner.txt'), encoding='utf-8').read().splitlines() if l.strip()]
BC, BR = 13, 13                                       # banner cell width/height in px
BW = max(map(len, BAN)) * BC; BX, BY = (W - BW) / 2, 66
Y0 = BY + len(BAN) * BR + 46   # CW = monospace char width at FS (0.6em)
G, DIM, AMB, WHT = '#33ff66', '#1f9e45', '#ffb000', '#d9ffe4'
script = [  # (kind, text) ; kind: cmd = typed command, out = printed output
 ('sys', 'IKJ56455I ATILADE LOGON IN PROGRESS'),
 ('sys', 'READY'),
 ('cmd', 'WHOAMI'),
 ('out', 'ATILADE OKE  //  ELECTRICAL ENGINEERING @ UNIVERSITY OF MANCHESTER'),
 ('cmd', 'ROLE'),
 ('out', 'ANALYST @ ION'),
 ('cmd', 'RANK --PROGRAM IBMZ'),
 ('hi',  '#1 IBM Z STUDENT AMBASSADOR WORLDWIDE  (2025-26)'),
 ('cmd', 'HACKATHONS --WINS'),
 ('hi',  '8X WINNER  //  1ST WORLDS LONDON  //  1ST AI AGENTS FOR ACCESSIBILITY'),
 ('cmd', 'COMMUNITY'),
 ('out', 'IBM Z SOCIETY: 2 FOUNDERS -> 50 MEMBERS, 15+ WORKSHOPS, 5 EVENTS'),
 ('cmd', 'STATUS'),
 ('out', 'BUILDING THE FUTURE'),
]
H = Y0 + LH * (len(script) + 1) + 46
css, body, t = [], [], 0.6
ban = []
for r, row in enumerate(BAN):                          # rows print top-down like a line printer
    cells = []
    for c, ch in enumerate(row):
        x, y = BX + c * BC, BY + r * BR
        if ch == '█':
            cells.append(f'<rect x="{x:.1f}" y="{y}" width="{BC-1}" height="{BR-1}"/>')
        elif ch in '═╗╔╚╝':
            cells.append(f'<rect class="sh" x="{x:.1f}" y="{y+BR/2-2:.1f}" width="{BC}" height="3"/>')
        elif ch == '║':
            cells.append(f'<rect class="sh" x="{x+BC/2-2:.1f}" y="{y}" width="3" height="{BR}"/>')
    css.append(f'.b{r}{{animation:on2 .18s {t:.2f}s both}}')
    ban.append(f'<g class="b{r}">' + ''.join(cells) + '</g>')
    t += 0.14
css.append('@keyframes on2{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}')
t += 0.5
for i, (kind, text) in enumerate(script):
    y = Y0 + i * LH
    prefix = '> ' if kind == 'cmd' else ('  ' if kind in ('out', 'hi') else '')
    line = prefix + text
    n = len(line)
    color = {'sys': DIM, 'cmd': WHT, 'out': G, 'hi': AMB}[kind]
    # commands type char-by-char; output appears near-instantly like a real terminal
    dur = n * 0.045 if kind == 'cmd' else 0.25
    css.append(f'#c{i} rect{{animation:t{i} {dur:.2f}s steps({n}) {t:.2f}s both}}'
               f'@keyframes t{i}{{from{{width:0}}to{{width:{(n+1)*CW*1.06:.0f}px}}}}')
    body.append(f'<clipPath id="c{i}"><rect x="{X0}" y="{y-FS}" height="{LH}" width="0"/></clipPath>'
                f'<text x="{X0}" y="{y}" fill="{color}" clip-path="url(#c{i})" xml:space="preserve">{escape(line)}</text>')
    t += dur + (0.35 if kind == 'cmd' else 0.5)
cy = Y0 + len(script) * LH
css.append(f'#cur{{animation:show 0s {t:.2f}s both,blink 1s steps(1) {t:.2f}s infinite}}'
           '@keyframes show{from{opacity:0}to{opacity:1}}@keyframes blink{50%{opacity:0}}')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Atilade Oke: Analyst at ION, number 1 IBM Z Student Ambassador worldwide, 8x hackathon winner">
<defs>
 <filter id="glow" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="bglow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".28"/></pattern>
 <radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".75"/></radialGradient>
 <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}" stop-opacity=".07"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient>
</defs>
<style>
 .sh{{fill:#0f5c28}}
 text{{font-family:'IBM Plex Mono','SF Mono',Menlo,'Cascadia Mono',Consolas,'DejaVu Sans Mono',monospace;font-size:{FS}px;font-weight:600}}
 #scr{{animation:on .5s ease-out both,flick 6s 1s infinite}}
 @keyframes on{{0%{{transform:scaleY(.005);opacity:0;filter:brightness(4)}}60%{{transform:scaleY(1);opacity:1;filter:brightness(2)}}100%{{transform:scaleY(1);filter:none}}}}
 @keyframes flick{{0%,96%,100%{{opacity:1}}97%{{opacity:.86}}98%{{opacity:1}}99%{{opacity:.92}}}}
 #beam{{animation:roll 5s linear infinite}}
 @keyframes roll{{from{{transform:translateY(-120px)}}to{{transform:translateY({H}px)}}}}
 {''.join(css)}
</style>
<rect width="{W}" height="{H}" rx="18" fill="#1b1d1c"/>
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="12" fill="#030a05"/>
<g id="scr" style="transform-origin:50% 50%" filter="url(#glow)">
 <text x="{X0}" y="38" fill="{DIM}" xml:space="preserve">z/OS 3.1  TSO/E  ===  ATILADE.OKE  ===  IBM Z</text>
 <line x1="{X0}" y1="48" x2="{W-X0}" y2="48" stroke="{DIM}" stroke-width="1" stroke-dasharray="6 4"/>
 <g fill="{G}" filter="url(#bglow)">{''.join(ban)}</g>
 <text x="{W/2}" y="{BY + len(BAN)*BR + 22}" fill="{DIM}" text-anchor="middle" xml:space="preserve">ELECTRICAL ENGINEER  ·  ANALYST  ·  BUILDER</text>
 {''.join(body)}
 <rect id="cur" x="{X0}" y="{cy-FS+2}" width="{CW+1}" height="{FS+2}" fill="{G}" opacity="0"/>
 <line x1="{X0}" y1="{H-40}" x2="{W-X0}" y2="{H-40}" stroke="{DIM}" stroke-width="1" stroke-dasharray="6 4"/>
 <text x="{X0}" y="{H-20}" fill="{DIM}" xml:space="preserve">MA  A     ATILADE.UK                                       {len(script)+1:03d}/001</text>
</g>
<rect id="beam" x="10" y="0" width="{W-20}" height="120" fill="url(#beam)"/>
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="12" fill="url(#scan)"/>
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="12" fill="url(#vig)"/>
</svg>'''
open(sys.argv[1], 'w').write(svg)
print('total animation', round(t, 1), 's; height', H)
