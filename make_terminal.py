#!/usr/bin/env python3
"""Собирает анимированный SVG-терминал для README профиля.

ЗАЧЕМ СВОЙ, А НЕ ЧУЖОЙ СЕРВИС. Три виджета, которые стоят у половины красивых профилей,
сегодня отвечают 402 и 503 — их владельцы об этом не знают, у них в браузере кэш. Картинка,
которая лежит в собственном репозитории, не зависит ни от чьей бесплатной квоты.

Позиции строк и задержки считаются здесь, а не пишутся руками: сдвинешь одну строку — поедут
все следующие, и это заметишь не ты, а посетитель.

    python3 make_terminal.py > terminal.svg
"""

FONT = 15
LINE = 23           # межстрочный интервал
CH = FONT * 0.601   # ширина знака моноширинного шрифта
PAD_X, TOP = 26, 74
WIDTH = 860

GREEN, RED, DIM, INK, ACCENT = "#2ea44f", "#f85149", "#8b949e", "#e6edf3", "#58a6ff"

PROMPT = "npx agent-quality-kit doctor --run"
TYPE_DUR = 1.9      # сколько печатается команда
GAP = 0.42          # пауза между строками вывода
HOLD = 3.2          # сколько готовый экран стоит перед повтором

# (отступ, знак, цвет знака, текст, цвет текста)
OUT = [
    ("", "", "", "", ""),
    ("  ", "✔", GREEN, "secrets-not-in-code", DIM),
    ("  ", "✘", RED, "no-print-in-prod", INK),
    ("       ", "", "", "./src/web/app.js:3:  console.log(\"debug\", x);", DIM),
    ("  ", "✔", GREEN, "swallowed-error", DIM),
    ("  ", "✔", GREEN, "todo-without-task", DIM),
    ("  ", "✘", RED, "deps-are-pinned", INK),
    ("       ", "", "", "requirements.txt:1:PyQt6>=6.6.0  — версия не закреплена", DIM),
    ("  ", "✔", GREEN, "file-size-limit", DIM),
    ("  ", "✔", GREEN, "complexity-limit", DIM),
    ("", "", "", "", ""),
]

TAIL = "  Level: AQK-2 · 6 of 8 green · declared is not the same as works"

HEIGHT = TOP + LINE * (len(OUT) + 2) + 30
TOTAL = TYPE_DUR + GAP * (len(OUT) + 1) + HOLD


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def pct(t):
    """Секунды → процент от цикла, для @keyframes."""
    return max(0.0, min(100.0, t / TOTAL * 100))


parts = []
add = parts.append

add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
    f'width="{WIDTH}" height="{HEIGHT}" font-family="ui-monospace,SFMono-Regular,'
    f'JetBrains Mono,Menlo,Consolas,monospace" font-size="{FONT}">')

# --- стиль и покадровка --------------------------------------------------------
css = [
    ".w{animation:none}",
    "@keyframes typing{"
    f"0%{{width:0}}{pct(TYPE_DUR):.3f}%{{width:{len(PROMPT) * CH:.1f}px}}"
    f"100%{{width:{len(PROMPT) * CH:.1f}px}}}}",
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
    f".cursor{{animation:blink 1.05s steps(1) infinite}}",
    f"#typed{{animation:typing {TOTAL:.2f}s steps({len(PROMPT)},end) infinite}}",
]
for i in range(len(OUT) + 1):
    t = TYPE_DUR + GAP * (i + 1)
    a, b = pct(t - 0.001), pct(t)
    css.append(f"@keyframes r{i}{{0%,{a:.3f}%{{opacity:0}}{b:.3f}%,100%{{opacity:1}}}}")
    css.append(f".r{i}{{opacity:0;animation:r{i} {TOTAL:.2f}s linear infinite}}")
add("<style>" + "".join(css) + "</style>")

# --- окно ----------------------------------------------------------------------
add(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="#0d1117" stroke="#30363d"/>')
add(f'<rect width="{WIDTH}" height="46" rx="12" fill="#161b22"/>')
add(f'<rect y="34" width="{WIDTH}" height="12" fill="#161b22"/>')
add(f'<line x1="0" y1="46" x2="{WIDTH}" y2="46" stroke="#30363d"/>')
for i, colour in enumerate(("#ff5f57", "#febc2e", "#28c840")):
    add(f'<circle cx="{26 + i * 22}" cy="23" r="6" fill="{colour}"/>')
add(f'<text x="{WIDTH / 2}" y="28" fill="{DIM}" font-size="13" text-anchor="middle">'
    'someone else&#39;s repository — 15 seconds, nothing written</text>')

# --- печатающаяся команда ------------------------------------------------------
y = TOP
add(f'<text x="{PAD_X}" y="{y}" fill="{GREEN}" font-weight="700">$</text>')
add(f'<clipPath id="clip"><rect id="typed" x="0" y="{y - FONT}" height="{FONT + 6}" width="0"/></clipPath>')
add(f'<g clip-path="url(#clip)" transform="translate({PAD_X + CH * 2},0)">'
    f'<text x="0" y="{y}" fill="{INK}">{esc(PROMPT)}</text></g>')

# --- вывод ---------------------------------------------------------------------
for i, (pad, mark, mcol, text, tcol) in enumerate(OUT):
    y += LINE
    if not text and not mark:
        continue
    x = PAD_X + len(pad) * CH
    add(f'<g class="r{i}">')
    if mark:
        add(f'<text x="{x:.1f}" y="{y}" fill="{mcol}" font-weight="700">{mark}</text>')
        x += CH * 3
    add(f'<text x="{x:.1f}" y="{y}" fill="{tcol}">{esc(text)}</text>')
    add("</g>")

y += LINE
add(f'<g class="r{len(OUT)}">'
    f'<text x="{PAD_X}" y="{y}" fill="{ACCENT}" font-weight="700">{esc(TAIL)}</text></g>')

# --- курсор --------------------------------------------------------------------
add(f'<rect class="cursor" x="{PAD_X + CH * (len(PROMPT) + 3):.1f}" y="{TOP - FONT + 2}" '
    f'width="{CH:.1f}" height="{FONT + 3}" fill="{GREEN}"/>')

add("</svg>")
print("".join(parts))
