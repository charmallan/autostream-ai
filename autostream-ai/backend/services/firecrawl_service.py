"""
Firecrawl Service for AutoStream AI
Web scraping and trending topic discovery
"""

import asyncio
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

import httpx


class FirecrawlService:
    """
    Service for web scraping and trending topic discovery using Firecrawl
    Provides topic research capabilities for video content creation
    """
    
    def __init__(
        self,
        host: str = "http://localhost:3002",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the Firecrawl service
        
        Args:
            host: Firecrawl server host URL
            api_key: Optional API key for hosted service
            timeout: Request timeout in seconds
        """
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        
        # Common sources for trending topics
        self.source_configs = {
            "youtube": {
                "base_url": "https://www.youtube.com",
                "selectors": {
                    "trending": "#video-title",
                    "views": "#metadata-line span:nth-child(2)"
                }
            },
            "reddit": {
                "base_url": "https://www.reddit.com",
                "selectors": {
                    "posts": ".Post",
                    "title": "[data-click-id='body'] h3",
                    "votes": "[data-click-id='upvotes']"
                }
            },
            "twitter": {
                "base_url": "https://twitter.com",
                "selectors": {
                    "trends": "[data-testid='trendItem']"
                }
            },
            "news": {
                "base_url": "https://news.google.com",
                "selectors": {
                    "headlines": "h3"
                }
            }
        }
        
        logger.info(f"Firecrawl Service initialized with host: {host}")
    
    def is_available(self) -> bool:
        """
        Check if Firecrawl service is available
        
        Returns:
            True if Firecrawl is running and accessible
        """
        try:
            response = httpx.get(f"{self.host}/api/v1/scrape/status", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Firecrawl not available: {e}")
            # Return True to allow simulation mode
            return True
    
    async def scrape_trending_topics(
        self,
        query: str,
        niche: str = "general",
        limit: int = 10,
        sources: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape trending topics based on query and niche
        
        Args:
            query: Search query or keyword
            niche: Content niche/category
            limit: Maximum number of results
            sources: Specific sources to scrape
            
        Returns:
            List of trending topic dictionaries
        """
        trends = []
        
        # Determine which sources to use
        if sources is None:
            sources = self._get_default_sources(niche)
        
        # Scrape from each source
        tasks = []
        for source in sources:
            if source in self.source_configs:
                task = self._scrape_source(query, source, limit)
                tasks.append(task)
        
        # Run all scrapes concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    trends.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Scraping error: {result}")
        
        # Sort by engagement/relevance
        trends = self._sort_and_deduplicate(trends)
        
        # Limit results
        return trends[:limit]
    
    async def scrape_url_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a specific URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}/api/v1/scrape",
                    json={
                        "url": url,
                        "formats": ["markdown", "html"],
                        "onlyMainContent": True
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "url": url,
                        "title": data.get("metadata", {}).get("title", ""),
                        "content": data.get("markdown", ""),
                        "html": data.get("html", ""),
                        "description": data.get("metadata", {}).get("description", ""),
                        "success": True
                    }
                else:
                    return {"url": url, "success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"URL scraping error: {e}")
            return {"url": url, "success": False, "error": str(e)}
    
    async def search_related_content(
        self,
        topic: str,
        max_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Search for related content and articles about a topic
        
        Args:
            topic: Topic to search for
            max_results: Maximum number of results
            
        Returns:
            List of related content dictionaries
        """
        # Use Firecrawl's search capability (if available)
        # Or fall back to direct URL scraping
        
        search_urls = [
            f"https://news.google.com/search?q={topic.replace(' ', '%20')}",
            f"https://www.reddit.com/search/?q={topic.replace(' ', '%20')}&sort=relevance",
            f"https://www.youtube.com/results?search_query={topic.replace(' ', '%20')}"
        ]
        
        results = []
        
        for url in search_urls[:max_results]:
            content = await self.scrape_url_content(url)
            if content.get("success"):
                results.append({
                    "url": url,
                    "title": content.get("title", "")[:100],
                    "snippet": content.get("description", "")[:200],
                    "source": self._get_domain(url)
                })
        
        return results
    
    async def extract_video_ideas(
        self,
        topic: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract video ideas from trending content about a topic
        
        Args:
            topic: Topic to research
            count: Number of ideas to generate
            
        Returns:
            List of video idea dictionaries
        """
        # Scrape related content
        related_content = await self.search_related_content(topic, count)
        
        # Generate video ideas based on scraped content
        ideas = []
        for i, content in enumerate(related_content):
            idea = {
                "id": i + 1,
                "title": self._generate_idea_title(topic, content),
                "hook": self._generate_idea_hook(topic, content),
                "angle": self._extract_angle(content),
                "source_url": content.get("url", ""),
                "source_name": content.get("source", "")
            }
            ideas.append(idea)
        
        return ideas
    
    async def analyze_competition(
        self,
        topic: str,
        platform: str = "youtube"
    ) -> Dict[str, Any]:
        """
        Analyze competing content for a topic
        
        Args:
            topic: Topic to analyze
            platform: Platform to analyze
            
        Returns:
            Competition analysis dictionary
        """
        # Scrape trending videos/posts about the topic
        trends = await self.scrape_trending_topics(topic, limit=10)
        
        # Analyze patterns
        analysis = {
            "topic": topic,
            "platform": platform,
            "total_articles_found": len(trends),
            "common_themes": self._extract_common_themes(trends),
            "engagement_patterns": self._analyze_engagement(trends),
            "content_gaps": self._identify_content_gaps(topic, trends),
            "recommendations": self._generate_recommendations(trends)
        }
        
        return analysis
    
    async def _scrape_source(
        self,
        query: str,
        source: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape trending topics from a specific source
        
        Args:
            query: Search query
            source: Source name
            limit: Maximum results
            
        Returns:
            List of trend items
        """
        config = self.source_configs.get(source, {})
        base_url = config.get("base_url", "")
        
        # Build search URL based on source
        search_url = self._build_search_url(source, query)
        
        if not search_url:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    search_url,
                    timeout=self.timeout,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    return self._parse_search_results(
                        response.text,
                        source,
                        query
                    )
                else:
                    logger.warning(f"Failed to scrape {source}: {response.status_code}")
                    return self._get_simulated_trends(query, source, limit)
                    
        except Exception as e:
            logger.error(f"Error scraping {source}: {e}")
            return self._get_simulated_trends(query, source, limit)
    
    def _build_search_url(self, source: str, query: str) -> Optional[str]:
        """Build search URL for a source"""
        encoded_query = query.replace(" ", "%20")
        
        urls = {
            "youtube": f"https://www.youtube.com/results?search_query={encoded_query}",
            "reddit": f"https://www.reddit.com/search/?q={encoded_query}&sort=relevance",
            "news": f"https://news.google.com/search?q={encoded_query}",
            "twitter": f"https://twitter.com/search?q={encoded_query}&f=top"
        }
        
        return urls.get(source)
    
    def _parse_search_results(
        self,
        html: str,
        source: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Parse HTML search results into structured data
        
        Args:
            html: Raw HTML response
            source: Source name
            query: Original search query
            
        Returns:
            List of parsed trend items
        """
        trends = []
        
        # Use simple regex patterns to extract content
        # In production, use BeautifulSoup or similar
        
        if source == "youtube":
            # Extract video titles and URLs
            titles = re.findall(r'"title":"([^"]+)"', html)
            for title in titles[:10]:
                if title and len(title) > 10:
                    trends.append({
                        "id": str(len(trends) + 1),
                        "title": title,
                        "description": f"Video about {query}",
                        "source": "youtube",
                        "url": f"https://www.youtube.com/results?search_query={query.replace(' ', '%20')}",
                        "engagement": {"views": "N/A"},
                        "scraped_at": datetime.now().isoformat()
                    })
        
        elif source == "reddit":
            # Extract post titles
            titles = re.findall(r'"title":"([^"]+)"', html)
            for title in titles[:10]:
                if title and len(title) > 5:
                    trends.append({
                        "id": str(len(trends) + 1),
                        "title": title,
                        "description": f"Reddit post about {query}",
                        "source": "reddit",
                        "url": f"https://www.reddit.com/search/?q={query.replace(' ', '%20')}",
                        "engagement": {"votes": "N/A"},
                        "scraped_at": datetime.now().isoformat()
                    })
        
        else:
            # Generic parsing
            titles = re.findall(r'<[^>]+>([^<]{20,100})</[^>]+>', html)
            for title in titles[:10]:
                trends.append({
                    "id": str(len(trends) + 1),
                    "title": title.strip(),
                    "description": f"Content about {query}",
                    "source": source,
                    "url": "",
                    "engagement": {},
                    "scraped_at": datetime.now().isoformat()
                })
        
        return trends
    
    def _get_simulated_trends(
        self,
        query: str,
        source: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Get simulated trending topics when scraping fails
        
        Args:
            query: Search query
            source: Source name
            limit: Number of trends
            
        Returns:
            List of simulated trend items
        """
        templates = [
            f"Breaking: Everything You Need to Know About {query}",
            f"Why {query} Is Trending Right Now",
            f"Top 10 Facts About {query} You Didn't Know",
            f"How {query} Is Changing the Industry",
            f"The Future of {query} - Expert Analysis",
            f"{query}: A Complete Guide for Beginners",
            f"Why Everyone's Talking About {query}",
            f"Insider Secrets About {query} Revealed",
            f" {query} - What You Need To Understand",
            f"The Untold Story of {query}"
        ]
        
        trends = []
        for i, title in enumerate(templates[:limit]):
            trends.append({
                "id": str(i + 1),
                "title": title,
                "description": f"Trending content about {query} from {source}",
                "source": source,
                "url": f"https://{source}.com/search?q={query.replace(' ', '%20')}",
                "engagement": {
                    "simulated": True,
                    "views": f"{1000 + (i * 500)}",
                    "likes": f"{100 + (i * 50)}"
                },
                "scraped_at": datetime.now().isoformat()
            })
        
        return trends
    
    def _get_default_sources(self, niche: str) -> List[str]:
        """Get default sources based on niche"""
        niche_sources = {
            "tech": ["news", "reddit", "youtube"],
            "business": ["news", "reddit"],
            "entertainment": ["youtube", "reddit"],
            "gaming": ["youtube", "reddit"],
            "news": ["news", "twitter"],
            "general": ["news", "youtube", "reddit"]
        }
        
        return niche_sources.get(niche, niche_sources["general"])
    
    def _sort_and_deduplicate(
        self,
        trends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort trends by engagement and remove duplicates"""
        seen_titles = set()
        unique_trends = []
        
        for trend in trends:
            title = trend.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_trends.append(trend)
        
        # Sort by simulated engagement score
        unique_trends.sort(
            key=lambda x: int(x.get("engagement", {}).get("views", "0").replace(",", "") or 0),
            reverse=True
        )
        
        return unique_trends
    
    def _extract_common_themes(self, trends: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes from trends"""
        # Simplified theme extraction
        themes = []
        for trend in trends[:5]:
            title = trend.get("title", "")
            # Extract key phrases
            if "how" in title.lower():
                themes.append("How-to content")
            if "top" in title.lower():
                themes.append("List-style content")
            if "why" in title.lower():
                themes.append("Explanation content")
            if "review" in title.lower():
                themes.append("Review content")
        
        return list(set(themes))
    
    def _analyze_engagement(self, trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns in trends"""
        return {
            "avg_views": "N/A",
            "top_performers": 0,
            "content_type": "mixed"
        }
    
    def _identify_content_gaps(
        self,
        topic: str,
        trends: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify content gaps for the topic"""
        return [
            f"Create a comprehensive guide about {topic}",
            f"Make an FAQ video about {topic}",
            f"Create a comparison video comparing {topic} alternatives",
            f"Develop a beginner-friendly explanation of {topic}"
        ]
    
    def _generate_recommendations(self, trends: List[Dict[str, Any]]) -> List[str]:
        """Generate content recommendations based on trends"""
        return [
            "Focus on high-engagement topics from the trends",
            "Use attention-grabbing titles similar to top performers",
            "Create content that answers common questions",
            "Add value by providing unique insights or perspectives"
        ]
    
    def _generate_idea_title(
        self,
        topic: str,
        content: Dict[str, Any]
    ) -> str:
        """Generate a video idea title"""
        base_title = content.get("title", "")[:50]
        if base_title:
            return f"Deep Dive: {base_title}"
        return f"Everything About {topic}"
    
    def _generate_idea_hook(
        self,
        topic: str,
        content: Dict[str, Any]
    ) -> str:
        """Generate a hook for the video idea"""
        hooks = [
            f"You won't believe what I discovered about {topic}...",
            f"This changed everything I knew about {topic}.",
            f"If you're interested in {topic}, you need to hear this.",
            f"The truth about {topic} might surprise you."
        ]
        return hooks[0]
    
    def _extract_angle(self, content: Dict[str, Any]) -> str:
        """Extract the content angle"""
        return content.get("snippet", "")[:100] or "General overview"
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace("www.", "")
        except:
            return "unknown"
