#!/bin/bash
set -e

mkdir -p /app/sql_data
chmod 777 /app/sql_data

touch /app/sql_data/database.db
chmod 666 /app/sql_data/database.db


python -m app.schelduler.finalize_transaction &
python -m app.schelduler.mail_send &


uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}