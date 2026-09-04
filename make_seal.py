#!/usr/bin/env python3
"""Печать восьми триграмм — анимированный SVG, нарисованный формулами.

ЗАЧЕМ ФОРМУЛАМИ. Спираль из полутора сотен точек, набранная руками, кривая: шаг гуляет, и это
видно на первом же витке. Здесь путь считается по уравнению Архимеда, а метки расставляются
делением круга — сдвинуть можно любой параметр, и рисунок останется правильным.

Вращение и цвет анимируются средствами самого SVG (SMIL), без CSS: картинка вставляется как
<img>, а там сторонний CSS-файл не подключить, и внутренний стиль иногда режут.

    python3 make_seal.py > seal.svg
"""

import math

SIZE = 380
C = SIZE / 2

CALM = "#2ea44f"       # печать держит
CHAKRA = "#ff6b1a"     # печать слабеет
EMBER = "#e8341c"
FAINT = "#1f6f3f"

SPIN_OUT = 42          # секунд на оборот внешнего кольца
SPIN_IN = 27           # внутреннее крутится в другую сторону
PULSE = 9              # период дыхания цвета


def spiral(turns=3.4, r_max=96, step=3):
    """Архимедова спираль от центра наружу."""
    pts = []
    total = int(turns * 360 / step)
    for i in range(total + 1):
        a = math.radians(i * step)
        r = r_max * (a / (turns * 2 * math.pi))
        pts.append(f"{C + r * math.cos(a - math.pi / 2):.2f},{C + r * math.sin(a - math.pi / 2):.2f}")
    return "M" + "L".join(pts)


def spokes(count, r1, r2, width, colour, opacity=1.0, offset=0.0):
    out = []
    for i in range(count):
        a = math.radians(offset + i * 360 / count)
        x1, y1 = C + r1 * math.cos(a), C + r1 * math.sin(a)
        x2, y2 = C + r2 * math.cos(a), C + r2 * math.sin(a)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                   f'stroke="{colour}" stroke-width="{width}" stroke-linecap="round" '
                   f'opacity="{opacity}"/>')
    return "".join(out)


def rotate(dur, reverse=False):
    a, b = (360, 0) if reverse else (0, 360)
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'from="{a} {C} {C}" to="{b} {C} {C}" dur="{dur}s" repeatCount="indefinite"/>')


def breathe(attr="stroke"):
    """Печать держит, потом на секунду наливается чакрой и снова держит."""
    return (f'<animate attributeName="{attr}" dur="{PULSE}s" repeatCount="indefinite" '
            f'values="{CALM};{CALM};{CHAKRA};{EMBER};{CHAKRA};{CALM};{CALM}" '
            f'keyTimes="0;0.45;0.58;0.66;0.74;0.87;1"/>')


p = []
add = p.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
    f'width="{SIZE}" height="{SIZE}" fill="none">')

# Внешнее кольцо с восемью печатями — вращается медленно по часовой.
add('<g>')
add(rotate(SPIN_OUT))
add(f'<circle cx="{C}" cy="{C}" r="176" stroke="{FAINT}" stroke-width="1.5" opacity="0.7"/>')
add(f'<circle cx="{C}" cy="{C}" r="168" stroke="{FAINT}" stroke-width="3" opacity="0.45"/>')
add(spokes(8, 150, 168, 9, CALM, 0.95))
add(spokes(8, 152, 166, 3, "#0d1117", 1.0))
add(spokes(24, 172, 179, 1.5, FAINT, 0.6, offset=7.5))
add('</g>')

# Среднее кольцо — против часовой, оно и дышит цветом.
add('<g>')
add(rotate(SPIN_IN, reverse=True))
add(f'<circle cx="{C}" cy="{C}" r="132" stroke="{CALM}" stroke-width="2">{breathe()}</circle>')
add(spokes(16, 118, 132, 2.5, CALM, 0.75))
add(spokes(4, 104, 132, 5, CALM, 0.9, offset=45))
add('</g>')

# Ядро: спираль Узумаки. Неподвижна — она и есть печать.
add(f'<circle cx="{C}" cy="{C}" r="104" stroke="{FAINT}" stroke-width="1.2" opacity="0.8"/>')
add(f'<path d="{spiral()}" stroke="{CALM}" stroke-width="7" stroke-linecap="round">'
    f'{breathe()}</path>')
add(f'<circle cx="{C}" cy="{C}" r="5" fill="{CALM}"><animate attributeName="fill" dur="{PULSE}s" '
    f'repeatCount="indefinite" values="{CALM};{CALM};{EMBER};{CALM};{CALM}" '
    f'keyTimes="0;0.5;0.66;0.85;1"/></circle>')

# Четыре знака по сторонам света — те, что удерживают контур.
add('<g>')
add(rotate(SPIN_OUT * 2, reverse=True))
for i in range(4):
    a = math.radians(45 + i * 90)
    x, y = C + 146 * math.cos(a), C + 146 * math.sin(a)
    add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" stroke="{CALM}" stroke-width="2" '
        f'opacity="0.9"/>')
add('</g>')

add("</svg>")
print("".join(p))
