"""
Video Compositor Service for AutoStream AI
Video composition and rendering with FFmpeg
"""

import os
import subprocess
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class VideoCompositor:
    """
    Service for video composition and rendering
    Handles combining avatar, audio, background, and overlays
    """
    
    def __init__(
        self,
        temp_dir: Optional[str] = None,
        output_dir: Optional[str] = None
    ):
        """
        Initialize the video compositor
        
        Args:
            temp_dir: Directory for temporary files
            output_dir: Directory for output files
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(__file__).parent.parent.parent / "temp"
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent.parent / "output"
        
        # Create directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg settings
        self.ffmpeg_path = "ffmpeg"
        self.ffprobe_path = "ffprobe"
        
        # Quality presets
        self.quality_presets = {
            "low": {
                "resolution": "720p",
                "bitrate": "2M",
                "fps": 24,
                "codec": "libx264"
            },
            "medium": {
                "resolution": "1080p",
                "bitrate": "5M",
                "fps": 30,
                "codec": "libx264"
            },
            "high": {
                "resolution": "1080p",
                "bitrate": "10M",
                "fps": 30,
                "codec": "libx264"
            },
            "4k": {
                "resolution": "2160p",
                "bitrate": "35M",
                "fps": 30,
                "codec": "libx265"
            }
        }
        
        # Aspect ratio presets
        self.aspect_ratios = {
            "9:16": (1080, 1920),    # TikTok/Reels
            "16:9": (1920, 1080),    # YouTube horizontal
            "1:1": (1080, 1080),     # Instagram square
            "4:5": (1080, 1350)      # Instagram portrait
        }
        
        logger.info("Video Compositor initialized")
    
    def is_available(self) -> bool:
        """
        Check if FFmpeg is available
        
        Returns:
            True if FFmpeg is installed and accessible
        """
        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found")
            return False
    
    async def generate_video(
        self,
        avatar_path: str,
        audio_path: str,
        background_path: Optional[str],
        logo_path: Optional[str],
        output_path: str,
        script_text: str = "",
        heygem_enabled: bool = True,
        quality: str = "high",
        aspect_ratio: str = "9:16"
    ) -> Dict[str, Any]:
        """
        Generate final video by compositing all elements
        
        Args:
            avatar_path: Path to avatar image/video
            audio_path: Path to audio file
            background_path: Path to background image/video
            logo_path: Path to logo overlay
            output_path: Path for output video
            script_text: Script text (for reference)
            heygem_enabled: Use HeyGem for lip-sync
            quality: Video quality preset
            aspect_ratio: Aspect ratio preset
            
        Returns:
            Video generation result
        """
        try:
            # Verify inputs
            if not Path(avatar_path).exists():
                raise FileNotFoundError(f"Avatar file not found: {avatar_path}")
            
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Get quality settings
            quality_settings = self.quality_presets.get(quality, self.quality_presets["high"])
            width, height = self.aspect_ratios.get(aspect_ratio, self.aspect_ratios["9:16"])
            
            # Get audio duration
            audio_duration = self._get_audio_duration(audio_path)
            
            # Prepare output
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate the video
            if heygem_enabled and Path(avatar_path).suffix in [".mp4", ".mov"]:
                # Avatar already has lip-sync applied
                result = await self._composite_with_heygem_avatar(
                    avatar_path, audio_path, background_path, logo_path,
                    output_path, quality_settings, width, height, audio_duration
                )
            else:
                # Create static avatar with audio
                result = await self._composite_static_avatar(
                    avatar_path, audio_path, background_path, logo_path,
                    output_path, quality_settings, width, height, audio_duration
                )
            
            # Verify output
            if result.get("success") and Path(output_path).exists():
                result["file_size"] = Path(output_path).stat().st_size
                result["resolution"] = f"{width}x{height}"
                result["duration"] = audio_duration
                result["format"] = "mp4"
                result["codec"] = quality_settings["codec"]
            
            return result
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    async def _composite_with_heygem_avatar(
        self,
        avatar_path: str,
        audio_path: str,
        background_path: Optional[str],
        logo_path: Optional[str],
        output_path: str,
        quality_settings: Dict[str, Any],
        width: int,
        height: int,
        duration: float
    ) -> Dict[str, Any]:
        """
        Composite video with HeyGem avatar (already lip-synced)
        
        Args:
            avatar_path: Path to avatar video
            audio_path: Path to audio
            background_path: Optional background
            logo_path: Optional logo
            output_path: Output path
            quality_settings: Quality settings
            width: Output width
            height: Output height
            duration: Audio duration
            
        Returns:
            Generation result
        """
        try:
            # Build FFmpeg filter complex
            filters = []
            
            # Add background
            if background_path and Path(background_path).exists():
                filters.append(
                    f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[bg];"
                )
                input_count = 2
            else:
                filters.append(
                    f"color=c=black:s={width}x{height}:d={duration}[bg];"
                )
                input_count = 1
            
            # Add avatar (centered, scaled to fit)
            avatar_scale = f"scale={int(width*0.6)}:{int(width*0.6*0.5625)}:force_original_aspect_ratio=decrease"
            filters.append(
                f"[0:v]{avatar_scale},"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[avatar];"
            )
            
            # Composite avatar over background
            filters.append("[bg][avatar]overlay=(W-w)/2:(H-h)/2+50")
            
            # Add logo if provided
            if logo_path and Path(logo_path).exists():
                logo_scale = f"scale={int(width*0.15)}:-1"
                filters.append(
                    f"[out]";
                    f"[1:v]{logo_scale}[logo];"
                    f"[composite][logo]overlay=W-{int(width*0.18)}:H-{int(width*0.18)}"
                )
            
            # Build FFmpeg command
            cmd = [
                self.ffmpeg_path, "-y",
                "-i", avatar_path
            ]
            
            if background_path and Path(background_path).exists():
                cmd.extend(["-i", background_path])
            
            if logo_path and Path(logo_path).exists():
                cmd.extend(["-i", logo_path])
            
            cmd.extend([
                "-i", audio_path,
                "-filter_complex", "".join(filters),
                "-map", "[out]",
                "-map", f"{'3' if (background_path and logo_path) else '2'}:a",
                "-c:v", quality_settings["codec"],
                "-b:v", quality_settings["bitrate"],
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-r", str(quality_settings["fps"]),
                output_path
            ])
            
            # Run FFmpeg
            result = await self._run_ffmpeg(cmd)
            
            return result
            
        except Exception as e:
            logger.error(f"HeyGem composite error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _composite_static_avatar(
        self,
        avatar_path: str,
        audio_path: str,
        background_path: Optional[str],
        logo_path: Optional[str],
        output_path: str,
        quality_settings: Dict[str, Any],
        width: int,
        height: int,
        duration: float
    ) -> Dict[str, Any]:
        """
        Composite video with static avatar image (simple lip-sync simulation)
        
        Args:
            avatar_path: Path to avatar image
            audio_path: Path to audio
            background_path: Optional background
            logo_path: Optional logo
            output_path: Output path
            quality_settings: Quality settings
            width: Output width
            height: Output height
            duration: Audio duration
            
        Returns:
            Generation result
        """
        try:
            # Build FFmpeg filter complex for static image with audio
            filters = []
            
            # Create background
            if background_path and Path(background_path).exists():
                filters.append(
                    f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[bg];"
                )
                input_count = 2
            else:
                # Create gradient background
                filters.append(
                    f"color=c=#1a1a2e:s={width}x{height}:d={duration}[bg];"
                )
                input_count = 1
            
            # Scale and position avatar
            avatar_scale = f"scale={int(width*0.7)}:{int(width*0.7*0.5625)}:force_original_aspect_ratio=decrease"
            filters.append(
                f"[0:v]{avatar_scale},"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                f"fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1[avatar];"
            )
            
            # Composite avatar over background
            filters.append("[bg][avatar]overlay=(W-w)/2:(H-h)/2+80")
            
            # Add subtle zoom effect to background
            if not background_path or not Path(background_path).exists():
                filters.append(
                    f"[bg]zoompan=z='min(zoom+0.001,1.1)':d={int(duration*25)}:s={width}x{height}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps=25[bg_zoomed];"
                )
                filters.append("[bg_zoomed][avatar]overlay=(W-w)/2:(H-h)/2+80")
            
            # Add logo if provided
            if logo_path and Path(logo_path).exists():
                logo_scale = f"scale={int(width*0.12)}:-1"
                filters.append(
                    f"[2:v]{logo_scale},"
                    f"fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5}:d=0.5[logo];"
                )
                filters.append(
                    f"[composite][logo]overlay=W-{int(width*0.15)}:H-{int(width*0.15)}"
                )
            
            # Build FFmpeg command
            cmd = [
                self.ffmpeg_path, "-y",
                "-loop", "1", "-framerate", "30",
                "-i", avatar_path,
                "-stream_loop", "-1",
                "-i", background_path if background_path and Path(background_path).exists() else "null",
            ]
            
            if logo_path and Path(logo_path).exists():
                cmd.extend(["-loop", "1", "-i", logo_path])
            
            cmd.extend([
                "-i", audio_path,
                "-filter_complex", "".join(filters) if not (background_path and Path(background_path).exists()) else "".join(filters),
                "-map", "[out]",
                "-map", f"{'3' if logo_path and Path(logo_path).exists() else '2'}:a",
                "-c:v", quality_settings["codec"],
                "-b:v", quality_settings["bitrate"],
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-r", str(quality_settings["fps"]),
                "-t", str(duration),
                "-shortest",
                output_path
            ])
            
            # Remove null input if not needed
            if not background_path or not Path(background_path).exists():
                cmd = [
                    self.ffmpeg_path, "-y",
                    "-loop", "1", "-framerate", "30",
                    "-i", avatar_path,
                ]
                if logo_path and Path(logo_path).exists():
                    cmd.extend(["-loop", "1", "-i", logo_path])
                
                cmd.extend([
                    "-i", audio_path,
                    "-filter_complex", f"color=c=#1a1a2e:s={width}x{height}:d={duration}[bg];"
                                      f"[0:v]scale={int(width*0.7)}:{int(width*0.7*0.5625)}:force_original_aspect_ratio=decrease,"
                                      f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[avatar];"
                                      f"[bg][avatar]overlay=(W-w)/2:(H-h)/2+80",
                    "-map", "[out]",
                    "-map", f"{'2' if logo_path and Path(logo_path).exists() else '2'}:a",
                    "-c:v", quality_settings["codec"],
                    "-b:v", quality_settings["bitrate"],
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-r", str(quality_settings["fps"]),
                    "-t", str(duration),
                    "-shortest",
                    output_path
                ])
            
            result = await self._run_ffmpeg(cmd)
            
            return result
            
        except Exception as e:
            logger.error(f"Static avatar composite error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _run_ffmpeg(self, cmd: List[str]) -> Dict[str, Any]:
        """
        Run FFmpeg command
        
        Args:
            cmd: FFmpeg command list
            
        Returns:
            Execution result
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": cmd[-1],
                    "message": "Video generated successfully"
                }
            else:
                error_msg = stderr.decode()[:500] if stderr else "Unknown error"
                logger.error(f"FFmpeg error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "output_path": None
                }
                
        except Exception as e:
            logger.error(f"FFmpeg execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio file duration in seconds
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            import subprocess
            
            result = subprocess.run(
                [
                    self.ffprobe_path, "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    audio_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            return float(result.stdout.strip())
        except:
            return 30.0  # Default to 30 seconds
    
    def add_captions(
        self,
        video_path: str,
        captions: List[Dict[str, Any]],
        output_path: str,
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add captions to a video
        
        Args:
            video_path: Input video path
            captions: List of caption segments with start, end, text
            output_path: Output path
            style: Caption style options
            
        Returns:
            Processing result
        """
        # This is a simplified implementation
        # In production, use proper subtitle burning
        
        try:
            # Create SRT file from captions
            srt_content = self._create_srt(captions)
            srt_path = self.temp_dir / "captions.srt"
            
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            
            # Build FFmpeg command with subtitles
            cmd = [
                self.ffmpeg_path, "-y",
                "-i", video_path,
                "-vf", f"subtitles={srt_path}",
                "-c:a", "copy",
                output_path
            ]
            
            result = asyncio.run(self._run_ffmpeg(cmd))
            
            # Clean up
            srt_path.unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Caption addition error: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_srt(self, captions: List[Dict[str, Any]]) -> str:
        """
        Create SRT subtitle format from captions
        
        Args:
            captions: List of caption segments
            
        Returns:
            SRT formatted string
        """
        srt_lines = []
        
        for i, caption in enumerate(captions, 1):
            start_time = self._format_srt_time(caption.get("start", 0))
            end_time = self._format_srt_time(caption.get("end", caption.get("start", 0) + 3))
            text = caption.get("text", "")
            
            srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
        
        return "\n".join(srt_lines)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT time format"""
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def add_background_music(
        self,
        video_path: str,
        music_path: str,
        output_path: str,
        volume: float = 0.3,
        fade_in: float = 2.0,
        fade_out: float = 2.0
    ) -> Dict[str, Any]:
        """
        Add background music to video
        
        Args:
            video_path: Input video path
            music_path: Background music path
            output_path: Output path
            volume: Music volume (0-1)
            fade_in: Fade in duration
            fade_out: Fade out duration
            
        Returns:
            Processing result
        """
        try:
            # Get video duration
            duration = self._get_video_duration(video_path)
            
            cmd = [
                self.ffmpeg_path, "-y",
                "-i", video_path,
                "-i", music_path,
                "-filter_complex",
                f"[0:a][1:a]amix=inputs=2:duration=first:weights=1 {volume}[outa];"
                f"[1:a]afade=t=in:st=0:d={fade_in},afade=t=out:st={duration-fade_out}:d={fade_out}[music];"
                f"[outa][music]amix=inputs=2:duration=first",
                "-map", "0:v",
                "-map", "[outa]",
                "-c:v", "copy",
                output_path
            ]
            
            return asyncio.run(self._run_ffmpeg(cmd))
            
        except Exception as e:
            logger.error(f"Background music error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        return self._get_audio_duration(video_path)
    
    def extract_audio(
        self,
        video_path: str,
        output_path: str,
        format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Extract audio from video
        
        Args:
            video_path: Input video path
            output_path: Output path
            format: Output format
            
        Returns:
            Extraction result
        """
        try:
            cmd = [
                self.ffmpeg_path, "-y",
                "-i", video_path,
                "-vn",
                "-acodec", "libmp3lame" if format == "mp3" else "aac",
                "-b:a", "192k",
                output_path
            ]
            
            return asyncio.run(self._run_ffmpeg(cmd))
            
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get information about a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video information dictionary
        """
        try:
            import json
            
            result = subprocess.run(
                [
                    self.ffprobe_path, "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    video_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            info = json.loads(result.stdout)
            
            video_stream = next(
                (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
                None
            )
            audio_stream = next(
                (s for s in info.get("streams", []) if s.get("codec_type") == "audio"),
                None
            )
            
            return {
                "path": video_path,
                "duration": float(info.get("format", {}).get("duration", 0)),
                "size": int(info.get("format", {}).get("size", 0)),
                "format": info.get("format", {}).get("format_name", ""),
                "video": {
                    "codec": video_stream.get("codec_name", "") if video_stream else "",
                    "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}" if video_stream else "",
                    "fps": eval(video_stream.get("r_frame_rate", "0")) if video_stream else 0,
                    "bitrate": int(video_stream.get("bit_rate", 0)) if video_stream else 0
                },
                "audio": {
                    "codec": audio_stream.get("codec_name", "") if audio_stream else "",
                    "channels": int(audio_stream.get("channels", 0)) if audio_stream else 0,
                    "sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Video info error: {e}")
            return {"path": video_path, "error": str(e)}
