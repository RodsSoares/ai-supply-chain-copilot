import json
from urllib.error import HTTPError, URLError

import pytest

from src.ai import tools


class RespostaFake:
    """
    Simula a resposta devolvida pelo urlopen.
    """

    def __init__(self, dados):
        self.dados = dados

    def read(self):
        """
        Retorna o conteúdo da resposta em bytes.
        """
        return self.dados

    def __enter__(self):
        """
        Permite usar a resposta dentro de um bloco with.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Finaliza o contexto sem suprimir exceções.
        """
        return False


def test_listar_inventario_retorna_dados_convertidos(monkeypatch):
    """
    Verifica se um JSON válido é convertido para objetos Python.
    """

    inventario_esperado = [
        {
            "sku": "SKU001",
            "descricao": "Produto de teste",
            "prioridade": "ALTA",
        }
    ]

    conteudo_json = json.dumps(inventario_esperado).encode("utf-8")

    def urlopen_fake(requisicao, timeout):
        assert requisicao.full_url == tools.URL_INVENTARIO
        assert timeout == tools.TIMEOUT_SEGUNDOS

        return RespostaFake(conteudo_json)

    monkeypatch.setattr(tools, "urlopen", urlopen_fake)

    resultado = tools.listar_inventario()

    assert resultado == inventario_esperado


def test_listar_inventario_gera_erro_para_json_invalido(monkeypatch):
    """
    Verifica se uma resposta sem JSON válido gera ValueError.
    """

    def urlopen_fake(requisicao, timeout):
        return RespostaFake(b"conteudo invalido")

    monkeypatch.setattr(tools, "urlopen", urlopen_fake)

    with pytest.raises(
        ValueError,
        match="não é um JSON válido",
    ):
        tools.listar_inventario()


def test_listar_inventario_gera_erro_de_conexao(monkeypatch):
    """
    Verifica o tratamento de falha de conexão com a API.
    """

    def urlopen_fake(requisicao, timeout):
        raise URLError("Servidor indisponível")

    monkeypatch.setattr(tools, "urlopen", urlopen_fake)

    with pytest.raises(
        ConnectionError,
        match="Não foi possível acessar a API",
    ):
        tools.listar_inventario()


def test_listar_inventario_gera_erro_http(monkeypatch):
    """
    Verifica o tratamento de erro HTTP retornado pela API.
    """

    def urlopen_fake(requisicao, timeout):
        raise HTTPError(
            url=tools.URL_INVENTARIO,
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(tools, "urlopen", urlopen_fake)

    with pytest.raises(
        RuntimeError,
        match="erro HTTP 500",
    ):
        tools.listar_inventario()


def test_listar_inventario_gera_erro_de_timeout(monkeypatch):
    """
    Verifica o tratamento de uma API que não responde no prazo.
    """

    def urlopen_fake(requisicao, timeout):
        raise TimeoutError

    monkeypatch.setattr(tools, "urlopen", urlopen_fake)

    with pytest.raises(
        ConnectionError,
        match="não respondeu em até 10 segundos",
    ):
        tools.listar_inventario()