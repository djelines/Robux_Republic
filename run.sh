#!/bin/bash

# Create sql_data directory with appropriate permissions
mkdir -p /tmp/sql_data
chmod 777 /tmp/sql_data
# Set PYTHONPATH environment variable
export PYTHONPATH=$PYTHONPATH:/app

# Start schedulers in the background
# python -m app.schelduler.finalize_transaction & 
# python -m app.schelduler.mail_send & 
python -m app.schelduler.worker &
python -m app.schelduler.process_ceiling_account &

# Start the FastAPI application with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}