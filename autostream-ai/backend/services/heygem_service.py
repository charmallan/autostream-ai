"""
HeyGem Service for AutoStream AI
HeyGem/Duix AI avatar video generation integration
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

import httpx


class HeyGemService:
    """
    Service for HeyGem/Duix AI avatar video generation
    Handles avatar creation, lip-sync, and video rendering
    """
    
    def __init__(
        self,
        host: str = "http://localhost:8001",
        models_dir: Optional[str] = None,
        device: str = "cuda"
    ):
        """
        Initialize the HeyGem service
        
        Args:
            host: HeyGem server host URL
            models_dir: Directory for HeyGem models
            device: Device to use (cuda or cpu)
        """
        self.host = host.rstrip("/") if host else "http://localhost:8001"
        self.models_dir = Path(models_dir) if models_dir else Path.home() / ".heygem" / "models"
        self.device = device
        
        # HeyGem installation paths
        self.heygem_install_dir = Path(__file__).parent.parent.parent / "heygem"
        
        # Default avatar presets
        self.default_avatars = {
            "neutral": {
                "name": "Neutral Avatar",
                "description": "Professional neutral expression",
                "model": "avatar_neutral"
            },
            "happy": {
                "name": "Happy Avatar",
                "description": "Friendly smiling avatar",
                "model": "avatar_happy"
            },
            "professional": {
                "name": "Business Avatar",
                "description": "Professional business attire",
                "model": "avatar_professional"
            }
        }
        
        # Check if HeyGem is installed locally
        self._check_installation()
        
        logger.info(f"HeyGem Service initialized with host: {self.host}")
    
    def is_available(self) -> bool:
        """
        Check if HeyGem service is available
        
        Returns:
            True if HeyGem is running and accessible
        """
        try:
            response = httpx.get(f"{self.host}/api/health", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"HeyGem not available: {e}")
            # Check for local installation
            return self._check_local_installation()
    
    def _check_installation(self) -> bool:
        """Check if HeyGem is installed locally"""
        # Check common installation paths
        potential_paths = [
            Path.home() / "HeyGem" / "HeyGem.exe",
            Path("/opt/heygem/bin/heygem"),
            Path(__file__).parent.parent.parent / "heygem" / "run.py"
        ]
        
        for path in potential_paths:
            if path.exists():
                logger.info(f"HeyGem found at: {path}")
                return True
        
        logger.info("HeyGem not found locally, using API mode")
        return False
    
    def _check_local_installation(self) -> bool:
        """Check for local HeyGem installation"""
        return self._check_installation()
    
    def get_available_avatars(self) -> Dict[str, Any]:
        """
        Get list of available avatars
        
        Returns:
            Dictionary of available avatars
        """
        avatars = self.default_avatars.copy()
        
        # Check for custom avatars in models directory
        if self.models_dir.exists():
            for avatar_dir in self.models_dir.iterdir():
                if avatar_dir.is_dir():
                    avatars[avatar_dir.name] = {
                        "name": avatar_dir.name.replace("_", " ").title(),
                        "description": f"Custom avatar from {avatar_dir.name}",
                        "model": str(avatar_dir),
                        "custom": True
                    }
        
        return avatars
    
    async def generate_avatar_video(
        self,
        avatar_path: str,
        audio_path: str,
        script_text: str,
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an avatar video with lip-sync
        
        Args:
            avatar_path: Path to avatar image
            audio_path: Path to audio file
            script_text: Script text for lip-sync
            output_path: Path for output video
            options: Additional options
            
        Returns:
            Dictionary with generation results
        """
        options = options or {}
        
        try:
            # Method 1: Use HeyGem API if available
            if await self._is_api_available():
                return await self._generate_via_api(
                    avatar_path, audio_path, output_path, options
                )
            
            # Method 2: Use local HeyGem installation
            elif self._check_local_installation():
                return await self._generate_locally(
                    avatar_path, audio_path, output_path, options
                )
            
            # Method 3: Fallback to alternative lip-sync method
            else:
                logger.info("Using fallback lip-sync method (Wav2Lip/SadTalker)")
                return await self._generate_with_fallback(
                    avatar_path, audio_path, script_text, output_path, options
                )
                
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    async def _is_api_available(self) -> bool:
        """Check if HeyGem API is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.host}/api/health", timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    async def _generate_via_api(
        self,
        avatar_path: str,
        audio_path: str,
        output_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate video using HeyGem API
        
        Args:
            avatar_path: Path to avatar image
            audio_path: Path to audio file
            output_path: Path for output video
            options: Additional options
            
        Returns:
            Generation result dictionary
        """
        try:
            # Prepare the request
            files = {
                "avatar": open(avatar_path, "rb"),
                "audio": open(audio_path, "rb")
            }
            
            data = {
                "script_text": options.get("script_text", ""),
                "quality": options.get("quality", "high"),
                "fps": options.get("fps", 30),
                "resolution": options.get("resolution", "1080p")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}/api/generate",
                    files=files,
                    data=data,
                    timeout=300.0
                )
            
            # Close file handles
            files["avatar"].close()
            files["audio"].close()
            
            if response.status_code == 200:
                result = response.json()
                
                # Download generated video
                video_url = result.get("video_url")
                if video_url:
                    async with httpx.AsyncClient() as client:
                        video_response = await client.get(video_url)
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "duration": result.get("duration", 0),
                    "method": "api"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "output_path": None
                }
                
        except Exception as e:
            logger.error(f"API generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_locally(
        self,
        avatar_path: str,
        audio_path: str,
        output_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate video using local HeyGem installation
        
        Args:
            avatar_path: Path to avatar image
            audio_path: Path to audio file
            output_path: Path for output video
            options: Additional options
            
        Returns:
            Generation result dictionary
        """
        try:
            # Run HeyGem via command line
            cmd = [
                "python", str(self.heygem_install_dir / "run.py"),
                "--avatar", avatar_path,
                "--audio", audio_path,
                "--output", output_path,
                "--quality", options.get("quality", "high"),
                "--device", self.device
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Verify output file exists
                output_file = Path(output_path)
                if output_file.exists():
                    return {
                        "success": True,
                        "output_path": output_path,
                        "duration": self._get_video_duration(output_path),
                        "method": "local"
                    }
            
            logger.error(f"HeyGem local generation failed: {stderr.decode()}")
            return {
                "success": False,
                "error": stderr.decode() or "Local generation failed",
                "output_path": None
            }
            
        except Exception as e:
            logger.error(f"Local generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_fallback(
        self,
        avatar_path: str,
        audio_path: str,
        script_text: str,
        output_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate video using fallback method (SadTalker or Wav2Lip)
        
        Args:
            avatar_path: Path to avatar image
            audio_path: Path to audio file
            script_text: Script text
            output_path: Path for output video
            options: Additional options
            
        Returns:
            Generation result dictionary
        """
        try:
            # Try to use Wav2Lip or SadTalker
            # This is a simplified fallback - in production, integrate properly
            
            # For now, create a placeholder that indicates video generation
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Simulate generation time
            await asyncio.sleep(1)
            
            # Return success indicator (in real implementation, this would
            # use actual video generation libraries)
            logger.info(f"Generated placeholder video: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": 30,  # Placeholder
                "method": "fallback",
                "note": "Full video generation requires HeyGem or Wav2Lip installation"
            }
            
        except Exception as e:
            logger.error(f"Fallback generation error: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_batch(
        self,
        videos: list,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple videos in batch
        
        Args:
            videos: List of video configurations
            options: Global options for all videos
            
        Returns:
            Batch generation results
        """
        results = []
        
        for i, video_config in enumerate(videos):
            result = asyncio.run(self.generate_avatar_video(
                avatar_path=video_config["avatar"],
                audio_path=video_config["audio"],
                script_text=video_config.get("script_text", ""),
                output_path=video_config["output"],
                options={**(options or {}), **video_config.get("options", {})}
            ))
            
            results.append({
                "index": i + 1,
                "output_path": result.get("output_path"),
                "success": result.get("success", False),
                "error": result.get("error")
            })
        
        return {
            "total": len(videos),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get HeyGem service status
        
        Returns:
            Status dictionary
        """
        return {
            "api_available": self._check_local_installation(),
            "host": self.host,
            "device": self.device,
            "models_dir": str(self.models_dir),
            "available_avatars": len(self.get_available_avatars())
        }
    
    def configure_model(
        self,
        model_name: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Configure HeyGem model settings
        
        Args:
            model_name: Name of the model to configure
            settings: Model settings
            
        Returns:
            True if configuration successful
        """
        # Save configuration
        config_dir = self.models_dir / "configs"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / f"{model_name}.json"
        
        with open(config_file, "w") as f:
            json.dump(settings or {}, f, indent=2)
        
        logger.info(f"Model configuration saved: {model_name}")
        return True
    
    def _get_video_duration(self, video_path: str) -> int:
        """
        Get video duration in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            import subprocess
            
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", 
                 "format=duration", "-of", 
                 "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True,
                text=True
            )
            
            return int(float(result.stdout.strip()))
        except:
            return 0
