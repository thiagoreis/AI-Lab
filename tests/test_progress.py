from datetime import date
from pathlib import Path

import pytest

from ai_lab import progress
from ai_lab.progress import LessonStatus

REPO_ROOT = Path(__file__).resolve().parents[1]


def make_raw(**overrides: object) -> dict:
    raw: dict = {
        "xp": {"exercise": 10, "experiment": 20, "boss": 50, "milestone": 100},
        "levels": [
            {"min_xp": 0, "title": "L1"},
            {"min_xp": 100, "title": "L2"},
        ],
        "stages": [{"id": 1, "name": "S1"}, {"id": 2, "name": "S2"}],
        "lessons": [
            {
                "id": "001",
                "stage": 1,
                "title": "A",
                "requires": [],
                "activities": [
                    {"kind": "exercise", "title": "e1", "done": True},
                    {"kind": "boss", "title": "b1", "done": False},
                ],
            },
            {
                "id": "002",
                "stage": 1,
                "title": "B",
                "requires": ["001"],
                "activities": [{"kind": "boss", "title": "b2", "done": False}],
            },
        ],
    }
    raw.update(overrides)
    return raw


def test_real_progress_file_is_valid() -> None:
    p = progress.load(REPO_ROOT / "progress" / "progress.toml")
    assert progress.current_lesson(p) is not None


def test_xp_counts_only_done_activities() -> None:
    p = progress.parse(make_raw())
    assert progress.total_xp(p) == 10


def test_level_boundaries() -> None:
    p = progress.parse(make_raw())
    assert progress.level_for(p, 99)[0] == 1
    number, level, nxt = progress.level_for(p, 100)
    assert (number, level.title, nxt) == (2, "L2", None)


def test_boss_gates_next_lesson() -> None:
    raw = make_raw()
    p = progress.parse(raw)
    assert progress.lesson_statuses(p) == {
        "001": LessonStatus.CURRENT,
        "002": LessonStatus.LOCKED,
    }

    raw["lessons"][0]["activities"][1]["done"] = True
    p = progress.parse(raw)
    assert progress.lesson_statuses(p) == {
        "001": LessonStatus.DONE,
        "002": LessonStatus.CURRENT,
    }
    assert progress.stage_progress(p, 1) == (1, 2)
    assert progress.stage_progress(p, 2) is None


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda r: r["lessons"][1].update(requires=["999"]), "pré-requisito 999"),
        (lambda r: r["lessons"][1].update(activities=[]), "exatamente uma atividade 'boss'"),
        (lambda r: r["lessons"][0]["activities"][0].update(kind="leitura"), "desconhecido"),
        (lambda r: r["levels"].reverse(), "min_xp"),
    ],
)
def test_validation_rejects_inconsistent_data(mutate, message: str) -> None:
    raw = make_raw()
    mutate(raw)
    with pytest.raises(ValueError, match=message):
        progress.parse(raw)


def test_weekly_sessions_groups_by_iso_week() -> None:
    raw = make_raw(
        sessions=[
            {"date": date(2026, 9, 28)},  # segunda da semana atual
            {"date": date(2026, 9, 27)},  # domingo da semana anterior
            {"date": date(2026, 9, 1)},  # fora da janela
        ]
    )
    p = progress.parse(raw)
    assert progress.weekly_sessions(p, today=date(2026, 9, 30)) == [0, 0, 1, 1]


def test_bar() -> None:
    assert progress.bar(0, 10, width=4) == "░░░░"
    assert progress.bar(5, 10, width=4) == "██░░"
    assert progress.bar(20, 10, width=4) == "████"


def test_replace_block_preserves_surrounding_text() -> None:
    doc = f"antes\n{progress.START_MARKER}\nvelho\n{progress.END_MARKER}\ndepois"
    out = progress.replace_block(doc, "NOVO")
    assert out == "antes\nNOVO\ndepois"


def test_replace_block_requires_markers() -> None:
    with pytest.raises(ValueError):
        progress.replace_block("sem marcadores", "x")


def test_write_markdown_uses_utf8_and_lf(tmp_path: Path) -> None:
    md = tmp_path / "PROGRESS.md"
    md.write_bytes(
        f"# Título 🎮\n{progress.START_MARKER}\n{progress.END_MARKER}\nfim\n".encode()
    )
    progress.write_markdown(progress.parse(make_raw()), md, date(2026, 9, 30))
    raw = md.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert text.startswith("# Título 🎮") and "Nível 1" in text and text.endswith("fim\n")
