
  
    
    

    create  table
      "warehouse"."marts"."fct_customers_daily__dbt_tmp"
  
    as (
      SELECT
    signup_date,
    COUNT(*) AS new_signups
FROM "warehouse"."marts"."stg_customers"
GROUP BY 1
    );
  
  