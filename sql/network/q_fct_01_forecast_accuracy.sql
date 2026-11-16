-- Q-FCT-01 / Q-FCT-02 — Qual foi a acurácia do forecast por CD / rota / loja?
--                        O forecast erra sistematicamente para cima ou para baixo?
--
-- KPIs: WAPE = Σ|A − F| / Σ A      Bias = Σ(F − A) / Σ A  (positivo = previsão acima)
--
-- Regras de negócio que a consulta precisa respeitar:
--   1. Só entram as semanas em que há forecast da versão E realizado disponível.
--   2. Semana-loja sem forecast conta como previsto 0; sem expedição, realizado 0.
--      Por isso previsto e realizado são empilhados (UNION ALL) e somados, em vez
--      de um INNER JOIN, que descartaria justamente os erros mais graves.
--   3. O erro absoluto é calculado no nível pedido, depois de agregar a semana.
--      Erros de lojas que se compensam dentro da rota não contam no WAPE da rota.
--
-- Grão da saída: uma linha por level_key (loja, rota, CD ou a rede inteira).
-- Parâmetros:    :forecast_version (ex.: 'BUDGET_2026')
--                :level ('STORE', 'ROUTE', 'DC' ou 'NETWORK')
-- Reconcilia com: forecasting.acuracia_forecast

WITH janela AS (
    SELECT
        (SELECT MIN(week_start) FROM tn_forecast WHERE forecast_version = :forecast_version) AS start_week,
        (SELECT MAX(week_start) FROM tn_demand_history)                                      AS end_week
),

loja_rota AS (
    SELECT DISTINCT
        route_id,
        store_id
    FROM tn_route_stops
),

previsto_e_realizado AS (
    SELECT
        week_start,
        store_id,
        forecast_pieces AS forecast_pieces,
        0               AS actual_pieces
    FROM tn_forecast
    WHERE forecast_version = :forecast_version

    UNION ALL

    SELECT
        week_start,
        store_id,
        0              AS forecast_pieces,
        pieces_shipped AS actual_pieces
    FROM tn_demand_history
),

por_nivel_e_semana AS (
    SELECT
        CASE :level
            WHEN 'STORE' THEN p.store_id
            WHEN 'ROUTE' THEN r.route_id
            WHEN 'DC'    THEN r.dc_id
            ELSE 'NETWORK'
        END                    AS level_key,
        p.week_start,
        SUM(p.forecast_pieces) AS forecast_pieces,
        SUM(p.actual_pieces)   AS actual_pieces
    FROM previsto_e_realizado AS p
    JOIN janela AS j
        ON p.week_start BETWEEN j.start_week AND j.end_week
    JOIN loja_rota AS lr
        ON lr.store_id = p.store_id
    JOIN tn_routes AS r
        ON r.route_id = lr.route_id
    GROUP BY
        level_key,
        p.week_start
)

SELECT
    :forecast_version                                                   AS forecast_version,
    :level                                                              AS level,
    level_key,
    SUM(actual_pieces)                                                  AS actual,
    SUM(forecast_pieces)                                                AS forecast,
    SUM(ABS(forecast_pieces - actual_pieces))                           AS abs_error,
    SUM(forecast_pieces - actual_pieces)                                AS error,
    1.0 * SUM(ABS(forecast_pieces - actual_pieces)) / NULLIF(SUM(actual_pieces), 0) AS wape,
    1.0 * SUM(forecast_pieces - actual_pieces)      / NULLIF(SUM(actual_pieces), 0) AS bias
FROM por_nivel_e_semana
GROUP BY
    level_key
ORDER BY
    wape DESC;
