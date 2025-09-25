from fastapi import FastAPI, HTTPException
from schemas import ModelSelection, ModelSelection_Regression
import os
import sys
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")


# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tqdm import tqdm


class BaseModel:
    def __init__(self, model, x_train, y_train, x_val, y_val, **kwargs):
        self.model = model
        self.x_train, self.y_train = x_train, y_train
        self.x_val, self.y_val = x_val, y_val
        self.is_trained = False
        self.kwargs = kwargs

    def predict(self, data):
        if not self.is_trained:
            raise Exception('Model not trained. Please train the model first')
        return self.model.predict(data)

    def predict_proba(self, data):
        if not self.is_trained:
            raise Exception('Model not trained. Please train the model first')
        probability = self.model.predict_proba(data)
        pred_class = probability.argmax(axis=1)
        pred_probs = probability.max(axis=1)
        return pred_class, pred_probs        

    def fit(self):
        print(f"training {self.model.__class__.__name__} as {self.__class__.__name__}")
        if self.x_val is not None and self.y_val is not None:
            if isinstance(self.model, CatBoostClassifier):
                self.model.fit(self.x_train, self.y_train, eval_set=(self.x_val, self.y_val), **self.kwargs)
            elif isinstance(self.model, TabNetClassifier):
                self.model.fit(X_train=self.x_train, y_train=self.y_train, eval_set=[(self.x_train, self.y_train), (self.x_val, self.y_val)], eval_name=['train', 'valid'], eval_metric=['balanced_accuracy'], **self.kwargs)
            else:
                self.model.fit(self.x_train, self.y_train, **self.kwargs)
        else:
            self.model.fit(self.x_train, self.y_train, **self.kwargs)
        self.is_trained = True

class BinaryModel(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fit()



class CountModel(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fit()

class AggregateModel:
    def __init__(self, binary_model, count_model):
        self.binary_model = binary_model
        self.count_model = count_model

    def predict(self, data):
        final_results = []
        reverse_label_mapping = {v: k for k, v in label_mapping.items()}
        bin_pred, bin_conf = self.binary_model.predict_proba(data)
        count_pred, count_conf = self.count_model.predict_proba(data)

        for bp, bc, cp, cc in tqdm(zip(bin_pred, bin_conf, count_pred, count_conf)):
            if bp == 0:
                cp = reverse_label_mapping[cp]
                final_results.append({
                    'has_zero_crashes': bp,
                    'has_zero_crashes_confidence': bc,
                    'pred_crash_counts': cp,
                    'pred_crash_counts_confidence': cc
                })
            else:
                final_results.append({
                    'has_zero_crashes': bp,
                    'has_zero_crashes_confidence': bc,
                    'pred_crash_counts': '0',
                    'pred_crash_counts_confidence': bc
                })
        return final_results


label_mapping = {
    '1-2': 0,
    '3-4': 1,
    '5+': 2
}


app = FastAPI(title="Crash Prediction API")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "data", "all_pickled_models")
loaded_models = {}



# Load all models from models folder at startup
@app.on_event("startup")
def load_models():
    # from crash_models import AggregateModel, BinaryModel, CountModel
    
    for filename in os.listdir(MODEL_DIR):
        if filename.endswith(".pkl"):
            model_name = filename.replace(".pkl", "")
            with open(os.path.join(MODEL_DIR, filename), "rb") as f:
                loaded_models[model_name] = pickle.load(f)
    print("Models loaded successfully:", list(loaded_models.keys()))


@app.get("/")
def root():
    return {"message": "Crash Prediction API is Live!"}

# /models endpoint
@app.get("/models")
def list_models():
    return {"available_models": list(loaded_models.keys())}


# /Classification predict endpoint
@app.post("/predict_classification")
def predict_classication(data: ModelSelection):
    print("\nUsing Classification Prediction Endpoint:\n")
    model_name = data.model_name
    if model_name not in loaded_models:
        raise HTTPException(status_code=404, detail="Model not found.")

    model = loaded_models[model_name]

    print("Model Used:", model_name)

    # Extract input dict
    input_data = data.inputs.model_dump()

    for field in ['is_weekend', 'is_holiday']:
        input_data[field] = int(input_data[field])

    # Flatten dict values if any are nested (e.g., {"value": 100})
    flattened_inputs = {
        k: (v["value"] if isinstance(v, dict) and "value" in v else v)
        for k, v in input_data.items()
    }

    # print("Flattened input:", flattened_inputs)

    features = np.array([list(flattened_inputs.values())])
    
    print("Features passed to the model:\n", features)

    print("Features shape:", features.shape)


    # Prediction using model
    try:
        prediction = model.predict(features)

        print("\nPrediction output:", prediction)

        pred_crash_counts = prediction[0]["pred_crash_counts"]

        pred_crash_counts = str(pred_crash_counts)

        print("\nPredicted crash counts:", str(pred_crash_counts))

        return {"predicted_crashes": pred_crash_counts}

    except Exception as e:
            print(f"Model prediction error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# /Regression predict endpoint
@app.post("/predict_regression")
def predict_regression(data: ModelSelection_Regression):
    print("\nUsing Regression Prediction Endpoint:\n")
    model_name = "catBoost_regression_pickled"
    if model_name not in loaded_models:
        raise HTTPException(status_code=404, detail="Regression model not found.")

    model = loaded_models[model_name]
    input_dict = data.inputs.dict()

    # Convert bool to int
    for field in ['is_weekend', 'is_holiday']:
        input_dict[field] = str(input_dict[field])

    regression_features = np.array([list(input_dict.values())])

    print("Features passed to the model:\n", regression_features)

    print("Features shape:", regression_features.shape)


    try:
        prediction = model.predict(regression_features)
        print("Prediction output:", prediction)
        return {"predicted_crash_count": round(float(prediction[0]))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)