SELECT
    signup_date,
    COUNT(*) AS new_signups
FROM {{ ref('stg_customers') }}
GROUP BY 1
