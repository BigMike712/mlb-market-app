from prediction_model.tracking import log_model_performance
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from xgboost import XGBClassifier
from prediction_model.tracking import log_model_performance  # if using logging module
import joblib
import os

def make_discrepancy_features(df):
    # 1. Normalize in-game attributes to 0–1 scale using live series max of 115
    df['contact_right_norm'] = df['contact_right'] / 115
    df['contact_left_norm'] = df['contact_left'] / 115
    df['power_right_norm'] = df['power_right'] / 115
    df['power_left_norm'] = df['power_left'] / 115
    df['discipline_norm'] = df['discipline'] / 115

    # 2. Discrepancy features (normalized rating - IRL stat)
    df['contact_right_vs_rhp_avg'] = df['contact_right_norm'] - df['rhp_AVG']
    df['contact_left_vs_lhp_avg'] = df['contact_left_norm'] - df['lhp_AVG']
    df['power_right_vs_rhp_slg'] = df['power_right_norm'] - df['rhp_SLG']
    df['power_left_vs_lhp_slg'] = df['power_left_norm'] - df['lhp_SLG']
    df['discipline_vs_bb'] = df['discipline_norm'] - df['rhp_BB%']

    # 3. IRL-derived indices
    df['plate_discipline_index'] = df['rhp_BB%'] - df['rhp_K%']

    # 4. Interaction features (raw in-game attributes x IRL stats)
    df['contact_right_x_avg'] = df['contact_right'] * df['rhp_AVG']
    df['power_right_x_slg'] = df['power_right'] * df['rhp_SLG']
    df['discipline_x_bb'] = df['discipline'] * df['rhp_BB%']

    # 5. Drop intermediate normalized features (used only to compute discrepancies)
    df.drop(columns=[
        'contact_right_norm', 'contact_left_norm',
        'power_right_norm', 'power_left_norm',
        'discipline_norm'
    ], inplace=True)

    return df


def train_model(
    df,
    target="upgrade_label",
    model_name="XGBoost_baseline",
    test_size=0.2,
    random_state=42,
    drop_columns=None,
    log_path="../prediction_model/experiment_logs/model_logs.jsonl",
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
        drop_columns = ["player_id", "player_name", "is_hitter", "new_overall", "overall_rating", "playerId", target]

    X = df.drop(columns=drop_columns)
    y = df[target]

    features = X.columns.tolist()

    # Step 2: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Step 3: Initialize and train model
    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        eval_metric="mlogloss",
        random_state=random_state
    )
    
    # Save the model's hyperparameters
    hyperparameters = model.get_params()

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
    log_model_performance(log_path=log_path, model_name=model_name, metrics=metrics, features=features, hyperparameters=hyperparameters, notes=notes)

    model_dir = "saved_models"
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, f"{model_name}.joblib")
    joblib.dump(model, model_path)

    print(f"💾 Model saved to {model_path}")

    return model, X_train, X_test, y_train, y_test, y_pred

