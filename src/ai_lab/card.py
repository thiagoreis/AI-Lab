"""Card SVG do progresso, exibido no README.

SVG puro e autocontido: o GitHub o renderiza via <img>, sem scripts nem fontes
externas. As cores trocam com o tema do visitante via prefers-color-scheme.
"""

from __future__ import annotations

from datetime import date
from xml.sax.saxutils import escape

from ai_lab.progress import (
    Progress,
    current_lesson,
    level_for,
    stage_progress,
    total_xp,
    weekly_sessions,
)

WIDTH = 880
PAD = 32
INNER = WIDTH - 2 * PAD

STYLE = """
  .bg { fill: #fcfcfb; stroke: #e4e3df; }
  .tile { fill: #f3f2ef; }
  .t1 { fill: #0b0b0b; }
  .t2 { fill: #52514e; }
  .track { fill: #cde2fb; }
  .fill { fill: #2a78d6; }
  .line { stroke: #d6d5d0; }
  .line-done { stroke: #0ca30c; }
  .node-done { fill: #0ca30c; }
  .node-current { fill: #2a78d6; }
  .halo { fill: #2a78d6; opacity: .18; }
  .node-locked { fill: #fcfcfb; stroke: #b5b4ae; }
  .icon-locked { stroke: #8a8983; fill: none; }
  .badge-on { fill: #fab219; }
  .badge-off { fill: none; stroke: #b5b4ae; stroke-dasharray: 4 3; }
  text { font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }
  @media (prefers-color-scheme: dark) {
    .bg { fill: #1a1a19; stroke: #383835; }
    .tile { fill: #262624; }
    .t1 { fill: #ffffff; }
    .t2 { fill: #c3c2b7; }
    .track { fill: #3a3a37; }
    .fill { fill: #3987e5; }
    .line { stroke: #4a4a46; }
    .node-current { fill: #3987e5; }
    .halo { fill: #3987e5; }
    .node-locked { fill: #1a1a19; stroke: #6b6a65; }
    .icon-locked { stroke: #8f8e87; }
    .badge-off { stroke: #6b6a65; }
  }
"""


def _text(x: float, y: float, content: str, cls: str, size: int, weight: int = 400,
          anchor: str = "start", spacing: float = 0) -> str:
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{escape(content)}</text>'
    )


def _meter(x: float, y: float, width: float, value: int, total: int, height: int = 10) -> str:
    ratio = 0 if total <= 0 else max(0.0, min(1.0, value / total))
    r = height / 2
    parts = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{r}" class="track"/>']
    if ratio > 0:
        w = max(height, width * ratio)
        parts.append(f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{height}" rx="{r}" class="fill"/>')
    return "".join(parts)


def _split_name(name: str) -> tuple[str, str]:
    """Quebra nomes longos de etapa em duas linhas no ' + '."""
    if " + " in name:
        head, tail = name.split(" + ", 1)
        return head, f"+ {tail}"
    return name, ""


def _header(p: Progress, y: int) -> tuple[list[str], int]:
    xp = total_xp(p)
    number, level, nxt = level_for(p, xp)
    out = [
        _text(PAD, y + 12, "AI-LAB · FORMAÇÃO EM AI ENGINEERING", "t2", 12, 600, spacing=1.2),
        _text(PAD, y + 56, f"Nível {number}", "t1", 40, 700),
        _text(PAD + 170, y + 56, level.title, "t2", 22, 500),
    ]
    y += 80
    if nxt is None:
        out.append(_meter(PAD, y, INNER, 1, 1))
        left, right = f"{xp} XP", "nível máximo"
    else:
        out.append(_meter(PAD, y, INNER, xp - level.min_xp, nxt.min_xp - level.min_xp))
        left, right = f"{xp} / {nxt.min_xp} XP", f"próximo: {nxt.title}"
    out.append(_text(PAD, y + 30, left, "t1", 13, 600))
    out.append(_text(WIDTH - PAD, y + 30, right, "t2", 13, anchor="end"))
    return out, y + 56


def _kpis(p: Progress, y: int, today: date) -> tuple[list[str], int]:
    lessons_done = sum(ls.is_done for ls in p.lessons)
    badges_done = sum(b.earned is not None for b in p.badges)
    tiles = [
        (str(total_xp(p)), "XP total"),
        (f"{lessons_done}/{len(p.lessons)}", "aulas concluídas"),
        (f"{badges_done}/{len(p.badges)}", "badges"),
        (str(sum(weekly_sessions(p, today))), "sessões (últimas 4 semanas)"),
    ]
    gap = 16
    w = (INNER - gap * (len(tiles) - 1)) / len(tiles)
    out = []
    for i, (value, label) in enumerate(tiles):
        x = PAD + i * (w + gap)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="76" rx="10" class="tile"/>')
        out.append(_text(x + 16, y + 38, value, "t1", 28, 700))
        out.append(_text(x + 16, y + 60, label, "t2", 12))
    return out, y + 76 + 36


def _journey(p: Progress, y: int) -> tuple[list[str], int]:
    out = [_text(PAD, y, "Jornada", "t1", 15, 600)]
    cy = y + 40
    r = 17
    n = len(p.stages)
    step = (INNER - 2 * 60) / (n - 1)
    xs = [PAD + 60 + i * step for i in range(n)]

    states: list[str] = []
    found_current = False
    for s in p.stages:
        prog = stage_progress(p, s.id)
        if prog is not None and prog[0] == prog[1]:
            states.append("done")
        elif not found_current:
            states.append("current")
            found_current = True
        else:
            states.append("locked")

    for i in range(n - 1):
        cls = "line-done" if states[i] == "done" else "line"
        out.append(
            f'<line x1="{xs[i] + r + 4:.1f}" y1="{cy}" x2="{xs[i + 1] - r - 4:.1f}" y2="{cy}" '
            f'class="{cls}" stroke-width="3" stroke-linecap="round"/>'
        )

    for x, s, state in zip(xs, p.stages, states):
        if state == "done":
            out.append(f'<circle cx="{x:.1f}" cy="{cy}" r="{r}" class="node-done"/>')
            out.append(
                f'<path d="M{x - 7:.1f} {cy} l5 5 l9 -10" stroke="#fff" stroke-width="3" '
                'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        elif state == "current":
            out.append(f'<circle cx="{x:.1f}" cy="{cy}" r="{r + 7}" class="halo"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{cy}" r="{r}" class="node-current"/>')
            out.append(
                f'<text x="{x:.1f}" y="{cy + 6}" fill="#fff" font-size="16" font-weight="700" '
                f'text-anchor="middle">{s.id}</text>'
            )
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{cy}" r="{r}" class="node-locked" stroke-width="2"/>')
            # cadeado: arco + corpo
            out.append(
                f'<path d="M{x - 4:.1f} {cy - 1} v-3 a4 4 0 0 1 8 0 v3" class="icon-locked" stroke-width="2"/>'
                f'<rect x="{x - 6.5:.1f}" y="{cy - 1}" width="13" height="9" rx="2" class="icon-locked" stroke-width="2"/>'
            )

        line1, line2 = _split_name(s.name)
        ty = cy + r + 26
        out.append(_text(x, ty, f"Etapa {s.id}", "t2", 11, 600, "middle"))
        out.append(_text(x, ty + 18, line1, "t1", 13, 600 if state == "current" else 400, "middle"))
        if line2:
            out.append(_text(x, ty + 34, line2, "t1", 13, 600 if state == "current" else 400, "middle"))
        prog = stage_progress(p, s.id)
        if state == "current" and prog is not None:
            out.append(_text(x, ty + (52 if line2 else 36), f"{prog[0]}/{prog[1]} aulas", "t2", 11, 400, "middle"))
    return out, cy + r + 26 + 70


def _mission(p: Progress, y: int) -> tuple[list[str], int]:
    lesson = current_lesson(p)
    if lesson is None:
        return [], y
    done = sum(a.done for a in lesson.activities)
    total = len(lesson.activities)
    out = [
        f'<rect x="{PAD}" y="{y}" width="{INNER}" height="74" rx="10" class="tile"/>',
        _text(PAD + 18, y + 28, "MISSÃO ATUAL", "t2", 11, 600, spacing=1.2),
        _text(PAD + 18, y + 52, f"Aula {lesson.id} — {lesson.title}", "t1", 17, 600),
        _text(WIDTH - PAD - 18, y + 28, f"{done}/{total} atividades", "t2", 12, anchor="end"),
        _meter(WIDTH - PAD - 18 - 200, y + 44, 200, done, total, 8),
    ]
    return out, y + 74 + 36


def _badges(p: Progress, y: int) -> tuple[list[str], int]:
    if not p.badges:
        return [], y
    earned = sum(b.earned is not None for b in p.badges)
    out = [_text(PAD, y, f"Badges · {earned}/{len(p.badges)}", "t1", 15, 600)]
    r = 22
    cy = y + 22 + r
    step = INNER / len(p.badges)
    for i, b in enumerate(p.badges):
        cx = PAD + step * i + step / 2
        if b.earned:
            initials = "".join(w[0] for w in b.name.split()[:2]).upper()
            out.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="{r}" class="badge-on"/>')
            out.append(
                f'<text x="{cx:.1f}" y="{cy + 6}" fill="#0b0b0b" font-size="16" font-weight="700" '
                f'text-anchor="middle">{escape(initials)}</text>'
            )
            out.append(_text(cx, cy + r + 20, b.name, "t1", 12, 500, "middle"))
        else:
            out.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="{r}" class="badge-off" stroke-width="2"/>')
            out.append(_text(cx, cy + 6, "?", "t2", 18, 700, "middle"))
            out.append(_text(cx, cy + r + 20, "???", "t2", 12, 400, "middle"))
    return out, cy + r + 20 + 28


def render_svg(p: Progress, today: date) -> str:
    body: list[str] = []
    y = PAD
    for section in (
        lambda y: _header(p, y),
        lambda y: _kpis(p, y, today),
        lambda y: _journey(p, y),
        lambda y: _mission(p, y),
        lambda y: _badges(p, y),
    ):
        parts, y = section(y)
        body += parts
    height = y + PAD - 28

    number, level, _ = level_for(p, total_xp(p))
    title = f"AI-Lab — Nível {number} · {level.title} · {total_xp(p)} XP"
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
            f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{escape(title)}">',
            f"<title>{escape(title)}</title>",
            f"<style>{STYLE}</style>",
            f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="16" class="bg"/>',
            *body,
            "</svg>",
            "",
        ]
    )
