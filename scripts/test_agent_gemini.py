"""
Full agent Gemini loop test with gemini-3.6-flash.
Uses the real GeminiAgent (not a stub) against mock MCP fixtures.
"""
import os
os.environ["TG_MOCK_MODE"] = "true"
from dotenv import load_dotenv
load_dotenv()

from agent.investigator import GeminiAgent

model = "gemini-3.5-flash"
key = os.getenv("GEMINI_API_KEY", "")

print(f"Testing full agent loop with: {model}\n")
agent = GeminiAgent(api_key=key, model_name=model)
report = agent.investigate("3514030")

print(f"Engine          : {report.engine}")
print(f"Verdict         : {report.verdict}")
print(f"Fraud prob      : {report.fraud_probability}")
print(f"Tools called    : {report.tools_called}")
print(f"Evidence items  : {len(report.evidence)}")
print(f"Risk signals    : {len(report.risk_signals)}")
print(f"Next best action: {report.next_best_actions[0].action if report.next_best_actions else 'none'}")
print(f"Approval route  : {report.approval_route}")
print(f"Warnings        : {report.warnings}")
print(f"\nSummary: {report.summary[:200]}")
