-- migrate:up

-- Load extensions

-- TimescaleDB is a time-series database built on top of PostgreSQL
create extension if not exists timescaledb cascade;

-- The pgcrypto module provides cryptographic functions for PostgreSQL
create extension if not exists pgcrypto cascade;

-- migrate:down

drop extension if exists pgcrypto cascade;

drop extension if exists timescaledb cascade;
