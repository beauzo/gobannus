#!/bin/bash

# Wait until the database is ready to accept migrations
dbmate wait

# Execute the migrations
dbmate up

# Invoke PostgREST to refresh API schema
echo "Refreshing PostgREST API schema..."
psql $DATABASE_URL -c "call pgrst_reload();"
