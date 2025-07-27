"""
Text Agent - Specialized agent for text processing and analysis
"""
import re
from typing import Dict, Any
from .base_agent import BaseAgent


class TextAgent(BaseAgent):
    """
    Agent specialized in text processing, analysis, and manipulation
    Can handle sentiment analysis, text statistics, and content processing
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        super().__init__(
            agent_name="TextAgent",
            description="Specialized in text processing, sentiment analysis, and content manipulation",
            mcp_server_url=mcp_server_url
        )
        
        # Keywords that indicate this agent should handle the message
        self.text_keywords = [
            'analyze', 'sentiment', 'text', 'words', 'characters', 'count',
            'summarize', 'summary', 'extract', 'process', 'content',
            'emotion', 'feeling', 'positive', 'negative', 'neutral',
            'reading', 'writing', 'language', 'string', 'paragraph'
        ]
    
    def can_handle(self, message: str) -> bool:
        """
        Determine if this message requires text processing
        """
        message_lower = message.lower()
        
        # Check for text processing keywords
        has_text_keywords = any(keyword in message_lower for keyword in self.text_keywords)
        
        # Check for text analysis patterns
        has_analysis_request = any(phrase in message_lower for phrase in [
            'what is the sentiment', 'how many words', 'analyze this text',
            'sentiment of', 'word count', 'character count', 'summarize'
        ])
        
        # Check if message is asking for text processing on quoted content
        has_quoted_text = bool(re.search(r'["\'].*["\']', message))
        
        return has_text_keywords or has_analysis_request or has_quoted_text
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process text analysis and manipulation requests
        """
        self.add_to_history("user", message)
        
        try:
            message_lower = message.lower()
            
            # Extract text to analyze (look for quoted text first)
            target_text = self._extract_target_text(message)
            
            # Handle sentiment analysis
            if any(word in message_lower for word in ['sentiment', 'emotion', 'feeling', 'positive', 'negative']):
                result = await self._analyze_sentiment(target_text)
                response = self._format_sentiment_response(result, target_text)
            
            # Handle word/character counting
            elif any(word in message_lower for word in ['count', 'words', 'characters', 'length']):
                result = await self._count_text_stats(target_text)
                response = self._format_stats_response(result, target_text)
            
            # Handle text summarization
            elif any(word in message_lower for word in ['summarize', 'summary']):
                result = await self._summarize_text(target_text)
                response = self._format_summary_response(result, target_text)
            
            # Handle number extraction
            elif any(word in message_lower for word in ['extract', 'numbers', 'find numbers']):
                result = await self._extract_numbers(target_text)
                response = self._format_extraction_response(result, target_text)
            
            # General text analysis
            else:
                result = await self._analyze_text_general(target_text)
                response = self._format_general_response(result, target_text)
            
            self.add_to_history("assistant", response["content"], {"analysis_result": result})
            return response
            
        except Exception as e:
            error_response = {
                "agent": self.agent_name,
                "content": f"I encountered an error while processing your text request: {str(e)}",
                "success": False,
                "error": str(e)
            }
            self.add_to_history("assistant", error_response["content"], {"error": str(e)})
            return error_response
    
    def _extract_target_text(self, message: str) -> str:
        """
        Extract the text to be analyzed from the message
        Looks for quoted text first, then uses the whole message
        """
        # Look for text in quotes
        quoted_match = re.search(r'["\']([^"\']*)["\']', message)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for text after common phrases
        after_phrases = [
            r'analyze\s+(?:this\s+)?text\s*:?\s*(.+)',
            r'sentiment\s+of\s*:?\s*(.+)',
            r'process\s+(?:this\s+)?text\s*:?\s*(.+)',
            r'text\s*:?\s*(.+)'
        ]
        
        for pattern in after_phrases:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no specific text found, use the whole message for analysis
        return message
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        result = await self.call_mcp_tool("text", "sentiment_analysis", {"text": text})
        return result
    
    async def _count_text_stats(self, text: str) -> Dict[str, Any]:
        """Count words and characters in text"""
        word_count_result = await self.call_mcp_tool("text", "word_count", {"text": text})
        char_count_result = await self.call_mcp_tool("text", "character_count", {"text": text})
        
        return {
            "success": True,
            "word_count": word_count_result.get("result", 0) if word_count_result.get("success") else 0,
            "character_count": char_count_result.get("result", 0) if char_count_result.get("success") else 0,
            "text": text
        }
    
    async def _summarize_text(self, text: str) -> Dict[str, Any]:
        """Summarize the text"""
        result = await self.call_mcp_tool("text", "summarize", {"text": text, "max_sentences": 3})
        return result
    
    async def _extract_numbers(self, text: str) -> Dict[str, Any]:
        """Extract numbers from text"""
        result = await self.call_mcp_tool("text", "extract_numbers", {"text": text})
        return result
    
    async def _analyze_text_general(self, text: str) -> Dict[str, Any]:
        """Perform general text analysis"""
        # Get multiple analysis results
        sentiment_result = await self._analyze_sentiment(text)
        stats_result = await self._count_text_stats(text)
        numbers_result = await self._extract_numbers(text)
        
        return {
            "success": True,
            "sentiment": sentiment_result.get("result") if sentiment_result.get("success") else None,
            "stats": {
                "word_count": stats_result.get("word_count", 0),
                "character_count": stats_result.get("character_count", 0)
            },
            "numbers": numbers_result.get("result", []) if numbers_result.get("success") else [],
            "text": text
        }
    
    def _format_sentiment_response(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Format sentiment analysis response"""
        if result.get("success"):
            sentiment_data = result.get("result", {})
            sentiment = sentiment_data.get("sentiment", "unknown")
            confidence = sentiment_data.get("confidence", 0)
            positive_words = sentiment_data.get("positive_words_found", 0)
            negative_words = sentiment_data.get("negative_words_found", 0)
            
            content = f"**Sentiment Analysis Results:**\n\n"
            content += f"**Text analyzed:** \"{original_text[:100]}{'...' if len(original_text) > 100 else ''}\"\n\n"
            content += f"**Sentiment:** {sentiment.title()}\n"
            content += f"**Confidence:** {confidence:.0%}\n"
            content += f"**Positive indicators:** {positive_words}\n"
            content += f"**Negative indicators:** {negative_words}\n"
            
            if sentiment == "positive":
                content += "\n😊 The text expresses positive emotions or attitudes."
            elif sentiment == "negative":
                content += "\n😔 The text expresses negative emotions or attitudes."
            else:
                content += "\n😐 The text appears to be neutral in sentiment."
        else:
            content = f"I couldn't analyze the sentiment: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_stats_response(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Format text statistics response"""
        if result.get("success"):
            word_count = result.get("word_count", 0)
            char_count = result.get("character_count", 0)
            
            content = f"**Text Statistics:**\n\n"
            content += f"**Text analyzed:** \"{original_text[:100]}{'...' if len(original_text) > 100 else ''}\"\n\n"
            content += f"**Word count:** {word_count}\n"
            content += f"**Character count:** {char_count}\n"
            content += f"**Average word length:** {char_count / word_count:.1f} characters per word\n" if word_count > 0 else ""
        else:
            content = f"I couldn't count the text statistics: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_summary_response(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Format text summary response"""
        if result.get("success"):
            summary = result.get("result", "")
            
            content = f"**Text Summary:**\n\n"
            content += f"**Original text:** \"{original_text[:150]}{'...' if len(original_text) > 150 else ''}\"\n\n"
            content += f"**Summary:** {summary}"
        else:
            content = f"I couldn't summarize the text: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_extraction_response(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Format number extraction response"""
        if result.get("success"):
            numbers = result.get("result", [])
            
            content = f"**Number Extraction:**\n\n"
            content += f"**Text analyzed:** \"{original_text[:100]}{'...' if len(original_text) > 100 else ''}\"\n\n"
            
            if numbers:
                content += f"**Numbers found:** {', '.join(map(str, numbers))}\n"
                content += f"**Count:** {len(numbers)} numbers\n"
                if len(numbers) > 1:
                    content += f"**Sum:** {sum(numbers)}\n"
                    content += f"**Average:** {sum(numbers) / len(numbers):.2f}"
            else:
                content += "**No numbers found in the text.**"
        else:
            content = f"I couldn't extract numbers: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_general_response(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Format general text analysis response"""
        if result.get("success"):
            sentiment = result.get("sentiment", {})
            stats = result.get("stats", {})
            numbers = result.get("numbers", [])
            
            content = f"**Complete Text Analysis:**\n\n"
            content += f"**Text:** \"{original_text[:100]}{'...' if len(original_text) > 100 else ''}\"\n\n"
            
            # Sentiment section
            if sentiment:
                content += f"**Sentiment:** {sentiment.get('sentiment', 'unknown').title()} "
                content += f"({sentiment.get('confidence', 0):.0%} confidence)\n"
            
            # Statistics section
            content += f"**Statistics:** {stats.get('word_count', 0)} words, "
            content += f"{stats.get('character_count', 0)} characters\n"
            
            # Numbers section
            if numbers:
                content += f"**Numbers found:** {', '.join(map(str, numbers))}"
            else:
                content += f"**Numbers found:** None"
        else:
            content = f"I couldn't analyze the text: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
