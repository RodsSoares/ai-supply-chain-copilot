"""(Re)gera o Golden Set v2 a partir do motor: JSON travado + versão Markdown.

Use apenas quando uma mudança intencional no motor ou nos dados alterar os
valores esperados; revise o diff antes de commitar.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluation.golden_network import construir_golden_set, escrever_markdown  # noqa: E402


def main() -> None:
    golden = construir_golden_set()
    Path("tests/golden").mkdir(parents=True, exist_ok=True)
    Path("tests/golden/network_golden_set.json").write_text(json.dumps(golden, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path("tests/golden_test_set_network.md").write_text(escrever_markdown(golden), encoding="utf-8")
    print(f"{len(golden['cases'])} casos -> tests/golden/network_golden_set.json, tests/golden_test_set_network.md")


if __name__ == "__main__":
    main()
