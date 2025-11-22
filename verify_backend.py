import requests
import os

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Test Root
    try:
        resp = requests.get(f"{BASE_URL}/")
        assert resp.status_code == 200
        print("Root endpoint: OK")
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return

    # 2. Test Upload
    file_path = "dummy_requirements.txt"
    if not os.path.exists(file_path):
        print("Dummy file not found.")
        return

    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{BASE_URL}/upload", files=files)
            assert resp.status_code == 200
            data = resp.json()
            uploaded_path = data["file_path"]
            print(f"Upload endpoint: OK. Path: {uploaded_path}")
    except Exception as e:
        print(f"Upload endpoint failed: {e}")
        return

    # 3. Test Generate
    try:
        payload = {"file_path": uploaded_path, "feature_name": "User Login"}
        print("Triggering generation (this may take a moment)...")
        resp = requests.post(f"{BASE_URL}/generate", json=payload)
        
        if resp.status_code == 200:
            result = resp.json()
            print("Generate endpoint: OK")
            print(f"Test Cases: {len(result.get('test_cases', []))}")
            print(f"Hallucination Issues: {result.get('hallucination_report', {}).get('found_issues')}")
        else:
            print(f"Generate endpoint failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Generate endpoint failed: {e}")

if __name__ == "__main__":
    test_api()
