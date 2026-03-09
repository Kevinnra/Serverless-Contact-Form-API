#!/usr/bin/env python3
import requests
import json

API_URL = "https://x51urh1uwd.execute-api.ap-northeast-1.amazonaws.com/prod/contact" # Replace with your actual API Gateway URL

# Test normal submission
def test_valid_submission():
    data = {
        "name": "Python Test User",
        "email": "pythontest@example.com",
        "message": "Testing from Python script"
    }
    response = requests.post(API_URL, json=data)
    print(f"✓ Valid submission: {response.status_code}")
    print(f"  Response: {response.json()}\n")

# Test invalid email format
def test_invalid_email():
    data = {
        "name": "Test",
        "email": "not-an-email",
        "message": "Test"
    }
    response = requests.post(API_URL, json=data)
    print(f"✓ Invalid email: {response.status_code}")
    print(f"  Response: {response.json()}\n")

# Test empty fields
def test_empty_fields():
    data = {
        "name": "",
        "email": "",
        "message": ""
    }
    response = requests.post(API_URL, json=data)
    print(f"✓ Empty fields: {response.status_code}")
    print(f"  Response: {response.json()}\n")

if __name__ == "__main__":
    print("Testing Contact Form API\n")
    test_valid_submission()
    test_invalid_email()
    test_empty_fields()
    print("All tests completed!")
