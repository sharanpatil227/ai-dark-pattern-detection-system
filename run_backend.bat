@echo off
echo ========================================================
echo  Starting DarkGuard Detection API Backend (FastAPI)
echo ========================================================
cd /d "%~dp0backend"
echo Checking ML model artifacts...
if not exist "ml\models\dark_pattern_model.joblib" (
    echo Model not found. Training model now...
    python -m ml.train_model
)
echo Starting server on http://localhost:8000
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

