@echo off
echo Starting CitiusTech AI Content Intelligence Backend...
set PYTHONPATH=.
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
