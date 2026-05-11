SELECT
    signup_date,
    COUNT(*) AS new_signups
FROM "warehouse"."marts"."stg_customers"
GROUP BY 1