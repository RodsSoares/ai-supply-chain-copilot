import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

URL_INVENTARIO = f"{API_BASE_URL}/inventory"

TIMEOUT_SEGUNDOS = 10


def listar_inventario() -> Any:
    """
    Consulta o endpoint de inventário da API.

    Returns:
        Dados do inventário convertidos de JSON para objetos Python.

    Raises:
        ConnectionError: Quando não é possível acessar a API.
        RuntimeError: Quando a API retorna erro HTTP.
        ValueError: Quando a resposta não contém um JSON válido.
    """

    requisicao = Request(
        URL_INVENTARIO,
        headers={
            "Accept": "application/json",
            "User-Agent": "AI-Supply-Chain-Copilot",
        },
        method="GET",
    )

    try:
        with urlopen(
            requisicao,
            timeout=TIMEOUT_SEGUNDOS,
        ) as resposta:
            conteudo = resposta.read().decode("utf-8")

    except HTTPError as erro:
        raise RuntimeError(
            f"A API retornou o erro HTTP {erro.code}: {erro.reason}"
        ) from erro

    except URLError as erro:
        raise ConnectionError(
            "Não foi possível acessar a API. "
            "Confirme se o servidor FastAPI está em execução."
        ) from erro

    except TimeoutError as erro:
        raise ConnectionError(
            f"A API não respondeu em até {TIMEOUT_SEGUNDOS} segundos."
        ) from erro

    try:
        return json.loads(conteudo)

    except json.JSONDecodeError as erro:
        raise ValueError(
            "A API respondeu, mas o conteúdo retornado não é um JSON válido."
        ) from erro


if __name__ == "__main__":
    inventario = listar_inventario()

    print("Inventário recebido com sucesso.")

    if isinstance(inventario, list):
        print(f"Registros recebidos: {len(inventario)}")
        print(inventario[:3])
    else:
        print(inventario)