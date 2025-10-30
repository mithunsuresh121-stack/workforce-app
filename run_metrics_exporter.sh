#!/bin/bash
cd backend
python -m app.monitoring.metrics_exporter "$@"
