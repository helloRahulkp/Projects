# PhishGuard — ML Phishing URL Detector

> End-to-end machine learning project: data collection → feature engineering → model training → REST API → web UI

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---v

## Project Structure

```
phishing-detection/
├── run.py                        # Flask app entry point
├── requirements.txt
│
├── app/                          # Web application
│   ├── __init__.py               # App factory
│   ├── config.py                 # Dev / Prod / Test configs
│   ├── routes.py                 # API + page routes
│   └── templates/
│       ├── index.html            # Main detector UI
│       └── about.html            # Project info page
│
├── src/                          # Core ML pipeline
│   ├── feature_extractor.py      # 30 URL features
│   ├── data_creation.py          # Download phishing + legit URLs
│   ├── dataset_builder.py        # Build url_dataset.csv
│   ├── RandomForestTraining.py   # Train & evaluate model
│   └── detect_url.py             # CLI predictor
│
├── scripts/
│   └── train_pipeline.py         # One-command full pipeline
│
├── data/
│   ├── raw/                      # Original source files
│   └── processed/                # phishing_urls.txt, legitimate_urls.txt, url_dataset.csv
│
├── models/
│   └── phishing_model.pkl        # Trained Random Forest (generated)
│
├── notebooks/
│   └── ...                       # EDA and model experiments
│
└── tests/
    └── test_features.py          # Feature extraction unit tests
```

---

## Quickstart

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train the model (one command)

```bash
python scripts/train_pipeline.py
```

This downloads data, extracts features, trains the model, and saves `models/phishing_model.pkl`.

### 3. Run the web app

```bash
python run.py
```

Open `http://localhost:5000`

### 4. CLI usage

```bash
python src/detect_url.py
```

---

## REST API

### Single prediction

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-secure-login.tk/verify"}'
```

**Response:**

```json
{
  "url": "http://paypal-secure-login.tk/verify",
  "label": "PHISHING",
  "is_phishing": true,
  "phishing_pct": 97.3,
  "legit_pct": 2.7,
  "confidence": 97.3,
  "risk_level": "HIGH",
  "features": { ... },
  "analysis_time_ms": 12.4
}
```

### Batch prediction (up to 50 URLs)

```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://google.com", "http://evil.tk/login"]}'
```

### Health check

```bash
curl http://localhost:5000/api/health
```

---

## Features Extracted (30 total)

| #     | Feature         | Description                                         |
| ----- | --------------- | --------------------------------------------------- |
| 1     | IP Address      | Raw IP used instead of domain                       |
| 2     | URL Length      | Penalises very long URLs (190+ chars)               |
| 3     | URL Shortener   | bit.ly, tinyurl, goo.gl, etc.                       |
| 4     | @ Symbol        | Forces browser to use post-@ part                   |
| 5     | Double Slash    | Redirect via `//` in path                           |
| 6     | Prefix/Suffix   | Hyphen in domain name                               |
| 7     | Subdomain Depth | Excessive subdomains                                |
| 8     | HTTPS in Domain | "https" appearing inside domain text                |
| 9     | Digit Ratio     | High proportion of digits                           |
| 10    | Special Chars   | Excess `?`, `=`, `&`                                |
| 11–30 | + 20 more       | Keywords, TLD, brand spoofing, entropy, encoding... |

---

## Model Performance

| Metric          | Score                     |
| --------------- | ------------------------- |
| Accuracy        | ~95%+                     |
| ROC-AUC         | ~0.98                     |
| Algorithm       | Random Forest (300 trees) |
| Class weighting | Balanced                  |

---

## Data Sources

| Type       | Source                                           |
| ---------- | ------------------------------------------------ |
| Phishing   | OpenPhish, URLhaus, PhishTank, Phishing.Database |
| Legitimate | Majestic Million, Tranco Top-1M                  |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Author

## **RAHUL•KP•KURUP** — [GitHub Portfolio](https://github.com/helloRahulkp)

## License

This project is licensed under the MIT License — see the LICENSE file for details.
