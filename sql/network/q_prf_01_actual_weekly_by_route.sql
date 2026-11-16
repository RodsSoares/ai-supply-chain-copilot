-- Q-PRF-01 (lado realizado) — Onde o custo realizado desviou do plano?
--
-- Consolida as viagens realizadas no grão rota + semana, que é o grão em que
-- o plano é comparado com o realizado. A decomposição volume / eficiência /
-- tarifa continua no motor (src/analytics/network/variance.py).
--
-- Grão da saída: uma linha por route_id + week_start.
-- Parâmetros:    :start_week e :end_week (YYYY-MM-DD; NULL = sem limite).
-- Reconcilia com: variance.realizado_semanal

SELECT
    route_id,
    week_start,
    SUM(pieces)                                                AS volume,
    COUNT(*)                                                   AS trips,
    SUM(freight_cost)                                          AS cost,
    SUM(extra_cost)                                            AS extra_cost,
    SUM(CASE WHEN trip_kind = 'OVERFLOW_SPOT' THEN 1 ELSE 0 END) AS overflow_trips
FROM tn_trips_actual
WHERE (:start_week IS NULL OR week_start >= :start_week)
  AND (:end_week   IS NULL OR week_start <= :end_week)
GROUP BY
    route_id,
    week_start
ORDER BY
    route_id,
    week_start;
