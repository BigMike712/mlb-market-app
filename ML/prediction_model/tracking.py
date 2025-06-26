import json
from datetime import datetime

def log_model_performance(log_path, model_name, metrics, notes=""):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "metrics": metrics,
        "notes": notes
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
