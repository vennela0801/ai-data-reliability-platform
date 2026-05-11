SELECT
    txn_date,
    COUNT(*) AS txn_count,

    ROUND(
        COUNT(CASE WHEN payment_method IS NULL THEN 1 END)
        * 100.0 / COUNT(*),
        2
    ) AS null_payment_rate

FROM {{ ref('stg_transactions') }}
GROUP BY 1
