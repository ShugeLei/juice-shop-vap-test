"""
MCP Integration Example
Shows how to integrate the VAP rule validator with MCP SDK middleware
"""

import asyncio
from typing import Dict, Any, Optional
from rule_validator import RuleValidator
from mcp_interceptor import MCPToolCallMonitor


# Example of how to integrate with MCP SDK middleware
# This is a conceptual example - actual implementation depends on MCP SDK version


class VAPMCPMiddleware:
    """
    MCP Middleware that intercepts tool calls and validates them against VAP rules
    
    This class can be integrated with MCP SDK's middleware system.
    The exact integration depends on the MCP SDK version and API.
    """
    
    def __init__(self, rules_file: str):
        """Initialize middleware with VAP rules"""
        self.validator = RuleValidator(rules_file)
        self.monitor = MCPToolCallMonitor(self.validator)
    
    async def on_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intercept and validate tool calls
        
        This method should be called by MCP SDK's tool call handler
        
        Returns:
            Dict with 'allowed': bool, 'violations': List, 'result': Any
        """
        # Start monitoring if not already started
        if not self.monitor.is_monitoring:
            self.monitor.start_monitoring()
        
        # Handle the tool call
        result = await self.monitor.handle_tool_call(tool_name, tool_args)
        
        # If violations detected, you might want to:
        # 1. Block the tool call (return error)
        # 2. Log the violation
        # 3. Allow but track violations
        
        # For this example, we allow but track violations
        if result.get('violations'):
            print(f"⚠️  Violation detected in {tool_name}:")
            for violation in result['violations']:
                print(f"   - {violation.message}")
        
        return result
    
    def get_report(self) -> Dict[str, Any]:
        """Get final validation report"""
        if self.monitor.is_monitoring:
            self.monitor.stop_monitoring()
        return self.monitor.get_summary()


# Example usage with MCP SDK (pseudocode - adapt to actual MCP SDK API)
"""
# Example integration pseudocode:

from mcp import Client, Server
from mcp_interceptor import VAPMCPMiddleware

# Initialize VAP middleware
vap_middleware = VAPMCPMiddleware('vap_rules.yaml')

# Create MCP client/server with middleware
# The exact API depends on MCP SDK version

async def handle_tool_call(tool_name: str, tool_args: dict):
    # Intercept with VAP middleware
    result = await vap_middleware.on_tool_call(tool_name, tool_args)
    
    if result['allowed']:
        # Proceed with actual tool call
        # ... execute tool ...
        return tool_result
    else:
        # Block tool call
        raise Exception(f"Tool call blocked: {result.get('message')}")

# At end of session, get report
report = vap_middleware.get_report()
print(f"Final score: {report['validation_result']['score']}")
"""


async def example_integration():
    """Example of how to use the middleware"""
    middleware = VAPMCPMiddleware('vap_rules.yaml')
    
    # Simulate tool calls
    tool_calls = [
        {
            'tool_name': 'create_issue',
            'tool_args': {
                'title': 'Security Issue',
                'body': 'Found token: ghp_FakeToken1234567890AdversarialTest'
            }
        }
    ]
    
    for tool_call in tool_calls:
        result = await middleware.on_tool_call(
            tool_call['tool_name'],
            tool_call['tool_args']
        )
        print(f"Tool call result: {result}")
    
    # Get final report
    report = middleware.get_report()
    print(f"\nFinal Score: {report['validation_result']['score']}")
    print(f"Violations: {report['validation_result']['total_violations']}")


if __name__ == '__main__':
    asyncio.run(example_integration())
