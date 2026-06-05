from flask import Flask, request, jsonify
from flask_cors import CORS 
from pipeline import predict_single
import pickle

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Load artifacts
with open("model.pkl", "rb") as f: model = pickle.load(f)
with open("vectorizers.pkl", "rb") as f: vectorizers = pickle.load(f)
with open("config.pkl", "rb") as f: config = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text', '')
    label, confidence = predict_single(text, model, vectorizers, 
                                      lang=config["lang"], 
                                      label_map=config["label_names"])
    return jsonify({"label": label, "confidence": confidence})

if __name__ == '__main__':
    app.run(port=5000)