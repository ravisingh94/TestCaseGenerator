"""
Simple test script for "all features" mode
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_all_features():
    """Test the all features mode"""
    print("="*60)
    print("Testing 'All Features' Mode")
    print("="*60)
    
    # Use an existing uploaded file
    file_path = "uploads/test_requirements.txt"
    
    # Test with "all features" keyword
    generate_request = {
        "file_path": file_path,
        "feature_name": "all features"
    }
    
    print("\nGenerating test cases for ALL FEATURES...")
    response = requests.post(
        f"{BASE_URL}/generate",
        json=generate_request,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nResponse Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        if result.get("batch_mode"):
            print(f"\n✅ Batch mode activated!")
            print(f"Features processed: {result.get('total_features', 0)}")
            print(f"Total test cases: {result.get('total_test_cases', 0)}")
        else:
            print("\n⚠️  Batch mode not activated")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_all_features()
