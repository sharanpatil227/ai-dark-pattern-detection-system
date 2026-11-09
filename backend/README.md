# AI-Powered Dark Pattern Detection System - Backend

Production-quality FastAPI backend featuring a multi-layer hybrid detection architecture:
1. **Rule-Based Detection**: Deterministic pattern matching across 7 dark pattern categories.
2. **DOM / Structural Analysis**: Visual hierarchy, element size asymmetry, hidden opt-outs.
3. **NLP / Machine Learning Classification**: TF-IDF vectorization + Logistic Regression classifier.
4. **Scoring & Risk Aggregation**: Multi-factor risk calculation with confidence weighting.

---

## Architecture

```
backend/
├── app/
│   ├── config.py             # Settings via Pydantic
│   ├── database.py           # Async Motor MongoDB connection with in-memory fallback
│   ├── main.py               # FastAPI application with CORS
│   ├── models/               # Pydantic v2 schemas
│   ├── routes/               # API endpoints (/scan, /reports, /dashboard, /health)
│   ├── detection/            # Multi-layer detection engine
│   │   ├── engine.py         # Detection orchestrator & deduplication
│   │   ├── rule_engine.py    # Rule executor
│   │   ├── nlp_engine.py     # ML model inference
│   │   ├── dom_analyzer.py   # DOM & asymmetry analysis
│   │   └── rules/            # Core category rules
│   └── utils/                # Text processing & risk scoring
├── ml/
│   ├── data/                 # Labelled training dataset (200+ samples)
│   ├── models/               # Saved serialized model artifacts
│   └── train_model.py        # ML training and evaluation script
└── tests/                    # Pytest test suite
```

---

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the ML Model
```bash
python -m ml.train_model
```

### 3. Run the Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

### 4. Run Automated Tests
```bash
pytest tests/ -v
```

