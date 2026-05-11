
  
    
    

    create  table
      "warehouse"."marts"."fct_transactions_daily__dbt_tmp"
  
    as (
      SELECT
    txn_date,
    COUNT(*) AS txn_count,

    ROUND(
        COUNT(CASE WHEN payment_method IS NULL THEN 1 END)
        * 100.0 / COUNT(*),
        2
    ) AS null_payment_rate

FROM "warehouse"."marts"."stg_transactions"
GROUP BY 1
    );
  
  