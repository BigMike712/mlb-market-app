import json
from datetime import datetime

def log_model_performance(log_path, model_name, metrics, features, hyperparameters, notes=""):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "metrics": metrics,
        "features": features,
        "hyperparameters": hyperparameters,
        "notes": notes
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
