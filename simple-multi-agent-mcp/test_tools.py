"""
Test script for MCP tools and agent functionality
"""
import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.tools import get_all_tools


def test_calculator_tool():
    """Test calculator tool functionality"""
    print("CALC: Testing Calculator Tool:")
    
    calc = get_all_tools()["calculator"]
    
    # Test basic operations
    print(f"  Addition: 15 + 27 = {calc.add(15, 27)}")
    print(f"  Subtraction: 27 - 15 = {calc.subtract(27, 15)}")
    print(f"  Multiplication: 6 * 7 = {calc.multiply(6, 7)}")
    print(f"  Division: 20 / 4 = {calc.divide(20, 4)}")
    print(f"  Square root: sqrt(144) = {calc.sqrt(144)}")
    print(f"  Power: 2^8 = {calc.power(2, 8)}")
    
    # Test equation solving
    equation_result = calc.solve_linear_equation("2x + 5 = 15")
    if equation_result.get("solution"):
        print(f"  Equation: 2x + 5 = 15, x = {equation_result['solution']}")
    else:
        print(f"  Equation solving: {equation_result}")
    
    print("OK: Calculator tests completed\n")


def test_text_tool():
    """Test text processing tool functionality"""
    print("TEXT: Testing Text Tool:")
    
    text_tool = get_all_tools()["text"]
    
    test_text = "I love sunny days and beautiful weather! This is amazing."
    
    # Test word count
    word_count = text_tool.word_count(test_text)
    print(f"  Word count: {word_count}")
    
    # Test character count
    char_count = text_tool.character_count(test_text)
    print(f"  Character count: {char_count}")
    
    # Test sentiment analysis
    sentiment = text_tool.sentiment_analysis(test_text)
    print(f"  Sentiment: {sentiment['sentiment']} ({sentiment['confidence']:.0%} confidence)")
    
    # Test number extraction
    number_text = "I have 5 apples, 3 oranges, and 12 bananas"
    numbers = text_tool.extract_numbers(number_text)
    print(f"  Numbers in '{number_text}': {numbers}")
    
    # Test summarization
    long_text = "This is a longer text. It has multiple sentences. We will test summarization on it."
    summary = text_tool.summarize(long_text, 2)
    print(f"  Summary: {summary}")
    
    print("OK: Text tool tests completed\n")


def test_utility_tool():
    """Test utility tool functionality"""
    print("UTIL: Testing Utility Tool:")
    
    util_tool = get_all_tools()["utility"]
    
    # Test time
    current_time = util_tool.get_current_time()
    print(f"  Current time: {current_time}")
    
    # Test email validation
    test_emails = ["user@example.com", "invalid-email", "test@domain.org"]
    for email in test_emails:
        is_valid = util_tool.validate_email(email)
        print(f"  Email '{email}': {'VALID' if is_valid else 'INVALID'}")
    
    # Test JSON formatting
    test_data = {"name": "Test", "value": 42, "active": True}
    formatted_json = util_tool.format_json(test_data)
    print(f"  JSON formatting: {formatted_json}")
    
    print("OK: Utility tool tests completed\n")


async def test_agent_can_handle():
    """Test agent message handling detection"""
    print("AGENT: Testing Agent Message Handling:")
    
    # Import agents (don't initialize to avoid MCP server dependency)
    from agents.math_agent import MathAgent
    from agents.text_agent import TextAgent
    from agents.task_agent import TaskAgent
    
    # Create agents (without MCP server for testing)
    math_agent = MathAgent("http://localhost:8000")
    text_agent = TextAgent("http://localhost:8000")
    task_agent = TaskAgent("http://localhost:8000")
    
    test_messages = [
        ("Calculate 15 + 27", "math"),
        ("Solve equation 2x + 5 = 15", "math"),
        ("Analyze sentiment of this text", "text"),
        ("Count words in this sentence", "text"), 
        ("Help me plan a task", "task"),
        ("Can you coordinate this workflow", "task"),
        ("What's the weather like?", "general")
    ]
    
    for message, expected_type in test_messages:
        print(f"  Message: '{message}'")
        print(f"    Math Agent: {'YES' if math_agent.can_handle(message) else 'NO'}")
        print(f"    Text Agent: {'YES' if text_agent.can_handle(message) else 'NO'}")
        print(f"    Task Agent: {'YES' if task_agent.can_handle(message) else 'NO'}")
        print()
    
    print("OK: Agent handling tests completed\n")


def main():
    """Run all tests"""
    print("TEST: Simple Multi-Agent System - Tool Tests")
    print("=" * 50)
    print()
    
    try:
        # Test MCP tools
        test_calculator_tool()
        test_text_tool()
        test_utility_tool()
        
        # Test agent message handling
        asyncio.run(test_agent_can_handle())
        
        print("SUCCESS: All tests completed successfully!")
        print("\nNext steps:")
        print("  - Run 'python demo.py' for automated demo")
        print("  - Run 'python main.py' for interactive mode")
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Test failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
