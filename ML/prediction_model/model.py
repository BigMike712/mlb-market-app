from prediction_model.tracking import log_model_performance
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from xgboost import XGBClassifier
from prediction_model.tracking import log_model_performance  # if using logging module
import pandas as pd

log_model_performance(
    log_path="model_logs.jsonl",
    model_name="XGBoost_baseline",
    metrics={"accuracy": acc, "f1": f1},
    notes="No scaling, raw features"
)


def train_model(
    df,
    target="upgrade_label",
    model_name="XGBoost_baseline",
    test_size=0.2,
    random_state=42,
    drop_columns=None,
    log_path="model_logs.jsonl",
    notes=""
):
    """
    Trains a classifier to predict the upgrade label.

    Parameters:
        df (pd.DataFrame): Input dataframe with features and target.
        target (str): Name of the target column.
        model_name (str): Identifier for the model version.
        test_size (float): Fraction of data to use for test set.
        random_state (int): Seed for reproducibility.
        drop_columns (list): Optional list of columns to exclude from features.
        log_path (str): File path for logging performance.
        notes (str): Description of what’s special about this model run.

    Returns:
        model: Trained model object
        X_train, X_test, y_train, y_test: Data splits
        y_pred: Predictions on test set
    """

    # Step 1: Feature/target split
    if drop_columns is None:
        drop_columns = ["player_id", "player_name", target]

    X = df.drop(columns=drop_columns)
    y = df[target]

    # Step 2: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Step 3: Initialize and train model
    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=random_state
    )
    model.fit(X_train, y_train)

    # Step 4: Predict and evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print("📊 Classification Report:")
    print(classification_report(y_test, y_pred))

    print(f"✅ Accuracy: {acc:.4f}")
    print(f"✅ Weighted F1 Score: {f1:.4f}")

    # Step 5: Log results
    metrics = {"accuracy": acc, "f1_score": f1}
    log_model_performance(log_path, model_name, metrics, notes)

    return model, X_train, X_test, y_train, y_test, y_pred

