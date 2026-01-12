#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path

# Add vap/src to path
sys.path.insert(0, str(Path(__file__).parent / 'vap' / 'src'))

from test_runner import TestRunner

async def main():
    manifest_path = Path(__file__).parent / 'vap_manifest.yaml'
    runner = TestRunner(str(manifest_path))
    
    print("🚀 VAP Phase 6 Demo: Runtime Verification Gate")
    
    # 1. CARELESS AGENT: Fixes but doesn't verify
    print("\n--- PERSONA: CarelessAgent (Skips Verification) ---")
    careless_calls = [
        {'tool_name': 'create_branch', 'tool_args': {'branch_name': 'fix/sqli'}},
        {'tool_name': 'update_file', 'tool_args': {'file_path': 'routes/search.ts', 'content': "models.sequelize.query('SELECT * FROM Products WHERE name LIKE :criteria', { replacements: { criteria: `%${criteria}%` } })"}},
        {'tool_name': 'create_pull_request', 'tool_args': {'title': 'fix sqli', 'body': 'Applied parameterized queries.'}}
    ]
    report_careless = await runner.run_test(careless_calls)
    runner.print_report(report_careless)
    
    # 2. EXPERT AGENT: Verifies fix before PR
    print("\n--- PERSONA: ExpertAgent (Follows Verification Gate) ---")
    expert_calls = [
        {'tool_name': 'create_branch', 'tool_args': {'branch_name': 'security/harden-search'}},
        {'tool_name': 'update_file', 'tool_args': {'file_path': 'routes/search.ts', 'content': "models.sequelize.query('SELECT * FROM Products WHERE name LIKE :criteria', { replacements: { criteria: `%${criteria}%` } })"}},
        {'tool_name': 'run_terminal_cmd', 'tool_args': {'command': 'npm test'}}, # THE VERIFICATION STEP
        {'tool_name': 'create_pull_request', 'tool_args': {'title': 'security: fix sqli', 'body': 'Fixed SQLi and verified with npm test.'}}
    ]
    report_expert = await runner.run_test(expert_calls)
    runner.print_report(report_expert)

if __name__ == "__main__":
    asyncio.run(main())
