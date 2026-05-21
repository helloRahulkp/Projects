"""
AI Currency Detection & Voice Assistant — Streamlit Frontend v2.1
Fixes:
  - use_column_width → use_container_width (Streamlit >=1.30)
  - TTS plays reliably after every detection
  - 30-country live conversion table on every detection page
"""
import os
import io
import base64
import time

import requests
import pandas as pd
import streamlit as st
from PIL import Image
import cv2

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Currency Detector",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("API_URL", "http://backend:8000")

def _check_api(url):
    try:
        r = requests.get(f"{url}/api/v1/ping", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#0f0f1a 0%,#1a1a2e 50%,#0f0f1a 100%); color:#e0e0e0; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#12122a 0%,#1e1e3f 100%); border-right:1px solid #2a2a5a; }
[data-testid="metric-container"] { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:16px; }
.stButton > button { background:linear-gradient(135deg,#667eea,#764ba2); color:white; border:none; border-radius:8px; font-weight:600; transition:all 0.3s; }
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 8px 20px rgba(102,126,234,0.4); }
[data-testid="stFileUploader"] { border:2px dashed #667eea; border-radius:12px; padding:20px; background:rgba(102,126,234,0.05); }
.total-card { background:linear-gradient(135deg,rgba(102,126,234,0.3),rgba(118,75,162,0.3)); border:1px solid rgba(102,126,234,0.5); border-radius:16px; padding:24px; text-align:center; margin:12px 0; }
.conv-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:12px 14px; margin:5px 0; display:flex; justify-content:space-between; align-items:center; }
.det-badge { display:inline-block; padding:4px 12px; border-radius:20px; background:rgba(102,126,234,0.3); border:1px solid rgba(102,126,234,0.5); margin:4px; font-size:0.85em; }
h1,h2,h3 { color:#a0aeff !important; }
.stSelectbox label,.stSlider label { color:#a0aeff !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in [("tts_enabled", True), ("voice_played", set()), ("history", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── 30-Country Data ───────────────────────────────────────────────────────────
THIRTY_COUNTRIES = [
    ("USD","$","🇺🇸","United States"),    ("EUR","€","🇪🇺","Eurozone"),
    ("GBP","£","🇬🇧","United Kingdom"),   ("JPY","¥","🇯🇵","Japan"),
    ("AUD","A$","🇦🇺","Australia"),        ("CAD","C$","🇨🇦","Canada"),
    ("CHF","Fr","🇨🇭","Switzerland"),      ("CNY","¥","🇨🇳","China"),
    ("SGD","S$","🇸🇬","Singapore"),        ("AED","د.إ","🇦🇪","UAE"),
    ("SAR","﷼","🇸🇦","Saudi Arabia"),     ("MYR","RM","🇲🇾","Malaysia"),
    ("THB","฿","🇹🇭","Thailand"),          ("IDR","Rp","🇮🇩","Indonesia"),
    ("PHP","₱","🇵🇭","Philippines"),       ("KRW","₩","🇰🇷","South Korea"),
    ("HKD","HK$","🇭🇰","Hong Kong"),       ("NZD","NZ$","🇳🇿","New Zealand"),
    ("NOK","kr","🇳🇴","Norway"),           ("SEK","kr","🇸🇪","Sweden"),
    ("DKK","kr","🇩🇰","Denmark"),          ("ZAR","R","🇿🇦","South Africa"),
    ("BRL","R$","🇧🇷","Brazil"),           ("MXN","$","🇲🇽","Mexico"),
    ("TRY","₺","🇹🇷","Turkey"),            ("PKR","₨","🇵🇰","Pakistan"),
    ("BDT","৳","🇧🇩","Bangladesh"),        ("LKR","₨","🇱🇰","Sri Lanka"),
    ("NPR","₨","🇳🇵","Nepal"),             ("QAR","﷼","🇶🇦","Qatar"),
]
THIRTY_CODES = [c[0] for c in THIRTY_COUNTRIES]

FALLBACK_INR = {
    "USD":0.012,"EUR":0.011,"GBP":0.0095,"JPY":1.80,"AUD":0.018,"CAD":0.016,
    "CHF":0.011,"CNY":0.087,"SGD":0.016,"AED":0.044,"SAR":0.045,"MYR":0.056,
    "THB":0.42,"IDR":188.0,"PHP":0.68,"KRW":16.0,"HKD":0.094,"NZD":0.020,
    "NOK":0.13,"SEK":0.13,"DKK":0.082,"ZAR":0.22,"BRL":0.062,"MXN":0.21,
    "TRY":0.41,"PKR":3.35,"BDT":1.32,"LKR":3.60,"NPR":1.60,"QAR":0.044,
}

DENOM_COLORS = {
    "10_Old":"#7691af","10_New":"#466e96","20_Old":"#64b464","20_New":"#00a5ff",
    "50_Old":"#e6d8ad","50_New":"#cd9600","100_Old":"#b4826e","100_New":"#820050",
    "200":"#008cff","500":"#808080","2000":"#783296",
}

# ── API Helpers ───────────────────────────────────────────────────────────────
def api_post(endpoint, **kwargs):
    try:
        r = requests.post(f"{API_URL}{endpoint}", timeout=30, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def api_get(endpoint, **kwargs):
    try:
        r = requests.get(f"{API_URL}{endpoint}", timeout=15, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ── TTS ───────────────────────────────────────────────────────────────────────
def play_audio_b64(b64_str, fmt):
    mime = "audio/mpeg" if fmt == "mp3" else "audio/wav"
    st.markdown(
        f'<audio autoplay style="display:none">'
        f'<source src="data:{mime};base64,{b64_str}" type="{mime}"></audio>',
        unsafe_allow_html=True,
    )

def trigger_tts(detections, total_amount, key=""):
    if not st.session_state.tts_enabled:
        return
    if key and key in st.session_state.voice_played:
        return
    with st.spinner("🔊 Generating voice announcement..."):
        result = api_post("/api/v1/tts/speak",
                          json={"detections": list(detections), "total_amount": int(total_amount)})
    if result and result.get("success") and result.get("audio_b64"):
        play_audio_b64(result["audio_b64"], result.get("format", "mp3"))
        st.success("🔊 Voice announced!")
        if key:
            st.session_state.voice_played.add(key)
    else:
        st.info("🔇 Voice unavailable (TTS needs internet for gTTS or espeak for pyttsx3).")

# ── UI Helpers ────────────────────────────────────────────────────────────────
def img_to_bytes(img, fmt="JPEG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))

def draw_badges(summary):
    badges = ""
    for label, count in sorted(summary.items()):
        color = DENOM_COLORS.get(label, "#667eea")
        badges += (f'<span class="det-badge" style="background:rgba({_hex_to_rgb(color)},0.3);'
                   f'border-color:{color}">{label} × {count}</span>')
    st.markdown(badges, unsafe_allow_html=True)

def render_total_card(total_amount, total_count):
    st.markdown(f"""
    <div class="total-card">
        <div style="font-size:2.6em;font-weight:800;color:#a0aeff">₹{total_amount:,}</div>
        <div style="font-size:1.1em;color:#c0c0e0;margin-top:6px">{total_count} note(s) detected</div>
    </div>""", unsafe_allow_html=True)

# ── 30-Country Conversion Panel ───────────────────────────────────────────────
def render_conversion_panel(total_inr):
    if total_inr <= 0:
        return
    st.divider()
    st.subheader("🌍 Live Currency Conversion — 30 Countries")

    with st.spinner("Fetching live exchange rates for 30 currencies..."):
        resp = api_post("/api/v1/conversion/convert-all",
                        json={"amount": total_inr, "currencies": THIRTY_CODES})

    if resp and "conversions" in resp:
        conv_data = resp["conversions"]
        source_live = True
    else:
        st.caption("📴 Using offline fallback rates (no internet)")
        conv_data = {
            code: {"converted_amount": round(total_inr * rate, 2), "rate": rate, "source": "fallback"}
            for code, rate in FALLBACK_INR.items()
        }
        source_live = False

    # Render 3 columns × 10 rows
    col_a, col_b, col_c = st.columns(3)
    col_map = {0: col_a, 1: col_b, 2: col_c}

    for i, (code, sym, flag, country) in enumerate(THIRTY_COUNTRIES):
        info = conv_data.get(code, {})
        val  = info.get("converted_amount", 0)
        rate = info.get("rate", FALLBACK_INR.get(code, 0))
        src  = "🌐" if info.get("source") == "api" else "📴"
        with col_map[i // 10]:
            st.markdown(f"""
            <div class="conv-card">
              <span style="font-size:1.15em">{flag} <b style="color:#a0aeff">{code}</b>
                <span style="font-size:0.72em;color:#606090"> {country}</span></span>
              <span style="font-weight:700;font-size:1.1em;color:#e0e0ff">{sym}{val:,.2f}
                <span style="font-size:0.62em;color:#505080">&nbsp;{src}</span></span>
            </div>""", unsafe_allow_html=True)

    st.caption(f"Base: ₹{total_inr:,} INR  |  "
               f"Source: {'Live API 🌐' if source_live else 'Offline Fallback 📴'}  |  "
               f"1 USD ≈ {conv_data.get('USD',{}).get('rate',0.012):.5f} INR⁻¹")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0">
        <div style="font-size:2.5em">💰</div>
        <div style="font-size:1.2em;font-weight:700;color:#a0aeff">AI Currency Detector</div>
        <div style="font-size:0.75em;color:#6060a0">v2.1 · Powered by YOLOv8</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    page = st.radio("Navigate", [
        "📸 Image Detection", "📦 Batch Detection",
        "🎥 Webcam Detection", "💱 Currency Conversion",
        "📊 Analytics Dashboard", "⚙️ Settings",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**⚙️ Quick Settings**")
    conf = st.slider("Confidence Threshold", 0.1, 1.0, 0.45, 0.05)
    st.session_state.tts_enabled = st.toggle(
        "🔊 Voice Announcements", value=st.session_state.tts_enabled)
    st.divider()
    if _check_api(API_URL):
        st.success("🟢 Backend Online")
    else:
        st.error("🔴 Backend Offline")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SINGLE IMAGE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
if page == "📸 Image Detection":
    st.title("📸 Single Image Detection")
    st.markdown("Upload a photo of Indian currency notes to detect denominations and get live world currency conversions.")

    uploaded = st.file_uploader(
        "Drop an image here or click to browse",
        type=["jpg","jpeg","png","webp"], key="single_upload")

    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader("Original")
            st.image(img, use_container_width=True)

        with st.spinner("🔍 Detecting currencies..."):
            files = {"file": (uploaded.name, img_to_bytes(img), "image/jpeg")}
            resp = api_post("/api/v1/detection/image",
                            files=files, params={"confidence": conf, "annotated": "true"})

        if resp and resp.get("success"):
            data    = resp["data"]
            ann_b64 = resp.get("annotated_image_b64")

            with col2:
                st.subheader("Detected")
                if ann_b64:
                    st.image(Image.open(io.BytesIO(base64.b64decode(ann_b64))),
                             use_container_width=True)

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Total Value", f"₹{data['total_amount']:,}")
            c2.metric("📝 Notes Detected", data["total_count"])
            c3.metric("🏦 Currency", data["currency"])

            if data["summary"]:
                st.subheader("Denomination Breakdown")
                draw_badges(data["summary"])
                df = pd.DataFrame(
                    [(k, v, v * int(k.split("_")[0])) for k, v in data["summary"].items()],
                    columns=["Denomination", "Count", "Value (₹)"])
                st.dataframe(df, use_container_width=True, hide_index=True)

            render_total_card(data["total_amount"], data["total_count"])
            trigger_tts(data["detections"], data["total_amount"],
                        key=f"img_{uploaded.name}_{data['total_amount']}")
            render_conversion_panel(data["total_amount"])
        else:
            st.warning("No detections found or API error.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — BATCH DETECTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Batch Detection":
    st.title("📦 Batch Image Detection")
    st.markdown("Upload **multiple images** — get per-image results, grand total, and live 30-country conversion.")

    uploads = st.file_uploader("Select multiple images", type=["jpg","jpeg","png","webp"],
                                accept_multiple_files=True, key="batch_upload")

    if uploads:
        st.info(f"📂 {len(uploads)} image(s) selected")
        if st.button("🚀 Run Batch Detection", type="primary"):
            files = [("files", (u.name, u.getvalue(), "image/jpeg")) for u in uploads]

            with st.spinner(f"Processing {len(uploads)} images..."):
                resp = api_post("/api/v1/detection/batch",
                                files=files, params={"confidence": conf})

            if resp and resp.get("success"):
                st.divider()
                c1, c2, c3 = st.columns(3)
                c1.metric("💰 Grand Total", f"₹{resp['grand_total_amount']:,}")
                c2.metric("📝 Total Notes", resp["grand_total_count"])
                c3.metric("📁 Images Processed", resp["total_images"])

                render_total_card(resp["grand_total_amount"], resp["grand_total_count"])

                if resp["combined_summary"]:
                    st.subheader("Combined Denomination Summary")
                    draw_badges(resp["combined_summary"])

                st.divider()
                st.subheader("Per-Image Results")
                for item in resp["results"]:
                    with st.expander(f"📄 {item['filename']}", expanded=False):
                        if "error" in item:
                            st.error(item["error"])
                        else:
                            d = item["data"]
                            cc1, cc2 = st.columns(2)
                            cc1.metric("Amount", f"₹{d['total_amount']:,}")
                            cc2.metric("Notes", d["total_count"])
                            if d["summary"]:
                                draw_badges(d["summary"])

                # Build detections list from combined_summary for accurate TTS
                _denom_val = {
                    "10_Old":10,"10_New":10,"20_Old":20,"20_New":20,
                    "50_Old":50,"50_New":50,"100_Old":100,"100_New":100,
                    "200":200,"500":500,"2000":2000,
                }
                batch_detections = []
                for label, count in resp.get("combined_summary", {}).items():
                    denom = _denom_val.get(label, 0)
                    for _ in range(count):
                        batch_detections.append({"denomination": denom})

                trigger_tts(batch_detections, resp["grand_total_amount"],
                            key=f"batch_{resp['grand_total_amount']}_{int(time.time())}")
                render_conversion_panel(resp["grand_total_amount"])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — WEBCAM DETECTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎥 Webcam Detection":
    st.title("🎥 Real-Time Webcam Detection")

    tab1, tab2 = st.tabs(["📷 Capture Photo", "🔴 Live Stream (Local Only)"])

    with tab1:
        st.subheader("Capture & Detect")
        photo = st.camera_input("Take a photo of currency notes")
        if photo:
            img      = Image.open(photo).convert("RGB")
            img_bytes = img_to_bytes(img)

            with st.spinner("Detecting..."):
                files = {"file": ("webcam.jpg", img_bytes, "image/jpeg")}
                resp  = api_post("/api/v1/detection/image",
                                 files=files, params={"confidence": conf, "annotated": "true"})

            if resp and resp.get("success"):
                data    = resp["data"]
                ann_b64 = resp.get("annotated_image_b64")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(img, caption="Captured", use_container_width=True)
                with col2:
                    if ann_b64:
                        st.image(Image.open(io.BytesIO(base64.b64decode(ann_b64))),
                                 caption="Detected", use_container_width=True)

                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("💰 Total", f"₹{data['total_amount']:,}")
                c2.metric("📝 Notes", data["total_count"])
                if data["summary"]:
                    draw_badges(data["summary"])
                render_total_card(data["total_amount"], data["total_count"])
                trigger_tts(data["detections"], data["total_amount"],
                            key=f"cam_{int(time.time())}")
                render_conversion_panel(data["total_amount"])

    with tab2:
        st.subheader("Live Streaming (Local Streamlit Only)")
        st.warning("""
        **Live streaming** requires Streamlit running natively (not in Docker).
        `cv2.VideoCapture()` cannot access the host webcam from inside a container.
        👉 Use the **Capture Photo** tab above — works everywhere including Docker.
        """)
        if st.button("▶️ Start Live Detection"):
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("❌ Cannot open webcam.")
            else:
                placeholder = st.empty()
                info_ph     = st.empty()
                stop_btn    = st.button("⏹ Stop")
                frame_count = 0
                while not stop_btn:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1
                    if frame_count % 10 == 0:
                        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        b64   = base64.b64encode(buf.tobytes()).decode()
                        r     = api_post("/api/v1/detection/frame",
                                         json={"frame_b64": b64, "confidence": conf})
                        if r and r.get("success"):
                            ann_b64 = r.get("annotated_frame_b64")
                            if ann_b64:
                                placeholder.image(
                                    Image.open(io.BytesIO(base64.b64decode(ann_b64))),
                                    use_container_width=True)
                            info_ph.metric("Detected Total", f"₹{r['data']['total_amount']:,}")
                    else:
                        placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                                          use_container_width=True)
                    time.sleep(0.03)
                cap.release()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CURRENCY CONVERSION (standalone)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💱 Currency Conversion":
    st.title("💱 Live Currency Conversion — 30 Countries")
    st.markdown("Convert Indian Rupees to 30 world currencies using live exchange rates.")

    amount = st.number_input("Amount (₹ INR)", min_value=1, value=500, step=50)
    if st.button("🔄 Convert Now", type="primary"):
        render_conversion_panel(int(amount))

    st.divider()
    st.subheader("🔁 Quick Single Converter")
    col1, col2, col3 = st.columns(3)
    with col1:
        single_amount = st.number_input("Amount", min_value=1, value=100, step=10, key="single_amt")
    with col2:
        from_c = st.selectbox("From", ["INR"] + THIRTY_CODES, index=0)
    with col3:
        to_c   = st.selectbox("To", THIRTY_CODES, index=0)

    if st.button("Convert", key="single_conv"):
        r = api_get("/api/v1/conversion/convert",
                    params={"amount": single_amount, "from_currency": from_c, "to_currency": to_c})
        if r:
            sym = dict((c[0], c[1]) for c in THIRTY_COUNTRIES).get(to_c, "")
            st.success(f"**{from_c} {single_amount:,}  →  {sym}{r.get('converted_amount',0):,.4f} {to_c}**"
                       f"  (Rate: 1 {from_c} = {r.get('rate',0):.6f} {to_c})")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics Dashboard":
    st.title("📊 Analytics Dashboard")

    stats        = api_get("/api/v1/analytics/stats")
    history_data = api_get("/api/v1/analytics/history?limit=50")

    if stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔍 Total Sessions",  stats["total_sessions"])
        c2.metric("💰 Total Detected",  f"₹{stats['total_amount_detected']:,.0f}")
        c3.metric("📊 Avg per Session", f"₹{stats['avg_amount_per_session']:,.0f}")
        c4.metric("📝 Most Common Note",
                  max(stats["denomination_counts"], key=stats["denomination_counts"].get)
                  if stats["denomination_counts"] else "—")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🪙 Denomination Distribution")
        if stats and stats["denomination_counts"]:
            df_d = pd.DataFrame(stats["denomination_counts"].items(),
                                columns=["Denomination","Count"]).sort_values("Count", ascending=False)
            st.bar_chart(df_d.set_index("Denomination"))

    with col2:
        st.subheader("📈 Detection Trend (Last 10)")
        if stats and stats["recent_trend"]:
            df_t = pd.DataFrame(stats["recent_trend"])
            if not df_t.empty and "amount" in df_t.columns:
                df_t["timestamp"] = pd.to_datetime(df_t["timestamp"])
                st.line_chart(df_t.set_index("timestamp")["amount"])

    if history_data and history_data.get("history"):
        st.divider()
        st.subheader("🗂️ Recent Detection History")
        hist   = history_data["history"][-20:][::-1]
        df_h   = pd.DataFrame(hist)
        if not df_h.empty:
            cols = [c for c in ["timestamp","source","total_amount","total_count","currency"]
                    if c in df_h.columns]
            # ✅ FIXED: use_container_width (was use_column_width)
            st.dataframe(df_h[cols], use_container_width=True, hide_index=True)

        ce1, ce2 = st.columns(2)
        with ce1:
            try:
                r = requests.get(f"{API_URL}/api/v1/analytics/export/csv", timeout=10)
                st.download_button("📥 Export CSV", r.text, "detections.csv", "text/csv")
            except Exception:
                pass
        with ce2:
            if st.button("🗑️ Clear History"):
                requests.delete(f"{API_URL}/api/v1/analytics/clear", timeout=5)
                st.success("History cleared!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    st.title("⚙️ Settings & System Info")

    health = api_get("/api/v1/health")
    if health:
        st.subheader("🖥️ System Status")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Backend",  "🟢 Online")
        c2.metric("Device",   health.get("device","cpu").upper())
        c3.metric("Model",    "✅ Loaded" if health.get("model_loaded") else "⚠️ Not Loaded")
        c4.metric("Platform", health.get("platform","—"))
        with st.expander("Full Health Report"):
            st.json(health)

    st.divider()
    st.subheader("🔊 Voice Settings")
    st.session_state.tts_enabled = st.toggle(
        "Enable Voice Announcements", value=st.session_state.tts_enabled)

    if st.button("🔊 Test Voice"):
        resp = api_post("/api/v1/tts/speak-text",
                        json={"text": "AI Currency Detector is ready. Voice system working."})
        if resp and resp.get("success") and resp.get("audio_b64"):
            play_audio_b64(resp["audio_b64"], resp.get("format","mp3"))
            st.success("✅ Voice test played!")
        else:
            st.warning("Voice test failed. TTS needs internet (gTTS) or espeak (pyttsx3).")

    st.divider()
    st.subheader("📡 Model Info")
    model_info = api_get("/api/v1/detection/info")
    if model_info:
        st.json(model_info)

    st.divider()
    st.subheader("🌐 API Configuration")
    st.code(f"Backend URL: {API_URL}\nDocs: {API_URL}/docs\nRedoc: {API_URL}/redoc")
    st.markdown(f"[📖 Open Swagger Docs]({API_URL}/docs)  |  [📗 Open ReDoc]({API_URL}/redoc)")
