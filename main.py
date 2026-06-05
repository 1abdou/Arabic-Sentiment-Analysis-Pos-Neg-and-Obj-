# ════════════════════════════════════════════════════════════════
# CELL 0: IMPORTS + TIMER
# ════════════════════════════════════════════════════════════════
import pandas as pd
import numpy as np
import time
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from preprocessing import detect_language, preprocess_df, text_stats
from pipeline import build_features, build_models, train_all_models, quick_tune_svc, quick_tune_lr, predict_single
from evaluate import evaluate_model, check_class_balance, pick_metric, find_failure_cases

START_TIME = time.time()

def elapsed():
    m = (time.time() - START_TIME) / 60
    print(f"\n⏱  Elapsed: {m:.1f} min | Remaining: {max(0, 480 - m):.1f} min\n")

print("Kit loaded. Competition clock started.")
elapsed()


# ════════════════════════════════════════════════════════════════
# HOUR 0–1: FOUNDATION
# ════════════════════════════════════════════════════════════════

# ── CELL 1: Load data ─────────────────────────────────────────
DATA_PATH  = "dataset.csv"
TEXT_COL   = "text"               # name of the text column
LABEL_COL  = "label"              # name of the target column

df = pd.read_csv(DATA_PATH)
print(f"Shape: {df.shape}")
print(df.head(3))
print(f"\nColumns: {list(df.columns)}")
print(f"Label distribution:\n{df[LABEL_COL].value_counts()}")
elapsed()


# ── CELL 2: EDA ──────────────────────────────
text_stats(df, text_col=TEXT_COL)
check_class_balance(df[LABEL_COL].values)
pick_metric(df[LABEL_COL].values)

# Quick checks — fix any issues before moving on
print("Null text rows :", df[TEXT_COL].isna().sum())
print("Null label rows:", df[LABEL_COL].isna().sum())
print("Duplicate rows :", df.duplicated(subset=[TEXT_COL]).sum())

# Drop nulls and duplicates if any
df = df.dropna(subset=[TEXT_COL, LABEL_COL]).reset_index(drop=True)
df = df.drop_duplicates(subset=[TEXT_COL], keep='first').reset_index(drop=True)

print()
print("Null text rows :", df[TEXT_COL].isna().sum())
print("Null label rows:", df[LABEL_COL].isna().sum())
print("Duplicate rows :", df.duplicated(subset=[TEXT_COL]).sum())

elapsed()


# ── CELL 3: Language detection + label encoding ──────────────
LANG = detect_language(df, text_col=TEXT_COL)

# Encode labels to integers if they aren't already
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df["label_enc"] = le.fit_transform(df[LABEL_COL])
LABEL_NAMES = list(le.classes_)
print(f"Classes: {LABEL_NAMES}")
elapsed()


# ── CELL 4: Train/val split ───────────────────────────────────
X_train_raw, X_val_raw, y_train, y_val = train_test_split(
    df[TEXT_COL].values,
    df["label_enc"].values,
    test_size=0.15,
    random_state=42,
    stratify=df["label_enc"].values,
)
print(f"Train: {len(X_train_raw)} | Val: {len(X_val_raw)}")
elapsed()


# ── CELL 5: Preprocessing ─────────────────────────────────────
from preprocessing import clean_text

X_train_clean = np.array([clean_text(t, lang=LANG) for t in X_train_raw])
X_val_clean   = np.array([clean_text(t, lang=LANG) for t in X_val_raw])

# Spot-check 3 examples
print("[Preprocessing sample]")
for i in range(3):
    print(f"  Raw : {X_train_raw[i][:80]}")
    print(f"  Clean: {X_train_clean[i][:80]}")
    print()
elapsed()


# ════════════════════════════════════════════════════════════════
# HOUR 1–4: DEVELOPMENT
# ════════════════════════════════════════════════════════════════

# ── CELL 6: Build features ────────────────────────────────────
X_train_feat, X_val_feat, VECTORIZERS = build_features(
    X_train_clean, X_val_clean,
    lang=LANG,
    use_char=True,
)
elapsed()


# ── CELL 7: Baseline — all models ────────────────────────────
models = build_models(y_train)
results, BEST_MODEL_NAME = train_all_models(
    X_train_feat, y_train,
    X_val_feat, y_val,
    models=models,
)
BEST_MODEL = results[BEST_MODEL_NAME]["model"]
elapsed()


# ── CELL 8: Full eval of best model ──────────────────────────
print(f"\n[Full Eval: {BEST_MODEL_NAME}]")
metrics = evaluate_model(BEST_MODEL, X_val_feat, y_val,
                          verbose=True, label_names=LABEL_NAMES)
elapsed()

# ── CELL 9: Quick tune ──────
if (time.time() - START_TIME) < 150 * 60:
    if BEST_MODEL_NAME == "LinearSVC":
        BEST_MODEL = quick_tune_svc(X_train_feat, y_train, X_val_feat, y_val)
    elif BEST_MODEL_NAME == "LogisticRegression":
        BEST_MODEL = quick_tune_lr(X_train_feat, y_train, X_val_feat, y_val)
    # Re-evaluate after tuning
    metrics = evaluate_model(BEST_MODEL, X_val_feat, y_val,
                              verbose=True, label_names=LABEL_NAMES)
elapsed()

# ════════════════════════════════════════════════════════════════
# HOUR 4–5: ANALYSIS & REVIEW
# ════════════════════════════════════════════════════════════════

# ── CELL 11: Know your numbers cold ──────────────────────────
print("\n" + "="*50)
print("FINAL MODEL SCORECARD")
print("="*50)
print(f"Model      : {BEST_MODEL_NAME}")
print(f"Language   : {LANG}")
print(f"Features   : word TF-IDF + char n-grams")
print(f"Accuracy   : {metrics['accuracy']*100:.1f}%")
print(f"F1         : {metrics['f1']:.4f}")
print(f"Precision  : {metrics['precision']:.4f}")
print(f"Recall     : {metrics['recall']:.4f}")
if metrics.get('auc'):
    print(f"AUC-ROC    : {metrics['auc']:.4f}")
print("="*50)
elapsed()


# ── CELL 12: Failure cases (for pitch) ───────────────────────
failures = find_failure_cases(
    BEST_MODEL,
    X_val_raw,        # original text for readability
    X_val_feat,
    y_val,
    n=5,
    label_names=LABEL_NAMES,
)
elapsed()

# ════════════════════════════════════════════════════════════════
# HOUR 5–6: DEMO + VISUALIZATION
# ════════════════════════════════════════════════════════════════

# ── CELL 13: Quick demo predictions ──────────────────────────
test_inputs = [
    "أنا لا أحب هذا اللاعب",
    "أنا أحب هذا اللاعب",
    "لم أشاهد هذا اللاعب من قبل",
]
print("\n[Demo Predictions]")
for text in test_inputs:
    label, conf = predict_single(text, BEST_MODEL, VECTORIZERS,
                                  lang=LANG, label_map=LABEL_NAMES)
    conf_str = f"{conf*100:.1f}%" if conf else "N/A"
    print(f"  Input      : {text[:60]}")
    print(f"  Prediction : {label} (confidence: {conf_str})")
    print()


from save_model import save_model
save_model(
    model=BEST_MODEL,
    vectorizers=VECTORIZERS,
    lang=LANG,
    label_names=LABEL_NAMES,
    model_name=BEST_MODEL_NAME,
    metrics=metrics,
)

# ── CELL 14: Top features per class ──────────────────────────
def print_top_features(model, vectorizer, label_names, n=10):
    """Works for LogisticRegression and LinearSVC."""
    if not hasattr(model, "coef_"):
        print("[Top features] Not available for this model type.")
        return
    feature_names = vectorizer.get_feature_names_out()
    coef = model.coef_
    if coef.shape[0] == 1:
        coef = np.vstack([-coef, coef])

    print("\n[Top Features Per Class]")
    for i, label in enumerate(label_names):
        if i >= coef.shape[0]:
            break
        # Limit coefficients to available features
        coef_i = coef[i][:len(feature_names)]
        top_idx = np.argsort(coef_i)[-n:][::-1]
        top_words = [feature_names[j] for j in top_idx]
        print(f"  {label}: {top_words}")

if "word" in VECTORIZERS:
    print_top_features(BEST_MODEL, VECTORIZERS["word"], LABEL_NAMES)
elapsed()