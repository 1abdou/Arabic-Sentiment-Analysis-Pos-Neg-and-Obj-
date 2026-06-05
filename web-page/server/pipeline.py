import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight
from scipy.sparse import hstack
import time
import warnings
warnings.filterwarnings("ignore")


# ── TF-IDF Feature Builders ───────────────────────────────────────────────────

def build_tfidf_word(lang="english", max_features=50000):
    """Word-level TF-IDF. Strong baseline for all languages."""
    return TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),          # unigrams + bigrams
        max_features=max_features,
        min_df=2,                    # ignore very rare terms
        max_df=0.95,                 # ignore near-universal terms
        sublinear_tf=True,           # log(tf) — helps with long docs
        strip_accents="unicode",
    )

def build_tfidf_char(lang="english", max_features=50000):
    ngram_range = (2, 5) if lang in ("arabic", "darija") else (3, 5)
    return TfidfVectorizer(
        analyzer="char_wb",          # char n-grams within word boundaries
        ngram_range=ngram_range,
        max_features=max_features,
        min_df=2,
        sublinear_tf=True,
    )

def build_features(X_train, X_val, lang="english", use_char=True):
    print(f"[Features] Building TF-IDF (lang={lang}, char_ngrams={use_char})...")
    t = time.time()

    word_vec = build_tfidf_word(lang=lang)
    X_train_w = word_vec.fit_transform(X_train)
    X_val_w = word_vec.transform(X_val)

    if use_char:
        char_vec = build_tfidf_char(lang=lang)
        X_train_c = char_vec.fit_transform(X_train)
        X_val_c = char_vec.transform(X_val)
        X_train_feat = hstack([X_train_w, X_train_c])
        X_val_feat = hstack([X_val_w, X_val_c])
        vectorizers = {"word": word_vec, "char": char_vec}
    else:
        X_train_feat = X_train_w
        X_val_feat = X_val_w
        vectorizers = {"word": word_vec}

    print(f"  Feature matrix shape: {X_train_feat.shape} | Time: {time.time()-t:.1f}s")
    return X_train_feat, X_val_feat, vectorizers

def transform_features(X, vectorizers):
    """Transform new data using fitted vectorizers (for inference)."""
    parts = [v.transform(X) for v in vectorizers.values()]
    return hstack(parts) if len(parts) > 1 else parts[0]


# ── Models ────────────────────────────────────────────────────────────────────

def get_class_weights(y):
    """Compute class weights — use when dataset is imbalanced."""
    classes = np.unique(y)
    weights = compute_class_weight("balanced", classes=classes, y=y)
    return dict(zip(classes, weights))

def build_models(y_train, task="classification"):
    cw = get_class_weights(y_train)
    is_binary = len(np.unique(y_train)) == 2

    models = {
        # LinearSVC: fastest, usually best for high-dim TF-IDF
        "LinearSVC": LinearSVC(
            C=1.0,
            max_iter=2000,
            class_weight="balanced",
        ),
        # Logistic Regression: interpretable, gives probabilities
        "LogisticRegression": LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
            n_jobs=-1,
        ),
        # MultinomialNB: fast baseline, often competitive on text
        "MultinomialNB": MultinomialNB(alpha=0.1),
    }
    return models


# ── Training + Comparison ─────────────────────────────────────────────────────

def train_all_models(X_train, y_train, X_val, y_val, models=None):
    from evaluate import evaluate_model

    if models is None:
        models = build_models(y_train)

    results = {}
    print("\n" + "-"*50)
    print(f"{'Model':<25} {'Val F1':>8} {'Val Acc':>9} {'Time':>7}")
    print("" + "-"*50)

    for name, model in models.items():
        t = time.time()
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_val, y_val, verbose=False)
        elapsed = time.time() - t
        print(f"{name:<25} {metrics['f1']:>8.4f} {metrics['accuracy']:>9.4f} {elapsed:>6.1f}s")
        results[name] = {"model": model, "metrics": metrics, "time": elapsed}

    print("-"*50)
    best = max(results, key=lambda k: results[k]["metrics"]["f1"])
    print(f"Best model: {best} (F1={results[best]['metrics']['f1']:.4f})\n")
    return results, best


# ── Hyperparameter Tuning (fast version) ─────────────────────────────────────

def quick_tune_svc(X_train, y_train, X_val, y_val):
    from evaluate import evaluate_model
    best_f1, best_C, best_model = 0, 1.0, None
    print("[Tuning] LinearSVC C sweep...")

    for C in [0.01, 0.1, 1.0, 5.0, 10.0]:
        m = LinearSVC(C=C, max_iter=2000, class_weight="balanced")
        m.fit(X_train, y_train)
        metrics = evaluate_model(m, X_val, y_val, verbose=False)
        flag = " <-- best" if metrics["f1"] > best_f1 else ""
        print(f"  C={C:<6} F1={metrics['f1']:.4f}{flag}")
        if metrics["f1"] > best_f1:
            best_f1, best_C, best_model = metrics["f1"], C, m

    print(f"Best C: {best_C} | F1: {best_f1:.4f}\n")
    return best_model

def quick_tune_lr(X_train, y_train, X_val, y_val):
    """Fast C-sweep for Logistic Regression."""
    from evaluate import evaluate_model
    best_f1, best_C, best_model = 0, 1.0, None
    print("[Tuning] LogisticRegression C sweep...")

    for C in [0.01, 0.1, 1.0, 5.0, 10.0]:
        m = LogisticRegression(C=C, max_iter=1000, class_weight="balanced",
                                solver="lbfgs", n_jobs=-1)
        m.fit(X_train, y_train)
        metrics = evaluate_model(m, X_val, y_val, verbose=False)
        flag = " <-- best" if metrics["f1"] > best_f1 else ""
        print(f"  C={C:<6} F1={metrics['f1']:.4f}{flag}")
        if metrics["f1"] > best_f1:
            best_f1, best_C, best_model = metrics["f1"], C, m

    print(f"Best C: {best_C} | F1: {best_f1:.4f}\n")
    return best_model


# ── Ensemble ─────────────────────────────────

def build_ensemble(X_train, y_train, X_val, y_val):
    from evaluate import evaluate_model

    svc = LinearSVC(C=1.0, max_iter=2000, class_weight="balanced")
    lr  = LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced",
                              solver="lbfgs", n_jobs=-1)
    nb  = ComplementNB(alpha=0.1)

    # Note: VotingClassifier needs predict_proba — use LR + NB for soft voting
    ensemble = VotingClassifier(
        estimators=[("lr", lr), ("nb", nb)],
        voting="soft",
        n_jobs=-1,
    )
    ensemble.fit(X_train, y_train)
    metrics = evaluate_model(ensemble, X_val, y_val, verbose=True)
    print(f"[Ensemble] F1={metrics['f1']:.4f}")
    return ensemble


# ── Inference helper ──────────────────────────────────────────────────────────

def predict_single(text, model, vectorizers, lang="english", label_map=None):
    from preprocessing import clean_text
    cleaned = clean_text(text, lang=lang)
    features = transform_features([cleaned], vectorizers)
    pred = model.predict(features)[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        confidence = float(proba.max())
    elif hasattr(model, "decision_function"):
        score = model.decision_function(features)[0]
        if hasattr(score, "__len__"):
            # Multi-class: softmax approximation
            exp_s = np.exp(score - score.max())
            confidence = float(exp_s.max() / exp_s.sum())
        else:
            # Binary: sigmoid approximation
            confidence = float(1 / (1 + np.exp(-abs(score))))

    label = label_map[pred] if label_map else pred
    return label, confidence