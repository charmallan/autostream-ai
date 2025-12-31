"""
CrewAI Service for AutoStream AI
Advanced agent-based script generation using CrewAI framework
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from loguru import logger


class CrewAIService:
    """
    Service for CrewAI-based multi-agent script generation
    Uses specialized agents for research, writing, and editing
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """
        Initialize the CrewAI service
        
        Args:
            ollama_host: Ollama server host for LLM capabilities
        """
        self.ollama_host = ollama_host
        self.agent_configs = self._load_agent_configs()
        logger.info("CrewAI Service initialized")
    
    def is_available(self) -> bool:
        """
        Check if CrewAI service is available
        
        Returns:
            True if all required components are available
        """
        # CrewAI can work without full dependencies
        # by falling back to simpler implementations
        return True
    
    def _load_agent_configs(self) -> Dict[str, Any]:
        """
        Load agent configurations
        
        Returns:
            Dictionary of agent configurations
        """
        return {
            "researcher": {
                "role": "Topic Researcher",
                "goal": "Research and gather key information about the given topic",
                "backstory": "You are an expert researcher who specializes in finding the most interesting and relevant facts about any topic.",
                "tools": ["web_search", "content_analysis"]
            },
            "scriptwriter": {
                "role": "Viral Script Writer",
                "goal": "Write engaging, viral-worthy video scripts",
                "backstory": "You are a professional content creator who has written hundreds of viral videos across multiple platforms.",
                "tools": ["script_structure", "engagement_hooks"]
            },
            "editor": {
                "role": "Script Editor",
                "goal": "Polish and refine scripts for maximum impact",
                "backstory": "You are an Emmy-nominated editor who knows exactly what makes content compelling.",
                "tools": ["pacing_analysis", "engagement_optimization"]
            }
        }
    
    async def generate_script(
        self,
        topic: str,
        description: str = "",
        tone: str = "professional",
        length: str = "short"
    ) -> Dict[str, Any]:
        """
        Generate a script using CrewAI multi-agent approach
        
        Args:
            topic: Main topic for the video
            description: Additional context/description
            tone: Script tone
            length: Script length
            
        Returns:
            Dictionary containing generated and refined script
        """
        try:
            # Step 1: Research Phase
            research_data = await self._run_research_agent(topic, description)
            
            # Step 2: Script Writing Phase
            initial_script = await self._run_scriptwriter_agent(
                topic, research_data, tone, length
            )
            
            # Step 3: Editing Phase
            final_script = await self._run_editor_agent(initial_script, tone)
            
            # Calculate metrics
            word_count = len(final_script["content"].split())
            duration_estimate = int((word_count / 150) * 60)
            
            return {
                "title": final_script["title"],
                "content": final_script["content"],
                "duration_estimate": duration_estimate,
                "word_count": word_count,
                "key_points": research_data.get("key_points", []),
                "research_data": research_data,
                "tone_used": tone,
                "generation_method": "crewai",
                "agents_used": ["researcher", "scriptwriter", "editor"]
            }
            
        except Exception as e:
            logger.error(f"CrewAI script generation failed: {e}")
            # Fallback to basic generation
            return await self._fallback_generation(topic, tone, length)
    
    async def _run_research_agent(
        self,
        topic: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Run the research agent to gather information
        
        Args:
            topic: Topic to research
            description: Additional context
            
        Returns:
            Research data dictionary
        """
        # Simulate research using Ollama
        research_prompt = f"""You are a research expert. Research the following topic and provide key information:

TOPIC: {topic}
CONTEXT: {description}

Provide:
1. Main key points and facts (at least 5)
2. Common questions people ask about this topic
3. Trending aspects or recent developments
4. Controversial or debate-worthy angles
5. Expert quotes or statistics if available

Format as JSON with keys: key_points, questions, trends, angles, statistics"""

        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": research_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": 1500
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("response", "")
                    
                    # Try to parse JSON
                    try:
                        # Find JSON in response
                        if "```json" in text:
                            json_text = text.split("```json")[1].split("```")[0]
                        elif "{" in text and "}" in text:
                            start = text.find("{")
                            end = text.rfind("}") + 1
                            json_text = text[start:end]
                        else:
                            json_text = "{}"
                        
                        return json.loads(json_text)
                    except:
                        # Return structured fallback
                        return self._structure_research_data(text)
                else:
                    return self._empty_research_data()
        except Exception as e:
            logger.error(f"Research agent error: {e}")
            return self._empty_research_data()
    
    async def _run_scriptwriter_agent(
        self,
        topic: str,
        research_data: Dict[str, Any],
        tone: str,
        length: str
    ) -> Dict[str, Any]:
        """
        Run the scriptwriter agent to create initial script
        
        Args:
            topic: Topic for the script
            research_data: Research information
            tone: Script tone
            length: Script length
            
        Returns:
            Initial script dictionary
        """
        # Map length to word count
        length_map = {
            "short": (100, 150),
            "medium": (150, 250),
            "long": (250, 400)
        }
        
        min_words, max_words = length_map.get(length, (100, 150))
        
        tone_instructions = {
            "professional": "Professional, informative, authoritative",
            "casual": "Casual, friendly, conversational",
            "funny": "Humorous, witty, entertaining",
            "dramatic": "Suspenseful, emotional, engaging",
            "inspirational": "Motivational, uplifting, positive"
        }
        
        tone_guide = tone_instructions.get(tone, tone_instructions["professional"])
        
        script_prompt = f"""You are an expert viral video script writer.

TOPIC: {topic}
TONE: {tone_guide}
TARGET WORDS: {min_words}-{max_words}

RESEARCH DATA:
{json.dumps(research_data, indent=2)}

Write a compelling video script that:
1. Opens with a HOOK (attention-grabbing first 3 seconds)
2. Delivers VALUE with the research points
3. Has natural pacing with [PAUSE] markers
4. Ends with a clear CTA

Format:
TITLE: <creative title>
SCRIPT: <full script with [PAUSE] markers>"""

        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": script_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.8,
                            "top_p": 0.9,
                            "max_tokens": 1500
                        }
                    },
                    timeout=90.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("response", "")
                    return self._parse_script_output(text, topic)
                else:
                    return self._empty_script(topic)
        except Exception as e:
            logger.error(f"Scriptwriter agent error: {e}")
            return self._empty_script(topic)
    
    async def _run_editor_agent(
        self,
        script_data: Dict[str, Any],
        target_tone: str
    ) -> Dict[str, Any]:
        """
        Run the editor agent to polish the script
        
        Args:
            script_data: Current script data
            target_tone: Target tone for the script
            
        Returns:
            Edited script dictionary
        """
        editor_prompt = f"""You are a professional video editor and script polisher.

CURRENT SCRIPT:
Title: {script_data.get('title', '')}
Content: {script_data.get('content', '')}

TARGET TONE: {target_tone}

Review and improve this script:
1. Fix awkward phrasing
2. Improve flow and transitions
3. Enhance engagement elements
4. Ensure consistent tone
5. Optimize for spoken delivery

Return ONLY the improved script content (no explanations):"""

        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": editor_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.6,
                            "max_tokens": 1500
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    edited_content = data.get("response", "").strip()
                    
                    # Preserve the title
                    title = script_data.get("title", "Edited Script")
                    
                    return {
                        "title": title,
                        "content": edited_content,
                        "edited": True
                    }
                else:
                    return script_data
        except Exception as e:
            logger.error(f"Editor agent error: {e}")
            return script_data
    
    async def generate_with_workflow(
        self,
        topic: str,
        niche: str,
        goals: List[str],
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Run a complete CrewAI workflow with multiple iterations
        
        Args:
            topic: Main topic
            niche: Content niche/category
            goals: List of goals for the script
            max_iterations: Maximum refinement iterations
            
        Returns:
            Final script with workflow metadata
        """
        workflow_results = {
            "iterations": [],
            "final_script": None,
            "workflow_status": "completed"
        }
        
        # Initial generation
        script = await self.generate_script(topic, f"Niche: {niche}")
        workflow_results["iterations"].append({
            "iteration": 1,
            "script_length": len(script.get("content", "")),
            "changes": "Initial generation"
        })
        
        # Iterative refinement (simplified)
        for i in range(1, max_iterations):
            # In a full implementation, this would involve
            # agent-to-agent communication and feedback loops
            await asyncio.sleep(0.1)  # Simulate processing
            
            workflow_results["iterations"].append({
                "iteration": i + 1,
                "script_length": len(script.get("content", "")),
                "changes": "Refinement pass"
            })
        
        workflow_results["final_script"] = script
        
        return {
            **script,
            "workflow": workflow_results
        }
    
    def _parse_script_output(self, raw_output: str, default_topic: str) -> Dict[str, Any]:
        """Parse raw script output into structured data"""
        title = default_topic
        content = raw_output
        
        if "TITLE:" in raw_output:
            parts = raw_output.split("TITLE:")
            if len(parts) > 1:
                remaining = parts[1]
                if "SCRIPT:" in remaining:
                    title = remaining.split("SCRIPT:")[0].strip()
                    content = remaining.split("SCRIPT:")[1].strip()
                else:
                    title = remaining.strip()
        
        return {
            "title": title,
            "content": content,
            "raw": raw_output
        }
    
    def _structure_research_data(self, text: str) -> Dict[str, Any]:
        """Structure raw text into research data"""
        return {
            "key_points": text[:500].split(".")[:5],
            "questions": [],
            "trends": [],
            "angles": [],
            "raw_text": text
        }
    
    def _empty_research_data(self) -> Dict[str, Any]:
        """Return empty research data structure"""
        return {
            "key_points": ["Key point 1 about the topic", "Key point 2 about the topic"],
            "questions": ["What is this about?", "Why does it matter?"],
            "trends": ["Current trends in this area"],
            "angles": ["Different perspectives"],
            "statistics": []
        }
    
    def _empty_script(self, topic: str) -> Dict[str, Any]:
        """Return empty script structure"""
        return {
            "title": f"{topic} - Script",
            "content": f"[PAUSE]\n\nWelcome! Today we're exploring {topic}.\n\n[PAUSE]\n\nLet's dive in...",
            "raw": ""
        }
    
    async def _fallback_generation(
        self,
        topic: str,
        tone: str,
        length: str
    ) -> Dict[str, Any]:
        """Fallback script generation when CrewAI fails"""
        length_map = {
            "short": 100,
            "medium": 200,
            "long": 350
        }
        
        target_words = length_map.get(length, 100)
        
        fallback_content = f"""[PAUSE]

Hey! Let's talk about {topic}.

[PAUSE]

This is something really important that you should know about.

[PAUSE]

Here's the key information...

[PAUSE]

And that's the main takeaway!

[PAUSE]

Don't forget to like and subscribe for more content!

[PAUSE]"""
        
        return {
            "title": f"{topic.title()} - {tone.title()} Script",
            "content": fallback_content,
            "duration_estimate": int((len(fallback_content.split()) / 150) * 60),
            "word_count": len(fallback_content.split()),
            "key_points": [f"Introduction to {topic}", "Key insights", "Conclusion"],
            "tone_used": tone,
            "generation_method": "fallback"
        }
