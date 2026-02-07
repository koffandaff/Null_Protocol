import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_chat():
    print("Testing Chat Functionality...")
    
    # 1. Health Check
    try:
        print("Checking Health...")
        response = requests.get(f"{BASE_URL}/api/chat/health")
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {json.dumps(response.json(), indent=2)}")
        
        if not response.json().get("ollama_connected"):
            print("❌ Ollama not connected!")
            return
        
        if not response.json().get("model_available"):
            print("❌ Model not available!")
            return

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    # 2. Login
    print("\nLogging in...")
    try:
        auth_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@example.com", 
            "password": "password123"
        })
        if auth_response.status_code != 200:
            print(f"❌ Login failed: {auth_response.text}")
            # Try signup if login fails
            print("Trying signup...")
            signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
                "username": "chattest",
                "email": "testuser@example.com",
                "password": "password123",
                "full_name": "Chat Tester"
            })
            if signup_response.status_code == 201:
                print("✅ Signup successful, logging in...")
                auth_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                    "email": "testuser@example.com", 
                    "password": "password123"
                })
            else:
                 print(f"❌ Signup failed: {signup_response.text}")
                 return

        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")

        # 3. Create Session (implicitly via send or explicit)
        # We'll use explicit create session to test that endpoint
        print("\nCreating Session...")
        session_response = requests.post(f"{BASE_URL}/api/chat/sessions", headers=headers)
        session_id = session_response.json()["id"]
        print(f"✅ Session Created: {session_id}")

        # 4. Send Message (Stream)
        print("\nSending Message: 'Hello, who are you?'")
        
        client = requests.Session()
        with client.post(
            f"{BASE_URL}/api/chat/send",
            headers=headers,
            json={"session_id": session_id, "message": "Hello, who are you?"},
            stream=True
        ) as response:
            if response.status_code != 200:
                print(f"❌ Send failed: {response.status_code}")
                print(response.text)
                return
            
            print("Stream Response:")
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data_str = decoded[6:]
                        try:
                            data = json.loads(data_str)
                            if "content" in data:
                                print(data["content"], end="", flush=True)
                            elif "error" in data:
                                print(f"\n❌ Error from stream: {data['error']}")
                        except:
                            print(f"\nError decoding: {data_str}")
        print("\n✅ Stream finished")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_chat()
