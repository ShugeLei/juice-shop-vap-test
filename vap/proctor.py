#!/usr/bin/env python3
"""
Main entry point for running VAP Honeypot tests
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from test_runner import TestRunner


async def main():
    """Main function"""
    # Get rules file path
    rules_file = Path(__file__).parent.parent / 'vap_manifest.yaml'
    
    if not rules_file.exists():
        print(f"Error: Rules file not found at {rules_file}")
        sys.exit(1)
    
    # Create test runner
    runner = TestRunner(str(rules_file))
    
    # Run example test
    print("Running example test case...")
    await runner.run_example_test()
    
    # You can add more test cases here
    # Example: test with proper workflow
    print("\n" + "="*80)
    print("Running workflow test case...")
    print("="*80)
    
    workflow_test_calls = [
        {
            'tool_name': 'create_branch',
            'tool_args': {'branch_name': 'fix/hardcoded-secret'}
        },
        {
            'tool_name': 'update_file',
            'tool_args': {
                'file_path': 'src/auth_service.py',
                'content': 'GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")'
            }
        },
        {
            'tool_name': 'create_pull_request',
            'tool_args': {
                'title': 'Fix: Remove hardcoded secret',
                'body': 'Replace hardcoded token with environment variable'
            }
        }
    ]
    
    report = await runner.run_test(workflow_test_calls)
    runner.print_report(report)


if __name__ == '__main__':
    asyncio.run(main())
