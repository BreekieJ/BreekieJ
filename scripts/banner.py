#!/usr/bin/env python3
"""Tekent banner.svg: het vlindereffect in één beeld.

Twee lijnen volgen dezelfde regels (de vergelijkingen van Lorenz, 1963) en
beginnen bijna op dezelfde plek: het verschil is één duizendste. Eerst lopen ze
gelijk op, daarna kiest elk een eigen weg. Rechtsonder staat de afstand tussen
de twee in de tijd.

De banen zijn echt uitgerekend (Runge-Kutta, vierde orde), niet getekend.

Gebruik:  python3 scripts/banner.py   (alleen de standaardbibliotheek)
"""

from __future__ import annotations

import base64
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1280, 384

# Kleuren: nachtblauw met helder blauw en goud
INK = "#0A1430"
BLAUW = "#2F6BFF"
BLAUW_LICHT = "#5AA9FF"
GOUD = "#F6B91E"
IJS = "#C9DDFF"
PAPIER = "#F2F7FF"
GEDEMPT = "#7D90B8"

# Lorenz (1963)
SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
STAP = 0.005  # tijdstap van de berekening
INLOOP = 20.0  # eerst naar de vlinder toe lopen, dat stuk tonen we niet
DUUR = 14.25  # zoveel tijd laat de banner zien; dan staan de twee elk op een eigen vleugel
VERSCHIL = 0.001  # het kleine verschil aan het begin

# De animatie: tekenen, even laten staan, opnieuw.
LOOPTIJD = 22  # seconden
TEKEN_DEEL = 0.84  # dit deel van de looptijd wordt er getekend
BEELDEN = 120  # aantal tussenstanden in de animatie

# Waar de vlinder staat (x van Lorenz naar rechts, z omhoog).
VLINDER = (48, 30, 400, 330)  # links, boven, breedte, hoogte
# Waar de grafiek van de afstand staat.
X0, X1, Y_LAAG, Y_HOOG = 470, 1215, 318, 250

Punt3 = tuple[float, float, float]


def lorenz(p: Punt3) -> Punt3:
    x, y, z = p
    return SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z


def stap(p: Punt3, h: float) -> Punt3:
    def plus(a: Punt3, b: Punt3, f: float) -> Punt3:
        return a[0] + b[0] * f, a[1] + b[1] * f, a[2] + b[2] * f

    k1 = lorenz(p)
    k2 = lorenz(plus(p, k1, h / 2))
    k3 = lorenz(plus(p, k2, h / 2))
    k4 = lorenz(plus(p, k3, h))
    return (
        p[0] + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
        p[1] + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
        p[2] + h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]),
    )


def baan(begin: Punt3) -> list[Punt3]:
    punten = [begin]
    for _ in range(round(DUUR / STAP)):
        punten.append(stap(punten[-1], STAP))
    return punten


def twee_banen() -> tuple[list[Punt3], list[Punt3]]:
    p: Punt3 = (1.0, 1.0, 1.0)
    for _ in range(round(INLOOP / STAP)):
        p = stap(p, STAP)
    return baan(p), baan((p[0], p[1], p[2] + VERSCHIL))


def naar_scherm(p: Punt3) -> tuple[float, float]:
    links, boven, breedte, hoogte = VLINDER
    x = links + (p[0] + 21) / 42 * breedte
    y = boven + hoogte - (p[2] - 2) / 48 * hoogte
    return x, y


def lengtes(punten: list[tuple[float, float]]) -> list[float]:
    """Afgelegde weg tot elk punt, als deel van het geheel (0 tot 1)."""
    som = [0.0]
    for (x0, y0), (x1, y1) in zip(punten, punten[1:]):
        som.append(som[-1] + math.hypot(x1 - x0, y1 - y0))
    return [s / som[-1] for s in som]


def pad(punten: list[tuple[float, float]]) -> str:
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in punten)


def keyframes(naam: str, deel: list[float]) -> str:
    """De lijn groeit en de stip loopt mee, precies in de tijd van de berekening."""
    regels = []
    n = len(deel) - 1
    for i in range(BEELDEN + 1):
        f = deel[round(i / BEELDEN * n)]
        procent = i / BEELDEN * TEKEN_DEEL * 100
        regels.append(
            f"{procent:.2f}%{{stroke-dashoffset:{1 - f:.4f};offset-distance:{f * 100:.2f}%;opacity:1}}"
        )
    regels.append("96%{stroke-dashoffset:0;offset-distance:100%;opacity:1}")
    regels.append("100%{stroke-dashoffset:0;offset-distance:100%;opacity:0}")
    return f"@keyframes {naam}{{{''.join(regels)}}}"


def font_face(naam: str, bestand: str, gewicht: int) -> str:
    data = base64.b64encode((ASSETS / "fonts" / bestand).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{naam}';font-weight:{gewicht};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
    )


def banner() -> str:
    a3, b3 = twee_banen()
    dun = 4  # elk vierde punt is genoeg voor een vloeiende lijn
    a = [naar_scherm(p) for p in a3[::dun]]
    b = [naar_scherm(p) for p in b3[::dun]]

    # De afstand tussen de twee banen, in de tijd.
    afstand = [math.dist(p, q) for p, q in zip(a3[::dun], b3[::dun])]
    top = max(afstand)
    n = len(afstand) - 1
    grafiek = [
        (X0 + i / n * (X1 - X0), Y_LAAG - d / top * (Y_LAAG - Y_HOOG))
        for i, d in enumerate(afstand)
    ]

    # Het moment waarop je het verschil voor het eerst echt ziet.
    splits = next(i for i, d in enumerate(afstand) if d > 0.06 * top)
    sx, sy = grafiek[splits]

    pad_a, pad_b, pad_g = pad(a), pad(b), pad(grafiek)
    tijd = f"{LOOPTIJD}s linear infinite"

    stijl = f"""
{font_face("Space Grotesk", "SpaceGrotesk-latin.woff2", 600)}
{font_face("DM Mono", "DMMono-latin.woff2", 400)}
.kop{{font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;fill:#fff;letter-spacing:-1.5px}}
.sub{{font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;fill:{IJS}}}
.mono{{font-family:'DM Mono',ui-monospace,monospace;font-size:12.5px;fill:{IJS}}}
.zacht{{fill:{GEDEMPT}}}
.motto{{font-size:12px;letter-spacing:3.5px;fill:{GEDEMPT}}}
.lijn{{fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:0}}
.stip{{offset-distance:100%;offset-rotate:0deg}}
.a{{animation:baan-a {tijd}}}
.b{{animation:baan-b {tijd}}}
.g{{animation:afstand {tijd}}}
.rand{{paint-order:stroke;stroke:{INK};stroke-width:5px;stroke-linejoin:round}}
.eind{{animation:eind {tijd}}}
@keyframes eind{{0%,{TEKEN_DEEL * 100 - 3:.0f}%{{opacity:0}}{TEKEN_DEEL * 100 + 1:.0f}%,96%{{opacity:1}}100%{{opacity:0}}}}
{keyframes("baan-a", lengtes(a))}
{keyframes("baan-b", lengtes(b))}
{keyframes("afstand", lengtes(grafiek))}
@media (prefers-reduced-motion:reduce){{.a,.b,.g,.eind{{animation:none}}}}
"""
    bx, by = a[0]
    (ax_, ay_), (bx_, by_) = a[-1], b[-1]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="titel omschrijving">
<title id="titel">Jesse Breekveldt</title>
<desc id="omschrijving">Het vlindereffect: twee lijnen beginnen bijna op dezelfde plek en volgen dezelfde regels. Eerst lopen ze gelijk op, daarna komt elk ergens anders uit. Klein verschil, andere uitkomst.</desc>
<defs>
<style>{stijl}</style>
<radialGradient id="gloed-links" cx="250" cy="190" r="340" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{BLAUW}" stop-opacity=".34"/><stop offset="1" stop-color="{BLAUW}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="gloed-rechts" cx="{W - 110}" cy="110" r="360" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{BLAUW}" stop-opacity=".30"/><stop offset="1" stop-color="{BLAUW}" stop-opacity="0"/>
</radialGradient>
<clipPath id="kader"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#kader)">
<rect width="{W}" height="{H}" fill="{INK}"/>
<rect width="{W}" height="{H}" fill="url(#gloed-links)"/>
<rect width="{W}" height="{H}" fill="url(#gloed-rechts)"/>

<path class="lijn a" pathLength="1" d="{pad_a}" stroke="{GOUD}" stroke-width="1.6"/>
<path class="lijn b" pathLength="1" d="{pad_b}" stroke="{BLAUW_LICHT}" stroke-width="1.6"/>
<circle cx="{bx:.1f}" cy="{by:.1f}" r="3.5" fill="none" stroke="{GEDEMPT}" stroke-width="1.2"/>
<circle class="stip a" r="5" fill="{GOUD}" style="offset-path:path('{pad_a}')"/>
<circle class="stip b" r="5" fill="{BLAUW_LICHT}" style="offset-path:path('{pad_b}')"/>

<text class="mono rand" x="{bx - 10:.1f}" y="{by + 4:.1f}" text-anchor="end">zelfde begin</text>
<text class="mono rand eind" x="{ax_ + 11:.1f}" y="{ay_ + 4:.1f}">uitkomst 1</text>
<text class="mono rand eind" x="{bx_ + 11:.1f}" y="{by_ + 4:.1f}">uitkomst 2</text>

<text class="kop" x="{X0}" y="128" font-size="68">Jesse Breekveldt</text>
<text class="sub" x="{X0 + 2}" y="170" font-size="25">Klein verschil, andere uitkomst</text>

<line x1="{X0}" y1="{Y_LAAG}" x2="{X1}" y2="{Y_LAAG}" stroke="{GEDEMPT}" stroke-opacity=".35" stroke-width="1"/>
<line x1="{sx:.1f}" y1="{Y_LAAG}" x2="{sx:.1f}" y2="{Y_HOOG + 6}" stroke="{GEDEMPT}" stroke-opacity=".5" stroke-width="1" stroke-dasharray="2 5"/>
<path class="lijn g" pathLength="1" d="{pad_g}" stroke="{IJS}" stroke-width="2.2"/>
<circle class="stip g" r="5" fill="{IJS}" style="offset-path:path('{pad_g}')"/>
<text class="mono" x="{X0}" y="{Y_LAAG - 18}">verschil aan het begin: 0,001</text>
<text class="mono zacht" x="{sx - 10:.1f}" y="{Y_HOOG + 16}" text-anchor="end">hier gaan ze uit elkaar</text>
<text class="mono zacht" x="{X0}" y="{Y_LAAG + 22}">afstand tussen de twee lijnen</text>
<text class="mono motto" x="{X1}" y="{H - 18}" text-anchor="end">LORENZ, 1963</text>
</g>
</svg>
"""


if __name__ == "__main__":
    doel = ROOT / "banner.svg"
    doel.write_text(banner())
    print(f"{doel.relative_to(ROOT)} geschreven ({doel.stat().st_size / 1024:.0f} kB)")
