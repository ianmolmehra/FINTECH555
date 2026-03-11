# ============================================================
# ml_models.py — ML model management stubs
# Extendable module for loading/saving trained models
# Currently, all ML logic is inline in the analytics modules.
# This file provides the save/load interface for future use.
# ============================================================

import pickle
import os


def save_model(model, filename: str):
    """Serializes a trained sklearn model to disk."""
    os.makedirs("models/saved", exist_ok=True)
    with open(f"models/saved/{filename}.pkl", "wb") as f:
        pickle.dump(model, f)


def load_model(filename: str):
    """Loads a pre-trained sklearn model from disk."""
    path = f"models/saved/{filename}.pkl"
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)
