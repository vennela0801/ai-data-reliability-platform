
  
  create view "warehouse"."marts"."stg_orders__dbt_tmp" as (
    SELECT *
FROM raw.orders
  );
