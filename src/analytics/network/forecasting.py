"""Forecast de demanda e medição de acurácia (v2.2).

Modelos baseline implementados em numpy (sem dependências estatísticas):
- SEASONAL_NAIVE: mesma semana do ano anterior;
- MOVING_AVERAGE: média das últimas k semanas;
- HOLT_WINTERS: suavização exponencial multiplicativa (nível, tendência, sazonalidade 52).

Todas as métricas são determinísticas e reproduzíveis.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.analytics.network.repository import DadosRede


SAZONALIDADE = 52
MODELOS = ("SEASONAL_NAIVE", "MOVING_AVERAGE", "HOLT_WINTERS")


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def wape(real, previsto) -> float:
    """Σ|A − F| / Σ A."""
    real, previsto = np.asarray(real, float), np.asarray(previsto, float)
    total = real.sum()
    return float(np.abs(real - previsto).sum() / total) if total else float("nan")


def vies(real, previsto) -> float:
    """Σ(F − A) / Σ A (positivo = super-previsão)."""
    real, previsto = np.asarray(real, float), np.asarray(previsto, float)
    total = real.sum()
    return float((previsto - real).sum() / total) if total else float("nan")


def tracking_signal(real, previsto) -> float:
    """Σ(F − A) / MAD."""
    erro = np.asarray(previsto, float) - np.asarray(real, float)
    mad = np.abs(erro).mean()
    return float(erro.sum() / mad) if mad else 0.0


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

def prever_seasonal_naive(y: np.ndarray, h: int) -> np.ndarray:
    if len(y) < SAZONALIDADE:
        raise ValueError("SEASONAL_NAIVE requer ao menos 52 semanas de histórico")
    ultimo_ano = y[-SAZONALIDADE:]
    return np.array([ultimo_ano[i % SAZONALIDADE] for i in range(h)], float)


def prever_media_movel(y: np.ndarray, h: int, k: int = 8) -> np.ndarray:
    return np.full(h, float(np.mean(y[-k:])))


@dataclass
class AjusteHoltWinters:
    alpha: float
    beta: float
    gamma: float
    sse: float
    nivel: float
    tendencia: float
    sazonal: np.ndarray


def _holt_winters(y: np.ndarray, alpha: float, beta: float, gamma: float) -> AjusteHoltWinters:
    m = SAZONALIDADE
    y = np.maximum(np.asarray(y, float), 1.0)
    nivel = y[:m].mean()
    tendencia = (y[m:2 * m].mean() - y[:m].mean()) / m if len(y) >= 2 * m else 0.0
    sazonal = y[:m] / nivel
    sse = 0.0
    for t in range(m, len(y)):
        s = sazonal[t % m]
        previsto = (nivel + tendencia) * s
        sse += (y[t] - previsto) ** 2
        nivel_anterior = nivel
        nivel = alpha * (y[t] / s) + (1 - alpha) * (nivel + tendencia)
        tendencia = beta * (nivel - nivel_anterior) + (1 - beta) * tendencia
        sazonal[t % m] = gamma * (y[t] / nivel) + (1 - gamma) * s
    return AjusteHoltWinters(alpha, beta, gamma, sse, nivel, tendencia, sazonal)


GRADE_HW = list(itertools.product((0.1, 0.2, 0.35), (0.0, 0.02), (0.05, 0.15, 0.3)))


def ajustar_holt_winters(y: np.ndarray) -> AjusteHoltWinters:
    """Seleciona (alpha, beta, gamma) por SSE one-step-ahead dentro da amostra."""
    if len(y) < SAZONALIDADE + 4:
        raise ValueError("HOLT_WINTERS requer ao menos 56 semanas de histórico")
    return min((_holt_winters(y, a, b, g) for a, b, g in GRADE_HW), key=lambda ajuste: ajuste.sse)


def prever_holt_winters(y: np.ndarray, h: int) -> np.ndarray:
    ajuste = ajustar_holt_winters(y)
    n = len(y)
    return np.array(
        [max(0.0, (ajuste.nivel + (i + 1) * ajuste.tendencia) * ajuste.sazonal[(n + i) % SAZONALIDADE]) for i in range(h)]
    )


def prever(modelo: str, y: np.ndarray, h: int) -> np.ndarray:
    if modelo == "SEASONAL_NAIVE":
        return prever_seasonal_naive(y, h)
    if modelo == "MOVING_AVERAGE":
        return prever_media_movel(y, h)
    if modelo == "HOLT_WINTERS":
        return prever_holt_winters(y, h)
    raise ValueError(f"Modelo desconhecido: {modelo}")


# ---------------------------------------------------------------------------
# Séries
# ---------------------------------------------------------------------------

def demanda_semanal_rota(dados: DadosRede) -> pd.DataFrame:
    """Matriz semana × rota da expedição histórica (semanas sem expedição = 0)."""
    hist = dados["tn_demand_history"].merge(dados.loja_rota, on="store_id")
    matriz = hist.pivot_table(index="week_start", columns="route_id", values="pieces_shipped", aggfunc="sum").fillna(0)
    semanas = dados["tn_calendar"]["week_start"]
    semanas = semanas[(semanas >= matriz.index.min()) & (semanas <= matriz.index.max())]
    return matriz.reindex(semanas, fill_value=0)


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

def backtest(
    dados: DadosRede,
    origens: list[str] | None = None,
    horizonte: int = 13,
    modelos: tuple[str, ...] = MODELOS,
) -> pd.DataFrame:
    """Backtest com origem móvel; retorna erros por rota × modelo × origem."""
    matriz = demanda_semanal_rota(dados)
    semanas = list(matriz.index)
    if origens is None:
        # origens a cada 4 semanas, com ≥ 60 semanas de treino e horizonte completo
        origens = semanas[60:len(semanas) - horizonte:4]
    linhas = []
    for origem in origens:
        corte = semanas.index(origem)
        for rota in matriz.columns:
            y = matriz[rota].to_numpy(float)
            treino, teste = y[:corte], y[corte:corte + horizonte]
            if treino[-SAZONALIDADE:].sum() == 0 or teste.sum() == 0:
                continue
            for modelo in modelos:
                previsto = prever(modelo, treino, len(teste))
                linhas.append(
                    {
                        "origin": origem,
                        "route_id": rota,
                        "model": modelo,
                        "actual": float(teste.sum()),
                        "abs_error": float(np.abs(teste - previsto).sum()),
                        "error": float((previsto - teste).sum()),
                    }
                )
    return pd.DataFrame(linhas)


def resumir_backtest(resultado: pd.DataFrame) -> pd.DataFrame:
    """WAPE e viés por rota × modelo; melhor modelo e FVA contra o naïve sazonal."""
    agregado = resultado.groupby(["route_id", "model"]).agg(actual=("actual", "sum"), abs_error=("abs_error", "sum"), error=("error", "sum"))
    agregado["wape"] = agregado["abs_error"] / agregado["actual"]
    agregado["bias"] = agregado["error"] / agregado["actual"]
    tabela = agregado["wape"].unstack("model")
    melhor = tabela.idxmin(axis=1)
    resumo = pd.DataFrame(
        {
            "best_model": melhor,
            "best_wape": tabela.min(axis=1),
            "naive_wape": tabela["SEASONAL_NAIVE"],
        }
    )
    resumo["fva_vs_naive"] = resumo["naive_wape"] - resumo["best_wape"]
    for modelo in tabela.columns:
        resumo[f"wape_{modelo.lower()}"] = tabela[modelo]
    return resumo.reset_index()


def resumo_rede_backtest(resultado: pd.DataFrame) -> pd.DataFrame:
    """WAPE e viés de rede por modelo (peso = volume)."""
    agregado = resultado.groupby("model").agg(actual=("actual", "sum"), abs_error=("abs_error", "sum"), error=("error", "sum"))
    agregado["wape"] = agregado["abs_error"] / agregado["actual"]
    agregado["bias"] = agregado["error"] / agregado["actual"]
    return agregado[["wape", "bias"]].reset_index()


# ---------------------------------------------------------------------------
# Acurácia de uma versão de forecast armazenada
# ---------------------------------------------------------------------------

NIVEIS = {"STORE": ["store_id"], "ROUTE": ["route_id"], "DC": ["dc_id"], "NETWORK": []}


def acuracia_forecast(dados: DadosRede, versao: str, nivel: str = "ROUTE", por_mes: bool = False) -> pd.DataFrame:
    """Compara uma versão de forecast com a expedição realizada (semanas em comum)."""
    if nivel not in NIVEIS:
        raise ValueError(f"Nível inválido: {nivel}")
    chaves = ["week_start", "store_id", "brand", "channel"]
    fc = dados["tn_forecast"]
    fc = fc[fc["forecast_version"] == versao]
    if fc.empty:
        raise ValueError(f"Versão de forecast não encontrada: {versao}")
    hist = dados["tn_demand_history"]
    base = fc[chaves + ["forecast_pieces"]].merge(hist[chaves + ["pieces_shipped"]], on=chaves, how="outer")
    base = base[base["week_start"].between(fc["week_start"].min(), hist["week_start"].max())]
    base = base.fillna({"forecast_pieces": 0, "pieces_shipped": 0})
    base = base.merge(dados.loja_rota, on="store_id").merge(dados["tn_routes"][["route_id", "dc_id"]], on="route_id")

    grupos = list(NIVEIS[nivel])
    if por_mes:
        base = base.merge(dados["tn_calendar"][["week_start", "retail_year", "retail_month"]], on="week_start")
        grupos += ["retail_year", "retail_month"]
    # erro absoluto é calculado no nível solicitado (agregação antes do |erro|)
    agreg = base.groupby(grupos + ["week_start"], dropna=False)[["forecast_pieces", "pieces_shipped"]].sum().reset_index() if grupos else (
        base.groupby("week_start")[["forecast_pieces", "pieces_shipped"]].sum().reset_index()
    )
    agreg["abs_error"] = (agreg["forecast_pieces"] - agreg["pieces_shipped"]).abs()
    agreg["error"] = agreg["forecast_pieces"] - agreg["pieces_shipped"]
    if grupos:
        saida = agreg.groupby(grupos).agg(actual=("pieces_shipped", "sum"), forecast=("forecast_pieces", "sum"),
                                          abs_error=("abs_error", "sum"), error=("error", "sum")).reset_index()
    else:
        saida = pd.DataFrame([{"actual": agreg["pieces_shipped"].sum(), "forecast": agreg["forecast_pieces"].sum(),
                               "abs_error": agreg["abs_error"].sum(), "error": agreg["error"].sum()}])
    saida["wape"] = saida["abs_error"] / saida["actual"]
    saida["bias"] = saida["error"] / saida["actual"]
    saida.insert(0, "forecast_version", versao)
    return saida


def variabilidade_demanda(dados: DadosRede, ultimas_semanas: int = 52) -> pd.DataFrame:
    """Coeficiente de variação semanal por loja (últimas N semanas)."""
    hist = dados["tn_demand_history"]
    semanas = sorted(hist["week_start"].unique())[-ultimas_semanas:]
    serie = hist[hist["week_start"].isin(semanas)].groupby(["store_id", "week_start"])["pieces_shipped"].sum().unstack(fill_value=0)
    cv = (serie.std(axis=1) / serie.mean(axis=1)).rename("cv")
    return cv.reset_index().merge(dados["tn_stores"][["store_id", "cluster", "uf"]], on="store_id").sort_values("cv", ascending=False)


# ---------------------------------------------------------------------------
# Geração de forecast pelo motor
# ---------------------------------------------------------------------------

def gerar_forecast_modelo(
    dados: DadosRede,
    versao: str,
    semana_inicio: str,
    semana_fim: str,
    modelo_por_rota: dict[str, str] | None = None,
    semanas_participacao: int = 26,
    versao_lojas_novas: str | None = None,
    ultima_semana_historico: str | None = None,
) -> pd.DataFrame:
    """Forecast por rota (melhor modelo) desagregado para loja × marca × canal.

    Lojas sem histórico (inaugurações futuras) não são cobertas pelo modelo;
    se `versao_lojas_novas` for informada, suas linhas são copiadas dessa versão.
    """
    matriz = demanda_semanal_rota(dados)
    if ultima_semana_historico:
        matriz = matriz[matriz.index <= ultima_semana_historico]
    cal = dados["tn_calendar"]
    alvo = cal[(cal["week_start"] >= semana_inicio) & (cal["week_start"] <= semana_fim)]["week_start"].tolist()
    ultima = matriz.index.max()
    passos = len(cal[(cal["week_start"] > ultima) & (cal["week_start"] <= semana_fim)])

    hist = dados["tn_demand_history"].merge(dados.loja_rota, on="store_id")
    hist = hist[hist["week_start"] <= ultima]
    recentes = sorted(hist["week_start"].unique())[-semanas_participacao:]
    participacao = hist[hist["week_start"].isin(recentes)].groupby(["route_id", "store_id", "brand", "channel"])["pieces_shipped"].sum()
    participacao = participacao / participacao.groupby("route_id").transform("sum")
    # lojas já fechadas na data de corte não recebem forecast
    lojas = dados["tn_stores"]
    fechadas = set(lojas.loc[lojas["closing_date"].notna() & (lojas["closing_date"] <= ultima), "store_id"])
    participacao = participacao[~participacao.index.get_level_values("store_id").isin(fechadas)]
    participacao = participacao / participacao.groupby("route_id").transform("sum")

    semanas_futuras = cal[cal["week_start"] > ultima]["week_start"].tolist()[:passos]
    blocos = []
    for rota in matriz.columns:
        modelo = (modelo_por_rota or {}).get(rota, "HOLT_WINTERS")
        previsto = pd.Series(prever(modelo, matriz[rota].to_numpy(float), passos), index=semanas_futuras)
        previsto = previsto[previsto.index.isin(alvo)]
        if rota not in participacao.index.get_level_values("route_id"):
            continue
        shares = participacao.loc[rota]
        for (store, brand, channel), share in shares.items():
            blocos.append(pd.DataFrame({"week_start": previsto.index, "store_id": store, "brand": brand, "channel": channel,
                                        "forecast_pieces": np.round(previsto.to_numpy() * share).astype(int), "model_name": modelo}))
    fc = pd.concat(blocos, ignore_index=True)

    if versao_lojas_novas:
        com_historico = set(hist["store_id"])
        base = dados["tn_forecast"]
        novas = base[(base["forecast_version"] == versao_lojas_novas) & (~base["store_id"].isin(com_historico))
                     & (base["week_start"].isin(alvo))].copy()
        novas["model_name"] = f"COPIED_FROM:{versao_lojas_novas}"
        fc = pd.concat([fc, novas[fc.columns]], ignore_index=True)

    fc.insert(0, "forecast_version", versao)
    fc["created_at"] = ultima
    return fc
