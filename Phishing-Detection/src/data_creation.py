import requests
import os
import zipfile
import io
import csv

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── Download phishing URLs ────────────────────────────────────────────────────
def download_phishing_urls():
    print("Downloading phishing URLs...")
    phishing_urls = set()

    # Source 1: OpenPhish
    try:
        r = requests.get("https://openphish.com/feed.txt", timeout=15)
        for line in r.text.split("\n"):
            line = line.strip()
            if line.startswith("http"):
                phishing_urls.add(line)
        print(f"  OpenPhish: {len(phishing_urls)} URLs")
    except Exception as e:
        print(f"  OpenPhish failed: {e}")

    # Source 2: PhishTank
    try:
        r = requests.get(
            "http://data.phishtank.com/data/online-valid.csv",
            timeout=30,
            headers={"User-Agent": "phishtank/python-script"}
        )
        reader = csv.DictReader(io.StringIO(r.text))
        before = len(phishing_urls)
        for row in reader:
            url = row.get("url", "").strip()
            if url.startswith("http"):
                phishing_urls.add(url)
        print(f"  PhishTank: +{len(phishing_urls) - before} URLs")
    except Exception as e:
        print(f"  PhishTank failed: {e}")

    # Source 3: URLhaus
    try:
        r = requests.get("https://urlhaus.abuse.ch/downloads/csv_recent/", timeout=30)
        before = len(phishing_urls)
        for line in r.text.split("\n"):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split('","')
            if len(parts) > 2:
                url = parts[2].strip('"')
                if url.startswith("http"):
                    phishing_urls.add(url)
        print(f"  URLhaus: +{len(phishing_urls) - before} URLs")
    except Exception as e:
        print(f"  URLhaus failed: {e}")

    # Source 4: Phishing.Database — cap at 50k to keep things manageable
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-links-ACTIVE.txt",
            timeout=30
        )
        before = len(phishing_urls)
        for line in r.text.split("\n"):
            if len(phishing_urls) >= 50000:
                break
            line = line.strip()
            if line and not line.startswith("#"):
                if not line.startswith("http"):
                    line = "http://" + line
                phishing_urls.add(line)
        print(f"  Phishing.Database: +{len(phishing_urls) - before} URLs")
    except Exception as e:
        print(f"  Phishing.Database failed: {e}")

    # Cap total phishing at 50k — more than enough
    phishing_urls = set(list(phishing_urls)[:50000])

    out_path = os.path.join(OUTPUT_DIR, "phishing_urls.txt")
    with open(out_path, "w") as f:
        for u in phishing_urls:
            f.write(u + "\n")

    print(f"\n  ✅ Phishing URLs saved: {len(phishing_urls)} -> {out_path}\n")
    return len(phishing_urls)


# ─── Download legitimate URLs ──────────────────────────────────────────────────
def download_legitimate_urls(target=10000):
    print(f"Downloading legitimate URLs (target: {target})...")
    domains = []
    seen = set()

    # Source 1: Majestic Million — streamed line by line, stops at target
    try:
        print("  Trying Majestic Million (streaming)...")
        r = requests.get(
            "https://downloads.majestic.com/majestic_million.csv",
            timeout=30,
            stream=True      # ← stream so we don't load 1M rows into RAM
        )
        # Read line by line
        buffer = ""
        first_line = True
        for chunk in r.iter_content(chunk_size=8192, decode_unicode=True):
            buffer += chunk
            lines = buffer.split("\n")
            buffer = lines[-1]  # keep incomplete last line
            for line in lines[:-1]:
                if first_line:
                    first_line = False
                    continue  # skip header
                parts = line.strip().split(",")
                # CSV format: Rank,TLD,Domain,...
                if len(parts) >= 3:
                    domain = parts[2].strip()
                    if domain and domain not in seen:
                        seen.add(domain)
                        domains.append(domain)
                if len(domains) >= target:
                    break
            if len(domains) >= target:
                break
        print(f"  Majestic Million: {len(domains)} domains")
    except Exception as e:
        print(f"  Majestic Million failed: {e}")

    # Source 2: Tranco (fallback)
    if len(domains) < target:
        try:
            print("  Trying Tranco list...")
            r = requests.get("https://tranco-list.eu/top-1m.csv.zip", timeout=60)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                fname = z.namelist()[0]
                with z.open(fname) as f:
                    reader = csv.reader(io.TextIOWrapper(f))
                    before = len(domains)
                    for row in reader:
                        if len(row) >= 2:
                            domain = row[1].strip()
                            if domain and domain not in seen:
                                seen.add(domain)
                                domains.append(domain)
                        if len(domains) >= target:
                            break
                    print(f"  Tranco: +{len(domains) - before} domains")
        except Exception as e:
            print(f"  Tranco failed: {e}")

    # Source 3: SecLists (last resort)
    if len(domains) < target:
        try:
            print("  Trying SecLists...")
            r = requests.get(
                "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/top-1million-domains.txt",
                timeout=30,
                stream=True
            )
            before = len(domains)
            for chunk in r.iter_lines(decode_unicode=True):
                line = chunk.strip()
                # format may be "rank,domain" or just "domain"
                if "," in line:
                    line = line.split(",")[-1].strip()
                if line and line not in seen:
                    seen.add(line)
                    domains.append(line)
                if len(domains) >= target:
                    break
            print(f"  SecLists: +{len(domains) - before} domains")
        except Exception as e:
            print(f"  SecLists failed: {e}")

    # Write output
    out_path = os.path.join(OUTPUT_DIR, "legitimate_urls.txt")
    written = 0
    with open(out_path, "w") as f:
        for d in domains[:target]:
            f.write("https://" + d + "\n")
            written += 1

    print(f"\n  ✅ Legitimate URLs saved: {written} -> {out_path}\n")
    return written


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    n_phish = download_phishing_urls()

    # Match legitimate count to phishing, capped at 50k
    target  = min(n_phish, 50000)
    n_legit = download_legitimate_urls(target=target)

    print("=" * 50)
    print(f"  Phishing URLs  : {n_phish}")
    print(f"  Legitimate URLs: {n_legit}")
    print(f"  Total          : {n_phish + n_legit}")
    print("=" * 50)
    print("\nDataset ready! Run dataset_builder.py next.")