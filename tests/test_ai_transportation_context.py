from src.ai.transportation_context import (
    preparar_contexto_transporte,
)


def test_preparar_contexto_transporte_lista():
    resultado_analitico = [
        {
            "route_id": "R002",
            "planned_cost": 3000.0,
        },
        {
            "route_id": "R001",
            "planned_cost": 5000.0,
        },
        {
            "route_id": "R001",
            "planned_cost": 4500.0,
        },
    ]

    contexto = preparar_contexto_transporte(
        tipo_analise="cost_ranking",
        resultado_analitico=resultado_analitico,
    )

    assert contexto["dominio"] == "transportation"
    assert contexto["tipo_analise"] == "cost_ranking"

    assert contexto["resumo"]["total_registros"] == 3
    assert contexto["resumo"]["route_ids"] == [
        "R001",
        "R002",
    ]

    assert contexto["resultado"] == resultado_analitico


def test_preparar_contexto_transporte_lista_vazia():
    contexto = preparar_contexto_transporte(
        tipo_analise="operational_changes",
        resultado_analitico=[],
    )

    assert contexto == {
        "dominio": "transportation",
        "tipo_analise": "operational_changes",
        "resumo": {
            "total_registros": 0,
            "route_ids": [],
        },
        "resultado": [],
    }


def test_preparar_contexto_transporte_resultado_nao_lista():
    resultado_analitico = {
        "total_cost": 778000.0,
        "total_trips": 192,
    }

    contexto = preparar_contexto_transporte(
        tipo_analise="executive_summary",
        resultado_analitico=resultado_analitico,
    )

    assert contexto["dominio"] == "transportation"
    assert contexto["tipo_analise"] == "executive_summary"
    assert contexto["resumo"]["total_registros"] == 1
    assert contexto["resumo"]["route_ids"] == []
    assert contexto["resultado"] == resultado_analitico