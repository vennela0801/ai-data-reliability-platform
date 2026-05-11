SELECT
    order_date,
    COUNT(*) AS order_count,
    ROUND(SUM(revenue),2) AS total_revenue,
    ROUND(AVG(revenue),2) AS avg_revenue
FROM "warehouse"."marts"."stg_orders"
GROUP BY 1