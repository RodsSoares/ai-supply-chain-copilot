-- Q-PRF-02 — Quanto custaram os extras, e por quais motivos?
--
-- KPI: extras share = extra_cost / freight_cost, por motivo.
-- O denominador é o frete de TODAS as viagens do período (com e sem extra),
-- por isso é calculado antes do filtro de motivo.
--
-- Grão da saída: uma linha por extra_reason.
-- Parâmetros:    :start_week e :end_week (YYYY-MM-DD; NULL = sem limite).
-- Reconcilia com: variance.analise_extras

WITH viagens AS (
    SELECT
        extra_reason,
        freight_cost,
        extra_cost
    FROM tn_trips_actual
    WHERE (:start_week IS NULL OR week_start >= :start_week)
      AND (:end_week   IS NULL OR week_start <= :end_week)
),

frete_do_periodo AS (
    SELECT SUM(freight_cost) AS freight_cost
    FROM viagens
)

SELECT
    v.extra_reason,
    COUNT(*)                                        AS occurrences,
    SUM(v.extra_cost)                               AS extra_cost,
    SUM(v.extra_cost) / NULLIF(f.freight_cost, 0)   AS share_of_freight
FROM viagens AS v
CROSS JOIN frete_do_periodo AS f
WHERE v.extra_reason <> 'NONE'
GROUP BY
    v.extra_reason,
    f.freight_cost
ORDER BY
    extra_cost DESC;
