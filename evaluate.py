import numpy as np
import time
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix, roc_auc_score,
)


def evaluate_model(model, X_val, y_val, verbose=True, label_names=None):
    y_pred = model.predict(X_val)
    is_binary = len(np.unique(y_val)) == 2
    avg = "binary" if is_binary else "weighted"

    metrics = {
        "accuracy":  accuracy_score(y_val, y_pred),
        "f1":        f1_score(y_val, y_pred, average=avg, zero_division=0),
        "precision": precision_score(y_val, y_pred, average=avg, zero_division=0),
        "recall":    recall_score(y_val, y_pred, average=avg, zero_division=0),
    }

    # AUC if model supports probabilities
    if hasattr(model, "predict_proba"):
        try:
            if is_binary:
                metrics["auc"] = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
            else:
                metrics["auc"] = roc_auc_score(
                    y_val, model.predict_proba(X_val),
                    multi_class="ovr", average="weighted"
                )
        except Exception:
            metrics["auc"] = None

    if verbose:
        print_metrics(metrics, y_val, y_pred, label_names=label_names)

    return metrics


def print_metrics(metrics, y_true, y_pred, label_names=None):
    print("\n" + "="*50)
    print("  Model Evaluation")
    print("="*50)
    print(f"  Accuracy  : {metrics['accuracy']:.4f}  ({metrics['accuracy']*100:.1f}%)")
    print(f"  F1 Score  : {metrics['f1']:.4f}")
    print(f"  Precision : {metrics['precision']:.4f}")
    print(f"  Recall    : {metrics['recall']:.4f}")
    if metrics.get("auc"):
        print(f"  AUC-ROC   : {metrics['auc']:.4f}")
    print("="*50)

    print("\n[Classification Report]")
    print(classification_report(y_true, y_pred, target_names=label_names,
                                  zero_division=0))

    print("[Confusion Matrix]")
    cm = confusion_matrix(y_true, y_pred)
    print(cm)
    print()


def find_failure_cases(model, X_val_raw, X_val_feat, y_val, n=10, label_names=None):
    y_pred = model.predict(X_val_feat)
    wrong_idx = np.where(y_pred != y_val)[0]

    if len(wrong_idx) == 0:
        print("No errors found on validation set — check for data leakage!")
        return []

    # Sort by confidence of wrong prediction if possible
    confidences = np.zeros(len(wrong_idx))
    if hasattr(model, "decision_function"):
        try:
            scores = model.decision_function(X_val_feat[wrong_idx])
            if scores.ndim > 1:
                confidences = scores.max(axis=1)
            else:
                confidences = np.abs(scores)
        except Exception:
            pass

    sorted_idx = wrong_idx[np.argsort(-confidences)][:n]

    print(f"\n[Failure Cases] Top {min(n, len(sorted_idx))} confident errors:\n")
    cases = []
    for i, idx in enumerate(sorted_idx):
        true_label = label_names[y_val[idx]] if label_names else y_val[idx]
        pred_label = label_names[y_pred[idx]] if label_names else y_pred[idx]
        text_preview = str(X_val_raw[idx])[:120]
        print(f"  [{i+1}] True: {true_label} | Predicted: {pred_label}")
        print(f"       Text: {text_preview}...")
        print()
        cases.append({"text": X_val_raw[idx], "true": true_label, "pred": pred_label})

    return cases


def check_class_balance(y, label_names=None):
    from collections import Counter
    counts = Counter(y)
    total = len(y)
    print("\n[Class Balance]")
    for label, count in sorted(counts.items()):
        name = label_names[label] if label_names else label
        bar = "█" * int(30 * count / total)
        print(f"  {str(name):<15} {count:>5} ({count/total*100:.1f}%)  {bar}")

    values = list(counts.values())
    ratio = max(values) / min(values)
    if ratio > 3:
        print(f"\n  [WARN] Imbalance ratio {ratio:.1f}:1 — use class_weight='balanced'")
        print(f"         Also consider: F1-macro as your primary metric, not accuracy.")
    else:
        print(f"\n  Ratio: {ratio:.1f}:1 — balanced enough for standard training.")
    print()


def pick_metric(y, task_description=""):
    from collections import Counter
    counts = Counter(y)
    values = list(counts.values())
    ratio = max(values) / min(values)
    n_classes = len(counts)

    print("\n[Metric Selection Guide]")
    if ratio > 3:
        print("  Dataset is IMBALANCED.")
        print("  => Primary metric : F1-macro (treats all classes equally)")
        print("  => Watch          : Per-class recall on minority class")
        print("  => Avoid          : Accuracy (misleading when imbalanced)")
    elif n_classes > 2:
        print("  Multi-class problem.")
        print("  => Primary metric : F1-weighted or F1-macro")
        print("  => Secondary      : Per-class F1 in classification report")
    else:
        print("  Binary, balanced problem.")
        print("  => Primary metric : F1 or AUC-ROC")
        print("  => Secondary      : Precision/Recall tradeoff curve")

    print(f"\n  Judge answer template:")
    print(f'  "I chose [metric] because [reason]. My model achieved [score].')
    print(f'   On the minority class specifically, recall was [X]."')
    print()