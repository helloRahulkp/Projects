import os
import pickle
import sys
import time
from flask import Blueprint, render_template, request, jsonify
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from feature_extractor import extract_features, FEATURE_NAMES

main = Blueprint("main", __name__)

_model = None


def get_model():
    global _model
    if _model is None:
        model_path = os.path.join(BASE_DIR, "models", "phishing_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                "Model not found. Run: python scripts/train_pipeline.py"
            )
        with open(model_path, "rb") as f:
            _model = pickle.load(f)
    return _model


def analyse_url(url: str) -> dict:
    model = get_model()
    features = extract_features(url)
    df = pd.DataFrame([features], columns=FEATURE_NAMES)

    prediction  = model.predict(df)[0]
    proba       = model.predict_proba(df)[0]
    phishing_pct = round(float(proba[1]) * 100, 2)
    legit_pct    = round(float(proba[0]) * 100, 2)
    confidence   = round(float(max(proba)) * 100, 2)

    # Risk level
    if phishing_pct >= 80:
        risk = "HIGH"
    elif phishing_pct >= 50:
        risk = "MEDIUM"
    elif phishing_pct >= 25:
        risk = "LOW"
    else:
        risk = "SAFE"

    # Feature breakdown for UI
    feature_detail = {
        "Has IP Address":       features[0],
        "Suspicious URL Length":features[1],
        "URL Shortener":        features[2],
        "@ Symbol":             features[3],
        "Suspicious TLD":       features[20],
        "Brand in Subdomain":   features[21],
        "Encoded Characters":   features[16],
        "Suspicious Keywords":  features[12],
        "Hyphen in Domain":     features[15],
        "Non-standard Port":    features[22],
    }

    return {
        "url":           url,
        "is_phishing":   bool(prediction == 1),
        "label":         "PHISHING" if prediction == 1 else "LEGITIMATE",
        "phishing_pct":  phishing_pct,
        "legit_pct":     legit_pct,
        "confidence":    confidence,
        "risk_level":    risk,
        "features":      feature_detail,
    }


# ── Pages ─────────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    return render_template("index.html")


@main.route("/about")
def about():
    return render_template("about.html")


# ── API ───────────────────────────────────────────────────────────────────────

@main.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    url  = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    if not url.startswith("http"):
        url = "https://" + url

    try:
        start  = time.time()
        result = analyse_url(url)
        result["analysis_time_ms"] = round((time.time() - start) * 1000, 2)
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@main.route("/api/health")
def health():
    try:
        get_model()
        model_loaded = True
    except Exception:
        model_loaded = False
    return jsonify({
        "status":       "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
    })


@main.route("/api/batch", methods=["POST"])
def batch_predict():
    """Predict multiple URLs at once."""
    data = request.get_json(silent=True) or {}
    urls = data.get("urls", [])

    if not urls or not isinstance(urls, list):
        return jsonify({"error": "Provide a JSON list under 'urls'"}), 400
    if len(urls) > 50:
        return jsonify({"error": "Maximum 50 URLs per batch"}), 400

    results = []
    for url in urls:
        url = url.strip()
        if not url.startswith("http"):
            url = "https://" + url
        try:
            results.append(analyse_url(url))
        except Exception as e:
            results.append({"url": url, "error": str(e)})

    return jsonify({"results": results, "total": len(results)})
