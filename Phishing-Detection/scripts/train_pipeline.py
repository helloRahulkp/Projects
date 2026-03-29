"""
scripts/train_pipeline.py
One-command full pipeline: download → features → train
"""
import os, sys, time, csv, io, zipfile
import requests

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(ROOT, "data", "processed")
MODELS    = os.path.join(ROOT, "models")
os.makedirs(PROCESSED, exist_ok=True)
os.makedirs(MODELS, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "src"))


def step(n, title):
    print(f"\n{'='*55}\n  STEP {n}/3 — {title}\n{'='*55}")


# ══════════════════════════════════════════════════════
# STEP 1: Download URLs
# ══════════════════════════════════════════════════════
step(1, "Downloading URL data")
t0 = time.time()

phishing_urls = set()

# Source 1: OpenPhish (~300 URLs, fast)
try:
    r = requests.get("https://openphish.com/feed.txt", timeout=15)
    for line in r.text.splitlines():
        l = line.strip()
        if l.startswith("http"):
            phishing_urls.add(l)
    print(f"  OpenPhish        : {len(phishing_urls)}")
except Exception as e:
    print(f"  OpenPhish failed : {e}")

# Source 2: URLhaus (~20k URLs, fast)
try:
    r = requests.get("https://urlhaus.abuse.ch/downloads/csv_recent/", timeout=30)
    before = len(phishing_urls)
    for line in r.text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split('","')
        if len(parts) > 2:
            url = parts[2].strip('"')
            if url.startswith("http"):
                phishing_urls.add(url)
    print(f"  URLhaus          : +{len(phishing_urls)-before}")
except Exception as e:
    print(f"  URLhaus failed   : {e}")

# Cap at 25k — enough for a great model, fast to process
CAP = 25000
phishing_urls = set(list(phishing_urls)[:CAP])
phish_out = os.path.join(PROCESSED, "phishing_urls.txt")
with open(phish_out, "w") as f:
    for u in phishing_urls:
        f.write(u + "\n")
n_phish = len(phishing_urls)
print(f"  ✅ Phishing saved : {n_phish}")

# Legitimate URLs — Majestic Million streamed, stops at target
target  = min(n_phish, 25000)
domains, seen = [], set()

print(f"\n  Downloading {target} legitimate URLs...")
try:
    r = requests.get(
        "https://downloads.majestic.com/majestic_million.csv",
        timeout=30, stream=True
    )
    buf, first = "", True
    for chunk in r.iter_content(chunk_size=8192, decode_unicode=True):
        buf += chunk
        lines = buf.split("\n")
        buf   = lines[-1]
        for line in lines[:-1]:
            if first:
                first = False
                continue
            parts = line.strip().split(",")
            if len(parts) >= 3:
                d = parts[2].strip()
                if d and d not in seen:
                    seen.add(d)
                    domains.append(d)
            if len(domains) >= target:
                break
        if len(domains) >= target:
            break
    print(f"  Majestic Million : {len(domains)}")
except Exception as e:
    print(f"  Majestic failed  : {e}")

# Fallback: Tranco
if len(domains) < target:
    try:
        r = requests.get("https://tranco-list.eu/top-1m.csv.zip", timeout=60)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            with z.open(z.namelist()[0]) as f:
                for row in csv.reader(io.TextIOWrapper(f)):
                    if len(row) >= 2:
                        d = row[1].strip()
                        if d and d not in seen:
                            seen.add(d)
                            domains.append(d)
                    if len(domains) >= target:
                        break
        print(f"  Tranco           : total {len(domains)}")
    except Exception as e:
        print(f"  Tranco failed    : {e}")

legit_out = os.path.join(PROCESSED, "legitimate_urls.txt")
with open(legit_out, "w") as f:
    for d in domains[:target]:
        f.write("https://" + d + "\n")
n_legit = min(len(domains), target)
print(f"  ✅ Legitimate saved: {n_legit}")
print(f"  ⏱  Time: {time.time()-t0:.1f}s")


# ══════════════════════════════════════════════════════
# STEP 2: Extract features
# ══════════════════════════════════════════════════════
step(2, "Extracting features")
t0 = time.time()

import pandas as pd
from feature_extractor import extract_features, FEATURE_NAMES

def load_urls(path, label):
    rows = []
    with open(path) as f:
        for line in f:
            u = line.strip()
            if u:
                rows.append((u, label))
    return rows

phish_rows = load_urls(phish_out,  1)
legit_rows = load_urls(legit_out,  0)

cap = min(len(phish_rows), len(legit_rows))
phish_rows = phish_rows[:cap]
legit_rows = legit_rows[:cap]
print(f"  Processing {cap} phishing + {cap} legitimate = {cap*2} total URLs")

data, errors = [], 0
total = len(phish_rows) + len(legit_rows)

for i, (url, label) in enumerate(phish_rows + legit_rows):
    try:
        data.append(extract_features(url) + [label])
    except Exception:
        errors += 1
    if (i + 1) % 5000 == 0:
        print(f"    {i+1}/{total} processed...")

df = pd.DataFrame(data, columns=FEATURE_NAMES + ["label"])
csv_out = os.path.join(PROCESSED, "url_dataset.csv")
df.to_csv(csv_out, index=False)
print(f"  ✅ Dataset saved  : {df.shape}  ({errors} errors skipped)")
print(f"  Class distribution:\n{df['label'].value_counts().to_string()}")
print(f"  ⏱  Time: {time.time()-t0:.1f}s")


# ══════════════════════════════════════════════════════
# STEP 3: Train model
# ══════════════════════════════════════════════════════
step(3, "Training Random Forest")
t0 = time.time()

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pickle

X = df.drop("label", axis=1)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"  Train: {len(X_train)} rows  |  Test: {len(X_test)} rows")
print("  Training... (this takes ~30-60 seconds)")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=20,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1          # use all CPU cores
)
model.fit(X_train, y_train)

y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print(f"\n  Accuracy : {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"  ROC-AUC  : {roc_auc_score(y_test, y_proba):.4f}")
print("\n" + classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"])) # type: ignore

model_out = os.path.join(MODELS, "phishing_model.pkl")
with open(model_out, "wb") as f:
    pickle.dump(model, f)

print(f"  ✅ Model saved    : {model_out}")
print(f"  ⏱  Time: {time.time()-t0:.1f}s")

print(f"""
{'='*55}
  PIPELINE COMPLETE!

  Run the web app:
    python run.py

  Open browser:
    http://localhost:5000
{'='*55}
""")