"""
Exporta os dados do Copilot no formato consumido pelo kit Power BI
(reports/powerbi/kit/data).

Convenção dos CSVs (igual a output/inventory_analysis.csv):
separador ";", decimal ",", UTF-8 com BOM.

As tabelas da rede (fato_rede_* e dim_rede_rotas) saem das consultas de
sql/network, executadas sobre a rede sintética gerada a partir da configuração.

Uso:
    python scripts/export_powerbi_kit.py
"""

import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics.network import powerbi_export  # noqa: E402
from src.synthetic.network_generator import carregar_config, gerar_rede  # noqa: E402


CAMINHO_DB = "database/supply_chain.db"
CAMINHO_ESTOQUE = "output/inventory_analysis.csv"
PASTA_SAIDA = "reports/powerbi/kit/data"

# Coordenadas ilustrativas (0-760 x 0-380) usadas pelo mapa de rede em Deneb.
# As rotas não têm geografia real no banco; o layout é apenas visual.
COORDENADAS_NOS = {
    "DC01": (300, 190),
    "DC02": (470, 220),
    "DEST001": (360, 140),
    "DEST002": (250, 100),
    "DEST003": (200, 230),
    "DEST004": (230, 300),
    "DEST005": (330, 320),
    "DEST006": (170, 160),
    "DEST007": (520, 180),
    "DEST008": (560, 280),
    "DEST009": (590, 120),
    "DEST010": (480, 340),
    "DEST011": (630, 220),
    "DEST012": (430, 60),
}


def salvar(df: pd.DataFrame, nome: str) -> None:
    caminho = os.path.join(PASTA_SAIDA, nome)
    df.to_csv(caminho, sep=";", decimal=",", index=False, encoding="utf-8-sig")
    print(f"{caminho}: {len(df)} linhas")


def carregar_transporte(conexao: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    rotas = pd.read_sql("SELECT * FROM routes", conexao)
    veiculos = pd.read_sql("SELECT * FROM vehicle_types", conexao)
    viagens = pd.read_sql("SELECT * FROM planned_trips", conexao)
    demanda = pd.read_sql("SELECT * FROM demand_forecast", conexao)
    return {"rotas": rotas, "veiculos": veiculos, "viagens": viagens, "demanda": demanda}


def montar_dim_rotas(rotas: pd.DataFrame) -> pd.DataFrame:
    dim = rotas.rename(
        columns={
            "route_id": "rota",
            "origin_id": "origem",
            "destination_id": "destino",
            "distance_km": "distancia_km",
        }
    )
    dim["origem_x"] = dim["origem"].map(lambda n: COORDENADAS_NOS[n][0])
    dim["origem_y"] = dim["origem"].map(lambda n: COORDENADAS_NOS[n][1])
    dim["destino_x"] = dim["destino"].map(lambda n: COORDENADAS_NOS[n][0])
    dim["destino_y"] = dim["destino"].map(lambda n: COORDENADAS_NOS[n][1])
    return dim


def montar_dim_semana(viagens: pd.DataFrame) -> pd.DataFrame:
    semanas = sorted(viagens["week_start"].unique())
    return pd.DataFrame(
        {
            "semana_inicio": semanas,
            "semana_ordem": range(1, len(semanas) + 1),
            "semana_label": [f"S{i}" for i in range(1, len(semanas) + 1)],
        }
    )


def montar_insights(estoque: pd.DataFrame, viagens: pd.DataFrame) -> pd.DataFrame:
    """
    Resumo executivo determinístico exibido no painel "Copilot Insight".
    Pode ser substituído por uma resposta salva do endpoint /copilot.
    """
    repor_alta = estoque[
        (estoque["acao_recomendada"] == "REPOR") & (estoque["prioridade"] == "ALTA")
    ]
    risco = int((estoque["risco_ruptura"] == "SIM").sum())
    reposicao_mi = estoque["valor_reposicao"].sum() / 1e6

    custo_rota = viagens.groupby("route_id")["planned_cost"].sum().sort_values(ascending=False)
    top2 = custo_rota.head(2)
    share_top2 = top2.sum() / custo_rota.sum() * 100

    deposito = estoque.groupby("deposito")["valor_estoque"].sum().sort_values(ascending=False)

    def brl(valor: float) -> str:
        return f"{valor:.2f}".replace(".", ",")

    return pd.DataFrame(
        [
            {
                "ordem": 1,
                "tag": "ALTA",
                "titulo": f"Repor {len(repor_alta)} SKUs críticos",
                "detalhe": f"{risco} itens com risco de ruptura, R$ {brl(reposicao_mi)} Mi em reposição.",
            },
            {
                "ordem": 2,
                "tag": "CUSTO",
                "titulo": f"Revisar {top2.index[0]} e {top2.index[1]}",
                "detalhe": f"Juntas somam {share_top2:.0f}% do custo de transporte.",
            },
            {
                "ordem": 3,
                "tag": "CAPITAL",
                "titulo": f"Liberar excesso no {deposito.index[0]}",
                "detalhe": f"Maior valor em estoque da rede (R$ {brl(deposito.iloc[0] / 1e6)} Mi).",
            },
        ]
    )


def exportar_rede() -> None:
    """Tabelas da rede (v2.x), geradas pelas consultas de sql/network."""
    rede = gerar_rede(carregar_config())
    conexao = powerbi_export.conexao_em_memoria(rede.tabelas)
    try:
        for nome, linhas in powerbi_export.exportar(conexao, PASTA_SAIDA).items():
            print(f"{os.path.join(PASTA_SAIDA, nome + '.csv')}: {linhas} linhas")
    finally:
        conexao.close()


def main() -> None:
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    with sqlite3.connect(CAMINHO_DB) as conexao:
        transporte = carregar_transporte(conexao)

    estoque = pd.read_csv(CAMINHO_ESTOQUE, sep=";", decimal=",", encoding="utf-8-sig")

    viagens = transporte["viagens"].rename(
        columns={
            "trip_id": "viagem",
            "week_start": "semana_inicio",
            "route_id": "rota",
            "vehicle_type_id": "veiculo",
            "planned_pieces": "pecas_planejadas",
            "planned_capacity": "capacidade_planejada",
            "planned_cost": "custo_planejado",
        }
    )
    demanda = transporte["demanda"].rename(
        columns={"week_start": "semana_inicio", "route_id": "rota", "forecast_pieces": "pecas_previstas"}
    )
    veiculos = transporte["veiculos"].rename(
        columns={"vehicle_type_id": "veiculo", "vehicle_name": "tipo_veiculo", "capacity_pieces": "capacidade_pecas"}
    )

    salvar(estoque, "fato_estoque.csv")
    salvar(viagens, "fato_viagens.csv")
    salvar(demanda, "fato_demanda.csv")
    salvar(montar_dim_rotas(transporte["rotas"]), "dim_rotas.csv")
    salvar(veiculos, "dim_veiculos.csv")
    salvar(montar_dim_semana(transporte["viagens"]), "dim_semana.csv")
    salvar(montar_insights(estoque, transporte["viagens"]), "copilot_insights.csv")
    exportar_rede()


if __name__ == "__main__":
    main()
