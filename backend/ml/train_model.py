"""
Machine Learning training pipeline for Dark Pattern text classification.
Trains a TF-IDF + LogisticRegression / LinearSVC pipeline on labeled dataset.
Evaluates model performance and saves the serialized artifacts.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "training_data.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_OUT_PATH = os.path.join(MODELS_DIR, "dark_pattern_model.joblib")


def preprocess_text(text: str) -> str:
    """Clean and normalize raw text for ML classification."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    return text


def train():
    """Train the classifier and persist model artifacts."""
    logger.info("Loading training data from %s", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        logger.error("Dataset not found at %s", DATA_PATH)
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    logger.info("Loaded %d training examples", len(df))
    logger.info("Class distribution:\n%s", df["category"].value_counts())

    # Preprocess
    df["clean_text"] = df["text"].apply(preprocess_text)
    X = df["clean_text"].values
    y = df["category"].values

    # Build Pipeline: TF-IDF + Multi-class Logistic Regression with probability estimates
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 3),
                min_df=1,
                max_features=5000,
                sublinear_tf=True,
            ),
        ),
        (
            "clf",
            LogisticRegression(
                C=1.5,
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    # Cross-validation
    logger.info("Running 5-fold cross-validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, X, y, cv=skf, scoring="accuracy")
    logger.info("Cross-validation Accuracy: %0.4f (+/- %0.4f)", np.mean(scores), np.std(scores))

    # Fit full model
    pipeline.fit(X, y)

    # In-sample evaluation
    y_pred = pipeline.predict(X)
    logger.info("Training Classification Report:\n%s", classification_report(y, y_pred))

    # Ensure models dir exists
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Save model
    joblib.dump(pipeline, MODEL_OUT_PATH)
    logger.info("Model successfully trained and saved to %s", MODEL_OUT_PATH)

    # Quick test inference
    sample_text = "No thanks, I don't want to save money today"
    pred_cat = pipeline.predict([sample_text])[0]
    probs = pipeline.predict_proba([sample_text])[0]
    conf = np.max(probs)
    logger.info("Inference sanity test: '%s' -> %s (conf: %.2f)", sample_text, pred_cat, conf)


if __name__ == "__main__":
    train()

