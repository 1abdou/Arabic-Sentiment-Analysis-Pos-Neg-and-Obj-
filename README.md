# NLP Hackathon - Arabic Text Classification

A complete machine learning pipeline for Arabic text classification with a web interface.

## 📋 Project Overview

This project combines:
- **Backend**: Python-based NLP pipeline with scikit-learn models (Logistic Regression, SVM, Naive Bayes, Random Forest)
- **Frontend**: Next.js web application with theme support
- **API**: Flask server for real-time predictions

## 🏗️ Project Structure

### Root Level (Python ML Pipeline)
- `main.py` - Main orchestration script for data loading, preprocessing, and model training
- `pipeline.py` - Feature engineering and model building (TF-IDF, ensemble methods)
- `preprocessing.py` - Text preprocessing, language detection, and statistics
- `evaluate.py` - Model evaluation and performance metrics
- `save_model.py` - Model persistence and artifact saving
- `dataset.csv` - Training/test dataset
- `requirements.txt` - Python dependencies

### Web Application (`web-page/`)
- **`client/`** - Next.js frontend (TypeScript/React)
  - UI components with theme toggle, forms, FAQs
  - Responsive design using Tailwind CSS
- **`server/`** - Flask backend API
  - `server.py` - Flask app with `/predict` endpoint
  - `test_server.py` - API testing utilities
  - Loads pre-trained models and vectorizers

## 🚀 Getting Started

### Backend Setup
```bash
cd Arabic-Sentiment-Analysis-Pos-Neg-and-Obj-
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Train & Save Models
```bash
python main.py
python save_model.py
```

### Start API Server
```bash
cd web-page/server
python server.py
```

### Frontend Setup
```bash
cd web-page/client
npm install
npm run dev
```

## 🔧 Key Features

- **Advanced NLP**: TF-IDF (word & character n-grams)
- **Web Interface**: Real-time predictions with interactive UI
- **REST API**: Flask endpoint for model predictions with confidence scores

## 📦 Dependencies

- `pandas`, `numpy` - Data processing
- `scikit-learn`, `scipy` - Machine learning
- `flask`, `flask-cors` - Backend API
- `streamlit` - Optional UI
- Next.js, React, TypeScript - Frontend

## 📝 License

Hackathon Project
