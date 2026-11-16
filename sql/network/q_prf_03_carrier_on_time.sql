-- Q-PRF-03 — Qual transportadora está abaixo da meta de entregas no prazo?
--
-- KPI: OTD = viagens entregues no prazo / total de viagens.
-- A meta vem do cadastro da transportadora (parâmetro é dado, não código).
--
-- Grão da saída: uma linha por carrier_id.
-- Reconcilia com: variance.desempenho_transportadoras(por_mes=False)

SELECT
    t.carrier_id,
    c.carrier_name,
    COUNT(*)                                                  AS trips,
    SUM(t.delivered_on_time)                                  AS on_time,
    1.0 * SUM(t.delivered_on_time) / COUNT(*)                 AS on_time_rate,
    c.on_time_target,
    1.0 * SUM(t.delivered_on_time) / COUNT(*) - c.on_time_target AS gap_to_target
FROM tn_trips_actual AS t
JOIN tn_carriers AS c
    ON c.carrier_id = t.carrier_id
GROUP BY
    t.carrier_id,
    c.carrier_name,
    c.on_time_target
ORDER BY
    gap_to_target;
