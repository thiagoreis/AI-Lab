import argparse
import sys
from datetime import date
from pathlib import Path

from ai_lab import card, progress


def main() -> None:
    parser = argparse.ArgumentParser(prog="ai-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    prog = sub.add_parser("progress", help="mostra o painel de progresso gamificado")
    prog.add_argument("--file", type=Path, default=Path("progress/progress.toml"))
    prog.add_argument(
        "--write",
        action="store_true",
        help="regenera o bloco gerado em PROGRESS.md",
    )
    prog.add_argument("--markdown", type=Path, default=Path("PROGRESS.md"))
    prog.add_argument("--readme", type=Path, default=Path("README.md"))
    prog.add_argument("--card", type=Path, default=Path("progress/dashboard.svg"))

    args = parser.parse_args()
    # Garante emojis e barras no console do Windows mesmo com saída redirecionada.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.command == "progress":
        data = progress.load(args.file)
        today = date.today()
        print(progress.render_dashboard(data, today))
        print()
        print(progress.render_next(data))
        if args.write:
            progress.write_block(args.markdown, progress.render_markdown(data, today))
            progress.write_text_lf(args.card, card.render_svg(data, today))
            progress.write_block(args.readme, progress.render_readme(data, args.card.as_posix()))
            print(f"\n✔ {args.markdown}, {args.card} e {args.readme} atualizados.")
