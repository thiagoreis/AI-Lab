import xml.etree.ElementTree as ET
from datetime import date

from ai_lab import card, progress
from tests.test_progress import make_raw

SVG_NS = "{http://www.w3.org/2000/svg}"


def render(**overrides: object) -> ET.Element:
    p = progress.parse(make_raw(**overrides))
    return ET.fromstring(card.render_svg(p, date(2026, 9, 30)))


def texts(root: ET.Element) -> list[str]:
    return [t.text or "" for t in root.iter(f"{SVG_NS}text")]


def test_svg_is_well_formed_and_titled() -> None:
    root = render()
    assert root.tag == f"{SVG_NS}svg"
    assert "Nível 1" in root.findtext(f"{SVG_NS}title", "")


def test_svg_shows_state() -> None:
    labels = texts(render())
    assert "10 / 100 XP" in labels
    assert "Aula 001 — A" in labels
    assert "1/2 atividades" in labels


def test_svg_escapes_xml_special_characters() -> None:
    raw = make_raw()
    raw["lessons"][0]["title"] = "Regras <&> do jogo"
    root = ET.fromstring(card.render_svg(progress.parse(raw), date(2026, 9, 30)))
    assert "Aula 001 — Regras <&> do jogo" in texts(root)


def test_unearned_badges_stay_hidden() -> None:
    labels = texts(
        render(badges=[{"id": "x", "name": "Segredo", "description": "d"}])
    )
    assert "Segredo" not in labels and "???" in labels
