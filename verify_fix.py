
import sys
import os

# Ensure we can import utils
sys.path.append(os.getcwd())

from utils import generate_menu_candidates

print("--- Verification Test ---")
ingredients = ["고등어", "무"]
requirements = ["매운거 싫어함"]

print(f"Requesting menu for: {ingredients}, reqs: {requirements}")
candidates = generate_menu_candidates(ingredients, requirements)

print(f"Received {len(candidates)} candidates.")
print("First 3 candidates:")
for c in candidates[:3]:
    print(f"- {c}")

# Check if it looks like mock data
mock_indicators = ["(Mock)", "김치볶음밥 (Mock)"]
is_mock = any(m in candidates[0] for m in mock_indicators)

if is_mock:
    print("FAILURE: Still receiving Mock Data.")
else:
    print("SUCCESS: Received generated data (likely).")
