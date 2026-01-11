# 🧠 Psychology Session Analyzer

**AI-powered therapy session analysis using microservices architecture.**

Upload a therapy video → Get deep psychological insights with clinical recommendations.

---

## 🛠 Built With

| **AI & ML** | **Backend** | **Infrastructure** | **DevOps** |
|-------------|-------------|-------------------|------------|
| OpenAI GPT-5 | FastAPI | RabbitMQ | Docker |
| AssemblyAI | Python 3.11 | MongoDB | Docker Compose |
| Prompt Engineering | Pydantic | Redis | Datadog |
| LLM Caching | Uvicorn | MinIO (S3) | Health Checks |

---

## ⚡ Quick Start

```bash
# 1. Clone & configure
git clone https://github.com/yourusername/psychology-session-analyzer.git
cp .env.example .env  # Add your API keys

# 2. Run
docker-compose up --build

# 3. Upload a session
curl -X POST "http://localhost:8000/upload" \
  -F "user_id=user123" \
  -F "file=@session.mp4"

# 4. Get results
curl "http://localhost:8001/analyses/{video_id}"
```

---

## 🏗 Architecture

```
Video Upload → [RabbitMQ] → Audio Extraction → Transcription → GPT-5 Analysis → MongoDB
     ↓                              ↓                ↓              ↓
   MinIO                        MoviePy         AssemblyAI      Redis Cache
```

**5 Microservices** | **Event-Driven** | **CQRS Pattern** | **Saga Pattern**

---

## 🔧 Services

| Service | Tech | Purpose |
|---------|------|---------|
| **Upload** | FastAPI | Video ingestion + event publishing |
| **Audio Extractor** | MoviePy/FFmpeg | Extract audio from video |
| **Transcription** | AssemblyAI | Speech-to-text + speaker diarization |
| **Analyzer** | OpenAI GPT-5 | Psychodynamic analysis + EFT |
| **Query** | FastAPI + MongoDB | Retrieve results + Super Advisor AI |

---

## 📡 API

```bash
POST /upload              # Upload video
GET  /my-videos?user_id=  # List sessions
GET  /analyses/{id}       # Get analysis
POST /advisor             # AI therapeutic advice
```

---

## ✨ Features

- 🎙 **Speaker Diarization** — Identifies therapist vs patient
- 🧠 **Deep Analysis** — Latent emotions, subtext, defense mechanisms
- 💡 **Clinical Recommendations** — Actionable therapeutic interventions  
- 🤖 **Super Advisor** — Context-aware AI coaching from session history
- ⚡ **Redis Caching** — Saves LLM costs via response deduplication

---

## 🔐 Environment

```env
OPENAI_API_KEY=          # GPT-5 analysis
ASSEMBLYAI_API_KEY=      # Transcription
RABBITMQ_USER/PASS=      # Message broker
MINIO_ROOT_USER/PASSWORD= # Object storage
DD_API_KEY=              # Datadog (optional)
```

---

**Author:** Ori Tal | **License:** Ori Tal
