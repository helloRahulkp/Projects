import os
import pickle
import pandas as pd
from feature_extractor import extract_features, FEATURE_NAMES

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "phishing_model.pkl")


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}\n"
            "Run the following first:\n"
            "  1. python data_creation.py\n"
            "  2. python dataset_builder.py\n"
            "  3. python RandomForestTraining.py"
        )
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def predict_url(url: str, model) -> dict:
    """Return prediction dict with label, phishing %, legit %, confidence."""
    features = extract_features(url)
    df = pd.DataFrame([features], columns=FEATURE_NAMES)

    prediction = model.predict(df)[0]
    proba      = model.predict_proba(df)[0]   # [P(legit), P(phishing)]

    phishing_pct = round(proba[1] * 100, 2)
    legit_pct    = round(proba[0] * 100, 2)
    confidence   = round(max(proba) * 100, 2)

    return {
        "url":          url,
        "label":        "PHISHING" if prediction == 1 else "LEGITIMATE",
        "is_phishing":  bool(prediction == 1),
        "phishing_pct": phishing_pct,
        "legit_pct":    legit_pct,
        "confidence":   confidence,
    }


def display_result(result: dict):
    url         = result["url"]
    label       = result["label"]
    is_phishing = result["is_phishing"]
    ph_pct      = result["phishing_pct"]
    lg_pct      = result["legit_pct"]
    conf        = result["confidence"]

    bar_width  = 30
    ph_filled  = int(ph_pct / 100 * bar_width)
    bar        = "█" * ph_filled + "░" * (bar_width - ph_filled)

    icon  = "⚠️  PHISHING" if is_phishing else "✅ LEGITIMATE"
    color = "\033[91m" if is_phishing else "\033[92m"   # red / green
    reset = "\033[0m"

    print("\n" + "─" * 55)
    print(f"  URL      : {url}")
    print("─" * 55)
    print(f"  Result   : {color}{icon}{reset}")
    print(f"  Phishing : {ph_pct:>6.2f}%  [{bar}]")
    print(f"  Legit    : {lg_pct:>6.2f}%")
    print(f"  Confidence: {conf:.2f}%")
    print("─" * 55 + "\n")


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = load_model()

    print("\n🔍 Phishing URL Detector")
    print("   Type 'quit' to exit\n")

    while True:
        url = input("Enter URL: ").strip()

        if not url:
            continue
        if url.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Auto-add scheme if missing
        if not url.startswith("http"):
            url = "https://" + url

        try:
            result = predict_url(url, model)
            display_result(result)
        except Exception as e:
            print(f"  Error analysing URL: {e}\n")


# This urls sysstem must classify as phising urls

# http://192.168.1.1/login/verify-account
# http://185.234.219.20/paypal/secure/login.php
# http://amazon-security-alert.tk/verify
# http://paypal-account-suspended.xyz/restore
# http://apple-id-locked.top/unlock
# http://paypal.account-verify.com/login
# http://google.com.security-alert.net/signin
# http://apple.id-verification.com/update
# http://xn--pypl-poa.com/login
# http://secure-login%40paypal.com.phish.net/verify
# http://g%6F%6Fgle.tk/account/reset
# http://www.paypal-secure-account-login-verify.com/signin
# http://amazon-prime-account-suspended-verify-now.com
# http://bit.ly/3xPhish99
# http://tinyurl.com/fakepaypal