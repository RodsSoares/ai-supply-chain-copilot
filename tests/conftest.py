"""Fixtures compartilhadas da rede sintética (v2.x)."""

import pytest

from src.analytics.network.repository import carregar_de_memoria
from src.synthetic.network_generator import carregar_config, gerar_rede


@pytest.fixture(scope="session")
def config_rede():
    return carregar_config()


@pytest.fixture(scope="session")
def rede_gerada(config_rede):
    return gerar_rede(config_rede)


@pytest.fixture(scope="session")
def dados_rede(rede_gerada):
    return carregar_de_memoria(rede_gerada.tabelas)
