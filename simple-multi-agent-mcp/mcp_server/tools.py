"""
MCP Server Tools - Available tools for agents to use
"""
import math
import re
from typing import Dict, Any, List
from datetime import datetime


class CalculatorTool:
    """Mathematical calculation tool"""
    
    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers"""
        return a + b
    
    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract b from a"""
        return a - b
    
    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers"""
        return a * b
    
    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide a by b"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    @staticmethod
    def power(base: float, exponent: float) -> float:
        """Raise base to the power of exponent"""
        return math.pow(base, exponent)
    
    @staticmethod
    def sqrt(x: float) -> float:
        """Calculate square root"""
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(x)
    
    @staticmethod
    def solve_linear_equation(equation: str) -> Dict[str, Any]:
        """
        Solve simple linear equations like '2x + 5 = 15'
        Returns the solution and steps
        """
        try:
            # Parse equation like "2x + 5 = 15"
            left, right = equation.replace(" ", "").split("=")
            right_val = float(right)
            
            # Extract coefficient and constant from left side
            # Pattern: ax + b or ax - b
            pattern = r'([+-]?\d*\.?\d*)x([+-]\d*\.?\d*)?'
            match = re.match(pattern, left)
            
            if not match:
                return {"error": "Could not parse equation format"}
            
            coeff_str = match.group(1)
            const_str = match.group(2)
            
            # Handle coefficient
            if coeff_str == '' or coeff_str == '+':
                coefficient = 1
            elif coeff_str == '-':
                coefficient = -1
            else:
                coefficient = float(coeff_str)
            
            # Handle constant
            constant = float(const_str) if const_str else 0
            
            # Solve: coefficient * x + constant = right_val
            # x = (right_val - constant) / coefficient
            if coefficient == 0:
                return {"error": "No variable term found"}
            
            x = (right_val - constant) / coefficient
            
            return {
                "equation": equation,
                "solution": x,
                "steps": [
                    f"Original equation: {equation}",
                    f"Isolate x: {coefficient}x = {right_val} - ({constant})",
                    f"Simplify: {coefficient}x = {right_val - constant}",
                    f"Divide by {coefficient}: x = {x}"
                ]
            }
        except Exception as e:
            return {"error": f"Error solving equation: {str(e)}"}


class TextTool:
    """Text processing and analysis tool"""
    
    @staticmethod
    def word_count(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def character_count(text: str) -> int:
        """Count characters in text"""
        return len(text)
    
    @staticmethod
    def sentiment_analysis(text: str) -> Dict[str, Any]:
        """
        Simple sentiment analysis based on positive/negative words
        """
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'awesome',
            'brilliant', 'perfect', 'beautiful', 'nice', 'best', 'superb'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'sad', 'angry', 'upset', 'disappointed', 'frustrated', 'annoyed',
            'worst', 'ugly', 'boring', 'stupid', 'ridiculous', 'pathetic'
        ]
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = positive_count / (positive_count + negative_count + 1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = negative_count / (positive_count + negative_count + 1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "text": text,
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "positive_words_found": positive_count,
            "negative_words_found": negative_count,
            "total_words": len(words)
        }
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from text"""
        pattern = r'-?\d+\.?\d*'
        numbers = re.findall(pattern, text)
        return [float(num) for num in numbers if num]
    
    @staticmethod
    def summarize(text: str, max_sentences: int = 3) -> str:
        """
        Simple text summarization by taking first few sentences
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        summary_sentences = sentences[:max_sentences]
        return '. '.join(summary_sentences) + '.'


class UtilityTool:
    """General utility functions"""
    
    @staticmethod
    def get_current_time() -> str:
        """Get current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_json(data: Dict[str, Any]) -> str:
        """Format dictionary as JSON string"""
        import json
        return json.dumps(data, indent=2)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Registry of available tools
AVAILABLE_TOOLS = {
    "calculator": CalculatorTool(),
    "text": TextTool(),
    "utility": UtilityTool()
}


def get_tool(tool_name: str):
    """Get tool instance by name"""
    return AVAILABLE_TOOLS.get(tool_name)


def get_all_tools() -> Dict[str, Any]:
    """Get all available tools"""
    return AVAILABLE_TOOLS
