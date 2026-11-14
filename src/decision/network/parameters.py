"""Resolução de parâmetros de cenário (tn_parameters + overrides de what-if).

Regras:
- um parâmetro tem chave, escopo e vigência (valid_from / valid_to);
- precedência de escopo: ROUTE > CARRIER > DC > NETWORK;
- overrides de what-if têm a mesma forma de tn_parameters e vencem o cenário base
  no mesmo escopo, sem alterar o cenário base.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


PRECEDENCIA = ("ROUTE", "CARRIER", "DC", "NETWORK")


def _tipo_escopo(escopo: str) -> str:
    return escopo.split(":", 1)[0]


@dataclass
class ParametrosCenario:
    """Parâmetros vigentes de um cenário, com overrides opcionais."""

    scenario_id: str
    linhas: pd.DataFrame
    overrides: list[dict] = field(default_factory=list)

    def __post_init__(self):
        base = self.linhas.copy()
        base["_origem"] = "SCENARIO"
        if self.overrides:
            extra = pd.DataFrame(self.overrides)
            for coluna, padrao in (("scope", "NETWORK"), ("valid_from", "0000-01-01"), ("valid_to", None), ("source_note", "what-if override")):
                if coluna not in extra.columns:
                    extra[coluna] = padrao
                elif padrao is not None:
                    extra[coluna] = extra[coluna].fillna(padrao)
            extra["value"] = extra["value"].astype(str)
            extra["_origem"] = "OVERRIDE"
            base = pd.concat([base, extra], ignore_index=True)
        base["valid_from"] = base["valid_from"].fillna("0000-01-01")
        self._tabela = base

    # ------------------------------------------------------------------

    def _candidatos(self, chave: str, escopos: list[str], data: str | None) -> pd.DataFrame:
        t = self._tabela[(self._tabela["parameter_key"] == chave) & (self._tabela["scope"].isin(escopos))]
        if data is not None:
            t = t[(t["valid_from"] <= data) & (t["valid_to"].isna() | (t["valid_to"] >= data))]
        return t

    def valor(self, chave: str, data: str | None = None, route_id: str | None = None,
              carrier_id: str | None = None, dc_id: str | None = None, padrao=None):
        """Valor bruto (str) do parâmetro mais específico vigente na data."""
        escopos = {"NETWORK": "NETWORK"}
        if route_id:
            escopos["ROUTE"] = f"ROUTE:{route_id}"
        if carrier_id:
            escopos["CARRIER"] = f"CARRIER:{carrier_id}"
        if dc_id:
            escopos["DC"] = f"DC:{dc_id}"
        t = self._candidatos(chave, list(escopos.values()), data)
        if t.empty:
            return padrao
        t = t.assign(_rank=t["scope"].map(lambda s: PRECEDENCIA.index(_tipo_escopo(s))),
                     _over=(t["_origem"] == "OVERRIDE").astype(int))
        t = t.sort_values(["_rank", "_over", "valid_from"], ascending=[True, False, False])
        return t.iloc[0]["value"]

    def numero(self, chave: str, padrao: float | None = None, **kwargs) -> float:
        v = self.valor(chave, padrao=None, **kwargs)
        return float(v) if v is not None else padrao

    # -- Atalhos de domínio -----------------------------------------------

    def frequencia_minima(self, perfil: str, route_id: str | None = None) -> int:
        especifica = self.valor("frequency_min", route_id=route_id) if route_id else None
        if especifica is not None:
            return int(float(especifica))
        return int(self.numero(f"frequency_min.{perfil}", padrao=1))

    def base_frequencia(self, route_id: str | None = None) -> str:
        return str(self.valor("frequency_basis", route_id=route_id, padrao="MEAN"))

    def veiculo(self, route_id: str) -> str | None:
        return self.valor("vehicle", route_id=route_id)

    def multiplicador_volume(self, data: str, route_id: str | None = None, dc_id: str | None = None) -> float:
        return self.numero("volume_multiplier", padrao=1.0, data=data, route_id=route_id, dc_id=dc_id)

    def fator_reajuste(self, carrier_id: str, data: str) -> float:
        """Produto dos reajustes do cenário vigentes até a data para a transportadora."""
        t = self._tabela[(self._tabela["parameter_key"] == "rate_adjustment")
                         & (self._tabela["scope"].isin([f"CARRIER:{carrier_id}", "NETWORK"]))
                         & (self._tabela["valid_from"] <= data)]
        # override no mesmo escopo e data substitui o valor do cenário
        t = t.sort_values("_origem").drop_duplicates(subset=["scope", "valid_from"], keep="first")
        fator = 1.0
        for v in t["value"]:
            fator *= 1 + float(v)
        return fator

    def descrever(self) -> list[dict]:
        """Parâmetros vigentes (para explicações e para o Copilot)."""
        colunas = ["parameter_key", "scope", "value", "valid_from", "valid_to", "source_note", "_origem"]
        return self._tabela[colunas].rename(columns={"_origem": "origin"}).to_dict("records")
