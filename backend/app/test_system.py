"""
Comprehensive test script for AgriVerse Farmer Advisory System
Tests all endpoints and functionality
"""

import requests
import json
import io
from PIL import Image
import numpy as np
import os
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE_PATH = "test_image.jpg"

def create_test_image():
    """Create a test image for disease detection"""
    # Create a simple test image
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(TEST_IMAGE_PATH)
    return TEST_IMAGE_PATH

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_languages_endpoint():
    """Test the languages endpoint"""
    print("🔍 Testing languages endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/languages")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Languages endpoint working. Found {len(data['languages'])} languages")
            
            # Check if Malayalam is included
            languages = [lang['code'] for lang in data['languages']]
            if 'ml' in languages:
                print("✅ Malayalam support confirmed")
            else:
                print("⚠️ Malayalam not found in supported languages")
            return True
        else:
            print(f"❌ Languages endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Languages endpoint error: {e}")
        return False

def test_disease_detection():
    """Test disease detection endpoint"""
    print("🔍 Testing disease detection endpoint...")
    try:
        # Create test image
        test_img_path = create_test_image()
        
        with open(test_img_path, 'rb') as f:
            files = {'file': f}
            data = {'language': 'en'}
            response = requests.post(f"{BASE_URL}/detect-disease/", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Disease detection endpoint working")
            print(f"   Prediction: {result.get('prediction', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Is Reliable: {result.get('is_reliable', 'N/A')}")
            return True
        else:
            print(f"❌ Disease detection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Disease detection error: {e}")
        return False
    finally:
        # Clean up test image
        if os.path.exists(TEST_IMAGE_PATH):
            os.remove(TEST_IMAGE_PATH)

def test_advisory_endpoint():
    """Test advisory endpoint"""
    print("🔍 Testing advisory endpoint...")
    try:
        payload = {
            "crop_name": "Rice",
            "location": "Kerala",
            "soil_type": "Clay",
            "query": "What fertilizer should I use for rice cultivation?",
            "language": "ml"
        }
        
        response = requests.post(f"{BASE_URL}/advisory/", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Advisory endpoint working")
            print(f"   Advisory length: {len(result.get('advisory', ''))} characters")
            print(f"   Language: {result.get('language', 'N/A')}")
            return True
        else:
            print(f"❌ Advisory endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Advisory endpoint error: {e}")
        return False

def test_gemini_direct():
    """Test direct Gemini endpoint"""
    print("🔍 Testing direct Gemini endpoint...")
    try:
        payload = {
            "query": "What are the symptoms of rice blast disease?",
            "language": "en"
        }
        
        response = requests.post(f"{BASE_URL}/ask-gemini/", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Direct Gemini endpoint working")
            print(f"   Response length: {len(result.get('response', ''))} characters")
            return True
        else:
            print(f"❌ Direct Gemini endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Direct Gemini endpoint error: {e}")
        return False

def test_tts_endpoint():
    """Test text-to-speech endpoint"""
    print("🔍 Testing TTS endpoint...")
    try:
        payload = {
            "text": "This is a test message for text to speech conversion.",
            "language": "en"
        }
        
        response = requests.post(f"{BASE_URL}/tts/", json=payload)
        
        if response.status_code == 200:
            print("✅ TTS endpoint working")
            print(f"   Audio size: {len(response.content)} bytes")
            print(f"   Content type: {response.headers.get('content-type', 'N/A')}")
            return True
        else:
            print(f"❌ TTS endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ TTS endpoint error: {e}")
        return False

def test_multilingual_support():
    """Test multilingual support across endpoints"""
    print("🔍 Testing multilingual support...")
    
    languages = ['en', 'hi', 'ml']
    results = {}
    
    for lang in languages:
        print(f"   Testing {lang}...")
        try:
            payload = {
                "crop_name": "Rice",
                "location": "Kerala",
                "soil_type": "Clay",
                "query": "What are the best practices for rice cultivation?",
                "language": lang
            }
            
            response = requests.post(f"{BASE_URL}/advisory/", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                results[lang] = {
                    "status": "success",
                    "advisory_length": len(result.get('advisory', ''))
                }
            else:
                results[lang] = {
                    "status": "failed",
                    "error": response.text
                }
        except Exception as e:
            results[lang] = {
                "status": "error",
                "error": str(e)
            }
    
    # Report results
    all_success = True
    for lang, result in results.items():
        if result["status"] == "success":
            print(f"   ✅ {lang}: {result['advisory_length']} chars")
        else:
            print(f"   ❌ {lang}: {result.get('error', 'Unknown error')}")
            all_success = False
    
    return all_success

def test_history_endpoint():
    """Test query history endpoint"""
    print("🔍 Testing history endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/history")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ History endpoint working")
            print(f"   Total queries: {result.get('total', 0)}")
            print(f"   History items: {len(result.get('history', []))}")
            return True
        else:
            print(f"❌ History endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History endpoint error: {e}")
        return False

def run_performance_test():
    """Run basic performance tests"""
    print("🔍 Running performance tests...")
    
    # Test response times
    endpoints = [
        ("/health", "GET", None),
        ("/languages", "GET", None),
        ("/history", "GET", None)
    ]
    
    for endpoint, method, payload in endpoints:
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: {response_time:.3f}s")
            else:
                print(f"   ❌ {endpoint}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")

def main():
    """Run all tests"""
    print("🚀 Starting AgriVerse System Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Languages Support", test_languages_endpoint),
        ("Disease Detection", test_disease_detection),
        ("Advisory Service", test_advisory_endpoint),
        ("Direct Gemini", test_gemini_direct),
        ("Text-to-Speech", test_tts_endpoint),
        ("Multilingual Support", test_multilingual_support),
        ("Query History", test_history_endpoint),
        ("Performance", run_performance_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()
