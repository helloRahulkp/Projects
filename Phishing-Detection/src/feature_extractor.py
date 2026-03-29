import re
import math
from urllib.parse import urlparse
from collections import Counter

KNOWN_LEGITIMATE = {
    "google.com", "youtube.com", "facebook.com", "twitter.com", "instagram.com",
    "linkedin.com", "microsoft.com", "apple.com", "amazon.com", "netflix.com",
    "github.com", "stackoverflow.com", "reddit.com", "wikipedia.org", "chatgpt.com",
    "openai.com", "coursera.org", "udemy.com", "gemini.google.com", "gmail.com",
    "outlook.com", "yahoo.com", "bing.com", "dropbox.com", "notion.so",
    "slack.com", "zoom.us", "twitch.tv", "spotify.com", "pinterest.com",
    "tiktok.com", "whatsapp.com", "telegram.org", "discord.com", "shopify.com",
    "ebay.com", "paypal.com", "stripe.com", "cloudflare.com", "wordpress.com",
    "medium.com", "substack.com", "canva.com", "figma.com", "adobe.com",
    "indiabix.com", "w3schools.com", "geeksforgeeks.org", "leetcode.com",
}

def get_root_domain(domain):
    """Extract root domain e.g. 'sub.google.com' -> 'google.com'"""
    domain = domain.lower().lstrip("www.")
    parts = domain.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain

def is_known_legit(domain):
    root = get_root_domain(domain)
    return root in KNOWN_LEGITIMATE

def entropy(s):
    if not s: return 0
    counts = Counter(s)
    total = len(s)
    return -sum((c/total)*math.log2(c/total) for c in counts.values())

# ── Features ──────────────────────────────────────────────────────────────────

def has_ip(url):
    pattern = r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])'
    return 1 if re.search(pattern, url) else 0

def url_length(url):
    # Real phishing URLs are often 200+ chars; legitimate deep-links can be 100-150
    l = len(url)
    if l < 100:   return 0
    elif l < 190: return 0.3   # long but plausible
    else:         return 1     # very long, suspicious

def has_shortener(url):
    shorteners = r"bit\.ly|goo\.gl|tinyurl|t\.co|is\.gd|buff\.ly|ow\.ly|short\.to|adf\.ly|tiny\.cc"
    return 1 if re.search(shorteners, url, re.I) else 0

def has_at_symbol(url):
    return 1 if "@" in url else 0

def double_slash_redirect(url):
    return 1 if url.rfind("//") > 7 else 0

def has_prefix_suffix(domain):
    return 1 if "-" in domain else 0

def subdomain_count(domain):
    domain = re.sub(r'^www\.', '', domain)
    dots = domain.count(".")
    if dots <= 1:  return 0
    elif dots == 2: return 0.3
    else:           return 1

def https_in_domain(domain):
    return 1 if "https" in domain.lower() else 0

def digit_ratio(url):
    if not url: return 0
    ratio = sum(c.isdigit() for c in url) / len(url)
    # UUIDs in legitimate URLs (e.g. ChatGPT) push ratio high — use stricter threshold
    return round(min(ratio * 0.5, 1.0), 4)   # dampen the signal

def special_char_count(url):
    # Query params are totally normal in legit URLs (YouTube, etc.)
    count = url.count("?") + url.count("=") + url.count("&")
    if count <= 5:  return 0
    elif count <= 10: return 0.5
    else:           return 1

def slash_count(url):
    # Coursera/YouTube have deep paths — raise threshold
    return 1 if url.count("/") > 9 else 0

def dot_count(url):
    return 1 if url.count(".") > 6 else 0

def has_suspicious_words(url):
    words = ["login", "secure", "account", "verify", "update",
             "password", "confirm", "support", "billing", "suspend",
             "unusual", "alert", "validation", "signin", "recover"]
    # "learn", "app", "home", "module" are NOT suspicious — exclude
    url_lower = url.lower()
    hits = sum(1 for w in words if w in url_lower)
    if hits == 0:   return 0
    elif hits == 1: return 0.4
    else:           return 1

def domain_length(domain):
    d = re.sub(r'^www\.', '', domain).split(".")[0]
    return 1 if len(d) > 25 else 0   # raised from 20

def has_exe(url):
    return 1 if url.lower().endswith(".exe") else 0

def hyphen_count(url):
    parsed = urlparse(url)
    # Only count hyphens in the domain, not the path
    return 1 if parsed.netloc.count("-") > 3 else 0

def has_encoded_chars(url):
    parsed = urlparse(url)
    # Encoded chars in path/query are normal; in domain = suspicious
    return 1 if "%" in parsed.netloc else 0

def path_depth(url):
    parsed = urlparse(url)
    depth = len([p for p in parsed.path.split("/") if p])
    # YouTube/Coursera have depth 3-5 — raise thresholds
    if depth <= 4:   return 0
    elif depth <= 7: return 0.3
    else:            return 1

def query_length(url):
    parsed = urlparse(url)
    q = parsed.query
    # Long query strings are normal in legitimate apps
    if len(q) < 50:   return 0
    elif len(q) < 150: return 0.3
    else:              return 1

def domain_entropy(domain):
    d = re.sub(r'^www\.', '', domain).split(".")[0]
    e = entropy(d)
    if e < 3.2:   return 0
    elif e < 3.9: return 0.3
    else:         return 1

def tld_suspicious(domain):
    suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
                       ".click", ".link", ".online", ".site", ".biz"]
    return 1 if any(domain.lower().endswith(t) for t in suspicious_tlds) else 0

def brand_in_subdomain(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    brands = ["paypal", "google", "amazon", "apple", "microsoft",
              "facebook", "netflix", "instagram", "twitter", "ebay"]
    parts = domain.split(".")
    if len(parts) > 2:
        subdomain_part = ".".join(parts[:-2])
        return 1 if any(b in subdomain_part for b in brands) else 0
    return 0

def non_standard_port(url):
    parsed = urlparse(url)
    netloc = parsed.netloc
    if ":" in netloc:
        try:
            port = int(netloc.split(":")[-1])
            if port not in (80, 443, 8080, 8443):
                return 1
        except ValueError:
            pass
    return 0

def digit_in_domain(domain):
    d = re.sub(r'^www\.', '', domain).split(".")[0]
    return 1 if any(c.isdigit() for c in d) else 0

def url_entropy(url):
    # UUIDs (ChatGPT, Gemini) legitimately raise entropy — only flag very high
    e = entropy(url)
    if e < 4.0:   return 0
    elif e < 4.6: return 0.3
    else:         return 1

def repeated_chars(url):
    return 1 if re.search(r'(.)\1{4,}', url) else 0   # raised from 3 to 4

def path_has_extension(url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    suspicious_exts = [".exe", ".bat", ".sh", ".cmd", ".vbs", ".ps1"]
    return 1 if any(path.endswith(e) for e in suspicious_exts) else 0
    # Removed .php/.asp — too many legit sites use these

def count_subdomains(url):
    parsed = urlparse(url)
    domain = re.sub(r'^www\.', '', parsed.netloc)
    parts = domain.split(".")
    n = len(parts) - 2
    if n <= 0:    return 0
    elif n == 1:  return 0.3
    else:         return 1

def numeric_ip_obfuscation(url):
    return 1 if re.search(r'https?://(0x[0-9a-fA-F]+|\d{8,10})([:/]|$)', url) else 0

def hex_in_path(url):
    # Legitimate UUIDs like ChatGPT/Gemini use hex — don't flag
    return 0

def path_contains_uuid(url):
    # UUIDs are totally normal in modern web apps — return 0 (not suspicious)
    return 0


# ── Master extractor ──────────────────────────────────────────────────────────
def extract_features(url):
    parsed = urlparse(url)
    domain = parsed.netloc

    # Known-legit override: if domain is a well-known site,
    # zero out all path/length-based features that cause false positives
    known = is_known_legit(domain)

    features = [
        has_ip(url),                                        # f1
        0 if known else url_length(url),                    # f2
        has_shortener(url),                                 # f3
        has_at_symbol(url),                                 # f4
        double_slash_redirect(url),                         # f5
        has_prefix_suffix(domain),                          # f6
        subdomain_count(domain),                            # f7
        https_in_domain(domain),                            # f8
        0 if known else digit_ratio(url),                   # f9
        0 if known else special_char_count(url),            # f10
        0 if known else slash_count(url),                   # f11
        dot_count(url),                                     # f12
        0 if known else has_suspicious_words(url),          # f13
        domain_length(domain),                              # f14
        has_exe(url),                                       # f15
        hyphen_count(url),                                  # f16
        has_encoded_chars(url),                             # f17
        0 if known else path_depth(url),                    # f18
        0 if known else query_length(url),                  # f19
        domain_entropy(domain),                             # f20
        tld_suspicious(domain),                             # f21
        brand_in_subdomain(url),                            # f22
        non_standard_port(url),                             # f23
        digit_in_domain(domain),                            # f24
        0 if known else url_entropy(url),                   # f25
        repeated_chars(url),                                # f26
        path_has_extension(url),                            # f27
        count_subdomains(url),                              # f28
        numeric_ip_obfuscation(url),                        # f29
        has_at_symbol(url),                                 # f30
    ]

    return features


FEATURE_NAMES = [f"f{i}" for i in range(1, 31)]