"""
AutoStream AI - Main Backend Application
FastAPI-based backend for faceless video automation
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.workflow_manager import WorkflowManager
from services.firecrawl_service import FirecrawlService
from services.ollama_service import OllamaService
from services.crewai_service import CrewAIService
from services.heygem_service import HeyGemService
from services.tts_service import TTSService
from services.video_compositor import VideoCompositor
from models.schemas import (
    TrendSearchRequest, TrendResult, ScriptGenerationRequest,
    TTSRequest, AssetUploadRequest, VideoRenderRequest,
    WorkflowState, TrendItem, ScriptData, AudioData,
    AvatarData, VideoRenderData
)


# Global service instances
workflow_manager: Optional[WorkflowManager] = None
firecrawl_service: Optional[FirecrawlService] = None
ollama_service: Optional[OllamaService] = None
crewai_service: Optional[CrewAIService] = None
heygem_service: Optional[HeyGemService] = None
tts_service: Optional[TTSService] = None
video_compositor: Optional[VideoCompositor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown events"""
    global workflow_manager, firecrawl_service, ollama_service
    global crewai_service, heygem_service, tts_service, video_compositor
    
    # Startup
    print("🚀 Starting AutoStream AI Backend...")
    
    # Create necessary directories
    base_dir = Path(__file__).parent.parent
    uploads_dir = base_dir / "frontend" / "public" / "uploads"
    avatars_dir = uploads_dir / "avatars"
    logos_dir = uploads_dir / "logos"
    backgrounds_dir = uploads_dir / "backgrounds"
    projects_dir = base_dir / "projects"
    temp_dir = base_dir / "temp"
    
    for dir_path in [uploads_dir, avatars_dir, logos_dir, backgrounds_dir, projects_dir, temp_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize services
    try:
        workflow_manager = WorkflowManager()
        firecrawl_service = FirecrawlService()
        ollama_service = OllamaService()
        crewai_service = CrewAIService()
        heygem_service = HeyGemService()
        tts_service = TTSService()
        video_compositor = VideoCompositor()
        
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"⚠️  Some services failed to initialize: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AutoStream AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="AutoStream AI API",
    description="Backend API for AI-powered faceless video automation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded assets
base_dir = Path(__file__).parent.parent
uploads_dir = base_dir / "frontend" / "public" / "uploads"

if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


# ============== Health & Status Endpoints ==============

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ollama": ollama_service.is_available() if ollama_service else False,
            "firecrawl": firecrawl_service.is_available() if firecrawl_service else False,
            "heygem": heygem_service.is_available() if heygem_service else False,
        }
    }


@app.get("/api/workflow/state")
async def get_workflow_state():
    """Get current workflow state"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    return workflow_manager.get_state()


# ============== Trend Discovery Endpoints ==============

@app.post("/api/trends/search", response_model=list[TrendResult])
async def search_trends(request: TrendSearchRequest):
    """
    Search for trending topics in the user's niche using Firecrawl
    """
    if not firecrawl_service:
        raise HTTPException(status_code=503, detail="Firecrawl service not available")
    
    try:
        trends = await firecrawl_service.scrape_trending_topics(
            query=request.query,
            niche=request.niche,
            limit=request.limit or 10
        )
        
        # Update workflow state
        workflow_manager.update_step("trends", {"trends": trends, "selected": None})
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search trends: {str(e)}")


@app.post("/api/trends/select")
async def select_trend(trend: TrendItem):
    """Select a specific trend to proceed with"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    workflow_manager.update_step("trends", {"selected": trend.dict()})
    workflow_manager.next_step()
    
    return {"status": "success", "next_step": workflow_manager.get_current_step()}


# ============== Script Generation Endpoints ==============

@app.post("/api/script/generate", response_model=dict)
async def generate_script(request: ScriptGenerationRequest):
    """
    Generate a script using Ollama or CrewAI based on selected trend
    """
    if not ollama_service and not crewai_service:
        raise HTTPException(status_code=503, detail="No LLM service available")
    
    try:
        # Get selected trend from workflow state
        state = workflow_manager.get_state()
        selected_trend = state.get("trends", {}).get("selected")
        
        if not selected_trend:
            raise HTTPException(status_code=400, detail="No trend selected")
        
        # Generate script
        if request.use_crewai and crewai_service:
            script_data = await crewai_service.generate_script(
                topic=selected_trend.get("title", ""),
                description=selected_trend.get("description", ""),
                tone=request.tone or "professional",
                length=request.length or "short"
            )
        else:
            script_data = await ollama_service.generate_script(
                topic=selected_trend.get("title", ""),
                description=selected_trend.get("description", ""),
                tone=request.tone or "professional",
                length=request.length or "short"
            )
        
        # Update workflow state
        workflow_manager.update_step("script", {
            "content": script_data["content"],
            "title": script_data["title"],
            "duration": script_data.get("duration_estimate")
        })
        
        return script_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")


@app.post("/api/script/update")
async def update_script(content: str):
    """Update the script with user edits"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    workflow_manager.update_step("script", {"content": content, "edited": True})
    
    # Estimate duration based on word count (average 150 words per minute)
    word_count = len(content.split())
    duration_estimate = (word_count / 150) * 60  # seconds
    
    return {
        "status": "success",
        "word_count": word_count,
        "duration_estimate_seconds": round(duration_estimate)
    }


@app.post("/api/script/approve")
async def approve_script():
    """Approve the script and proceed to next step"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    workflow_manager.next_step()
    return {"status": "success", "next_step": workflow_manager.get_current_step()}


# ============== Voice & Audio Endpoints ==============

@app.get("/api/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    if not tts_service:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    return tts_service.get_available_voices()


@app.post("/api/audio/generate", response_model=dict)
async def generate_audio(request: TTSRequest):
    """Generate audio from script using selected voice"""
    if not tts_service:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    try:
        # Get script from workflow state
        state = workflow_manager.get_state()
        script_content = state.get("script", {}).get("content")
        
        if not script_content:
            raise HTTPException(status_code=400, detail="No script content available")
        
        # Generate audio
        audio_data = await tts_service.generate_audio(
            text=script_content,
            voice_id=request.voice_id,
            stability=request.stability or 0.5,
            similarity_boost=request.similarity_boost or 0.75
        )
        
        # Update workflow state
        workflow_manager.update_step("audio", audio_data)
        
        return audio_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")


@app.post("/api/audio/approve")
async def approve_audio():
    """Approve the audio and proceed to next step"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    workflow_manager.next_step()
    return {"status": "success", "next_step": workflow_manager.get_current_step()}


# ============== Asset Management Endpoints ==============

@app.post("/api/assets/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """Upload a custom avatar image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    base_dir = Path(__file__).parent.parent
    avatars_dir = base_dir / "frontend" / "public" / "uploads" / "avatars"
    
    # Save file
    file_path = avatars_dir / file.filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update workflow state
    workflow_manager.update_step("assets", {
        "avatar": {
            "filename": file.filename,
            "path": str(file_path),
            "url": f"/uploads/avatars/{file.filename}"
        }
    })
    
    return {
        "status": "success",
        "avatar": {
            "filename": file.filename,
            "url": f"/uploads/avatars/{file.filename}"
        }
    }


@app.post("/api/assets/logo")
async def upload_logo(file: UploadFile = File(...)):
    """Upload a custom logo"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    base_dir = Path(__file__).parent.parent
    logos_dir = base_dir / "frontend" / "public" / "uploads" / "logos"
    
    # Save file
    file_path = logos_dir / file.filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update workflow state
    workflow_manager.update_step("assets", {
        "logo": {
            "filename": file.filename,
            "path": str(file_path),
            "url": f"/uploads/logos/{file.filename}"
        }
    })
    
    return {
        "status": "success",
        "logo": {
            "filename": file.filename,
            "url": f"/uploads/logos/{file.filename}"
        }
    }


@app.post("/api/assets/background")
async def upload_background(file: UploadFile = File(...)):
    """Upload a background image or video"""
    valid_types = ["image/", "video/"]
    if not any(file.content_type.startswith(t) for t in valid_types):
        raise HTTPException(status_code=400, detail="File must be an image or video")
    
    base_dir = Path(__file__).parent.parent
    backgrounds_dir = base_dir / "frontend" / "public" / "uploads" / "backgrounds"
    
    # Save file
    file_path = backgrounds_dir / file.filename
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update workflow state
    workflow_manager.update_step("assets", {
        "background": {
            "filename": file.filename,
            "path": str(file_path),
            "url": f"/uploads/backgrounds/{file.filename}",
            "type": "video" if file.content_type.startswith("video/") else "image"
        }
    })
    
    return {
        "status": "success",
        "background": {
            "filename": file.filename,
            "url": f"/uploads/backgrounds/{file.filename}",
            "type": "video" if file.content_type.startswith("video/") else "image"
        }
    }


@app.get("/api/assets/list/{asset_type}")
async def list_assets(asset_type: str):
    """List all uploaded assets of a specific type"""
    base_dir = Path(__file__).parent.parent
    asset_dir = base_dir / "frontend" / "public" / "uploads" / asset_type
    
    if not asset_dir.exists():
        return {"assets": []}
    
    assets = []
    for file in asset_dir.iterdir():
        if file.is_file():
            assets.append({
                "filename": file.name,
                "url": f"/uploads/{asset_type}/{file.name}",
                "size": file.stat().st_size
            })
    
    return {"assets": assets}


# ============== Video Generation Endpoints ==============

@app.post("/api/video/generate", response_model=dict)
async def generate_video(request: VideoRenderRequest, background_tasks: BackgroundTasks):
    """
    Generate the final video using HeyGem for avatar lip-sync
    """
    if not heygem_service or not video_compositor:
        raise HTTPException(status_code=503, detail="Video generation services not available")
    
    try:
        # Get workflow state
        state = workflow_manager.get_state()
        
        audio_path = state.get("audio", {}).get("path")
        avatar_path = state.get("assets", {}).get("avatar", {}).get("path")
        logo_path = state.get("assets", {}).get("logo", {}).get("path")
        background_path = state.get("assets", {}).get("background", {}).get("path")
        script_content = state.get("script", {}).get("content")
        
        if not audio_path or not avatar_path:
            raise HTTPException(status_code=400, detail="Missing audio or avatar")
        
        # Start video generation in background
        base_dir = Path(__file__).parent.parent
        output_dir = base_dir / "projects" / workflow_manager.get_state().get("id", "default")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "output.mp4"
        
        # Run video generation
        result = await video_compositor.generate_video(
            avatar_path=avatar_path,
            audio_path=audio_path,
            background_path=background_path,
            logo_path=logo_path,
            output_path=str(output_path),
            script_text=script_content,
            heygem_enabled=request.use_heygem,
            quality=request.quality or "high"
        )
        
        # Update workflow state
        workflow_manager.update_step("video", {
            "output_path": str(output_path),
            "url": f"/projects/{workflow_manager.get_state().get('id', 'default')}/output.mp4",
            "duration": result.get("duration"),
            "status": "completed"
        })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")


@app.get("/api/video/progress/{project_id}")
async def get_video_progress(project_id: str):
    """Get video generation progress"""
    base_dir = Path(__file__).parent.parent
    progress_file = base_dir / "temp" / f"{project_id}_progress.json"
    
    if not progress_file.exists():
        return {"progress": 0, "status": "not_started"}
    
    import json
    with open(progress_file, "r") as f:
        progress_data = json.load(f)
    
    return progress_data


@app.post("/api/video/approve")
async def approve_video():
    """Approve the final video"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    workflow_manager.complete_workflow()
    return {"status": "success", "message": "Video approved and workflow completed"}


# ============== Project Management Endpoints ==============

@app.post("/api/projects/create")
async def create_project(name: str = "New Project"):
    """Create a new video project"""
    if not workflow_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    project_id = workflow_manager.create_project(name)
    return {"project_id": project_id, "name": name}


@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    base_dir = Path(__file__).parent.parent
    projects_dir = base_dir / "projects"
    
    if not projects_dir.exists():
        return {"projects": []}
    
    projects = []
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            state_file = project_dir / "workflow_state.json"
            if state_file.exists():
                import json
                with open(state_file, "r") as f:
                    state = json.load(f)
                projects.append({
                    "id": project_dir.name,
                    "name": state.get("name", "Untitled"),
                    "created_at": state.get("created_at"),
                    "status": state.get("current_step")
                })
    
    return {"projects": projects}


# ============== Settings Endpoints ==============

@app.get("/api/settings/ollama/models")
async def get_ollama_models():
    """Get list of available Ollama models"""
    if not ollama_service:
        raise HTTPException(status_code=503, detail="Ollama service not available")
    
    return ollama_service.get_available_models()


@app.post("/api/settings/ollama/change-model")
async def change_ollama_model(model_name: str):
    """Change the active Ollama model"""
    if not ollama_service:
        raise HTTPException(status_code=503, detail="Ollama service not available")
    
    success = ollama_service.set_model(model_name)
    if success:
        return {"status": "success", "model": model_name}
    raise HTTPException(status_code=400, detail="Failed to change model")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
