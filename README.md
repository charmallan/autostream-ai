# AutoStream AI - Faceless Video Automation Platform

<div align="center">

![AutoStream AI](https://img.shields.io/badge/AutoStream-AI-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-18-61dafb?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge)

**Automate viral faceless video creation with AI-powered tools**

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Configuration](#configuration)

</div>

---

## 🚀 Features

### End-to-End Video Automation
- **Trend Discovery**: Scrape trending topics in your niche using Firecrawl
- **Script Generation**: AI-powered script creation using Ollama or CrewAI
- **Voice Synthesis**: Multiple TTS providers (ElevenLabs, gTTS)
- **Avatar Animation**: HeyGem/Duix integration for lip-sync video generation
- **Video Compositing**: FFmpeg-based video rendering with custom assets

### User-Friendly Interface
- Step-by-step workflow with progress tracking
- Real-time preview at each stage
- Drag-and-drop asset uploads
- Dark mode UI with modern design

### Full Control
- Upload custom avatars, logos, and backgrounds
- Choose voice, tone, and script length
- Configure video quality and settings
- Edit and refine at every step

---

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **FFmpeg** (for video processing)
- **Ollama** (optional, for local LLM)
- **NVIDIA GPU** (recommended for video rendering)

---

## 🛠️ Quick Start

### Option 1: Manual Installation

#### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/autostream-ai.git
cd autostream-ai
```

#### 2. Install Backend Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

#### 4. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### 5. Open Browser
Navigate to `http://localhost:5173`

### Option 2: Docker Compose

```bash
docker-compose up -d
```

This will start:
- AutoStream AI Backend (port 8000)
- AutoStream AI Frontend (port 5173)
- Ollama (port 11434)
- Firecrawl (port 3002)

---

## 🎯 Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   TRENDS    │ ──▶ │   SCRIPT    │ ──▶ │   VOICE     │ ──▶ │   ASSETS    │ ──▶ │   VIDEO     │
│  Discovery  │     │  Generation │     │  Selection  │     │  Upload     │     │ Generation  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Step 1: Trend Discovery
1. Enter a topic keyword (e.g., "AI Technology")
2. Select your niche category
3. Choose from trending topics found

### Step 2: Script Generation
1. Select script tone (Professional, Casual, Funny, etc.)
2. Choose length (Short, Medium, Long)
3. Generate and edit your script

### Step 3: Voice Selection
1. Browse available voices
2. Adjust stability and similarity settings
3. Generate audio preview

### Step 4: Asset Upload
1. Upload avatar image (required)
2. Upload logo (optional)
3. Upload background (image or video)

### Step 5: Video Generation
1. Select quality settings
2. Choose lip-sync method (HeyGem or static)
3. Generate and download your video

---

## 🏗️ Architecture

```
autostream-ai/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── workflow_manager.py # Step orchestration
│   │   ├── ollama_service.py   # LLM integration
│   │   ├── crewai_service.py   # Multi-agent scripting
│   │   ├── firecrawl_service.py # Web scraping
│   │   ├── heygem_service.py   # Video generation
│   │   ├── tts_service.py      # Text-to-speech
│   │   └── video_compositor.py # FFmpeg rendering
│   └── models/schemas.py       # Data models
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # State management
│   │   └── services/           # API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# ElevenLabs TTS (optional)
ELEVENLABS_API_KEY=your_api_key

# HeyGem Settings
HEYGEM_HOST=http://localhost:8001
HEYGEM_DEVICE=cuda

# Firecrawl Settings
FIRECRAWL_HOST=http://localhost:3002

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3
```

### Quality Presets

| Preset | Resolution | Bitrate | FPS |
|--------|-----------|---------|-----|
| Low | 720p | 2M | 24 |
| Medium | 1080p | 5M | 30 |
| High | 1080p | 10M | 30 |
| 4K | 2160p | 35M | 30 |

---

## 📦 Dependencies

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **httpx** - HTTP client
- **Pydantic** - Data validation
- **loguru** - Logging
- **FFmpeg-python** - Video processing
- **gTTS** - Google TTS

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Zustand** - State management
- **Axios** - HTTP client
- **React Dropzone** - File uploads

---

## 🐳 Docker Usage

### Build and Run
```bash
docker-compose up --build
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [HeyGem/Duix](https://github.com/duixcom/Duix-Avatar) - Open source AI avatars
- [Ollama](https://ollama.com/) - Local LLM runtime
- [Firecrawl](https://www.firecrawl.dev/) - Web scraping
- [CrewAI](https://crewai.com/) - Multi-agent framework

---

<div align="center">
Made with ❤️ by MiniMax Agent
</div>
