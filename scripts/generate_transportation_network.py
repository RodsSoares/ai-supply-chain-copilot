"""Gera a rede sintética de Transportation (v2.1).

Uso:
    python scripts/generate_transportation_network.py [--seed 42] [--output DIR]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.synthetic.network_generator import (  # noqa: E402
    DIRETORIO_SAIDA,
    carregar_config,
    escrever_rede,
    gerar_rede,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output", type=Path, default=DIRETORIO_SAIDA)
    args = parser.parse_args()

    rede = gerar_rede(carregar_config(), seed=args.seed)
    escrever_rede(rede, args.output)
    for tabela, linhas in rede.relatorio["row_counts"].items():
        print(f"{tabela:<28} {linhas:>9,}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
