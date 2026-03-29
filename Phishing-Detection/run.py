#!/usr/bin/env python3
"""
Entry point — run the Flask web application.

    python run.py              # development
    python run.py --prod       # production (gunicorn)
"""
import os
import sys
import argparse

# Make sure src/ is importable from app/
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

parser = argparse.ArgumentParser()
parser.add_argument("--prod", action="store_true", help="Run in production mode")
args = parser.parse_args()

config = ProductionConfig if args.prod else DevelopmentConfig
app    = create_app(config)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  PhishGuard running at http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=config.DEBUG)
