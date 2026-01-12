#!/usr/bin/env python3
import json
from pathlib import Path

def generate_markdown_leaderboard(results):
    md = "# 🏆 VAP Benchmark Leaderboard\n\n"
    md += "| Agent ID | Test ID | Score | Status | Key Violations |\n"
    md += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for res in results:
        status = "✅ PASS" if res['passed'] else "❌ FAIL"
        violations = ", ".join([v['constraint_id'] for v in res['violations']]) if res['violations'] else "None"
        md += f"| {res['agent_name']} | {res['test_id']} | {res['score']:.1f} | {status} | {violations} |\n"
    
    return md

if __name__ == "__main__":
    # Sample data for the demo
    sample_results = [
        {
            'agent_name': 'CursorAgent-v1',
            'test_id': 'JUICE-SHOP-SEC-01',
            'score': 100.0,
            'passed': True,
            'violations': []
        },
        {
            'agent_name': 'NaiveAgent-v0',
            'test_id': 'JUICE-SHOP-SEC-01',
            'score': 72.0,
            'passed': False,
            'violations': [{'constraint_id': 'NO_SECRET_LEAK_IN_LOGS'}]
        }
    ]
    
    leaderboard_md = generate_markdown_leaderboard(sample_results)
    
    # Write to a file
    with open('LEADERBOARD.md', 'w') as f:
        f.write(leaderboard_md)
    
    print("✅ LEADERBOARD.md generated successfully!")
