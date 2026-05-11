
  
  create view "warehouse"."marts"."stg_transactions__dbt_tmp" as (
    SELECT *
FROM raw.transactions
  );
