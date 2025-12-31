"""
Enhanced TTS Service for AutoStream AI
Supports Piper, Bark, Coqui XTTS with voice cloning, and ElevenLabs
"""

import os
import asyncio
import subprocess
import json
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

import httpx


class EnhancedTTSService:
    """
    Comprehensive TTS service supporting multiple engines:
    - Piper (fast, high quality, offline)
    - Bark (expressive, ambient sounds, offline)
    - Coqui XTTS (voice cloning, offline)
    - ElevenLabs (premium, online)
    - gTTS (fallback, online)
    """
    
    def __init__(
        self,
        voices_dir: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None
    ):
        """
        Initialize the enhanced TTS service
        
        Args:
            voices_dir: Directory for custom voice models
            elevenlabs_api_key: ElevenLabs API key
        """
        self.voices_dir = Path(voices_dir) if voices_dir else Path(__file__).parent.parent.parent / "voices"
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
        
        # Create directories
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        
        # Audio directories
        self.audio_dir = self.voices_dir / "generated"
        self.clones_dir = self.voices_dir / "clones"
        self.samples_dir = self.voices_dir / "samples"
        
        for dir_path in [self.audio_dir, self.clones_dir, self.samples_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize voice registry
        self.voice_registry = self._load_voice_registry()
        
        # Active TTS engine
        self.active_engine = "piper"
        
        logger.info("Enhanced TTS Service initialized")
    
    def _load_voice_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load voice registry from disk or create default"""
        registry_file = self.voices_dir / "registry.json"
        
        if registry_file.exists():
            with open(registry_file, "r") as f:
                return json.load(f)
        
        # Default voices for each engine
        default_voices = {
            # Piper voices
            "piper_sarah": {
                "id": "piper_sarah",
                "name": "Sarah",
                "engine": "piper",
                "model_path": "piper_en_US_Sarah.onnx",
                "gender": "female",
                "language": "en-US",
                "description": "Clear, professional American female voice",
                "quality": "high",
                "speed": "fast",
                "expressiveness": "moderate",
                "cloned": False,
                "sample_text": "Hello, welcome to this video about artificial intelligence."
            },
            "piper_joe": {
                "id": "piper_joe",
                "name": "Joe",
                "engine": "piper",
                "model_path": "piper_en_US_Joe.onnx",
                "gender": "male",
                "language": "en-US",
                "description": "Warm, engaging American male voice",
                "quality": "high",
                "speed": "fast",
                "expressiveness": "moderate",
                "cloned": False,
                "sample_text": "Hey there! Today we're going to explore something amazing."
            },
            "piper_jenny": {
                "id": "piper_jenny",
                "name": "Jenny",
                "engine": "piper",
                "model_path": "piper_en_GB_Jenny_Direct.onnx",
                "gender": "female",
                "language": "en-GB",
                "description": "Elegant British female voice",
                "quality": "high",
                "speed": "fast",
                "expressiveness": "moderate",
                "cloned": False,
                "sample_text": "Hello and welcome to this presentation."
            },
            
            # Bark voices
            "bark_en_0": {
                "id": "bark_en_0",
                "name": "Bark Speaker 0",
                "engine": "bark",
                "speaker_id": 0,
                "gender": "female",
                "language": "en",
                "description": "Expressive voice with full emotion range",
                "quality": "very_high",
                "speed": "medium",
                "expressiveness": "full",
                "ambient_sounds": True,
                "cloned": False,
                "sample_text": "Hello! This is Bark, an expressive text-to-speech system!"
            },
            "bark_en_1": {
                "id": "bark_en_1",
                "name": "Bark Speaker 1",
                "engine": "bark",
                "speaker_id": 1,
                "gender": "male",
                "language": "en",
                "description": "Deep, resonant male voice with strong emotions",
                "quality": "very_high",
                "speed": "medium",
                "expressiveness": "full",
                "ambient_sounds": True,
                "cloned": False,
                "sample_text": "This is a deeper, more dramatic voice sample."
            },
            "bark_en_3": {
                "id": "bark_en_3",
                "name": "Bark Speaker 3",
                "engine": "bark",
                "speaker_id": 3,
                "gender": "female",
                "language": "en",
                "description": "Animated, enthusiastic female voice",
                "quality": "very_high",
                "speed": "medium",
                "expressiveness": "full",
                "ambient_sounds": True,
                "cloned": False,
                "sample_text": "Wow! This is incredibly exciting! I love this!"
            },
            
            # Coqui XTTS
            "xtts_default": {
                "id": "xtts_default",
                "name": "XTTS Default",
                "engine": "xtts",
                "gender": "neutral",
                "language": "en",
                "description": "Coqui XTTS default voice - clear and natural",
                "quality": "very_high",
                "speed": "fast",
                "expressiveness": "moderate",
                "voice_cloning": True,
                "cloned": False,
                "sample_text": "This is the default Coqui XTTS voice."
            },
            
            # ElevenLabs
            "eleven_rachel": {
                "id": "eleven_rachel",
                "name": "Rachel",
                "engine": "elevenlabs",
                "elevenlabs_id": "21m00Tcm4TlvDq8ikWAM",
                "gender": "female",
                "language": "en",
                "description": "Professional female voice, great for narration",
                "quality": "premium",
                "speed": "fast",
                "expressiveness": "high",
                "cloned": False,
                "premium": True,
                "sample_text": "Welcome to this video. Let's explore something amazing together."
            },
            "eleven_antoni": {
                "id": "eleven_antoni",
                "name": "Antoni",
                "engine": "elevenlabs",
                "elevenlabs_id": "ErXwobaYiN019PkySvjV",
                "gender": "male",
                "language": "en",
                "description": "Professional male voice, warm and engaging",
                "quality": "premium",
                "speed": "fast",
                "expressiveness": "high",
                "cloned": False,
                "premium": True,
                "sample_text": "Hey there! Great to have you watching this video."
            },
            
            # gTTS
            "gtts_en": {
                "id": "gtts_en",
                "name": "Google English",
                "engine": "gtts",
                "language": "en",
                "description": "Google Translate TTS - basic but reliable",
                "quality": "basic",
                "speed": "fast",
                "expressiveness": "minimal",
                "cloned": False,
                "free": True,
                "sample_text": "This is a basic Google TTS voice."
            }
        }
        
        self._save_voice_registry(default_voices)
        return default_voices
    
    def _save_voice_registry(self, registry: Dict[str, Dict[str, Any]]):
        """Save voice registry to disk"""
        registry_file = self.voices_dir / "registry.json"
        with open(registry_file, "w") as f:
            json.dump(registry, f, indent=2)
    
    def is_available(self) -> bool:
        """Check if any TTS engine is available"""
        return True  # Always have gTTS fallback
    
    def get_available_voices(self, engine: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        voices = []
        for voice_id, voice_data in self.voice_registry.items():
            if engine and voice_data.get("engine") != engine:
                continue
            voices.append({**voice_data, "available": True})
        return voices
    
    def get_engines(self) -> Dict[str, Any]:
        """Get information about all TTS engines"""
        return {
            "piper": {
                "name": "Piper",
                "description": "Fast, high-quality neural TTS",
                "quality": "high",
                "speed": "fast",
                "offline": True,
                "free": True,
                "available": self._check_piper()
            },
            "bark": {
                "name": "Bark",
                "description": "Expressive with laughter, sighs, emotions",
                "quality": "very_high",
                "speed": "medium",
                "offline": True,
                "free": True,
                "available": self._check_bark(),
                "features": ["emotions", "laughter", "ambient_sounds"]
            },
            "xtts": {
                "name": "Coqui XTTS",
                "description": "Voice cloning & multi-language TTS",
                "quality": "very_high",
                "speed": "fast",
                "offline": True,
                "free": True,
                "available": self._check_xtts(),
                "features": ["voice_cloning"]
            },
            "elevenlabs": {
                "name": "ElevenLabs",
                "description": "Premium AI voice synthesis",
                "quality": "premium",
                "speed": "fast",
                "offline": False,
                "free": False,
                "api_required": True,
                "available": self._check_elevenlabs()
            },
            "gtts": {
                "name": "Google TTS",
                "description": "Basic but reliable",
                "quality": "basic",
                "speed": "fast",
                "offline": False,
                "free": True,
                "available": self._check_gtts()
            }
        }
    
    def _check_piper(self) -> bool:
        try:
            subprocess.run(["piper", "--help"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _check_bark(self) -> bool:
        try:
            from bark import SAMPLE_RATE
            return True
        except ImportError:
            return False
    
    def _check_xtts(self) -> bool:
        try:
            from TTS import TTS
            return True
        except ImportError:
            return False
    
    def _check_elevenlabs(self) -> bool:
        return bool(self.elevenlabs_api_key)
    
    def _check_gtts(self) -> bool:
        try:
            import gtts
            return True
        except ImportError:
            return False
    
    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        engine: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate audio from text using specified voice"""
        voice_data = self.voice_registry.get(voice_id)
        if not voice_data:
            raise ValueError(f"Voice not found: {voice_id}")
        
        engine = engine or voice_data.get("engine", "piper")
        
        # Generate unique filename
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.audio_dir / f"{voice_id}_{timestamp}_{text_hash}.wav"
        
        try:
            if engine == "piper":
                result = await self._generate_piper(text, voice_data, output_path, **kwargs)
            elif engine == "bark":
                result = await self._generate_bark(text, voice_data, output_path, **kwargs)
            elif engine == "xtts":
                result = await self._generate_xtts(text, voice_data, output_path, **kwargs)
            elif engine == "elevenlabs":
                result = await self._generate_elevenlabs(text, voice_data, output_path, **kwargs)
            elif engine == "gtts":
                result = await self._generate_gtts(text, voice_data, output_path, **kwargs)
            else:
                raise ValueError(f"Unknown engine: {engine}")
            
            return result
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise
    
    async def _generate_piper(self, text: str, voice_data: Dict[str, Any], output_path: Path, **kwargs) -> Dict[str, Any]:
        """Generate audio using Piper TTS"""
        model_path = self.voices_dir / voice_data.get("model_path")
        
        if not model_path.exists():
            raise FileNotFoundError(f"Piper model not found: {model_path}")
        
        cmd = ["piper", "--model", str(model_path), "--output_file", str(output_path)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(input=text.encode())
        
        if process.returncode != 0:
            raise RuntimeError(f"Piper failed: {stderr.decode()}")
        
        return self._create_result(output_path, voice_data, "piper")
    
    async def _generate_bark(self, text: str, voice_data: Dict[str, Any], output_path: Path, **kwargs) -> Dict[str, Any]:
        """Generate audio using Bark with expressive features"""
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            import numpy as np
            
            speaker_id = kwargs.get("speaker_id", voice_data.get("speaker_id", 0))
            text_temp = kwargs.get("text_temp", 0.7)
            waveform_temp = kwargs.get("waveform_temp", 0.7)
            
            # Try to preload models first
            try:
                preload_models()
            except:
                pass
            
            audio_array = generate_audio(
                text,
                history_prompt=speaker_id,
                text_temp=text_temp,
                waveform_temp=waveform_temp
            )
            
            # Save audio
            try:
                from scipy.io.wavfile import write as write_wav
                audio_array = np.int16(audio_array * 32767)
                write_wav(str(output_path), SAMPLE_RATE, audio_array)
            except:
                import wave
                audio_array = np.int16(audio_array * 32767)
                with wave.open(str(output_path), 'w') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(audio_array.tobytes())
            
            return self._create_result(output_path, voice_data, "bark")
            
        except ImportError as e:
            raise ImportError("Bark not installed. Run: pip install git+https://github.com/suno-ai/bark.git")
    
    async def _generate_xtts(self, text: str, voice_data: Dict[str, Any], output_path: Path, **kwargs) -> Dict[str, Any]:
        """Generate audio using Coqui XTTS with optional voice cloning"""
        try:
            from TTS import TTS
            
            voice_clone_path = kwargs.get("voice_clone_path")
            
            if voice_clone_path and os.path.exists(voice_clone_path):
                model = TTS(model_name="xtts_v2", progress_bar=False)
                model.tts_to_file(
                    text=text, speaker_wav=voice_clone_path, file_path=str(output_path)
                )
            else:
                model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
                model.tts_to_file(text=text, file_path=str(output_path))
            
            return self._create_result(output_path, voice_data, "xtts")
            
        except ImportError as e:
            raise ImportError("Coqui TTS not installed. Run: pip install TTS")
    
    async def _generate_elevenlabs(self, text: str, voice_data: Dict[str, Any], output_path: Path, **kwargs) -> Dict[str, Any]:
        """Generate audio using ElevenLabs API"""
        voice_id = voice_data.get("elevenlabs_id")
        
        if not self.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {"xi-api-key": self.elevenlabs_api_key, "Content-Type": "application/json"}
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": kwargs.get("stability", 0.5),
                "similarity_boost": kwargs.get("similarity_boost", 0.75),
                "speed": kwargs.get("speed", 1.0)
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=60.0)
            
            if response.status_code != 200:
                raise RuntimeError(f"ElevenLabs API error: {response.text}")
            
            with open(output_path, "wb") as f:
                f.write(response.content)
        
        return self._create_result(output_path, voice_data, "elevenlabs")
    
    async def _generate_gtts(self, text: str, voice_data: Dict[str, Any], output_path: Path, **kwargs) -> Dict[str, Any]:
        """Generate audio using Google TTS"""
        try:
            from gtts import gTTS
            
            language = voice_data.get("language", "en")
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(str(output_path))
            
            return self._create_result(output_path, voice_data, "gtts")
            
        except ImportError:
            raise ImportError("gTTS not installed. Run: pip install gTTS")
    
    def _create_result(self, output_path: Path, voice_data: Dict[str, Any], engine: str) -> Dict[str, Any]:
        """Create standardized result dictionary"""
        return {
            "success": True,
            "path": str(output_path),
            "url": f"/uploads/audio/{output_path.name}",
            "duration": self._estimate_duration(str(output_path)),
            "format": "wav",
            "engine": engine,
            "voice": {"id": voice_data.get("id"), "name": voice_data.get("name"), "engine": engine},
            "timestamp": datetime.now().isoformat()
        }
    
    def _estimate_duration(self, audio_path: str) -> float:
        """Estimate audio duration"""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", 
                 "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True, text=True
            )
            return float(result.stdout.strip())
        except:
            return 3.0
    
    # ========== Voice Cloning Methods ==========
    
    async def create_voice_clone(self, reference_audio_paths: List[str], clone_name: str, description: str = "") -> Dict[str, Any]:
        """Create a custom voice clone from reference audio samples"""
        valid_files = [f for f in reference_audio_paths if os.path.exists(f)]
        if len(valid_files) < 1:
            raise ValueError("At least one valid reference audio file is required")
        
        clone_id = f"clone_{hashlib.md5(clone_name.encode()).hexdigest()[:8]}"
        clone_dir = self.clones_dir / clone_id
        clone_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            from TTS import TTS
            
            # Copy reference files
            for i, audio_path in enumerate(valid_files[:5]):
                import shutil
                shutil.copy(audio_path, clone_dir / f"reference_{i+1}.wav")
            
            # Create metadata
            metadata = {
                "id": clone_id, "name": clone_name, "description": description,
                "created_at": datetime.now().isoformat(), "reference_files": len(valid_files),
                "engine": "xtts"
            }
            
            with open(clone_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Add to registry
            self.voice_registry[clone_id] = {
                "id": clone_id, "name": clone_name, "engine": "xtts",
                "gender": "custom", "language": "en",
                "description": description or f"Custom voice clone: {clone_name}",
                "quality": "custom", "expressiveness": "custom",
                "voice_cloning": True, "cloned": True,
                "clone_path": str(clone_dir),
                "sample_text": f"This is the cloned voice of {clone_name}."
            }
            
            self._save_voice_registry(self.voice_registry)
            
            return {"success": True, "clone_id": clone_id, "name": clone_name, 
                    "message": f"Voice clone '{clone_name}' created successfully"}
            
        except Exception as e:
            import shutil
            if clone_dir.exists():
                shutil.rmtree(clone_dir)
            raise RuntimeError(f"Voice cloning failed: {str(e)}")
    
    def get_cloned_voices(self) -> List[Dict[str, Any]]:
        """Get list of all cloned voices"""
        clones = []
        for voice_id, voice_data in self.voice_registry.items():
            if voice_data.get("cloned"):
                clones.append({
                    "id": voice_id, "name": voice_data.get("name"),
                    "description": voice_data.get("description", ""),
                    "created_at": voice_data.get("created_at", ""),
                    "clone_path": voice_data.get("clone_path")
                })
        return clones
    
    def delete_voice_clone(self, clone_id: str) -> bool:
        """Delete a custom voice clone"""
        if clone_id not in self.voice_registry:
            return False
        
        clone_data = self.voice_registry[clone_id]
        clone_path = clone_data.get("clone_path")
        
        del self.voice_registry[clone_id]
        self._save_voice_registry(self.voice_registry)
        
        if clone_path and os.path.exists(clone_path):
            import shutil
            shutil.rmtree(clone_path)
        
        return True
    
    def get_bark_settings_schema(self) -> Dict[str, Any]:
        """Get Bark-specific settings that can be configured"""
        return {
            "text_temp": {"type": "float", "range": [0.1, 1.0], "default": 0.7,
                         "description": "Controls text generation diversity. Higher = more creative."},
            "waveform_temp": {"type": "float", "range": [0.1, 1.0], "default": 0.7,
                             "description": "Controls audio variation. Higher = more diverse output."}
        }
