"""Tabelas da rede no kit Power BI: vêm da camada SQL e fecham entre si.

Os CSVs versionados em reports/powerbi/kit/data precisam ser exatamente o que
as consultas de sql/network produzem hoje, e os totais de fatos diferentes
precisam contar a mesma história.
"""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from src.analytics.network import forecasting, powerbi_export, variance


RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "reports" / "powerbi" / "kit" / "data"
TABELAS_REDE = [*powerbi_export.FATOS, "dim_rede_rotas"]

_spec = importlib.util.spec_from_file_location("build_powerbi_pbip", RAIZ / "scripts" / "build_powerbi_pbip.py")
gerador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gerador)


def ler_csv(nome: str) -> pd.DataFrame:
    return pd.read_csv(DADOS / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")


@pytest.fixture(scope="module")
def exportado(rede_gerada, tmp_path_factory):
    """Exportação nova, a partir da rede dos testes, relida no formato do kit."""
    pasta = tmp_path_factory.mktemp("kit_rede")
    conexao = powerbi_export.conexao_em_memoria(rede_gerada.tabelas)
    try:
        powerbi_export.exportar(conexao, pasta)
    finally:
        conexao.close()
    return {
        nome: pd.read_csv(pasta / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
        for nome in TABELAS_REDE
    }


@pytest.mark.parametrize("tabela", TABELAS_REDE)
def test_csv_versionado_e_o_que_o_sql_produz_hoje(exportado, tabela):
    """Se uma consulta mudar, o kit precisa ser regenerado (scripts/export_powerbi_kit.py)."""
    pd.testing.assert_frame_equal(ler_csv(tabela), exportado[tabela])


def test_todo_fato_da_rede_vem_de_uma_consulta_catalogada():
    from src.analytics.network.sql_queries import CONSULTAS

    for tabela, (consulta, colunas) in powerbi_export.FATOS.items():
        assert consulta in CONSULTAS, tabela
        assert list(ler_csv(tabela).columns) == list(colunas.values()), tabela


def test_tabelas_da_rede_estao_no_modelo_pbip():
    assert set(TABELAS_REDE) <= set(gerador.TABELAS)
    for relacao in powerbi_export.RELACIONAMENTOS:
        assert relacao in gerador.RELACIONAMENTOS


def test_relacionamento_da_rede_sem_orfaos():
    for fato, coluna, dimensao, chave in powerbi_export.RELACIONAMENTOS:
        assert ler_csv(dimensao)[chave].is_unique
        assert set(ler_csv(fato)[coluna]) <= set(ler_csv(dimensao)[chave])


def test_semana_do_realizado_e_lida_como_data():
    assert dict(gerador.tipos_das_colunas("fato_rede_realizado"))["semana_inicio"] == "dateTime"


def test_extras_fecham_entre_o_fato_semanal_e_o_fato_por_motivo():
    """Q-PRF-01 e Q-PRF-02 leem as mesmas viagens: o custo extra total tem de ser igual."""
    semanal = ler_csv("fato_rede_realizado")
    motivo = ler_csv("fato_rede_extras")
    assert semanal["custo_extra"].sum() == pytest.approx(motivo["custo_extra"].sum())
    assert motivo["participacao_frete"].sum() == pytest.approx(semanal["custo_extra"].sum() / semanal["custo"].sum())


def test_viagens_fecham_entre_realizado_e_pontualidade():
    """Q-PRF-01 e Q-PRF-03 contam as mesmas viagens."""
    assert ler_csv("fato_rede_realizado")["viagens"].sum() == ler_csv("fato_rede_pontualidade")["viagens"].sum()


def test_otd_mensal_reagregado_bate_com_o_motor(dados_rede):
    """A medida % OTD (razão de somas) sobre o fato mensal reproduz o OTD por transportadora."""
    mensal = ler_csv("fato_rede_pontualidade").groupby("transportadora")[["no_prazo", "viagens"]].sum()
    motor = variance.desempenho_transportadoras(dados_rede).set_index("carrier_id")
    for transportadora, linha in mensal.iterrows():
        assert linha["no_prazo"] / linha["viagens"] == pytest.approx(motor.loc[transportadora, "on_time_rate"])


def test_wape_e_bias_da_rede_batem_com_o_motor(dados_rede):
    rede = ler_csv("fato_rede_acuracia").query("nivel == 'NETWORK'")
    motor = forecasting.acuracia_forecast(dados_rede, powerbi_export.VERSAO_FORECAST, "NETWORK").iloc[0]
    assert len(rede) == 1
    assert rede["erro_absoluto"].sum() / rede["realizado"].sum() == pytest.approx(float(motor["wape"]))
    assert rede["erro"].sum() / rede["realizado"].sum() == pytest.approx(float(motor["bias"]))


def test_volume_realizado_e_igual_em_todos_os_niveis_de_acuracia():
    """Trocar o nível muda o erro absoluto, nunca o volume realizado nem o previsto."""
    por_nivel = ler_csv("fato_rede_acuracia").groupby("nivel")[["realizado", "previsto"]].sum()
    assert por_nivel["realizado"].nunique() == 1
    assert por_nivel["previsto"].nunique() == 1


def test_medidas_da_rede_estao_no_dax_com_formato():
    medidas = dict(gerador.ler_medidas())
    esperadas = {
        "Custo Realizado Rede": "\\R$ #,0",
        "Custo por Peca Rede": "\\R$ #,0.00",
        "% Extras sobre Frete": "0.0%",
        "% Viagens Overflow": "0.0%",
        "% OTD": "0.0%",
        "% WAPE Forecast": "0.0%",
        "% Bias Forecast Rede": "0.0%",
        "Meses Abaixo da Meta OTD": "#,0",
    }
    for nome, formato in esperadas.items():
        assert nome in medidas, nome
        assert gerador.formato_medida(nome) == formato, nome
    # medidas de acurácia só respondem com um único nível no contexto
    assert "HASONEVALUE ( fato_rede_acuracia[nivel] )" in medidas["% WAPE Forecast"]
    assert "HASONEVALUE ( fato_rede_acuracia[nivel] )" in medidas["% Bias Forecast"]
