"""
Pydantic Models for AutoStream AI API
Data validation schemas for API requests and responses
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============== Workflow State Models ==============

class WorkflowStep(str, Enum):
    """Enum for workflow steps"""
    IDLE = "idle"
    TRENDS = "trends"
    SCRIPT = "script"
    AUDIO = "audio"
    ASSETS = "assets"
    VIDEO = "video"
    COMPLETE = "complete"


class WorkflowState(BaseModel):
    """Complete workflow state model"""
    id: str = Field(..., description="Unique project ID")
    name: str = Field(..., description="Project name")
    current_step: WorkflowStep = Field(default=WorkflowStep.IDLE)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    trends: Dict[str, Any] = Field(default_factory=dict)
    script: Dict[str, Any] = Field(default_factory=dict)
    audio: Dict[str, Any] = Field(default_factory=dict)
    assets: Dict[str, Any] = Field(default_factory=dict)
    video: Dict[str, Any] = Field(default_factory=dict)


# ============== Trend Discovery Models ==============

class TrendItem(BaseModel):
    """Model for a trending topic item"""
    id: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    engagement: Optional[Dict[str, Any]] = None
    scraped_at: Optional[datetime] = None


class TrendSearchRequest(BaseModel):
    """Request model for trend search"""
    query: str = Field(..., description="Search query or keyword")
    niche: Optional[str] = Field(default="general", description="Content niche/category")
    limit: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum number of results")
    sources: Optional[List[str]] = Field(default=None, description="Specific sources to scrape")


class TrendResult(BaseModel):
    """Response model for trend results"""
    trends: List[TrendItem]
    total_count: int
    search_query: str
    scraped_at: datetime = Field(default_factory=datetime.now)


# ============== Script Generation Models ==============

class ScriptGenerationRequest(BaseModel):
    """Request model for script generation"""
    tone: Optional[str] = Field(default="professional", description="Script tone (professional, casual, funny, dramatic)")
    length: Optional[str] = Field(default="short", description="Script length (short, medium, long)")
    use_crewai: Optional[bool] = Field(default=False, description="Use CrewAI instead of Ollama")
    custom_instructions: Optional[str] = Field(default=None, description="Custom instructions for script generation")


class ScriptData(BaseModel):
    """Model for generated script data"""
    title: str
    content: str
    duration_estimate: Optional[int] = Field(None, description="Estimated duration in seconds")
    word_count: int
    key_points: List[str] = Field(default_factory=list)


# ============== Audio/TTS Models ==============

class TTSRequest(BaseModel):
    """Request model for text-to-speech generation"""
    voice_id: str = Field(..., description="Selected voice ID")
    stability: Optional[float] = Field(default=0.5, ge=0, le=1, description="Voice stability parameter")
    similarity_boost: Optional[float] = Field(default=0.75, ge=0, le=1, description="Similarity boost parameter")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")


class VoiceOption(BaseModel):
    """Model for available voice option"""
    id: str
    name: str
    gender: Optional[str] = None
    language: Optional[str] = None
    accent: Optional[str] = None
    preview_url: Optional[str] = None


class AudioData(BaseModel):
    """Model for generated audio data"""
    path: str
    url: str
    duration: float
    format: str = "mp3"
    sample_rate: int = 44100


# ============== Asset Management Models ==============

class AssetUploadRequest(BaseModel):
    """Request model for asset upload"""
    asset_type: str = Field(..., description="Type of asset (avatar, logo, background)")
    position: Optional[Dict[str, int]] = Field(None, description="Position coordinates {x, y}")
    scale: Optional[float] = Field(default=1.0, ge=0.1, le=2.0, description="Scale factor")
    opacity: Optional[float] = Field(default=1.0, ge=0, le=1, description="Opacity level")


class AvatarData(BaseModel):
    """Model for avatar configuration"""
    filename: str
    path: str
    url: str
    type: str = Field(default="image", description="Image or custom avatar")
    expression: Optional[str] = None
    emotions: Optional[List[str]] = None


class LogoData(BaseModel):
    """Model for logo configuration"""
    filename: str
    path: str
    url: str
    position: str = Field(default="bottom-right", description="Logo position")
    scale: float = Field(default=0.15)
    opacity: float = Field(default=0.8)


class BackgroundData(BaseModel):
    """Model for background configuration"""
    filename: str
    path: str
    url: str
    type: str = Field(default="image", description="image or video")
    loop: bool = Field(default=True, description="Loop video background")


# ============== Video Generation Models ==============

class VideoRenderRequest(BaseModel):
    """Request model for video rendering"""
    use_heygem: Optional[bool] = Field(default=True, description="Use HeyGem for lip-sync")
    quality: Optional[str] = Field(default="high", description="Video quality (low, medium, high, 4k)")
    resolution: Optional[str] = Field(default="1080p", description="Output resolution")
    aspect_ratio: Optional[str] = Field(default="9:16", description="Video aspect ratio (9:16, 16:9, 1:1)")
    fps: Optional[int] = Field(default=30, description="Frames per second")
    watermark_enabled: Optional[bool] = Field(default=False, description="Add platform watermark")


class VideoRenderData(BaseModel):
    """Model for rendered video data"""
    path: str
    url: str
    duration: float
    resolution: str
    file_size: int
    format: str = "mp4"
    codec: str = "h264"


class VideoProgress(BaseModel):
    """Model for video generation progress"""
    status: str = Field(default="pending", description="Status: pending, processing, completed, failed")
    progress: float = Field(default=0.0, ge=0, le=100, description="Progress percentage")
    current_stage: Optional[str] = None
    eta_seconds: Optional[int] = None
    error_message: Optional[str] = None


# ============== API Response Models ==============

class SuccessResponse(BaseModel):
    """Standard success response"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ============== Settings Models ==============

class OllamaSettings(BaseModel):
    """Model for Ollama settings"""
    host: str = "http://localhost:11434"
    model: str = "llama3"
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=1, le=8192)


class HeyGemSettings(BaseModel):
    """Model for HeyGem settings"""
    host: str = "http://localhost:8001"
    model_path: Optional[str] = None
    device: str = "cuda"
    gpu_memory: Optional[int] = None


class FirecrawlSettings(BaseModel):
    """Model for Firecrawl settings"""
    host: str = "http://localhost:3002"
    api_key: Optional[str] = None
    timeout: int = 30
    max_pages: int = 10
