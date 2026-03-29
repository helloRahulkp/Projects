import os
import pandas as pd
from feature_extractor import extract_features, FEATURE_NAMES

# ─── Paths (relative to this script's directory) ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
phishing_file  = os.path.join(BASE_DIR, "phishing_urls.txt")
legit_file     = os.path.join(BASE_DIR, "legitimate_urls.txt")
output_csv     = os.path.join(BASE_DIR, "url_dataset.csv")


# ─── Load URLs ────────────────────────────────────────────────────────────────
def load_urls(filepath, label):
    urls, labels = [], []
    with open(filepath) as f:
        for line in f:
            u = line.strip()
            if u:
                urls.append(u)
                labels.append(label)
    return urls, labels


# ─── Build dataset ────────────────────────────────────────────────────────────
phish_urls, phish_labels = load_urls(phishing_file, label=1)
legit_urls,  legit_labels  = load_urls(legit_file,  label=0)

# Balance: match phishing count to avoid model bias toward "legitimate"
min_count = min(len(phish_urls), len(legit_urls))
phish_urls   = phish_urls[:min_count]
phish_labels = phish_labels[:min_count]
legit_urls   = legit_urls[:min_count]
legit_labels = legit_labels[:min_count]

print(f"Building dataset: {min_count} phishing + {min_count} legitimate = {min_count*2} total")

all_urls   = phish_urls   + legit_urls
all_labels = phish_labels + legit_labels

data = []
errors = 0

for url, label in zip(all_urls, all_labels):
    try:
        features = extract_features(url)
        data.append(features + [label])
    except Exception:
        errors += 1
        continue

print(f"  Features extracted: {len(data)} rows ({errors} errors skipped)")

columns = FEATURE_NAMES + ["label"]
df = pd.DataFrame(data, columns=columns)
df.to_csv(output_csv, index=False)

print(f"  Dataset saved → {output_csv}")
print(f"  Shape: {df.shape}")
print(f"  Class distribution:\n{df['label'].value_counts().to_string()}")