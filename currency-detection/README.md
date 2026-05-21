# 💰 AI Currency Detection & Smart Voice Assistant System

> **Powered by YOLOv8 · FastAPI · Streamlit · Docker Compose**

An enterprise-grade, cross-platform system for detecting Indian currency notes using deep learning, with live currency conversion, voice announcements, analytics, and a professional dark-mode dashboard.

---

## 🚀 Quick Start — One Command

```bash
docker compose up --build
```

Then open:
| Service | URL |
|---|---|
| 🖥️ **App (via Nginx)** | http://localhost |
| 📊 **Streamlit UI** | http://localhost:8501 |
| ⚡ **FastAPI Backend** | http://localhost:8000 |
| 📚 **API Docs (Swagger)** | http://localhost:8000/docs |

---

## ✨ Features

| Feature | Description |
|---|---|
| 📸 Single Image Detection | Upload one image, detect all notes |
| 📦 Batch Detection | Upload up to 20 images, get per-image + grand total |
| 🎥 Webcam Detection | Camera capture + live streaming (local mode) |
| 💱 Currency Conversion | Real-time INR → USD / EUR / GBP / AED / SGD / JPY |
| 🔊 Voice Announcements | TTS announces detected denominations & totals |
| 📊 Analytics Dashboard | Charts, history, export CSV |
| 🌙 Dark Mode UI | Professional gradient dashboard |
| 🐳 Docker Compose | Single command deployment |

---

## 🏗️ Architecture

```
currency-detection/
├── backend/                    # FastAPI + YOLOv8 inference
│   ├── api/
│   │   ├── main.py             # FastAPI app factory
│   │   └── routes/
│   │       ├── detection.py    # /api/v1/detection/*
│   │       ├── conversion.py   # /api/v1/conversion/*
│   │       ├── tts.py          # /api/v1/tts/*
│   │       ├── analytics.py    # /api/v1/analytics/*
│   │       └── health.py       # /api/v1/health, /ping
│   ├── core/
│   │   ├── config.py           # Pydantic settings
│   │   ├── constants.py        # Colors, denomination maps
│   │   └── logger.py           # Loguru logger
│   ├── detection/
│   │   └── detect_image.py     # YOLOv8 detector (singleton)
│   └── services/
│       ├── currency_service.py # Exchange rate API + cache
│       ├── tts_service.py      # gTTS + pyttsx3 fallback
│       └── analytics_service.py# Detection history + stats
├── frontend/
│   └── app.py                  # Streamlit multi-page app
├── models/
│   └── checkpoints/
│       └── best.pt             # YOLOv8 trained weights
├── configs/
│   └── streamlit_config.toml
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── deployment/
│   └── nginx.conf
├── requirements/
│   ├── backend.txt
│   └── frontend.txt
├── tests/
│   └── test_system.py
├── scripts/
│   ├── setup_windows.bat
│   └── setup_unix.sh
├── docker-compose.yml
└── .env.example
```

---

## 🌍 Cross-Platform Compatibility

| Platform | Status | Notes |
|---|---|---|
| macOS M1/M2/M3 (ARM64) | ✅ Full | MPS available natively |
| macOS Intel (x86_64) | ✅ Full | CPU mode |
| Windows 10/11 (x86_64) | ✅ Full | Docker Desktop required |
| Linux (x86_64) | ✅ Full | CPU + CUDA |
| Linux (ARM64) | ✅ Full | CPU mode |

### Windows Setup

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Enable WSL2 backend in Docker Desktop settings
3. Clone the project
4. Run `scripts\setup_windows.bat` **or** open PowerShell and run:

```powershell
docker compose up --build
```

### macOS Setup

```bash
# Ensure Docker Desktop is running
chmod +x scripts/setup_unix.sh
./scripts/setup_unix.sh
# or simply:
docker compose up --build
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```env
DEVICE=cpu          # cpu | cuda | mps
LOG_LEVEL=INFO
CONFIDENCE_THRESHOLD=0.45
MODEL_PATH=models/checkpoints/best.pt
```

**GPU support:**

For NVIDIA GPU, change in docker-compose.yml:
```yaml
environment:
  - DEVICE=cuda
```
And add to the backend service:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - capabilities: [gpu]
```

---

## 🔌 API Reference

### Detection
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/detection/image` | Single image detection |
| POST | `/api/v1/detection/batch` | Batch image detection |
| POST | `/api/v1/detection/frame` | Webcam frame (base64) |
| GET  | `/api/v1/detection/info` | Model metadata |

### Conversion
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/conversion/rates?base=INR` | Live exchange rates |
| GET | `/api/v1/conversion/convert?amount=500&from_currency=INR&to_currency=USD` | Convert amount |
| POST | `/api/v1/conversion/convert-all` | Convert to all currencies |

### TTS
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/tts/speak` | TTS for detections |
| POST | `/api/v1/tts/speak-text` | TTS for custom text |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/analytics/stats` | Aggregate statistics |
| GET | `/api/v1/analytics/history` | Detection history |
| GET | `/api/v1/analytics/export/csv` | Download CSV |
| DELETE | `/api/v1/analytics/clear` | Clear history |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Full health report |
| GET | `/api/v1/ping` | Simple ping |

---

## 🧠 Model

- **Architecture:** YOLOv8 (custom trained)
- **Classes:** 11 Indian currency denominations
  - `10_Old`, `10_New`, `20_Old`, `20_New`, `50_Old`, `50_New`
  - `100_Old`, `100_New`, `200`, `500`, `2000`
- **Input size:** 640×640
- **Device:** CPU (default) | CUDA | MPS (macOS native)

---

## 🧪 Testing

```bash
# Run inside container
docker compose exec backend pytest tests/ -v

# Or locally (with venv)
pip install -r requirements/backend.txt
pytest tests/ -v
```

---

## 🔊 Voice System

Voice announcements use:
1. **gTTS** (Google TTS — online, natural voice) — primary
2. **pyttsx3** (offline, system TTS) — fallback

Audio is returned as base64 and played in the browser. No speaker hardware needed in the container.

---

## 🐛 Troubleshooting

**Q: Backend health check fails on first start**  
A: YOLOv8 model loading takes ~30–60s. Docker will retry. Wait for `✅ Model pre-loaded` in logs.

**Q: Webcam not working in Docker**  
A: Use the **Capture Photo** tab (works via browser). Live streaming requires native Streamlit.

**Q: Currency conversion shows fallback rates**  
A: Container has no internet access or rate API is down. Rates auto-update when connectivity returns.

**Q: TTS not working**  
A: gTTS requires internet. If offline, pyttsx3 is used (needs `espeak` installed — already in Docker image).

**Q: `docker compose` not found (Windows)**  
A: Use `docker-compose` (with hyphen) for older Docker installations.

**Q: Port 80 already in use**  
A: Change in docker-compose.yml: `"8080:80"` and access via http://localhost:8080

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

## 🤝 Credits

- **YOLOv8** by Ultralytics
- **FastAPI** by Sebastián Ramírez  
- **Streamlit** by Streamlit Inc.
- Indian Currency Dataset (custom trained model)
