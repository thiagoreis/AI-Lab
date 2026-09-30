import argparse
from datetime import date
from pathlib import Path

from ai_lab import progress


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

    args = parser.parse_args()
    if args.command == "progress":
        data = progress.load(args.file)
        today = date.today()
        print(progress.render_dashboard(data, today))
        print()
        print(progress.render_next(data))
        if args.write:
            progress.write_markdown(data, args.markdown, today)
            print(f"\n✔ {args.markdown} atualizado.")
