-- migrate:up

create role api_anon nologin;

-- migrate:down

drop role api_anon;
