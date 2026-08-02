import json
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

ARQUIVO_REGRAS = (
    RAIZ_PROJETO
    / "config"
    / "business_rules.json"
)


def carregar_regras() -> dict[str, Any]:
    """
    Carrega e retorna as regras de negócio do sistema.
    """
    if not ARQUIVO_REGRAS.is_file():
        raise FileNotFoundError(
            "Arquivo de regras não encontrado.\n"
            f"Caminho procurado: {ARQUIVO_REGRAS}"
        )

    with ARQUIVO_REGRAS.open(
        mode="r",
        encoding="utf-8",
    ) as arquivo:
        regras = json.load(arquivo)

    validar_regras(regras)

    return regras


def validar_regras(regras: dict[str, Any]) -> None:
    """
    Verifica se todas as seções obrigatórias estão presentes.
    """
    secoes_obrigatorias = {
        "inventory",
        "financial",
        "abc",
        "stockout",
        "lead_time",
        "priority",
    }

    secoes_ausentes = secoes_obrigatorias - set(regras)

    if secoes_ausentes:
        raise ValueError(
            "Seções obrigatórias ausentes no arquivo de regras: "
            f"{sorted(secoes_ausentes)}"
        )


if __name__ == "__main__":
    regras = carregar_regras()

    print("Regras carregadas com sucesso.")
    print(f"Arquivo: {ARQUIVO_REGRAS}")
    print(f"Seções encontradas: {list(regras.keys())}")