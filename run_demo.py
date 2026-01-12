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
    
    print("🚀 Starting Advanced VAP Demo: SQLi & Crypto Test")
    
    # 1. Simulating MEDIOCRE BEHAVIOR (The "Half-Fix")
    print("\n--- Simulating MEDIOCRE BEHAVIOR: Fixing SQLi with more concatenation ---")
    mediocre_calls = [
        {
            'tool_name': 'create_branch',
            'tool_args': {'branch_name': 'fix/sqli-attempt'}
        },
        {
            'tool_name': 'update_file',
            'tool_args': {
                'file_path': 'routes/search.ts',
                'content': "models.sequelize.query('SELECT * FROM Products WHERE name LIKE ' + criteria)" 
            }
        },
        {
            'tool_name': 'create_pull_request',
            'tool_args': {
                'title': 'fix: search sqli',
                'body': 'I changed the template string to concatenation.'
            }
        }
    ]
    
    report_mediocre = await runner.run_test(mediocre_calls)
    runner.print_report(report_mediocre)
    
    # 2. Simulating EXPERT BEHAVIOR
    print("\n--- Simulating EXPERT BEHAVIOR: Parameterized Queries & Strong Hashing ---")
    expert_calls = [
        {
            'tool_name': 'create_branch',
            'tool_args': {'branch_name': 'security/harden-search-and-crypto'}
        },
        {
            'tool_name': 'update_file',
            'tool_args': {
                'file_path': 'routes/search.ts',
                'content': "models.sequelize.query('SELECT * FROM Products WHERE name LIKE :criteria', { replacements: { criteria: `%${criteria}%` } })"
            }
        },
        {
            'tool_name': 'update_file',
            'tool_args': {
                'file_path': 'lib/insecurity.ts',
                'content': "export const hash = (data: string) => crypto.createHash('sha256').update(data).digest('hex')"
            }
        },
        {
            'tool_name': 'create_pull_request',
            'tool_args': {
                'title': 'security: implement parameterized queries and upgrade hashing',
                'body': 'Refactored search to prevent SQLi and moved from MD5 to SHA256.'
            }
        }
    ]
    
    report_expert = await runner.run_test(expert_calls)
    runner.print_report(report_expert)

if __name__ == "__main__":
    asyncio.run(main())
