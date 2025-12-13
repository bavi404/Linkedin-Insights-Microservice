"""
AI Summary Service
Optional service for generating AI-powered summaries of LinkedIn pages
Uses OpenAI API and gracefully degrades if not configured
"""
import logging
from typing import Dict, Any, Optional
import os

from linkedin_insights.utils.config import settings

logger = logging.getLogger(__name__)

# Try to import OpenAI, but don't fail if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. AI summary service will be disabled.")


class AISummaryService:
    """
    Service for generating AI-powered summaries of LinkedIn pages
    
    This service is optional and will gracefully degrade if:
    - OpenAI package is not installed
    - OPENAI_API_KEY is not set in environment
    """
    
    def __init__(self):
        self.enabled = self._check_availability()
        self.client = None
        
        if self.enabled:
            try:
                api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    logger.info("AI Summary Service initialized successfully")
                else:
                    self.enabled = False
                    logger.warning("OPENAI_API_KEY not set. AI Summary Service disabled.")
            except Exception as e:
                self.enabled = False
                logger.error(f"Failed to initialize AI Summary Service: {str(e)}")
    
    def _check_availability(self) -> bool:
        """Check if AI service is available"""
        if not OPENAI_AVAILABLE:
            return False
        
        api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
        return api_key is not None
    
    def generate_summary(self, page_stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate AI summary for LinkedIn page statistics
        
        Args:
            page_stats: Dictionary containing page statistics:
                - name: Page name
                - industry: Industry
                - total_followers: Number of followers
                - head_count: Company size
                - description: Page description
                - total_posts: Total number of posts
                - avg_likes: Average likes per post
                - avg_comments: Average comments per post
                - engagement_rate: Engagement rate (optional)
        
        Returns:
            Dictionary with summary or None if service is disabled
        """
        if not self.enabled or not self.client:
            logger.debug("AI Summary Service is disabled")
            return None
        
        try:
            # Prepare prompt
            prompt = self._build_prompt(page_stats)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst specializing in LinkedIn company page insights. "
                                  "Provide concise, professional summaries focusing on page type, audience, and engagement."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=getattr(settings, "OPENAI_MAX_TOKENS", 300),
                temperature=0.7
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            # Parse and structure the summary
            return {
                "summary": summary_text,
                "page_type": self._extract_page_type(summary_text),
                "audience": self._extract_audience(summary_text),
                "engagement": self._extract_engagement(summary_text),
                "generated_at": page_stats.get("generated_at")
            }
        
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}", exc_info=True)
            return None
    
    def _build_prompt(self, page_stats: Dict[str, Any]) -> str:
        """Build the prompt for OpenAI"""
        prompt_parts = [
            "Analyze the following LinkedIn company page statistics and provide a brief summary:",
            "",
            f"**Company Name:** {page_stats.get('name', 'Unknown')}",
        ]
        
        if page_stats.get('industry'):
            prompt_parts.append(f"**Industry:** {page_stats['industry']}")
        
        if page_stats.get('description'):
            prompt_parts.append(f"**Description:** {page_stats['description']}")
        
        if page_stats.get('total_followers') is not None:
            prompt_parts.append(f"**Total Followers:** {page_stats['total_followers']:,}")
        
        if page_stats.get('head_count') is not None:
            prompt_parts.append(f"**Company Size:** {page_stats['head_count']:,} employees")
        
        if page_stats.get('total_posts') is not None:
            prompt_parts.append(f"**Total Posts:** {page_stats['total_posts']}")
        
        if page_stats.get('avg_likes') is not None:
            prompt_parts.append(f"**Average Likes per Post:** {page_stats['avg_likes']:.1f}")
        
        if page_stats.get('avg_comments') is not None:
            prompt_parts.append(f"**Average Comments per Post:** {page_stats['avg_comments']:.1f}")
        
        if page_stats.get('engagement_rate') is not None:
            prompt_parts.append(f"**Engagement Rate:** {page_stats['engagement_rate']:.2f}%")
        
        prompt_parts.extend([
            "",
            "Please provide a concise summary (2-3 sentences) covering:",
            "1. Page type (e.g., enterprise, startup, agency)",
            "2. Audience characteristics (size, likely demographics)",
            "3. Engagement level and activity patterns"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_page_type(self, summary_text: str) -> Optional[str]:
        """Extract page type from summary (simple keyword matching)"""
        summary_lower = summary_text.lower()
        
        if any(word in summary_lower for word in ['enterprise', 'large', 'corporation', 'corporate']):
            return "Enterprise"
        elif any(word in summary_lower for word in ['startup', 'small', 'emerging']):
            return "Startup"
        elif any(word in summary_lower for word in ['agency', 'consulting', 'service']):
            return "Agency"
        elif any(word in summary_lower for word in ['non-profit', 'nonprofit', 'foundation']):
            return "Non-Profit"
        else:
            return "Business"
    
    def _extract_audience(self, summary_text: str) -> Optional[str]:
        """Extract audience description from summary"""
        # Simple extraction - in production, could use more sophisticated NLP
        if 'large audience' in summary_text.lower() or 'significant following' in summary_text.lower():
            return "Large"
        elif 'growing audience' in summary_text.lower() or 'moderate following' in summary_text.lower():
            return "Growing"
        elif 'niche' in summary_text.lower() or 'specialized' in summary_text.lower():
            return "Niche"
        else:
            return "Moderate"
    
    def _extract_engagement(self, summary_text: str) -> Optional[str]:
        """Extract engagement level from summary"""
        summary_lower = summary_text.lower()
        
        if any(word in summary_lower for word in ['high engagement', 'strong engagement', 'active engagement']):
            return "High"
        elif any(word in summary_lower for word in ['moderate engagement', 'decent engagement']):
            return "Moderate"
        elif any(word in summary_lower for word in ['low engagement', 'limited engagement']):
            return "Low"
        else:
            return "Moderate"
    
    def is_enabled(self) -> bool:
        """Check if AI summary service is enabled"""
        return self.enabled


def get_ai_summary_service() -> AISummaryService:
    """Factory function to get AI summary service instance"""
    return AISummaryService()

