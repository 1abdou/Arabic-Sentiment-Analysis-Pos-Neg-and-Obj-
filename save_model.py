import pickle, os

def save_model(model, vectorizers, lang, label_names, model_name, metrics,
               path="artifacts"):
    """Save everything the demo app needs."""
    os.makedirs(path, exist_ok=True)

    with open(f"{path}/model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(f"{path}/vectorizers.pkl", "wb") as f:
        pickle.dump(vectorizers, f)
    with open(f"{path}/config.pkl", "wb") as f:
        pickle.dump({
            "lang":        lang,
            "label_names": label_names,
            "model_name":  model_name,
            "metrics":     metrics,
        }, f)

    print(f"[Saved] Model artifacts to '{path}/'")
    print(f"  Model     : {model_name}")
    print(f"  Language  : {lang}")
    print(f"  Classes   : {label_names}")
    print(f"  F1        : {metrics.get('f1', 0):.4f}")
    print(f"\nRun the app with: streamlit run app.py")

# ── Usage (paste this at the end of main.py, Cell 14) ─────────
# from save_model import save_model
# save_model(
#     model=BEST_MODEL,
#     vectorizers=VECTORIZERS,
#     lang=LANG,
#     label_names=LABEL_NAMES,
#     model_name=BEST_MODEL_NAME,
#     metrics=metrics,
# )