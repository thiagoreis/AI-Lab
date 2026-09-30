"""Progresso gamificado do AI-Lab.

`progress/progress.toml` é a fonte da verdade. Este módulo deriva dele o estado
(XP, nível, aulas desbloqueadas, ritmo semanal) e renderiza o painel exibido no
terminal e no bloco gerado de `PROGRESS.md`.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from pathlib import Path

START_MARKER = "<!-- progress:start -->"
END_MARKER = "<!-- progress:end -->"
BAR_WIDTH = 20


class LessonStatus(Enum):
    DONE = "done"
    CURRENT = "current"
    AVAILABLE = "available"
    LOCKED = "locked"


@dataclass(frozen=True)
class Activity:
    kind: str
    title: str
    done: bool


@dataclass(frozen=True)
class Lesson:
    id: str
    stage: int
    title: str
    file: str
    requires: tuple[str, ...]
    activities: tuple[Activity, ...]

    @property
    def is_done(self) -> bool:
        """Uma aula só termina quando o boss fight é vencido."""
        return any(a.kind == "boss" and a.done for a in self.activities)


@dataclass(frozen=True)
class Level:
    min_xp: int
    title: str


@dataclass(frozen=True)
class Stage:
    id: int
    name: str


@dataclass(frozen=True)
class Badge:
    id: str
    name: str
    description: str
    earned: date | None


@dataclass(frozen=True)
class Session:
    date: date
    note: str


@dataclass(frozen=True)
class Progress:
    xp_rules: dict[str, int]
    levels: tuple[Level, ...]
    stages: tuple[Stage, ...]
    lessons: tuple[Lesson, ...]
    badges: tuple[Badge, ...] = ()
    sessions: tuple[Session, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Carga e validação
# ---------------------------------------------------------------------------


def parse(raw: dict) -> Progress:
    progress = Progress(
        xp_rules={k: int(v) for k, v in raw["xp"].items()},
        levels=tuple(Level(int(lv["min_xp"]), lv["title"]) for lv in raw["levels"]),
        stages=tuple(Stage(int(s["id"]), s["name"]) for s in raw["stages"]),
        lessons=tuple(
            Lesson(
                id=ls["id"],
                stage=int(ls["stage"]),
                title=ls["title"],
                file=ls.get("file", ""),
                requires=tuple(ls.get("requires", [])),
                activities=tuple(
                    Activity(a["kind"], a["title"], bool(a.get("done", False)))
                    for a in ls.get("activities", [])
                ),
            )
            for ls in raw.get("lessons", [])
        ),
        badges=tuple(
            Badge(b["id"], b["name"], b["description"], b.get("earned"))
            for b in raw.get("badges", [])
        ),
        sessions=tuple(Session(s["date"], s.get("note", "")) for s in raw.get("sessions", [])),
    )
    validate(progress)
    return progress


def load(path: Path) -> Progress:
    with path.open("rb") as f:
        return parse(tomllib.load(f))


def validate(p: Progress) -> None:
    """Falha cedo em dados inconsistentes, em vez de renderizar um painel mentiroso."""
    errors: list[str] = []

    if not p.levels or p.levels[0].min_xp != 0:
        errors.append("o primeiro nível deve ter min_xp = 0")
    thresholds = [lv.min_xp for lv in p.levels]
    if thresholds != sorted(set(thresholds)):
        errors.append("min_xp dos níveis deve ser estritamente crescente")

    stage_ids = {s.id for s in p.stages}
    lesson_ids = [ls.id for ls in p.lessons]
    if len(lesson_ids) != len(set(lesson_ids)):
        errors.append("ids de aula duplicados")

    for ls in p.lessons:
        if ls.stage not in stage_ids:
            errors.append(f"aula {ls.id}: etapa {ls.stage} inexistente")
        for req in ls.requires:
            if req not in lesson_ids:
                errors.append(f"aula {ls.id}: pré-requisito {req} inexistente")
        if sum(a.kind == "boss" for a in ls.activities) != 1:
            errors.append(f"aula {ls.id}: deve ter exatamente uma atividade 'boss'")
        for a in ls.activities:
            if a.kind not in p.xp_rules:
                errors.append(f"aula {ls.id}: tipo de atividade desconhecido '{a.kind}'")

    if errors:
        raise ValueError("progress.toml inválido:\n- " + "\n- ".join(errors))


# ---------------------------------------------------------------------------
# Regras do jogo
# ---------------------------------------------------------------------------


def total_xp(p: Progress) -> int:
    return sum(p.xp_rules[a.kind] for ls in p.lessons for a in ls.activities if a.done)


def level_for(p: Progress, xp: int) -> tuple[int, Level, Level | None]:
    """Retorna (número do nível, nível atual, próximo nível ou None se for o último)."""
    index = max(i for i, lv in enumerate(p.levels) if xp >= lv.min_xp)
    nxt = p.levels[index + 1] if index + 1 < len(p.levels) else None
    return index + 1, p.levels[index], nxt


def lesson_statuses(p: Progress) -> dict[str, LessonStatus]:
    """A primeira aula desbloqueada e não concluída é a atual; as demais desbloqueadas ficam disponíveis."""
    done = {ls.id for ls in p.lessons if ls.is_done}
    statuses: dict[str, LessonStatus] = {}
    current_assigned = False
    for ls in p.lessons:
        if ls.id in done:
            statuses[ls.id] = LessonStatus.DONE
        elif all(r in done for r in ls.requires):
            statuses[ls.id] = LessonStatus.AVAILABLE if current_assigned else LessonStatus.CURRENT
            current_assigned = True
        else:
            statuses[ls.id] = LessonStatus.LOCKED
    return statuses


def current_lesson(p: Progress) -> Lesson | None:
    statuses = lesson_statuses(p)
    return next((ls for ls in p.lessons if statuses[ls.id] is LessonStatus.CURRENT), None)


def stage_progress(p: Progress, stage_id: int) -> tuple[int, int] | None:
    """(aulas concluídas, aulas cadastradas) da etapa, ou None se ainda não há aulas."""
    lessons = [ls for ls in p.lessons if ls.stage == stage_id]
    if not lessons:
        return None
    return sum(ls.is_done for ls in lessons), len(lessons)


def weekly_sessions(p: Progress, today: date, weeks: int = 4) -> list[int]:
    """Sessões por semana (segunda a domingo), da mais antiga para a atual."""
    this_monday = today - timedelta(days=today.weekday())
    counts = []
    for back in range(weeks - 1, -1, -1):
        start = this_monday - timedelta(weeks=back)
        end = start + timedelta(days=7)
        counts.append(sum(start <= s.date < end for s in p.sessions))
    return counts


# ---------------------------------------------------------------------------
# Renderização
# ---------------------------------------------------------------------------


def bar(value: int, total: int, width: int = BAR_WIDTH) -> str:
    filled = 0 if total <= 0 else min(width, round(width * value / total))
    return "█" * filled + "░" * (width - filled)


def render_dashboard(p: Progress, today: date) -> str:
    xp = total_xp(p)
    number, level, nxt = level_for(p, xp)
    lines = [f"🧠 AI-Lab — Nível {number} · {level.title}"]

    if nxt is None:
        lines.append(f"XP  {bar(1, 1)}  {xp} (nível máximo)")
    else:
        span = nxt.min_xp - level.min_xp
        lines.append(
            f"XP  {bar(xp - level.min_xp, span)}  {xp} / {nxt.min_xp}  → {nxt.title}"
        )

    lines.append("")
    name_width = max(len(f"Etapa {s.id} · {s.name}") for s in p.stages)
    for s in p.stages:
        label = f"Etapa {s.id} · {s.name}".ljust(name_width)
        prog = stage_progress(p, s.id)
        if prog is None:
            lines.append(f"{label}  🔒")
        else:
            done, total = prog
            lines.append(f"{label}  {bar(done, total, 10)}  {done}/{total} aulas")

    lines.append("")
    earned = [b for b in p.badges if b.earned]
    shown = [f"[{b.name}]" for b in earned] + ["???"] * (len(p.badges) - len(earned))
    lines.append(f"🏅 Badges {len(earned)}/{len(p.badges)}: " + " · ".join(shown))

    counts = weekly_sessions(p, today)
    lines.append(
        "📅 Sessões/semana (últimas 4): "
        + " ".join(str(c) for c in counts)
        + f"  · total {len(p.sessions)}"
    )
    return "\n".join(lines)


def render_next(p: Progress) -> str:
    lesson = current_lesson(p)
    if lesson is None:
        return "Nenhuma aula desbloqueada pendente. Cadastre a próxima aula em `progress/progress.toml`."
    lines = [f"**Aula {lesson.id} — {lesson.title}** (`{lesson.file}`)", ""]
    for a in lesson.activities:
        mark = "x" if a.done else " "
        lines.append(f"- [{mark}] `{a.kind}` +{p.xp_rules[a.kind]} XP — {a.title}")
    return "\n".join(lines)


_MERMAID_CLASS = {
    LessonStatus.DONE: "done",
    LessonStatus.CURRENT: "current",
    LessonStatus.AVAILABLE: "available",
    LessonStatus.LOCKED: "locked",
}


def render_skill_tree(p: Progress) -> str:
    statuses = lesson_statuses(p)
    lines = ["```mermaid", "flowchart LR"]
    for s in p.stages:
        lessons = [ls for ls in p.lessons if ls.stage == s.id]
        if not lessons:
            continue
        lines.append(f'  subgraph S{s.id}["Etapa {s.id} · {s.name}"]')
        for ls in lessons:
            cls = _MERMAID_CLASS[statuses[ls.id]]
            lines.append(f'    L{ls.id}["{ls.id} · {ls.title}"]:::{cls}')
        lines.append("  end")
    for ls in p.lessons:
        for req in ls.requires:
            lines.append(f"  L{req} --> L{ls.id}")
    lines += [
        "  classDef done fill:#2e7d32,stroke:#1b5e20,color:#fff",
        "  classDef current fill:#f9a825,stroke:#f57f17,color:#000",
        "  classDef available fill:#1565c0,stroke:#0d47a1,color:#fff",
        "  classDef locked fill:#616161,stroke:#424242,color:#ddd",
        "```",
    ]
    return "\n".join(lines)


def render_markdown(p: Progress, today: date) -> str:
    return "\n".join(
        [
            START_MARKER,
            "<!-- Bloco gerado por `uv run ai-lab progress --write`. Não edite à mão: edite progress/progress.toml. -->",
            "",
            "```text",
            render_dashboard(p, today),
            "```",
            "",
            "### 🗺️ Skill tree",
            "",
            "🟩 concluída · 🟨 atual · 🟦 disponível · ⬛ bloqueada",
            "",
            render_skill_tree(p),
            "",
            "### 🎯 Missão atual",
            "",
            render_next(p),
            END_MARKER,
        ]
    )


def replace_block(document: str, block: str) -> str:
    start = document.find(START_MARKER)
    end = document.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"marcadores {START_MARKER} / {END_MARKER} não encontrados")
    return document[:start] + block + document[end + len(END_MARKER) :]


def write_markdown(p: Progress, md_path: Path, today: date) -> None:
    # UTF-8 e LF explícitos: no Windows o padrão seria cp1252 e CRLF.
    document = md_path.read_text(encoding="utf-8")
    md_path.write_text(
        replace_block(document, render_markdown(p, today)), encoding="utf-8", newline="\n"
    )
