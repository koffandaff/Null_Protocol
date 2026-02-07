import requests
import os
from dotenv import load_dotenv

load_dotenv()

ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
print(f"Testing Connection to: {ollama_url}")

try:
    print(f"1. Testing /api/tags (Health Check)...")
    resp = requests.get(f"{ollama_url}/api/tags", timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Response (First 200 chars): {resp.text[:200]}")
    
    if resp.status_code == 200:
        try:
            data = resp.json()
            models = [m.get("name") for m in data.get("models", [])]
            print(f"✅ Connection Successful! Found models: {models}")
        except:
            print("❌ Response was not valid JSON (Likely ngrok browser warning page)")
    else:
        print("❌ Endpoint returned error status")

except Exception as e:
    print(f"❌ Connection Failed: {str(e)}")
