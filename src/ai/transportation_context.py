from typing import Any


def preparar_contexto_transporte(
    tipo_analise: str,
    resultado_analitico: Any,
) -> dict[str, Any]:
    """
    Prepara deterministicamente o contexto de Transportation
    enviado à camada de IA.

    A função não recalcula métricas, não interpreta resultados
    e não cria conclusões.

    Apenas estrutura o resultado oficial produzido pela
    camada analítica determinística.
    """

    if isinstance(resultado_analitico, list):
        total_registros = len(resultado_analitico)

        route_ids = sorted(
            {
                registro["route_id"]
                for registro in resultado_analitico
                if isinstance(registro, dict)
                and registro.get("route_id")
            }
        )

    else:
        total_registros = (
            0 if resultado_analitico is None else 1
        )
        route_ids = []

    return {
        "dominio": "transportation",
        "tipo_analise": tipo_analise,
        "resumo": {
            "total_registros": total_registros,
            "route_ids": route_ids,
        },
        "resultado": resultado_analitico,
    }