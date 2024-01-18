-- migrate:up

-------------------------------------------------------------------------------
-- create schemas

create schema if not exists api;
grant usage on schema api to api_anon;

-------------------------------------------------------------------------------
-- restrict access to functions

alter default privileges revoke execute on functions from public;


-- migrate:down

drop schema api cascade;
