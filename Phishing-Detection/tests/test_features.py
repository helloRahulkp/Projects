"""
tests/test_features.py
─────────────────────
Run: pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from feature_extractor import extract_features, FEATURE_NAMES


# ── Helpers ────────────────────────────────────────────────────────────────────
def features_dict(url):
    return dict(zip(FEATURE_NAMES, extract_features(url)))

def phishing_score(url):
    return sum(extract_features(url))


# ── Feature count ──────────────────────────────────────────────────────────────
def test_feature_count():
    feats = extract_features("https://google.com")
    assert len(feats) == 30, f"Expected 30 features, got {len(feats)}"


# ── Known-legit sites should score LOW ────────────────────────────────────────
@pytest.mark.parametrize("url", [
    "https://www.google.com",
    "https://chatgpt.com/c/69abaa4b-7674-8323-b419-37dedc7d6382",
    "https://gemini.google.com/app/d03204b65cebf39f",
    "https://youtube.com/shorts/9a_7EuJOBfg?si=w1AMtyXuq_2OrZf2",
    "https://www.coursera.org/learn/python-project/home/module/1",
    "https://github.com/user/repo/blob/main/README.md",
])
def test_legit_urls_low_score(url):
    score = phishing_score(url)
    assert score <= 2.0, f"Legit URL scored too high ({score}): {url}"


# ── Clear phishing URLs should score HIGH ────────────────────────────────────
@pytest.mark.parametrize("url", [
    "http://192.168.1.1/login/verify-account",
    "http://paypal-account-suspended.xyz/restore",
    "http://secure-banking-update.com/account/verify/login/confirm/password/reset",
    "http://paypal.account-verify.com/login",
    "http://amazon-security-alert.tk/verify",
])
def test_phishing_urls_high_score(url):
    score = phishing_score(url)
    assert score >= 2.0, f"Phishing URL scored too low ({score}): {url}"


# ── Individual feature tests ───────────────────────────────────────────────────
def test_has_ip():
    f = features_dict("http://192.168.1.1/login")
    assert f["f1"] == 1

def test_no_ip():
    f = features_dict("https://google.com")
    assert f["f1"] == 0

def test_shortener():
    f = features_dict("http://bit.ly/abc123")
    assert f["f3"] == 1

def test_at_symbol():
    f = features_dict("http://example.com@evil.com/path")
    assert f["f4"] == 1

def test_suspicious_tld():
    f = features_dict("http://fakesite.tk/login")
    assert f["f21"] == 1

def test_brand_in_subdomain():
    f = features_dict("http://paypal.evil-site.com/login")
    assert f["f22"] == 1

def test_encoded_chars_in_domain():
    f = features_dict("http://g%6Fgle.com/search")
    assert f["f17"] == 1

def test_clean_https():
    f = features_dict("https://github.com/user/repo")
    assert f["f8"] == 0
