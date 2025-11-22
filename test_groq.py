"""
Test script to verify Groq integration with the Test Case Generator
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_status():
    """Test if the server is running"""
    print("Testing server status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.json()}")
    return response.status_code == 200

def test_upload_and_generate():
    """Test uploading a document and generating test cases with Groq"""
    print("\n" + "="*60)
    print("Testing Test Case Generation with Groq")
    print("="*60)
    
    # Create a simple test requirements document
    test_content = """
    User Authentication Feature
    
    The system shall provide a login functionality where users can authenticate using their email and password.
    
    Requirements:
    1. The login page shall have fields for email and password
    2. The system shall validate the email format
    3. The system shall verify the password against the stored hash
    4. Upon successful authentication, the user shall be redirected to the dashboard
    5. Upon failed authentication, an error message shall be displayed
    6. The system shall lock the account after 3 failed login attempts
    """
    
    # Save test document
    test_file_path = "uploads/test_requirements.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    print(f"\nCreated test requirements file: {test_file_path}")
    
    # Generate test cases
    print("\nGenerating test cases using Groq...")
    generate_request = {
        "file_path": test_file_path,
        "feature_name": "User Authentication"
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/generate",
        json=generate_request,
        headers={"Content-Type": "application/json"}
    )
    end_time = time.time()
    
    print(f"\nResponse Status Code: {response.status_code}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*60)
        print("GENERATED TEST CASES")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        # Check if test cases were generated
        if "test_cases" in result and len(result["test_cases"]) > 0:
            print(f"\n✅ Successfully generated {len(result['test_cases'])} test cases!")
            
            # Check for hallucination flags
            hallucinated = [tc for tc in result["test_cases"] if tc.get("hallucination_flag", False)]
            if hallucinated:
                print(f"⚠️  Warning: {len(hallucinated)} test case(s) flagged as potential hallucinations")
            else:
                print("✅ All test cases passed hallucination check!")
            
            return True
        else:
            print("❌ No test cases were generated")
            return False
    else:
        print(f"❌ Error: {response.text}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Groq Integration Test")
    print("="*60)
    print("\nNote: Make sure LLM_PROVIDER is set to 'groq' in .env file")
    
    # Test server status
    if not test_status():
        print("❌ Server is not running!")
        exit(1)
    
    # Test generation
    success = test_upload_and_generate()
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ TESTS FAILED!")
        print("="*60)
