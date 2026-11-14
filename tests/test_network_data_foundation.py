"""Testes da v2.1 — Data Foundation da rede sintética."""

import hashlib
import sqlite3

import pytest

import src.database.connection as connection
from src.analytics.network import data_quality as dq
from src.etl.network.load_network import carregar_network
from src.synthetic.network_generator import (
    escrever_rede,
    fator_sazonal,
    gerar_calendario,
    gerar_rede,
    meses_retail,
    semana_black_friday,
)


def _hashes(diretorio):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(diretorio.glob("*.csv"))}


def test_geracao_reprodutivel(tmp_path, config_rede, rede_gerada):
    """Mesma seed e versão devem produzir arquivos idênticos."""
    escrever_rede(rede_gerada, tmp_path / "a")
    escrever_rede(gerar_rede(config_rede), tmp_path / "b")
    assert _hashes(tmp_path / "a") == _hashes(tmp_path / "b")


def test_seed_diferente_muda_dados(config_rede, rede_gerada):
    outra = gerar_rede(config_rede, seed=7)
    assert not outra.tabelas["tn_demand_history"].equals(rede_gerada.tabelas["tn_demand_history"])


def test_escala_da_rede(dados_rede):
    assert len(dados_rede["tn_dcs"]) == 3
    assert len(dados_rede["tn_stores"]) == 120
    assert 25 <= len(dados_rede["tn_routes"]) <= 40
    assert set(dados_rede["tn_routes"]["route_type"]) >= {"STANDARD", "ALTERNATING_WEEK", "AIR", "TWO_DRIVERS"}
    assert set(dados_rede["tn_stores"]["status"]) == {"ACTIVE", "PLANNED", "CLOSED"}


def test_calendario_retail_454():
    assert meses_retail(52).count(2) == 5 and meses_retail(52).count(1) == 4
    assert len(meses_retail(53)) == 53 and meses_retail(53)[-1] == 12
    cal = gerar_calendario("2026-W01", "2026-W53")
    assert len(cal) == 53
    assert cal.iloc[-1]["retail_month"] == 12


def test_black_friday_e_sazonalidade():
    assert semana_black_friday(2026) == 48  # 27/11/2026
    assert fator_sazonal(48, 48) > 1.4
    assert fator_sazonal(1, 48) < 0.9


def test_integridade_e_cobertura(dados_rede):
    assert dq.checar_integridade_referencial(dados_rede) == []
    assert dq.checar_cobertura_tarifas(dados_rede) == []
    assert dq.checar_atribuicao_lojas(dados_rede) == []
    assert dq.checar_calendario(dados_rede) == []


def test_viagens_reconciliam_com_historico(dados_rede):
    resultado = dq.reconciliar_viagens_historico(dados_rede)
    assert resultado["routes_divergent"] == []
    assert resultado["total_history"] == resultado["total_trips"] > 0


def test_viagens_respeitam_capacidade(dados_rede):
    assert dq.checar_capacidade_viagens(dados_rede) == []


def test_faixas_validas(dados_rede):
    assert (dados_rede["tn_demand_history"]["pieces_shipped"] >= 0).all()
    assert (dados_rede["tn_trips_actual"]["freight_cost"] >= 0).all()
    assert (dados_rede["tn_rates"]["rate_value"] > 0).all()


def test_anomalias_injetadas_sao_detectadas(rede_gerada, dados_rede):
    injetadas = {a["type"]: a["rows"] for a in rede_gerada.relatorio["anomalies"]}
    detectadas = dq.detectar_anomalias_demanda(dados_rede)
    assert detectadas["zero_shipments"] == injetadas["ZERO_SHIPMENT"]
    assert detectadas["missing_rows"] == pytest.approx(injetadas["MISSING_ROW"], rel=0.10)
    assert detectadas["outliers"] >= 0.8 * injetadas["OUTLIER"]


def test_ajustes_gerenciais_tem_motivo_e_aprovacao(dados_rede):
    ajustes = dados_rede["tn_management_adjustments"]
    assert ajustes["reason"].str.len().gt(0).all()
    aprovados = ajustes[ajustes["status"] == "APPROVED"]
    assert aprovados["approved_by_role"].notna().all()


def test_carga_sqlite(tmp_path, monkeypatch, rede_gerada):
    """Os CSVs gerados carregam no SQLite respeitando constraints e FKs."""
    escrever_rede(rede_gerada, tmp_path / "net")
    banco = tmp_path / "net.db"
    monkeypatch.setattr(connection, "CAMINHO_BANCO", banco)
    contagem = carregar_network(tmp_path / "net")
    with sqlite3.connect(banco) as conexao:
        for tabela, linhas in contagem.items():
            assert conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] == linhas
        assert conexao.execute("PRAGMA foreign_key_check").fetchall() == []
