import joblib
import json
import pandas as pd

def model_fn(model_dir):
    model = joblib.load(f"{model_dir}/model.joblib")
    return model

def input_fn(request_body, content_type):
    if content_type == 'application/json':
        data = json.loads(request_body)
        # Convert list of dicts to DataFrame
        return pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    # input_data is a DataFrame
    predictions = model.predict(input_data)
    return predictions

def output_fn(prediction, content_type):
    return json.dumps(prediction.tolist())
