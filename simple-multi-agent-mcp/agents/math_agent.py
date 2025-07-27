"""
Math Agent - Specialized agent for mathematical calculations and problem solving
"""
import re
from typing import Dict, Any
from .base_agent import BaseAgent


class MathAgent(BaseAgent):
    """
    Agent specialized in mathematical calculations and problem solving
    Can handle arithmetic, algebra, and basic mathematical analysis
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        super().__init__(
            agent_name="MathAgent",
            description="Specialized in mathematical calculations, equation solving, and numerical analysis",
            mcp_server_url=mcp_server_url
        )
        
        # Keywords that indicate this agent should handle the message
        self.math_keywords = [
            'calculate', 'compute', 'solve', 'equation', 'math', 'mathematics',
            'add', 'subtract', 'multiply', 'divide', 'sum', 'difference',
            'product', 'quotient', 'square', 'root', 'power', 'algebra',
            'number', 'numbers', '+', '-', '*', '/', '=', 'x', 'y'
        ]
    
    def can_handle(self, message: str) -> bool:
        """
        Determine if this message contains mathematical content
        """
        message_lower = message.lower()
        
        # Check for math keywords
        has_math_keywords = any(keyword in message_lower for keyword in self.math_keywords)
        
        # Check for numbers and mathematical operators
        has_numbers = bool(re.search(r'\d+', message))
        has_operators = bool(re.search(r'[+\-*/=]', message))
        
        # Check for equation patterns
        has_equation = bool(re.search(r'\w*[xyz]\w*\s*[+\-*/]?\s*\d*\s*=', message))
        
        # Exclude text analysis requests even if they contain numbers
        text_exclusions = ['sentiment', 'analyze', 'count words', 'text analysis', 'extract numbers']
        has_text_exclusions = any(exclusion in message_lower for exclusion in text_exclusions)
        
        # Strong math indicators should override text exclusions
        strong_math = has_equation or 'solve' in message_lower or any(op in message for op in ['=', 'calculate', 'sum of'])
        
        if strong_math:
            return True
        elif has_text_exclusions:
            return False
        else:
            return has_math_keywords or (has_numbers and has_operators)
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process mathematical queries and calculations
        """
        self.add_to_history("user", message)
        
        try:
            # Detect the type of mathematical operation needed
            message_lower = message.lower()
            
            # Handle equation solving
            if any(word in message_lower for word in ['solve', 'equation']) and '=' in message:
                result = await self._solve_equation(message)
                response = self._format_equation_response(result)
            
            # Handle basic arithmetic
            elif any(op in message for op in ['+', '-', '*', '/']):
                result = await self._handle_arithmetic(message)
                response = self._format_arithmetic_response(result)
            
            # Handle specific mathematical functions
            elif 'square root' in message_lower or 'sqrt' in message_lower:
                result = await self._handle_sqrt(message)
                response = self._format_function_response(result, "square root")
            
            elif 'power' in message_lower or '^' in message or '**' in message:
                result = await self._handle_power(message)
                response = self._format_function_response(result, "power")
            
            # General mathematical calculation
            else:
                result = await self._handle_general_math(message)
                response = self._format_general_response(result)
            
            self.add_to_history("assistant", response["content"], {"calculation_result": result})
            return response
            
        except Exception as e:
            error_response = {
                "agent": self.agent_name,
                "content": f"I encountered an error while processing your mathematical request: {str(e)}",
                "success": False,
                "error": str(e)
            }
            self.add_to_history("assistant", error_response["content"], {"error": str(e)})
            return error_response
    
    async def _solve_equation(self, message: str) -> Dict[str, Any]:
        """Extract and solve equations from the message"""
        # Extract equation from message - look for various patterns
        equation_patterns = [
            r'equation\s*:?\s*([^.!?]*[=][^.!?]*)',  # "equation: 2x + 5 = 15"
            r'solve\s*:?\s*([^.!?]*[=][^.!?]*)',     # "solve: 2x + 5 = 15"
            r'([^.!?]*\w+[xyz]\w*[^.!?]*[=][^.!?]*)', # any line with x/y/z and =
        ]
        
        equation = None
        for pattern in equation_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                equation = match.group(1).strip()
                break
        
        if not equation:
            # Try to find any equation in the message
            eq_match = re.search(r'([^.!?]*[=][^.!?]*)', message)
            if eq_match:
                equation = eq_match.group(1).strip()
        
        if equation:
            result = await self.call_mcp_tool("calculator", "solve_linear_equation", {"equation": equation})
            return result
        else:
            return {"success": False, "error": "Could not extract equation from message"}
    
    async def _handle_arithmetic(self, message: str) -> Dict[str, Any]:
        """Handle basic arithmetic operations"""
        # Extract numbers from the message
        numbers = re.findall(r'-?\d+\.?\d*', message)
        if len(numbers) < 2:
            return {"success": False, "error": "Need at least two numbers for arithmetic"}
        
        a, b = float(numbers[0]), float(numbers[1])
        
        # Determine operation
        if '+' in message or 'add' in message.lower() or 'sum' in message.lower():
            result = await self.call_mcp_tool("calculator", "add", {"a": a, "b": b})
        elif '-' in message or 'subtract' in message.lower() or 'difference' in message.lower():
            result = await self.call_mcp_tool("calculator", "subtract", {"a": a, "b": b})
        elif '*' in message or 'multiply' in message.lower() or 'product' in message.lower():
            result = await self.call_mcp_tool("calculator", "multiply", {"a": a, "b": b})
        elif '/' in message or 'divide' in message.lower() or 'quotient' in message.lower():
            result = await self.call_mcp_tool("calculator", "divide", {"a": a, "b": b})
        else:
            # Default to addition if operation is unclear
            result = await self.call_mcp_tool("calculator", "add", {"a": a, "b": b})
        
        return result
    
    async def _handle_sqrt(self, message: str) -> Dict[str, Any]:
        """Handle square root calculations"""
        numbers = re.findall(r'\d+\.?\d*', message)
        if numbers:
            x = float(numbers[0])
            result = await self.call_mcp_tool("calculator", "sqrt", {"x": x})
            return result
        else:
            return {"success": False, "error": "Could not find number for square root"}
    
    async def _handle_power(self, message: str) -> Dict[str, Any]:
        """Handle power calculations"""
        numbers = re.findall(r'\d+\.?\d*', message)
        if len(numbers) >= 2:
            base, exponent = float(numbers[0]), float(numbers[1])
            result = await self.call_mcp_tool("calculator", "power", {"base": base, "exponent": exponent})
            return result
        else:
            return {"success": False, "error": "Need base and exponent for power calculation"}
    
    async def _handle_general_math(self, message: str) -> Dict[str, Any]:
        """Handle general mathematical queries"""
        # Extract all numbers and try to determine what to do
        numbers = re.findall(r'-?\d+\.?\d*', message)
        
        if not numbers:
            return {"success": False, "error": "No numbers found in the message"}
        
        # If multiple numbers, try to add them
        if len(numbers) > 1:
            total = sum(float(num) for num in numbers)
            return {"success": True, "result": total, "operation": "sum", "numbers": numbers}
        else:
            # Single number - provide basic info
            num = float(numbers[0])
            return {
                "success": True, 
                "result": num, 
                "operation": "analysis",
                "info": {
                    "value": num,
                    "square": num * num,
                    "absolute": abs(num)
                }
            }
    
    def _format_equation_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format equation solving response"""
        if result.get("success"):
            solution_data = result.get("result", {})
            if "solution" in solution_data:
                content = f"I solved the equation! Here's the solution:\n\n"
                content += f"**Equation:** {solution_data.get('equation', 'N/A')}\n"
                content += f"**Solution:** x = {solution_data['solution']}\n\n"
                content += "**Steps:**\n"
                for step in solution_data.get('steps', []):
                    content += f"• {step}\n"
            else:
                content = f"I had trouble solving that equation: {solution_data.get('error', 'Unknown error')}"
        else:
            content = f"I couldn't solve the equation: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_arithmetic_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format arithmetic operation response"""
        if result.get("success"):
            content = f"The calculation result is: **{result['result']}**"
        else:
            content = f"I couldn't perform the calculation: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_function_response(self, result: Dict[str, Any], function_name: str) -> Dict[str, Any]:
        """Format mathematical function response"""
        if result.get("success"):
            content = f"The {function_name} calculation result is: **{result['result']}**"
        else:
            content = f"I couldn't calculate the {function_name}: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
    
    def _format_general_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format general mathematical response"""
        if result.get("success"):
            if result.get("operation") == "sum":
                content = f"The sum of the numbers {result.get('numbers', [])} is: **{result['result']}**"
            elif result.get("operation") == "analysis":
                info = result.get("info", {})
                content = f"Mathematical analysis of {info.get('value')}:\n"
                content += f"• Value: {info.get('value')}\n"
                content += f"• Square: {info.get('square')}\n"
                content += f"• Absolute value: {info.get('absolute')}"
            else:
                content = f"Mathematical result: **{result['result']}**"
        else:
            content = f"I couldn't process the mathematical request: {result.get('error', 'Unknown error')}"
        
        return {
            "agent": self.agent_name,
            "content": content,
            "success": result.get("success", False),
            "result": result
        }
