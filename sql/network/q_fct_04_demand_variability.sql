-- Q-FCT-04 — Quais lojas têm a demanda mais volátil?
--
-- KPI: CV = σ(demanda semanal) / μ(demanda semanal), nas últimas N semanas.
--
-- Regras de negócio que a consulta precisa respeitar:
--   1. Semana sem expedição é demanda zero, não semana ausente. A grade
--      loja × semana (CROSS JOIN) garante que os zeros entrem na média e no
--      desvio; sem ela, lojas intermitentes pareceriam mais estáveis do que são.
--   2. O desvio-padrão é amostral (divisor n − 1), igual ao do motor.
--
-- Grão da saída: uma linha por store_id.
-- Parâmetros:    :last_weeks (número de semanas mais recentes; padrão do motor = 52)
-- Reconcilia com: forecasting.variabilidade_demanda
-- Observação:    usa SQRT(); o executor registra a função se o SQLite não a tiver.

WITH semanas AS (
    SELECT DISTINCT week_start
    FROM tn_demand_history
    ORDER BY week_start DESC
    LIMIT :last_weeks
),

demanda_semanal AS (
    SELECT
        h.store_id,
        h.week_start,
        SUM(h.pieces_shipped) AS pieces
    FROM tn_demand_history AS h
    JOIN semanas AS s
        ON s.week_start = h.week_start
    GROUP BY
        h.store_id,
        h.week_start
),

lojas AS (
    SELECT DISTINCT store_id
    FROM demanda_semanal
),

grade AS (
    SELECT
        l.store_id,
        s.week_start,
        COALESCE(d.pieces, 0) AS pieces
    FROM lojas AS l
    CROSS JOIN semanas AS s
    LEFT JOIN demanda_semanal AS d
        ON d.store_id = l.store_id
        AND d.week_start = s.week_start
),

media AS (
    SELECT
        store_id,
        COUNT(*)    AS weeks,
        AVG(pieces) AS mean_weekly_pieces
    FROM grade
    GROUP BY store_id
),

dispersao AS (
    SELECT
        g.store_id,
        m.weeks,
        m.mean_weekly_pieces,
        SQRT(
            SUM((g.pieces - m.mean_weekly_pieces) * (g.pieces - m.mean_weekly_pieces))
            / (m.weeks - 1)
        ) AS std_weekly_pieces
    FROM grade AS g
    JOIN media AS m
        ON m.store_id = g.store_id
    GROUP BY
        g.store_id,
        m.weeks,
        m.mean_weekly_pieces
)

SELECT
    d.store_id,
    d.std_weekly_pieces / NULLIF(d.mean_weekly_pieces, 0) AS cv,
    s.cluster,
    s.uf,
    d.mean_weekly_pieces,
    d.std_weekly_pieces,
    d.weeks
FROM dispersao AS d
JOIN tn_stores AS s
    ON s.store_id = d.store_id
ORDER BY
    cv DESC;
