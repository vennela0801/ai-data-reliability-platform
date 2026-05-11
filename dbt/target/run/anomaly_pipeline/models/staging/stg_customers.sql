
  
  create view "warehouse"."marts"."stg_customers__dbt_tmp" as (
    SELECT *
FROM raw.customers
  );
