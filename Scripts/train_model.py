import argparse
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def model_fn(model_dir):
    """Load model for inference"""
    return joblib.load(os.path.join(model_dir, "model.joblib"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # SageMaker specific arguments (auto-passed)
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST'))
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR'))

    args = parser.parse_args()

    # Load train/test data from input channels
    train_data = pd.read_csv(os.path.join(args.train, "train.csv"))
    test_data = pd.read_csv(os.path.join(args.test, "test.csv"))

    # Separate features and labels
    X_train = train_data.drop('Class', axis=1)
    y_train = train_data['Class']

    X_test = test_data.drop('Class', axis=1)
    y_test = test_data['Class']

    # ✅ Train model with class_weight to handle severe imbalance
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight='balanced_subsample',
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Evaluate and print to CloudWatch logs
    y_pred = model.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred, digits=4))

    # Save model in the directory SageMaker expects
    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))
