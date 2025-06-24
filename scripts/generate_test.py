import sys
import httpx
import os

url, username, password, scenario = sys.argv[1:5]

prompt = f"""
You are a senior QA automation engineer. Write Java + Selenium + TestNG code for:
- App URL: {url}
- Username: {username}
- Password: {password}
- Scenario: {scenario}

Use XPath or IDs. Add proper waits. Include imports. ChromeDriver assumed.
"""

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}

response = httpx.post(
    f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={os.getenv('GEMINI_API_KEY')}",
    headers={"Content-Type": "application/json"},
    json=payload
)

try:
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
except Exception:
    print("❌ Gemini response error:", response.text)
    sys.exit(1)

# Output file
output_path = "src/test/java/tests/GeneratedTest.java"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    f.write(content)
