-- migrate:up

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Initial schema
--
-- (Once this database is deployed, changes to the schema must go through the
-- "dbmate" migration process. Please see `./db-migration/README.md`)
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
-- camera

create table if not exists api.camera
(
    id          integer not null generated always as identity primary key,
    url         text unique,
    mac_address text unique
);

grant
select,
insert
on api.camera to api_anon;

-------------------------------------------------------------------------------
-- log entry

create table if not exists api.log_type
(
    id   integer unique,
    name text unique
);

insert into api.log_type (id, name)
values (1, 'practice')
     , (2, 'planning')
     , (3, 'research')
     , (4, 'assembly')
     , (5, 'training')
     , (6, 'inventory')
     , (7, 'quality assurance')
;

create table if not exists api.log
(
    id               integer not null generated always as identity primary key,
    type             integer not null references api.log_type (id) on delete restrict,
    description      text,
    duration_seconds real
);

grant
select,
insert
on api.log to api_anon;

-------------------------------------------------------------------------------
-- recording

create table if not exists api.recording
(
    id           integer not null generated always as identity primary key,
    is_recording boolean,
    start_time   timestamp, -- time recording started
    stop_time    timestamp, -- time recording stopped
    output_file  text unique,

    log_id       integer not null references api.log (id) on delete restrict,
    camera_id    integer not null references api.camera (id) on delete restrict
);

grant
select,
insert
on api.recording to api_anon;


-- migrate:down

drop table api.recording cascade;

drop table api.log cascade;

drop table api.log_type cascade;

drop table api.camera cascade;
