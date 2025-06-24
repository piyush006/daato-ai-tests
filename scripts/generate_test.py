import sys
import httpx
import os
import json

# Load extracted elements from DOM
with open("element_dump.json") as f:
    elements = json.load(f)

# Build prompt dynamically based on real elements
element_descriptions = "\n".join([
    f"- A <{el['tag']}> element with text '{el['text']}', type '{el['type']}', xpath: {el['xpath']}"
    for el in elements if el['text']
])

prompt = f"""
You are a senior QA automation engineer. Write Java + Selenium + TestNG code.

Context:
These are real DOM elements extracted after login and navigation:
{element_descriptions}

Instructions:
- Use proper waits before interacting
- Use the XPath provided for each element
- Assume ChromeDriver is already setup
- Add necessary imports
"""

# Gemini API call
api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

response = httpx.post(
    f"{api_url}?key={os.getenv('GEMINI_API_KEY')}",
    headers={"Content-Type": "application/json"},
    json={
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    },
    timeout=60
)

try:
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
except Exception:
    print("❌ Gemini response error:", response.text)
    sys.exit(1)

# Save generated test to file
output_path = "src/test/java/tests/GeneratedTest.java"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    f.write(content)

print("✅ Test code saved to GeneratedTest.java")
