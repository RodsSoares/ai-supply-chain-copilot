-- Q-PRF-03 — Em quais meses cada transportadora ficou abaixo da meta?
--
-- Mesma regra de OTD da visão por transportadora, aberta por mês de embarque.
-- A coluna below_target marca os meses em que a meta não foi atingida.
--
-- Grão da saída: uma linha por carrier_id + month (YYYY-MM).
-- Reconcilia com: variance.desempenho_transportadoras(por_mes=True)

WITH otd_mensal AS (
    SELECT
        carrier_id,
        SUBSTR(ship_date, 1, 7)                    AS month,
        COUNT(*)                                   AS trips,
        SUM(delivered_on_time)                     AS on_time,
        1.0 * SUM(delivered_on_time) / COUNT(*)    AS on_time_rate
    FROM tn_trips_actual
    GROUP BY
        carrier_id,
        SUBSTR(ship_date, 1, 7)
)

SELECT
    o.carrier_id,
    o.month,
    o.trips,
    o.on_time,
    o.on_time_rate,
    c.on_time_target,
    o.on_time_rate - c.on_time_target                               AS gap_to_target,
    CASE WHEN o.on_time_rate < c.on_time_target THEN 1 ELSE 0 END    AS below_target
FROM otd_mensal AS o
JOIN tn_carriers AS c
    ON c.carrier_id = o.carrier_id
ORDER BY
    o.carrier_id,
    o.month;
