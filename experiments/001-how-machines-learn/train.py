"""Aula 001 — loop mínimo de treinamento (from scratch, sem bibliotecas).

Modelo: y_pred = w * x + b, treinado com gradient descent sobre um único exemplo.

Uso:
    uv run python experiments/001-how-machines-learn/train.py
    uv run python experiments/001-how-machines-learn/train.py --lr 0.1 --x 5 --y 25
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class TrainResult:
    w: float
    b: float
    losses: list[float]


def train(
    x: float, y_real: float, learning_rate: float, epochs: int = 100, verbose: bool = False
) -> TrainResult:
    w, b = 0.0, 0.0
    losses: list[float] = []

    for epoch in range(epochs):
        y_pred = w * x + b
        loss = (y_real - y_pred) ** 2
        losses.append(loss)

        # Derivadas parciais de (y_real - (w*x + b))^2 — chain rule.
        dw = -2 * x * (y_real - y_pred)
        db = -2 * (y_real - y_pred)

        w -= learning_rate * dw
        b -= learning_rate * db

        if verbose:
            print(f"epoch={epoch:03d} prediction={y_pred:.4f} loss={loss:.4f}")

    return TrainResult(w=w, b=b, losses=losses)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x", type=float, default=2.0)
    parser.add_argument("--y", type=float, default=10.0)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--epochs", type=int, default=100)
    args = parser.parse_args()

    result = train(args.x, args.y, args.lr, args.epochs, verbose=True)
    print(f"w = {result.w:.4f}")
    print(f"b = {result.b:.4f}")
    print(f"prediction final = {result.w * args.x + result.b:.4f}")


if __name__ == "__main__":
    main()
