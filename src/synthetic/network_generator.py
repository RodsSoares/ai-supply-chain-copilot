"""Gerador determinístico da rede sintética de Transportation (v2.1).

Todos os dados são 100% sintéticos. O gerador reconstrói uma classe de
problema de planejamento de transportes (rede multi-CD, lojas, rotas,
sazonalidade, tarifas, execução) sem reproduzir nenhuma operação real.

Mesma seed + mesmo dataset_version => arquivos idênticos.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


CAMINHO_CONFIG = Path("config/synthetic_network.json")
DIRETORIO_SAIDA = Path("data/synthetic/transportation/network")

SEMANAS_ANO_ANTERIOR = 52
FERIADOS_FIXOS = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)]


# ---------------------------------------------------------------------------
# Utilidades de calendário
# ---------------------------------------------------------------------------

def semana_iso_para_data(semana: str) -> date:
    """Converte 'YYYY-Www' na segunda-feira da semana ISO."""
    ano, numero = semana.split("-W")
    return date.fromisocalendar(int(ano), int(numero), 1)


def semana_black_friday(ano: int) -> int:
    """Semana ISO que contém a quarta sexta-feira de novembro."""
    primeiro = date(ano, 11, 1)
    deslocamento = (4 - primeiro.weekday()) % 7
    black_friday = primeiro + timedelta(days=deslocamento + 21)
    return black_friday.isocalendar()[1]


def meses_retail(semanas_no_ano: int) -> list[int]:
    """Mês retail (4-5-4) de cada semana do ano; a 53ª semana vai para dezembro."""
    padrao = [4, 5, 4] * 4
    meses = []
    for mes, quantidade in enumerate(padrao, start=1):
        meses.extend([mes] * quantidade)
    if semanas_no_ano == 53:
        meses.append(12)
    return meses


def gerar_calendario(primeira: str, ultima: str) -> pd.DataFrame:
    """Gera o calendário semanal (ISO, retail 4-5-4, civil e sazonalidade)."""
    inicio = semana_iso_para_data(primeira)
    fim = semana_iso_para_data(ultima)
    linhas = []
    indice = 0
    atual = inicio
    while atual <= fim:
        ano_iso, semana_iso, _ = atual.isocalendar()
        semanas_ano = date(ano_iso, 12, 28).isocalendar()[1]
        meses = meses_retail(semanas_ano)
        mes_retail = meses[semana_iso - 1]
        semana_do_mes = sum(1 for m in meses[:semana_iso] if m == mes_retail)

        dias = [atual + timedelta(days=d) for d in range(7)]
        participacao: dict[str, float] = {}
        for dia in dias:
            chave = f"{dia.year:04d}-{dia.month:02d}"
            participacao[chave] = participacao.get(chave, 0) + 1 / 7
        participacao = {k: round(v, 6) for k, v in participacao.items()}

        feriados = sum(1 for dia in dias if (dia.month, dia.day) in FERIADOS_FIXOS)

        semana_bf = semana_black_friday(ano_iso)
        if semana_iso == semana_bf:
            flag = "BLACK_FRIDAY"
        elif 49 <= semana_iso <= 51:
            flag = "CHRISTMAS"
        elif 19 <= semana_iso <= 26:
            flag = "WINTER"
        elif 4 <= semana_iso <= 7:
            flag = "BACK_TO_SCHOOL"
        else:
            flag = "NORMAL"

        linhas.append(
            {
                "week_start": atual.isoformat(),
                "week_idx": indice,
                "iso_year": ano_iso,
                "iso_week": semana_iso,
                "retail_year": ano_iso,
                "retail_month": mes_retail,
                "retail_week_of_month": semana_do_mes,
                "civil_month_share_json": json.dumps(participacao, sort_keys=True),
                "season_flag": flag,
                "holiday_count": feriados,
            }
        )
        atual += timedelta(days=7)
        indice += 1
    return pd.DataFrame(linhas)


def _sino(x: float, centro: float, largura: float) -> float:
    return math.exp(-0.5 * ((x - centro) / largura) ** 2)


def fator_sazonal(semana_iso: int, semana_bf: int) -> float:
    """Curva sazonal sintética de expedição (multiplicativa, média ≈ 1)."""
    w = semana_iso
    fator = 1.0
    fator += 0.25 * _sino(w, 22, 3.0)      # abastecimento de inverno
    fator += 0.10 * _sino(w, 6, 1.5)       # volta às aulas
    fator += 0.10 * _sino(w, 40, 3.0)      # coleção primavera/verão
    fator += 0.55 * _sino(w, semana_bf, 0.7)
    fator += 0.45 * _sino(w, 50, 1.1)      # Natal
    fator -= 0.20 * _sino(w, 1.5, 1.2)     # janeiro fraco
    fator -= 0.30 * _sino(w, 52.5, 0.7)    # última semana do ano
    return fator


# ---------------------------------------------------------------------------
# Estrutura de saída
# ---------------------------------------------------------------------------

@dataclass
class RedeSintetica:
    """Conjunto completo de tabelas geradas."""

    tabelas: dict[str, pd.DataFrame] = field(default_factory=dict)
    relatorio: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Gerador
# ---------------------------------------------------------------------------

class GeradorRede:
    """Gera a rede sintética completa a partir da configuração."""

    def __init__(self, config: dict, seed: int | None = None):
        self.config = config
        self.seed = config["seed"] if seed is None else seed
        self.rng = np.random.default_rng(self.seed)
        self.rede = RedeSintetica()
        self.anomalias: list[dict] = []

    # -- Mestres -------------------------------------------------------------

    def gerar_lojas(self) -> pd.DataFrame:
        cfg = self.config["stores"]
        clusters = list(cfg["cluster_weights"].keys())
        pesos = np.array(list(cfg["cluster_weights"].values()))
        linhas = []
        numero = 1
        for uf, info in self.config["ufs"].items():
            n_cidades = max(1, math.ceil(info["stores"] / 4))
            offsets = sorted(self.rng.uniform(0, cfg["max_city_offset_km"], n_cidades))
            offsets[0] = 0.0
            for i in range(info["stores"]):
                cidade = i % n_cidades
                cluster = str(self.rng.choice(clusters, p=pesos))
                linhas.append(
                    {
                        "store_id": f"ST{numero:04d}",
                        "store_name": f"Store {numero:04d}",
                        "brand_set": "",
                        "city": f"{uf}_C{cidade + 1:02d}",
                        "uf": uf,
                        "cluster": cluster,
                        "opening_date": "2019-01-01",
                        "closing_date": None,
                        "status": "ACTIVE",
                        "primary_dc_id": info["dc_id"],
                        "_city_offset_km": float(offsets[cidade]),
                        "_mode": info["mode"],
                    }
                )
                numero += 1
        lojas = pd.DataFrame(linhas)

        # Inaugurações e fechamentos
        inicio, fim = (date.fromisoformat(d) for d in cfg["opening_window"])
        janela = (fim - inicio).days
        candidatas = lojas.index[lojas["_mode"] == "ROAD"].to_numpy()
        escolhidas = self.rng.choice(candidatas, cfg["openings"] + cfg["closures"], replace=False)
        aberturas = escolhidas[: cfg["openings"]]
        fechamentos = escolhidas[cfg["openings"]:]
        for idx in aberturas:
            dia = inicio + timedelta(days=int(self.rng.integers(0, janela)))
            lojas.loc[idx, "opening_date"] = dia.isoformat()
            lojas.loc[idx, "status"] = "ACTIVE" if dia <= date(2026, 11, 14) else "PLANNED"
        for idx in fechamentos:
            lojas.loc[idx, "closing_date"] = cfg["closing_date"]
            lojas.loc[idx, "status"] = "CLOSED"

        # Marcas
        conjuntos = []
        for _, loja in lojas.iterrows():
            marcas = ["BRAND_A"]
            if self.rng.random() < cfg["brand_b_probability"]:
                marcas.append("BRAND_B")
            if loja["cluster"] != "S" and self.rng.random() < cfg["brand_c_probability"]:
                marcas.append("BRAND_C")
            conjuntos.append("|".join(marcas))
        lojas["brand_set"] = conjuntos
        return lojas

    def gerar_veiculos(self) -> pd.DataFrame:
        return pd.DataFrame(self.config["vehicles"])

    def gerar_carriers(self) -> pd.DataFrame:
        return pd.DataFrame(self.config["carriers"]).drop(columns=["on_time_probability"])

    # -- Demanda -------------------------------------------------------------

    def gerar_series(self, lojas: pd.DataFrame) -> pd.DataFrame:
        """Cria as séries loja × marca × canal com nível, tendência e ruído."""
        cfg = self.config["stores"]
        linhas = []
        for _, loja in lojas.iterrows():
            marcas = loja["brand_set"].split("|")
            share_total = sum(cfg["brand_share"][m] for m in marcas)
            base_loja = cfg["cluster_base_weekly_pieces"][loja["cluster"]] * self.rng.uniform(0.85, 1.15)
            tendencia = self.rng.normal(cfg["annual_trend_mean"], cfg["annual_trend_sd"])
            tem_ecom = loja["cluster"] in ("L", "XL") and self.rng.random() < cfg["ecom_probability_l_xl"]
            for marca in marcas:
                nivel_marca = base_loja * cfg["brand_share"][marca] / share_total
                canais = [("STORE", 1.0)]
                if tem_ecom and marca == "BRAND_A":
                    canais.append(("ECOM_REPLENISHMENT", cfg["ecom_share"]))
                for canal, fator in canais:
                    linhas.append(
                        {
                            "store_id": loja["store_id"],
                            "brand": marca,
                            "channel": canal,
                            "base_level": nivel_marca * fator,
                            "trend": tendencia,
                            "noise_cv": cfg["cluster_noise_cv"][loja["cluster"]],
                            "opening_date": loja["opening_date"],
                            "closing_date": loja["closing_date"],
                        }
                    )
        return pd.DataFrame(linhas)

    def gerar_demanda_verdadeira(self, series: pd.DataFrame, calendario: pd.DataFrame) -> pd.DataFrame:
        """Demanda 'verdadeira' semanal para todo o horizonte (base para histórico e forecasts)."""
        cfg = self.config["stores"]
        semanas = calendario[["week_start", "week_idx", "iso_year", "iso_week", "holiday_count"]].copy()
        semanas["week_date"] = pd.to_datetime(semanas["week_start"])
        sazonal = np.array(
            [fator_sazonal(w, semana_black_friday(a)) for a, w in zip(semanas["iso_year"], semanas["iso_week"])]
        )
        feriado = 1 - 0.08 * semanas["holiday_count"].to_numpy()
        anos = (semanas["week_idx"].to_numpy()) / 52.0
        datas = semanas["week_date"].to_numpy()

        blocos = []
        for _, serie in series.iterrows():
            abertura = np.datetime64(serie["opening_date"])
            fechamento = np.datetime64(serie["closing_date"]) if pd.notna(serie["closing_date"]) else None
            semanas_abertas = (datas - abertura) / np.timedelta64(7, "D")
            rampa = np.clip(0.4 + 0.6 * semanas_abertas / cfg["ramp_up_weeks"], 0, 1)
            ativo = semanas_abertas >= 0
            if fechamento is not None:
                ativo &= datas < fechamento
            ruido = self.rng.lognormal(-0.5 * serie["noise_cv"] ** 2, serie["noise_cv"], len(semanas))
            valor = serie["base_level"] * (1 + serie["trend"]) ** anos * sazonal * feriado * rampa * ruido
            valor = np.where(ativo, np.round(valor), np.nan)
            bloco = pd.DataFrame(
                {
                    "week_start": semanas["week_start"].to_numpy(),
                    "week_idx": semanas["week_idx"].to_numpy(),
                    "store_id": serie["store_id"],
                    "brand": serie["brand"],
                    "channel": serie["channel"],
                    "true_pieces": valor,
                }
            )
            blocos.append(bloco.dropna(subset=["true_pieces"]))
        demanda = pd.concat(blocos, ignore_index=True)
        demanda["true_pieces"] = demanda["true_pieces"].astype(int)
        return demanda

    def gerar_historico(self, verdade: pd.DataFrame, calendario: pd.DataFrame) -> pd.DataFrame:
        """Histórico de expedição até a última semana realizada, com anomalias injetadas."""
        cfg = self.config["anomalies"]
        ultima = semana_iso_para_data(self.config["horizon"]["history_last_week"]).isoformat()
        hist = verdade[verdade["week_start"] <= ultima].copy().reset_index(drop=True)
        hist["pieces_shipped"] = hist["true_pieces"]

        sorteio = self.rng.random(len(hist))
        zeros = sorteio < cfg["zero_rate"]
        faltantes = (sorteio >= cfg["zero_rate"]) & (sorteio < cfg["zero_rate"] + cfg["missing_rate"])
        outliers = (sorteio >= cfg["zero_rate"] + cfg["missing_rate"]) & (
            sorteio < cfg["zero_rate"] + cfg["missing_rate"] + cfg["outlier_rate"]
        )
        multiplicadores = self.rng.uniform(*cfg["outlier_multiplier_range"], len(hist))
        hist.loc[zeros, "pieces_shipped"] = 0
        hist.loc[outliers, "pieces_shipped"] = np.round(hist.loc[outliers, "true_pieces"] * multiplicadores[outliers]).astype(int)

        self.anomalias = [
            {"type": "ZERO_SHIPMENT", "rows": int(zeros.sum())},
            {"type": "MISSING_ROW", "rows": int(faltantes.sum())},
            {"type": "OUTLIER", "rows": int(outliers.sum())},
        ]
        hist = hist[~faltantes]
        return hist[["week_start", "store_id", "brand", "channel", "pieces_shipped"]].reset_index(drop=True)

    def gerar_forecasts(self, verdade: pd.DataFrame, calendario: pd.DataFrame) -> pd.DataFrame:
        """Forecasts de orçamento no estilo do time de planejamento.

        Prática comum simulada: mesma semana ISO do ano anterior × premissa de
        crescimento por loja × ruído. Isso herda deslocamentos de calendário
        (ex.: Black Friday muda de semana) e o viés otimista da premissa.
        Lojas sem ano anterior usam uma estimativa do planejador (nível real × viés).
        """
        anos = calendario.set_index("week_start")["iso_year"]
        chaves = ["store_id", "brand", "channel"]
        ano_anterior = verdade[chaves + ["week_idx", "true_pieces"]].copy()
        ano_anterior["week_idx"] += SEMANAS_ANO_ANTERIOR
        ano_anterior = ano_anterior.rename(columns={"true_pieces": "ly_pieces"})
        blocos = []
        for versao, cfg in self.config["forecasts"].items():
            sub = verdade[verdade["week_start"].map(anos) == cfg["year"]].copy()
            sub = sub.merge(ano_anterior, on=chaves + ["week_idx"], how="left")
            lojas = sub["store_id"].unique()
            crescimento = dict(zip(lojas, self.rng.normal(cfg["growth_mean"], cfg["growth_sd"], len(lojas))))
            ruido = self.rng.lognormal(-0.5 * cfg["noise_cv"] ** 2, cfg["noise_cv"], len(sub))
            fator = 1 + sub["store_id"].map(crescimento)
            base = np.where(sub["ly_pieces"].notna(), sub["ly_pieces"], sub["true_pieces"])
            sub["forecast_pieces"] = np.round(base * fator * ruido).astype(int)
            sub["forecast_version"] = versao
            sub["model_name"] = np.where(sub["ly_pieces"].notna(), "PLANNING_LY_PLUS_GROWTH", "PLANNING_NEW_STORE_ESTIMATE")
            sub["created_at"] = cfg["created_at"]
            blocos.append(sub)
        fc = pd.concat(blocos, ignore_index=True)
        return fc[["forecast_version", "week_start", "store_id", "brand", "channel", "forecast_pieces", "model_name", "created_at"]]

    # -- Rotas ---------------------------------------------------------------

    def gerar_rotas(self, lojas: pd.DataFrame, verdade: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        cfg = self.config["routes"]
        limites = cfg["profile_thresholds_km"]
        media_loja = (
            verdade[verdade["week_start"].str.startswith("2025")]
            .groupby("store_id")["true_pieces"].sum()
            / 52
        )
        # lojas novas sem histórico 2025: usa nível base aproximado pelo cluster
        base_cluster = self.config["stores"]["cluster_base_weekly_pieces"]

        rotas, paradas = [], []
        carriers_dc = {"DC01": ["ATLAS", "NOVA"], "DC02": ["NOVA"], "DC03": ["ORION"]}
        numero = 1
        for uf, info in self.config["ufs"].items():
            lojas_uf = lojas[lojas["uf"] == uf].sort_values(["_city_offset_km", "store_id"])
            grupos, atual, volume = [], [], 0.0
            for _, loja in lojas_uf.iterrows():
                vol = float(media_loja.get(loja["store_id"], base_cluster[loja["cluster"]]))
                limite_stops = 99 if info["mode"] == "AIR" else cfg["max_stops"]
                if atual and (len(atual) >= limite_stops or (info["mode"] == "ROAD" and volume + vol > cfg["max_weekly_pieces"])):
                    grupos.append(atual)
                    atual, volume = [], 0.0
                atual.append(loja)
                volume += vol
            if atual:
                grupos.append(atual)

            for grupo in grupos:
                route_id = f"NR{numero:03d}"
                distancia = info["base_km"] + max(l["_city_offset_km"] for l in grupo) + cfg["km_per_extra_stop"] * (len(grupo) - 1)
                distancia = round(float(distancia), 1)
                if info["mode"] == "AIR":
                    tipo, perfil = "AIR", "LONG"
                else:
                    perfil = "SHORT" if distancia < limites["short_max"] else ("MEDIUM" if distancia <= limites["medium_max"] else "LONG")
                    tipo = "TWO_DRIVERS" if distancia >= cfg["two_drivers_min_km"] else "STANDARD"
                carrier = carriers_dc[info["dc_id"]][numero % len(carriers_dc[info["dc_id"]])]
                if info["mode"] == "AIR":
                    carrier = "ATLAS"
                rotas.append(
                    {
                        "route_id": route_id,
                        "dc_id": info["dc_id"],
                        "carrier_id": carrier,
                        "route_type": tipo,
                        "distance_km": distancia,
                        "stops_count": len(grupo),
                        "route_profile": perfil,
                        "uf": uf,
                        "active_from": "2024-01-01",
                        "active_to": None,
                    }
                )
                for seq, loja in enumerate(grupo, start=1):
                    paradas.append(
                        {
                            "route_id": route_id,
                            "store_id": loja["store_id"],
                            "stop_sequence": seq,
                            "valid_from": max("2024-01-01", loja["opening_date"]),
                            "valid_to": loja["closing_date"] if pd.notna(loja["closing_date"]) else None,
                        }
                    )
                numero += 1
        return pd.DataFrame(rotas), pd.DataFrame(paradas)

    def definir_veiculos_rotas(self, rotas: pd.DataFrame, paradas: pd.DataFrame, verdade: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Define veículos elegíveis, default e rotas de semana alternada."""
        veiculos = pd.DataFrame(self.config["vehicles"]).set_index("vehicle_type_id")
        freq_min = {"SHORT": 3, "MEDIUM": 2, "LONG": 1}
        volume_rota = (
            verdade[verdade["week_start"].str.startswith("2025")]
            .merge(paradas[["route_id", "store_id"]], on="store_id")
            .groupby("route_id")["true_pieces"].sum()
            / 52
        )
        opcoes = []
        rotas = rotas.copy()
        for i, rota in rotas.iterrows():
            if rota["route_type"] == "AIR":
                opcoes.append({"route_id": rota["route_id"], "vehicle_type_id": "NA01", "is_default": 1})
                continue
            elegiveis = self.config["eligible_vehicles_by_profile"][rota["route_profile"]]
            vol = float(volume_rota.get(rota["route_id"], 0))
            freq = freq_min[rota["route_profile"]]
            default = elegiveis[-1]
            for v in elegiveis:
                if vol / (freq * veiculos.loc[v, "capacity_pieces"]) <= 1.10:
                    default = v
                    break
            if rota["route_profile"] == "LONG" and vol < 0.45 * veiculos.loc[default, "capacity_pieces"]:
                rotas.loc[i, "route_type"] = "ALTERNATING_WEEK"
            for v in elegiveis:
                opcoes.append({"route_id": rota["route_id"], "vehicle_type_id": v, "is_default": int(v == default)})
        return rotas, pd.DataFrame(opcoes)

    def gerar_tarifas(self, rotas: pd.DataFrame, opcoes: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config["rates"]
        veiculos = pd.DataFrame(self.config["vehicles"]).set_index("vehicle_type_id")
        rotas_idx = rotas.set_index("route_id")
        linhas = []
        for _, op in opcoes.iterrows():
            rota = rotas_idx.loc[op["route_id"]]
            if rota["route_type"] == "AIR":
                base, basis = round(float(self.rng.uniform(*cfg["air_rate_per_piece_range"])), 4), "PER_PIECE"
            else:
                v = veiculos.loc[op["vehicle_type_id"]]
                base = (v["fixed_cost"] + v["cost_per_km"] * rota["distance_km"]) * self.rng.uniform(*cfg["noise_range"])
                if rota["route_type"] == "TWO_DRIVERS":
                    base *= cfg["two_drivers_multiplier"]
                base, basis = round(float(base), 2), "PER_TRIP"
            ajustes = cfg["adjustments"][rota["carrier_id"]]
            # base = tarifa vigente após o último reajuste; reconstrói o histórico para trás
            valores = [base]
            for _, pct in reversed(ajustes):
                valores.insert(0, valores[0] / (1 + pct))
            inicios = ["2024-01-01"] + [d for d, _ in ajustes]
            for k, inicio in enumerate(inicios):
                fim = None
                if k + 1 < len(inicios):
                    fim = (date.fromisoformat(inicios[k + 1]) - timedelta(days=1)).isoformat()
                linhas.append(
                    {
                        "route_id": op["route_id"],
                        "vehicle_type_id": op["vehicle_type_id"],
                        "rate_basis": basis,
                        "rate_value": round(valores[k], 4 if basis == "PER_PIECE" else 2),
                        "spot_premium": cfg["spot_premium"],
                        "effective_from": inicio,
                        "effective_to": fim,
                    }
                )
        return pd.DataFrame(linhas)

    # -- Execução ------------------------------------------------------------

    def gerar_viagens_realizadas(
        self,
        historico: pd.DataFrame,
        forecasts: pd.DataFrame,
        verdade: pd.DataFrame,
        calendario: pd.DataFrame,
        rotas: pd.DataFrame,
        paradas: pd.DataFrame,
        opcoes: pd.DataFrame,
        tarifas: pd.DataFrame,
    ) -> pd.DataFrame:
        """Simula a execução: plano mensal fixo do operador + transbordo spot + extras."""
        cfg = self.config["execution"]
        inicio = semana_iso_para_data(cfg["first_week"]).isoformat()
        fim = semana_iso_para_data(cfg["last_week"]).isoformat()
        cal = calendario.set_index("week_start")
        veiculos = pd.DataFrame(self.config["vehicles"]).set_index("vehicle_type_id")
        prob_ontime = {c["carrier_id"]: c["on_time_probability"] for c in self.config["carriers"]}
        freq_min = {"SHORT": 3, "MEDIUM": 2, "LONG": 1}

        volume = (
            historico[(historico["week_start"] >= inicio) & (historico["week_start"] <= fim)]
            .merge(paradas[["route_id", "store_id"]], on="store_id")
            .groupby(["route_id", "week_start"])["pieces_shipped"].sum()
        )
        # Plano do operador: 2025 usa demanda verdadeira com ruído; 2026 usa o BUDGET_2026
        plano_2025 = (
            verdade[(verdade["week_start"] >= inicio) & (verdade["week_start"] < "2025-12-29")]
            .merge(paradas[["route_id", "store_id"]], on="store_id")
            .groupby(["route_id", "week_start"])["true_pieces"].sum()
            * 1.03
        )
        plano_2026 = (
            forecasts[forecasts["forecast_version"] == "BUDGET_2026"]
            .merge(paradas[["route_id", "store_id"]], on="store_id")
            .groupby(["route_id", "week_start"])["forecast_pieces"].sum()
        )
        plano = pd.concat([plano_2025, plano_2026])

        default = opcoes[opcoes["is_default"] == 1].set_index("route_id")["vehicle_type_id"]
        semanas = cal[(cal.index >= inicio) & (cal.index <= fim)]
        linhas = []
        contador = 1
        for _, rota in rotas.iterrows():
            rid = rota["route_id"]
            vid = default[rid]
            tar = tarifas[(tarifas["route_id"] == rid) & (tarifas["vehicle_type_id"] == vid)]

            def tarifa_em(dia: str) -> tuple[float, float]:
                vigente = tar[(tar["effective_from"] <= dia) & (tar["effective_to"].isna() | (tar["effective_to"] >= dia))]
                linha = vigente.iloc[0]
                return float(linha["rate_value"]), float(linha["spot_premium"])

            # Frequência mensal fixa pelo plano (média arredondada, frequência mínima)
            freq_mes = {}
            if rota["route_type"] != "AIR":
                cap = veiculos.loc[vid, "capacity_pieces"]
                for (ano, mes), grupo in semanas.groupby(["retail_year", "retail_month"]):
                    necessidades = []
                    for ws in grupo.index:
                        vol_plano = float(plano.get((rid, ws), 0))
                        if rota["route_type"] == "ALTERNATING_WEEK":
                            vol_plano *= 2
                        necessidades.append(math.ceil(vol_plano / cap) if vol_plano > 0 else 0)
                    freq_mes[(ano, mes)] = (
                        0 if sum(necessidades) == 0
                        else max(freq_min[rota["route_profile"]], int(math.floor(np.mean(necessidades) + 0.5)))
                    )

            acumulado = 0
            for ws, semana in semanas.iterrows():
                vol = int(volume.get((rid, ws), 0))
                if rota["route_type"] == "ALTERNATING_WEEK" and semana["week_idx"] % 2 == 0:
                    acumulado += vol
                    continue
                vol += acumulado
                acumulado = 0
                pico = semana["season_flag"] in ("BLACK_FRIDAY", "CHRISTMAS", "WINTER")
                taxa, premio = tarifa_em(ws)
                ship_date = (date.fromisoformat(ws) + timedelta(days=1)).isoformat()

                if rota["route_type"] == "AIR":
                    viagens = [("PLANNED", vol, round(vol * taxa, 2))]
                else:
                    cap = veiculos.loc[vid, "capacity_pieces"]
                    freq = freq_mes[(semana["retail_year"], semana["retail_month"])]
                    necessarias = math.ceil(vol / cap) if vol > 0 else 0
                    extras_spot = max(0, necessarias - freq)
                    total = freq + extras_spot
                    if total == 0:
                        continue
                    base = vol // total
                    resto = vol - base * total
                    viagens = []
                    for k in range(total):
                        pecas = base + (1 if k < resto else 0)
                        tipo = "PLANNED" if k < freq else "OVERFLOW_SPOT"
                        custo = taxa if tipo == "PLANNED" else taxa * premio
                        viagens.append((tipo, pecas, round(custo, 2)))

                p_extra = cfg["extra_probability_peak"] if pico else cfg["extra_probability"]
                p_ontime = prob_ontime[rota["carrier_id"]] - (cfg["peak_on_time_penalty"] if pico else 0)
                for tipo, pecas, custo in viagens:
                    extra, motivo = 0.0, "NONE"
                    if self.rng.random() < p_extra:
                        motivo = str(self.rng.choice(["RE_DELIVERY", "FISCAL_HOLD", "EXTRA_HELPER", "WAITING_TIME"]))
                        bases = {"RE_DELIVERY": 0.15 * custo, "FISCAL_HOLD": 600.0, "EXTRA_HELPER": 350.0, "WAITING_TIME": 250.0}
                        extra = round(bases[motivo] * self.rng.uniform(0.8, 1.2), 2)
                    linhas.append(
                        {
                            "trip_id": f"TRP{contador:07d}",
                            "week_start": ws,
                            "ship_date": ship_date,
                            "route_id": rid,
                            "vehicle_type_id": vid,
                            "carrier_id": rota["carrier_id"],
                            "trip_kind": tipo,
                            "pieces": int(pecas),
                            "freight_cost": custo,
                            "extra_cost": extra,
                            "extra_reason": motivo,
                            "delivered_on_time": int(self.rng.random() < p_ontime),
                        }
                    )
                    contador += 1
        return pd.DataFrame(linhas)

    # -- Cenários e governança ----------------------------------------------

    def gerar_cenarios(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        cenarios = pd.DataFrame(
            [
                {"scenario_id": "PLAN_2026", "scenario_name": "Transportation Plan 2026", "scenario_type": "BUDGET", "base_scenario_id": None,
                 "forecast_version": "BUDGET_2026", "plan_year": 2026, "description": "Approved 2026 plan built on the BUDGET_2026 forecast.",
                 "created_by_role": "Transportation Planning", "created_at": "2025-10-31", "locked": 1},
                {"scenario_id": "BUDGET_2027", "scenario_name": "Transportation Budget 2027", "scenario_type": "BUDGET", "base_scenario_id": None,
                 "forecast_version": "BUDGET_2027", "plan_year": 2027, "description": "2027 budget proposal on the BUDGET_2027 forecast.",
                 "created_by_role": "Transportation Planning", "created_at": "2026-10-31", "locked": 0},
            ]
        )
        comuns = [
            ("frequency_min.SHORT", "NETWORK", 3, "Planning policy: minimum weekly frequency for short routes"),
            ("frequency_min.MEDIUM", "NETWORK", 2, "Planning policy: minimum weekly frequency for medium routes"),
            ("frequency_min.LONG", "NETWORK", 1, "Planning policy: minimum weekly frequency for long routes"),
            ("frequency_basis", "NETWORK", "MEAN", "Monthly fixed frequency = rounded mean of weekly required trips"),
            ("extras_rate", "NETWORK", 0.04, "Extras (re-delivery, fiscal hold, helpers, waiting) as share of freight"),
            ("credit_rate.PIS_COFINS", "NETWORK", 0.0925, "Recoverable tax credit on gross freight (synthetic assumption)"),
            ("utilization_threshold", "NETWORK", 0.60, "Below this utilization a route is a consolidation candidate"),
        ]
        parametros = []
        for cid, inicio, fim in [("PLAN_2026", "2026-01-01", "2026-12-31"), ("BUDGET_2027", "2027-01-01", "2027-12-31")]:
            for chave, escopo, valor, nota in comuns:
                parametros.append({"scenario_id": cid, "parameter_key": chave, "scope": escopo, "value": str(valor),
                                   "valid_from": inicio, "valid_to": fim, "source_note": nota})
        for carrier, data_ajuste, pct in [("ATLAS", "2027-03-01", 0.06), ("NOVA", "2027-05-01", 0.07), ("ORION", "2027-01-01", 0.05)]:
            parametros.append({"scenario_id": "BUDGET_2027", "parameter_key": "rate_adjustment", "scope": f"CARRIER:{carrier}",
                               "value": str(pct), "valid_from": data_ajuste, "valid_to": "2027-12-31",
                               "source_note": "Expected contractual rate adjustment (synthetic)"})
        ajustes = pd.DataFrame(
            [
                {"adjustment_id": "ADJ-2027-001", "scenario_id": "BUDGET_2027", "scope": "NETWORK", "adjustment_type": "MULTIPLIER",
                 "value": 0.97, "reason": "Top-down efficiency target: 3% freight savings expected from carrier renegotiation",
                 "requested_by_role": "Board of Directors", "approved_by_role": "CFO", "approved_at": "2026-11-05", "status": "APPROVED"},
                {"adjustment_id": "ADJ-2027-002", "scenario_id": "BUDGET_2027", "scope": "DC:DC03", "adjustment_type": "ABSOLUTE_BRL",
                 "value": 180000.0, "reason": "Contingency for a new regional route launch in Q2",
                 "requested_by_role": "Operations Director", "approved_by_role": "CFO", "approved_at": "2026-11-05", "status": "APPROVED"},
                {"adjustment_id": "ADJ-2027-003", "scenario_id": "BUDGET_2027", "scope": "MONTH:2027-11", "adjustment_type": "MULTIPLIER",
                 "value": 1.05, "reason": "Black Friday contingency (pending review)",
                 "requested_by_role": "Transportation Manager", "approved_by_role": None, "approved_at": None, "status": "PROPOSED"},
            ]
        )
        fatores = pd.DataFrame(
            [
                {"factor_key": "DIESEL", "unit": "kg_co2e_per_liter", "value": 2.60, "valid_from": "2024-01-01",
                 "source_note": "Illustrative value within the range of public diesel factors (e.g. GHG Protocol / DEFRA tables). Replace with an official source before real use."},
                {"factor_key": "AIR_FREIGHT", "unit": "kg_co2e_per_tonne_km", "value": 0.60, "valid_from": "2024-01-01",
                 "source_note": "Illustrative order of magnitude for air freight. Replace with an official source before real use."},
                {"factor_key": "PIECE_WEIGHT", "unit": "kg_per_piece", "value": 0.25, "valid_from": "2024-01-01",
                 "source_note": "Synthetic average weight per piece."},
            ]
        )
        return cenarios, pd.DataFrame(parametros), ajustes, fatores

    # -- Orquestração --------------------------------------------------------

    def gerar(self) -> RedeSintetica:
        hz = self.config["horizon"]
        calendario = gerar_calendario(hz["first_week"], hz["last_week"])
        lojas = self.gerar_lojas()
        series = self.gerar_series(lojas)
        verdade = self.gerar_demanda_verdadeira(series, calendario)
        historico = self.gerar_historico(verdade, calendario)
        forecasts = self.gerar_forecasts(verdade, calendario)
        rotas, paradas = self.gerar_rotas(lojas, verdade)
        rotas, opcoes = self.definir_veiculos_rotas(rotas, paradas, verdade)
        tarifas = self.gerar_tarifas(rotas, opcoes)
        viagens = self.gerar_viagens_realizadas(historico, forecasts, verdade, calendario, rotas, paradas, opcoes, tarifas)
        cenarios, parametros, ajustes, fatores = self.gerar_cenarios()

        lojas_saida = lojas.drop(columns=["_city_offset_km", "_mode"])
        self.rede.tabelas = {
            "tn_calendar": calendario,
            "tn_dcs": pd.DataFrame(self.config["dcs"]),
            "tn_stores": lojas_saida,
            "tn_carriers": self.gerar_carriers(),
            "tn_vehicles": self.gerar_veiculos().drop(columns=["fixed_cost", "cost_per_km"]),
            "tn_routes": rotas,
            "tn_route_stops": paradas,
            "tn_route_vehicle_options": opcoes,
            "tn_rates": tarifas,
            "tn_demand_history": historico,
            "tn_forecast": forecasts,
            "tn_trips_actual": viagens,
            "tn_scenarios": cenarios,
            "tn_parameters": parametros,
            "tn_management_adjustments": ajustes,
            "tn_emission_factors": fatores,
        }
        self.rede.relatorio = {
            "dataset_version": self.config["dataset_version"],
            "seed": self.seed,
            "row_counts": {nome: len(df) for nome, df in self.rede.tabelas.items()},
            "anomalies": self.anomalias,
            "route_types": rotas["route_type"].value_counts().sort_index().to_dict(),
            "route_profiles": rotas["route_profile"].value_counts().sort_index().to_dict(),
            "store_status": lojas["status"].value_counts().sort_index().to_dict(),
        }
        return self.rede


def carregar_config(caminho: Path = CAMINHO_CONFIG) -> dict:
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def gerar_rede(config: dict | None = None, seed: int | None = None) -> RedeSintetica:
    """Gera a rede sintética completa em memória."""
    return GeradorRede(config or carregar_config(), seed=seed).gerar()


def escrever_rede(rede: RedeSintetica, diretorio: Path = DIRETORIO_SAIDA) -> None:
    """Escreve as tabelas em CSV e o relatório de geração."""
    diretorio.mkdir(parents=True, exist_ok=True)
    for nome, df in rede.tabelas.items():
        df.to_csv(diretorio / f"{nome}.csv", index=False, lineterminator="\n")
    r = rede.relatorio
    linhas = [
        "# Synthetic Network — Generation Report",
        "",
        f"- **dataset_version:** `{r['dataset_version']}`",
        f"- **seed:** `{r['seed']}`",
        "- **data:** 100% synthetic — no real companies, stores, carriers, tariffs or volumes.",
        "",
        "## Row counts",
        "",
        "| Table | Rows |",
        "|---|---:|",
        *[f"| `{t}` | {n:,} |" for t, n in r["row_counts"].items()],
        "",
        "## Injected anomalies (tn_demand_history)",
        "",
        "| Type | Rows |",
        "|---|---:|",
        *[f"| {a['type']} | {a['rows']:,} |" for a in r["anomalies"]],
        "",
        "## Network shape",
        "",
        f"- Route types: {r['route_types']}",
        f"- Route profiles: {r['route_profiles']}",
        f"- Store status: {r['store_status']}",
        "",
    ]
    (diretorio / "generation_report.md").write_text("\n".join(linhas), encoding="utf-8")
