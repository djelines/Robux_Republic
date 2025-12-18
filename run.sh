#!/bin/bash

mkdir -p /tmp/sql_data
chmod 777 /tmp/sql_data

python -m app.schelduler.finalize_transaction &

python -m app.schelduler.mail_send &

uvicorn app.main:app --host 0.0.0.0 --port $PORT