"""
MCP Interceptor for VAP Honeypot
Intercepts tool calls using MCP and validates them against rules
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from rule_validator import RuleValidator, Violation, ValidationResult


class ToolCallInterceptor:
    """Intercepts and validates tool calls"""
    
    def __init__(self, validator: RuleValidator):
        """Initialize interceptor with rule validator"""
        self.validator = validator
        self.all_violations: List[Violation] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.callback: Optional[Callable] = None
    
    def register_callback(self, callback: Callable[[str, Dict[str, Any], List[Violation]], None]):
        """Register a callback to be called after each tool call validation"""
        self.callback = callback
    
    async def intercept_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intercept a tool call, validate it, and optionally block it
        
        Returns:
            Dict with 'allowed': bool, 'violations': List[Violation], 'result': Any
        """
        # Store the tool call
        self.tool_calls.append({
            'tool_name': tool_name,
            'tool_args': tool_args
        })
        
        # Validate against rules
        violations = self.validator.validate_tool_call(tool_name, tool_args)
        self.all_violations.extend(violations)
        
        # Call registered callback if available
        if self.callback:
            try:
                self.callback(tool_name, tool_args, violations)
            except Exception as e:
                print(f"Error in callback: {e}")
        
        # For now, allow all tool calls but track violations
        # In a real implementation, you might want to block certain calls
        return {
            'allowed': True,
            'violations': violations,
            'tool_name': tool_name,
            'tool_args': tool_args
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all intercepted tool calls and violations"""
        return {
            'total_tool_calls': len(self.tool_calls),
            'total_violations': len(self.all_violations),
            'violations': [
                {
                    'constraint_id': v.constraint_id,
                    'message': v.message,
                    'penalty': v.penalty,
                    'tool_name': v.tool_name
                }
                for v in self.all_violations
            ],
            'tool_calls': self.tool_calls
        }
    
    def reset(self):
        """Reset the interceptor state"""
        self.all_violations = []
        self.tool_calls = []


class MCPToolCallMonitor:
    """
    Monitor tool calls from an MCP client/server
    This is a wrapper that can be integrated with MCP SDK
    """
    
    def __init__(self, validator: RuleValidator):
        """Initialize monitor with validator"""
        self.validator = validator
        self.interceptor = ToolCallInterceptor(validator)
        self.is_monitoring = False
    
    def start_monitoring(self):
        """Start monitoring tool calls"""
        self.is_monitoring = True
        self.interceptor.reset()
        self.validator.reset()
    
    def stop_monitoring(self):
        """Stop monitoring tool calls"""
        self.is_monitoring = False
    
    async def handle_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an intercepted tool call
        
        This method should be called by your MCP middleware/handler
        """
        if not self.is_monitoring:
            return {'allowed': True, 'violations': []}
        
        return await self.interceptor.intercept_tool_call(tool_name, tool_args)
    
    def get_final_result(self) -> ValidationResult:
        """Get final validation result"""
        return self.validator.calculate_final_score(self.interceptor.all_violations)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring session"""
        summary = self.interceptor.get_summary()
        result = self.get_final_result()
        
        summary['validation_result'] = {
            'score': result.score,
            'security_score': result.security_score,
            'workflow_score': result.workflow_score,
            'pass_threshold': self.validator.pass_threshold,
            'passed': result.score >= self.validator.pass_threshold,
            'tool_sequence': result.tool_call_sequence
        }
        
        return summary


# Example usage function for testing
async def simulate_tool_calls(monitor: MCPToolCallMonitor, test_tool_calls: List[Dict[str, Any]]):
    """Simulate tool calls for testing purposes"""
    monitor.start_monitoring()
    
    for tool_call in test_tool_calls:
        tool_name = tool_call['tool_name']
        tool_args = tool_call.get('tool_args', {})
        await monitor.handle_tool_call(tool_name, tool_args)
    
    monitor.stop_monitoring()
    return monitor.get_summary()
