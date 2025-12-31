"""
Ollama Service for AutoStream AI
Local LLM integration for script generation
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional, List
from loguru import logger

from pathlib import Path


class OllamaService:
    """
    Service for interacting with local Ollama LLM
    Provides script generation capabilities
    """
    
    def __init__(self, host: str = "http://localhost:11434"):
        """
        Initialize the Ollama service
        
        Args:
            host: Ollama server host URL
        """
        self.host = host
        self.model = "llama3"
        self.available_models: List[str] = []
        
        logger.info(f"Ollama Service initialized with host: {host}")
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            import httpx
            response = httpx.get(f"{self.host}/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available Ollama models
        
        Returns:
            List of model names
        """
        try:
            response = httpx.get(f"{self.host}/api/tags", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                self.available_models = [
                    model["name"] for model in data.get("models", [])
                ]
                return self.available_models
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
        
        # Fallback to common models
        return ["llama3", "llama3.1", "mistral", "codellama", "gemma"]
    
    def set_model(self, model_name: str) -> bool:
        """
        Set the active model
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            True if model was set successfully
        """
        # Check if model is available
        available = self.get_available_models()
        
        # Try to pull if not available
        if model_name not in available:
            logger.info(f"Model {model_name} not found, attempting to pull...")
            if not self.pull_model(model_name):
                return False
        
        self.model = model_name
        logger.info(f"Active model set to: {model_name}")
        return True
    
    def pull_model(self, model_name: str, timeout: int = 600) -> bool:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Name of the model to pull
            timeout: Timeout in seconds
            
        Returns:
            True if model was pulled successfully
        """
        try:
            response = httpx.post(
                f"{self.host}/api/pull",
                json={"name": model_name},
                timeout=timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    async def generate_script(
        self,
        topic: str,
        description: str = "",
        tone: str = "professional",
        length: str = "short",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a video script based on the topic
        
        Args:
            topic: Main topic for the video
            description: Additional context/description
            tone: Script tone (professional, casual, funny, dramatic)
            length: Script length (short, medium, long)
            system_prompt: Custom system prompt (optional)
            
        Returns:
            Dictionary containing generated script
        """
        # Estimate duration based on length
        duration_map = {
            "short": (30, 60),   # 30-60 seconds
            "medium": (60, 120), # 1-2 minutes
            "long": (120, 300)   # 2-5 minutes
        }
        
        min_duration, max_duration = duration_map.get(length, (60, 120))
        
        # Build the prompt
        prompt = self._build_script_prompt(topic, description, tone, min_duration, max_duration)
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Generate the script
        script_content = await self._generate_with_ollama(full_prompt)
        
        if not script_content:
            # Return a fallback script
            return self._create_fallback_script(topic, tone, min_duration)
        
        # Parse and structure the script
        structured_script = self._parse_script(script_content, topic, min_duration)
        
        logger.info(f"Generated script for topic: {topic}")
        return structured_script
    
    async def generate_script_with_context(
        self,
        context: str,
        user_request: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a script with conversation context
        
        Args:
            context: Background context/information
            user_request: User's request or requirements
            history: Previous conversation messages
            
        Returns:
            Dictionary containing generated script
        """
        # Build context-rich prompt
        prompt = f"""You are a professional video script writer. Use the following context:

CONTEXT:
{context}

USER REQUEST:
{user_request}

Write a compelling video script that:
1. Engages viewers in the first 3 seconds
2. Follows a clear structure (hook, body, conclusion)
3. Includes natural pauses and pacing
4. Ends with a call-to-action

Script length: 60-90 seconds of spoken content.

Write the script now:"""
        
        # Add history if provided
        if history:
            formatted_history = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in history[-5:]
            ])
            prompt = f"Previous conversation:\n{formatted_history}\n\n{prompt}"
        
        script_content = await self._generate_with_ollama(prompt)
        
        if not script_content:
            return self._create_fallback_script(user_request, "professional", 60)
        
        return self._parse_script(script_content, user_request, 60)
    
    async def refine_script(
        self,
        current_script: str,
        feedback: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Refine an existing script based on feedback
        
        Args:
            current_script: The current script content
            feedback: Refinement instructions
            history: Previous refinement history
            
        Returns:
            Dictionary containing refined script
        """
        prompt = f"""You are a professional video script editor. 

CURRENT SCRIPT:
{current_script}

REFINEMENT FEEDBACK:
{feedback}

Please revise the script to address the feedback while maintaining:
1. Engaging hook
2. Clear structure
3. Natural flow
4. Appropriate length

Write the revised script:"""
        
        if history:
            prompt = f"Previous edits: {history}\n\n{prompt}"
        
        refined_content = await self._generate_with_ollama(prompt)
        
        if not refined_content:
            return {
                "content": current_script,
                "title": "Refined Script",
                "refined": False,
                "message": "Could not refine script, original retained"
            }
        
        # Calculate word count and duration
        word_count = len(refined_content.split())
        duration = (word_count / 150) * 60  # Average speaking rate
        
        return {
            "content": refined_content,
            "title": "Refined Script",
            "duration_estimate": int(duration),
            "word_count": word_count,
            "refined": True,
            "feedback_applied": feedback
        }
    
    async def _generate_with_ollama(self, prompt: str) -> Optional[str]:
        """
        Generate text using Ollama API
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            Generated text or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 2048
                        }
                    },
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    logger.error(f"Ollama generation failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None
    
    def _build_script_prompt(
        self,
        topic: str,
        description: str,
        tone: str,
        min_duration: int,
        max_duration: int
    ) -> str:
        """
        Build a comprehensive script generation prompt
        
        Args:
            topic: Main topic
            description: Additional description
            tone: Script tone
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            
        Returns:
            Formatted prompt string
        """
        tone_instructions = {
            "professional": "Use a professional, informative tone with clear explanations and authoritative delivery.",
            "casual": "Use a friendly, conversational tone as if talking to a friend. Be relaxed and relatable.",
            "funny": "Use humor, witty remarks, and entertaining language. Make viewers laugh while informing.",
            "dramatic": "Use suspenseful, emotional language. Create tension and surprise in the narrative.",
            "inspirational": "Use motivational, uplifting language. Inspire viewers and spark positive emotions."
        }
        
        tone_guide = tone_instructions.get(tone, tone_instructions["professional"])
        
        prompt = f"""You are a professional viral video script writer. Create a compelling {tone} video script.

TOPIC: {topic}
DESCRIPTION: {description if description else 'Create an engaging video about this topic'}

REQUIREMENTS:
- Target duration: {min_duration}-{max_duration} seconds (~{(max_duration/60):.1f} minutes)
- {tone_guide}
- Start with a powerful HOOK to grab attention in the first 3 seconds
- Follow structure: HOOK → VALUE → CONCLUSION → CTA
- Use natural speech patterns and conversational flow
- Include strategic pauses and emphasis markers [PAUSE] for editing
- End with a clear Call-To-Action (like, subscribe, etc.)

Format your response as a structured script with:
1. Title: <descriptive title>
2. Script: <full script text with [PAUSE] markers>
3. Key Points: <bullet points covered>
4. Estimated Duration: <in seconds>

Write the script now:"""
        
        return prompt
    
    def _parse_script(self, raw_script: str, topic: str, target_duration: int) -> Dict[str, Any]:
        """
        Parse and structure the raw script output
        
        Args:
            raw_script: Raw script text from LLM
            topic: Original topic
            target_duration: Target duration in seconds
            
        Returns:
            Structured script dictionary
        """
        # Extract title
        title = topic
        if "Title:" in raw_script:
            title = raw_script.split("Title:")[1].split("\n")[0].strip()
        elif "# " in raw_script:
            title = raw_script.split("# ")[1].split("\n")[0].strip()
        
        # Extract script content
        script_content = raw_script
        for delimiter in ["Script:", "## Script:", "SCRIPT:"]:
            if delimiter in raw_script:
                parts = raw_script.split(delimiter)
                if len(parts) > 1:
                    script_content = parts[1].strip()
                    break
        
        # Remove trailing sections
        for section in ["Key Points:", "## Key Points:", "KEY POINTS:", "Estimated Duration:"]:
            if section in script_content:
                script_content = script_content.split(section)[0].strip()
        
        # Extract key points
        key_points = []
        if "Key Points:" in raw_script:
            points_text = raw_script.split("Key Points:")[1].split("\n")
            for point in points_text:
                point = point.strip().lstrip("-•* ")
                if point and len(point) > 3:
                    key_points.append(point)
        
        # Calculate word count and duration
        word_count = len(script_content.split())
        duration_estimate = int((word_count / 150) * 60)  # ~150 words per minute
        
        return {
            "title": title,
            "content": script_content,
            "duration_estimate": duration_estimate,
            "word_count": word_count,
            "key_points": key_points,
            "tone_used": "professional",
            "target_duration": target_duration
        }
    
    def _create_fallback_script(
        self,
        topic: str,
        tone: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Create a fallback script when LLM generation fails
        
        Args:
            topic: Main topic
            tone: Script tone
            duration: Target duration
            
        Returns:
            Fallback script dictionary
        """
        fallback_script = f"""[PAUSE]

Hey there! Today we're talking about {topic}.

[PAUSE]

This is something that's been making waves recently, and here's why it matters...

[PAUSE]

First, let's look at the key points...

[PAUSE]

And here's the bottom line...

[PAUSE]

If you found this helpful, make sure to like and subscribe for more content like this!

[PAUSE]

See you in the next video!"""
        
        word_count = len(fallback_script.split())
        
        return {
            "title": f"{topic.title()} - {tone.title()} Script",
            "content": fallback_script,
            "duration_estimate": duration,
            "word_count": word_count,
            "key_points": [
                f"Introduction to {topic}",
                "Key insights and analysis",
                "Conclusion and takeaways"
            ],
            "tone_used": tone,
            "target_duration": duration,
            "fallback": True
        }
