#!/usr/bin/env python3
"""Tekent banner.svg: de zelfdeterminatietheorie in één beeld.

Links de drie basisbehoeften (autonomie, competentie, verbondenheid) die samen
de schakelaar omzetten. Onderaan het continuüm van Ryan & Deci (2000): van
amotivatie, via vier vormen van externe motivatie, naar intrinsieke motivatie.

De curve is een illustratie, geen gemeten model: een logistische lijn die laat
zien dat gedrag steeds meer "van jezelf" wordt naarmate de behoeften vervuld
raken.

Gebruik:  python3 scripts/banner.py   (alleen de standaardbibliotheek)
"""

from __future__ import annotations

import base64
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1280, 384

# BringOn-kleuren
INK = "#1A0A38"
DEEP = "#2D1151"
PAARS = "#9A37F4"
LAVENDEL = "#E4C8FD"
PAPIER = "#FAF4FF"
GEDEMPT = "#8F7BB0"

# De drie basisbehoeften, als hoek op de cirkel rond de schakelaar.
BEHOEFTEN = [("autonomie", -90), ("competentie", 150), ("verbondenheid", 30)]

# Het continuüm van zelfdeterminatie, van links naar rechts.
CONTINUUM = [
    "amotivatie",
    "extern",
    "introjectie",
    "identificatie",
    "integratie",
    "intrinsiek",
]

CX, CY, STRAAL = 215, 186, 100  # de driehoek van behoeften
X0, X1 = 470, 1215  # het continuüm
Y_LAAG, Y_HOOG = 304, 246


def font_face(naam: str, bestand: str, gewicht: int) -> str:
    data = base64.b64encode((ASSETS / "fonts" / bestand).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{naam}';font-weight:{gewicht};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
    )


def internalisatie(u: float) -> float:
    """Logistische curve: 0 = volledig van buitenaf, 1 = volledig van jezelf."""
    return 1 / (1 + math.exp(-(u * 10 - 5)))


def punt(u: float) -> tuple[float, float]:
    x = X0 + u * (X1 - X0)
    y = Y_LAAG - internalisatie(u) * (Y_LAAG - Y_HOOG)
    return round(x, 1), round(y, 1)


def curve() -> str:
    punten = [punt(i / 60) for i in range(61)]
    return "M" + " L".join(f"{x},{y}" for x, y in punten)


def echo() -> str:
    """Echo, de mascotte, ongewijzigd ingevoegd."""
    svg = (ASSETS / "echo-waving.svg").read_text()
    binnen = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    hoogte = 178
    breedte = hoogte * 692.1 / 845
    return (
        f'<svg x="{W - breedte - 44:.0f}" y="30" width="{breedte:.0f}" height="{hoogte}" '
        f'viewBox="0 0 692.1 845">{binnen}</svg>'
    )


def behoeften() -> str:
    delen = []
    for i, (naam, hoek) in enumerate(BEHOEFTEN):
        r = math.radians(hoek)
        x, y = CX + STRAAL * math.cos(r), CY + STRAAL * math.sin(r)
        # Lijn van de behoefte naar de schakelaar; de streepjes stromen naar binnen.
        delen.append(
            f'<line class="stroom" x1="{x:.1f}" y1="{y:.1f}" x2="{CX}" y2="{CY}" '
            f'style="animation-delay:{-i * 0.6:.1f}s"/>'
        )
        delen.append(
            f'<circle class="pols" cx="{x:.1f}" cy="{y:.1f}" r="9" '
            f'style="animation-delay:{i * 0.9:.1f}s"/>'
        )
        delen.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{LAVENDEL}"/>')
        if hoek == -90:
            lx, ly, anker = x, y - 20, "middle"
        elif hoek > 90:
            lx, ly, anker = x - 4, y + 30, "middle"
        else:
            lx, ly, anker = x + 4, y + 30, "middle"
        delen.append(
            f'<text class="mono" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anker}">{naam}</text>'
        )
    return "\n".join(delen)


def schakelaar() -> str:
    b, h = 84, 46
    x, y = CX - b / 2, CY - h / 2
    return (
        f'<rect x="{x - 10}" y="{y - 10}" width="{b + 20}" height="{h + 20}" rx="{(h + 20) / 2}" fill="{INK}"/>'
        f'<rect class="baan" x="{x}" y="{y}" width="{b}" height="{h}" rx="{h / 2}"/>'
        f'<circle class="knop" cx="{x + b - h / 2}" cy="{CY}" r="{h / 2 - 6}" fill="#fff"/>'
    )


def continuum() -> str:
    delen = [f'<path d="{curve()}" fill="none" stroke="url(#verloop)" stroke-width="2.5" stroke-linecap="round"/>']
    n = len(CONTINUUM)
    for i, naam in enumerate(CONTINUUM):
        u = i / (n - 1)
        x, y = punt(u)
        kleur = PAARS if i == n - 1 else LAVENDEL
        dekking = 0.45 + 0.55 * u
        delen.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{kleur}" opacity="{dekking:.2f}"/>')
        anker = "start" if i == 0 else "end" if i == n - 1 else "middle"
        delen.append(
            f'<text class="mono klein" x="{x}" y="{Y_LAAG + 26}" text-anchor="{anker}" '
            f'opacity="{dekking:.2f}">{naam}</text>'
        )
    delen.append(f'<circle class="reiziger" r="6" fill="{PAPIER}"/>')
    return "\n".join(delen)


def banner() -> str:
    stijl = f"""
{font_face("Space Grotesk", "SpaceGrotesk-latin.woff2", 600)}
{font_face("DM Mono", "DMMono-latin.woff2", 400)}
.kop{{font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;fill:#fff;letter-spacing:-1.5px}}
.sub{{font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;fill:{LAVENDEL}}}
.mono{{font-family:'DM Mono',ui-monospace,monospace;font-size:14px;fill:{LAVENDEL}}}
.klein{{font-size:12.5px}}
.motto{{font-size:12px;letter-spacing:3.5px;fill:{GEDEMPT}}}
.stroom{{stroke:{PAARS};stroke-width:2;stroke-dasharray:3 9;stroke-linecap:round;animation:stroom 2.4s linear infinite}}
.pols{{fill:{PAARS};opacity:.35;transform-box:fill-box;transform-origin:center;animation:pols 2.7s ease-out infinite}}
.baan{{fill:{PAARS};animation:aan .6s ease-out 1.1s backwards}}
.knop{{animation:schuif .32s ease-out 1.1s backwards}}
.reiziger{{offset-path:path('{curve()}');offset-distance:0%;animation:reis 11s ease-in-out infinite}}
@keyframes stroom{{to{{stroke-dashoffset:-24}}}}
@keyframes pols{{0%{{transform:scale(1);opacity:.45}}70%,100%{{transform:scale(2.4);opacity:0}}}}
@keyframes aan{{from{{fill:#4B2A7E}}}}
@keyframes schuif{{from{{transform:translateX(-38px)}}}}
@keyframes reis{{0%{{offset-distance:0%;opacity:0}}6%{{opacity:1}}88%{{offset-distance:100%;opacity:1}}100%{{offset-distance:100%;opacity:0}}}}
@media (prefers-reduced-motion:reduce){{
  .stroom,.pols,.reiziger{{animation:none}}
  .pols{{opacity:0}}
  .reiziger{{offset-distance:100%}}
  .baan,.knop{{animation:none}}
}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="titel omschrijving">
<title id="titel">Jesse Breekveldt bouwt aan BringOn</title>
<desc id="omschrijving">De zelfdeterminatietheorie: autonomie, competentie en verbondenheid zetten de schakelaar om. Daaronder het continuüm van amotivatie naar intrinsieke motivatie: van moeten naar willen.</desc>
<defs>
<style>{stijl}</style>
<radialGradient id="gloed-links" cx="{CX}" cy="{CY}" r="330" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{PAARS}" stop-opacity=".42"/><stop offset="1" stop-color="{PAARS}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="gloed-rechts" cx="{W - 110}" cy="110" r="360" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{PAARS}" stop-opacity=".30"/><stop offset="1" stop-color="{PAARS}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="verloop" x1="{X0}" x2="{X1}" y1="0" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{GEDEMPT}" stop-opacity=".5"/><stop offset=".6" stop-color="{LAVENDEL}"/><stop offset="1" stop-color="{PAARS}"/>
</linearGradient>
<clipPath id="kader"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#kader)">
<rect width="{W}" height="{H}" fill="{INK}"/>
<rect width="{W}" height="{H}" fill="url(#gloed-links)"/>
<rect width="{W}" height="{H}" fill="url(#gloed-rechts)"/>
{behoeften()}
{schakelaar()}
<text class="kop" x="{X0}" y="128" font-size="68">Jesse Breekveldt</text>
<text class="sub" x="{X0 + 2}" y="170" font-size="25">Bouwt aan BringOn</text>
{echo()}
{continuum()}
<text class="mono motto" x="{X1}" y="{H - 18}" text-anchor="end">VAN MOETEN NAAR WILLEN</text>
</g>
</svg>
"""


if __name__ == "__main__":
    doel = ROOT / "banner.svg"
    doel.write_text(banner())
    print(f"{doel.relative_to(ROOT)} geschreven ({doel.stat().st_size / 1024:.0f} kB)")
