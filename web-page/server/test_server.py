from flask import Flask, request, jsonify
from flask_cors import CORS
from pipeline import predict_single
import pickle
import traceback

app = Flask(__name__)
CORS(app)

with open('model.pkl', 'rb') as f: model = pickle.load(f)
with open('vectorizers.pkl', 'rb') as f: vectorizers = pickle.load(f)
with open('config.pkl', 'rb') as f: config = pickle.load(f)

print("Models loaded successfully")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        text = data.get('text', '')
        print(f"Received text: {text}")
        label, confidence = predict_single(text, model, vectorizers, 
                                          lang=config['lang'], 
                                          label_map=config['label_names'])
        print(f"Result: {label}, {confidence}")
        return jsonify({'label': label, 'confidence': confidence})
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(port=5000)