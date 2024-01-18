-- migrate:up

-- create an event trigger function that forces PostgREST to reload the schema
create or replace procedure pgrst_reload()
  language plpgsql
  as $$
begin
  notify pgrst, 'reload schema';
end;
$$;


-- migrate:down

drop function public.pgrst_reload;
