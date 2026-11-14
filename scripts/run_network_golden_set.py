"""Executa o Golden Set v2 (rede + política de estoque) contra o LLM real.

Uso:
    python scripts/run_network_golden_set.py                 # todos os casos (requer OPENAI_API_KEY)
    python scripts/run_network_golden_set.py --cases N01,N06
    python scripts/run_network_golden_set.py --dry-run       # só checagens determinísticas, sem LLM

Para cada caso de Transportation Network:
    1. roteamento real (intenção + campos extraídos) vs. esperado;
    2. execução determinística (dispatcher) e fatos esperados vs. resultado;
    3. resposta real do LLM e cobertura dos fatos numéricos na resposta;
    4. critérios qualitativos listados para revisão humana (PASS/FAIL manual).

Casos de política de estoque (I*) são apenas determinísticos até a
integração ao Copilot de Inventory.

Saída: docs/evaluations/Network_Real_LLM_Golden_Set_<data>.md
"""

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluation.golden_network import eh_fato_numerico, executar_chamada, extrair, fato_presente  # noqa: E402

CAMINHO_GOLDEN = Path("tests/golden/network_golden_set.json")


def iguais(esperado, obtido) -> bool:
    if isinstance(esperado, (int, float)) and not isinstance(esperado, bool):
        return math.isclose(float(esperado), float(obtido), rel_tol=1e-6, abs_tol=1e-6)
    return esperado == obtido


def avaliar_roteamento(caso: dict, intencao) -> tuple[bool, str]:
    ok_intent = intencao.intent in caso["expected_intent"]
    erros = [] if ok_intent else [f"intent={intencao.intent}"]
    for campo, valor in caso["expected_fields"].items():
        obtido = getattr(intencao, campo, None)
        if obtido is None or not iguais(valor, obtido):
            erros.append(f"{campo}={obtido!r} (esperado {valor!r})")
    return not erros, ", ".join(erros) or "OK"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(f"docs/evaluations/Network_Real_LLM_Golden_Set_{date.today().isoformat()}.md"))
    args = parser.parse_args()

    golden = json.loads(CAMINHO_GOLDEN.read_text(encoding="utf-8"))
    filtro = {c.strip() for c in args.cases.split(",") if c.strip()}
    casos = [c for c in golden["cases"] if not filtro or c["id"] in filtro]

    if not args.dry_run:
        from src.ai.client import gerar_resposta
        from src.ai.prompts import NETWORK_PROMPT, SYSTEM_PROMPT, TRANSPORTATION_PROMPT
        from src.ai.transportation_context import preparar_contexto_transporte
        from src.ai.transportation_dispatcher import executar_intencao_transporte
        from src.ai.transportation_router import rotear_pergunta_transporte
        from src.analytics.network.service import CAPACIDADES_NETWORK

    linhas = []
    for caso in casos:
        registro = {"id": caso["id"], "title": caso["title"], "question": caso["question"]}

        # Fatos determinísticos (sempre)
        resultado_ref = executar_chamada(caso)
        divergentes = [n for n, cam in caso["facts"].items() if not iguais(caso["expected_facts"][n], extrair(resultado_ref, cam))]
        registro["deterministic"] = "PASS" if not divergentes else f"FAIL ({', '.join(divergentes)})"

        if args.dry_run or caso["domain"] != "transportation_network":
            registro.update(routing="—", answer="(not executed)" if args.dry_run else "(pending Inventory Copilot integration)",
                            fact_coverage="—")
            linhas.append(registro)
            continue

        intencao = rotear_pergunta_transporte(caso["question"])
        ok, detalhe = avaliar_roteamento(caso, intencao)
        registro["routing"] = ("PASS" if ok else "FAIL") + f" — {intencao.intent} · {detalhe}"

        if intencao.intent == "out_of_scope":
            resposta = "A pergunta está fora do escopo analítico de Transportation."
            cobertura = "n/a (out_of_scope)"
        else:
            resultado = executar_intencao_transporte(intencao)
            contexto = preparar_contexto_transporte(tipo_analise=intencao.intent, resultado_analitico=resultado)
            instrucoes = SYSTEM_PROMPT + "\n\n" + TRANSPORTATION_PROMPT
            if intencao.intent in CAPACIDADES_NETWORK:
                instrucoes += "\n\n" + NETWORK_PROMPT
            resposta = gerar_resposta(pergunta=caso["question"], contexto=contexto, instrucoes=instrucoes)
            numericos = {n: v for n, v in caso["expected_facts"].items() if eh_fato_numerico(v)}
            presentes = [n for n, v in numericos.items() if fato_presente(resposta, v)]
            cobertura = "n/a (qualitative only)" if not numericos else f"{len(presentes)}/{len(numericos)}" + (f" (missing: {', '.join(sorted(set(numericos) - set(presentes)))})" if len(presentes) < len(numericos) else "")
        registro.update(answer=resposta, fact_coverage=cobertura)
        linhas.append(registro)
        print(f"{caso['id']}: {registro['routing']} | facts {cobertura}")

    # Relatório
    md = [
        "# Network — Real LLM Golden Set Validation",
        "",
        f"- Date: {date.today().isoformat()}",
        f"- Golden set: `{CAMINHO_GOLDEN}` ({golden['version']}, dataset {golden['dataset']})",
        f"- Mode: {'dry-run (deterministic only)' if args.dry_run else 'real LLM'}",
        "",
        "Fact coverage is an automatic heuristic (expected numbers found in the answer, pt-BR/en formats).",
        "Qualitative criteria require human review: fill the **Review** column with PASS/FAIL.",
        "",
        "| ID | Case | Deterministic | Routing | Fact coverage | Review |",
        "|---|---|---|---|---|---|",
        *[f"| {r['id']} | {r['title']} | {r['deterministic']} | {r['routing'].replace('|', '/')} | {r['fact_coverage'].replace('|', '/')} | |" for r in linhas],
        "",
        "## Answers and criteria",
        "",
    ]
    criterios = {c["id"]: c["criteria"] for c in golden["cases"]}
    for r in linhas:
        md += [f"### {r['id']} — {r['title']}", "", f"**Question:** {r['question']}", "",
               "**Criteria:**", *[f"- [ ] {c}" for c in criterios[r["id"]]], "", "**Answer:**", "", r["answer"], ""]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(md), encoding="utf-8")
    print(f"Report: {args.output}")


if __name__ == "__main__":
    main()
