# Gobannus Database Migration

## Overview

This directory defines a docker container that contains migration files for managing database schema changes in the
PostgreSQL database using `dbmate`. This docker container is intended to execute the migrations once during cluster
start-up. `dbmate` is a lightweight, framework-agnostic tool for SQL database migrations. It's designed to track,
manage, and apply database schema changes.

## Migration Files

Each file in this directory represents a single schema change. The files contain plain SQL commands to be executed on
the database. Each migration file is named in the format `YYYYMMDDHHMMSS_label.sql`, where `YYYYMMDDHHMMSS` is the
timestamp of creation, and `label` is a short description of the migration. Migrations are applied in the order of their
timestamp. It is crucial that each migration file be idempotent -- running it multiple times should have the same effect
as running it once. 

Migration files typically consist of two sections:
* `-- migrate:up`: Contains SQL commands to apply the migration.
* `-- migrate:down`: Contains SQL commands to roll back (undo) the migration.

## How To Create a New Migration

From the `./db-migrations` directory, run:

```shell
dbmate -d ./ n <label>
```

Where `label` is a brief description of the migration intent.
