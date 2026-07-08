"""
Test the Grad-CAM fix by uploading a test X-ray image and triggering analysis.
"""
import requests
import json
from PIL import Image
import numpy as np
import io
import uuid
import time

BASE_URL = "http://127.0.0.1:8000"

# User credentials (test account with random email)
TEST_EMAIL = f"gradcam_test_{uuid.uuid4().hex[:8]}@testmail.com"
PASSWORD = "TestPassword123!"

def create_test_xray():
    """Create a simple test X-ray image (grayscale, chest-like)."""
    # Create a realistic chest X-ray-like image
    img_array = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
    # Add some simple patterns
    img_array[50:100, 50:100] = np.random.randint(100, 150, (50, 50))
    img_array[150:200, 100:150] = np.random.randint(120, 180, (50, 50))
    
    img = Image.fromarray(img_array, mode='L')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def login():
    """Login and get token."""
    print("📝 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": PASSWORD}
    )
    if response.status_code == 401:
        # User doesn't exist, register first
        print("   User not found, registering...")
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": PASSWORD,
                "full_name": "Grad-CAM Test User"
            }
        )
        if register_response.status_code != 200:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(register_response.text)
            return None
        print("✅ User registered successfully")
        # Try login again
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": PASSWORD}
        )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None
    
    token = response.json()["access_token"]
    print(f"✅ Login successful. Token: {token[:20]}...")
    return token

def upload_xray(token):
    """Upload test X-ray image."""
    print("\n📸 Uploading test X-ray image...")
    xray_image = create_test_xray()
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {
        "file": ("test_xray.png", xray_image, "image/png")
    }
    
    response = requests.post(
        f"{BASE_URL}/radiology/upload",
        headers=headers,
        files=files,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return None
    
    upload_data = response.json()
    print(f"✅ Upload successful. Response: {upload_data}")
    image_id = upload_data.get("id") or upload_data.get("image_id")
    if image_id is None:
        print(f"❌ No image_id in response. Keys: {upload_data.keys()}")
        return None
    print(f"   Image ID: {image_id}")
    return image_id

def analyze_xray(token, image_id):
    """Trigger analysis with Grad-CAM."""
    print(f"\n🔬 Starting analysis on image {image_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "generate_heatmaps": True,  # THIS TRIGGERS GRAD-CAM
        "include_findings": True
    }
    
    response = requests.post(
        f"{BASE_URL}/radiology/{image_id}/analyze",
        headers=headers,
        json=payload,
        timeout=120  # Long timeout for analysis
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
        return None
    
    analysis = response.json()
    print("✅ Analysis successful!")
    print("\n📊 Analysis Results:")
    results_str = json.dumps(analysis, indent=2, default=str)
    print(results_str[:500] + "...")
    
    # Check if findings exist
    findings_count = analysis.get("finding_count", 0)
    print(f"\n📋 Findings count: {findings_count}")
    
    return analysis

def get_heatmap(token, image_id):
    """Retrieve heatmap for a finding."""
    print(f"\n📥 Retrieving heatmap for image {image_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/radiology/{image_id}/heatmap/infiltration",
            headers=headers,
            timeout=30
        )
        
        print(f"Heatmap Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Heatmap retrieval failed: {response.status_code}")
            print(response.text[:200])
            return False
        
        print(f"✅ Heatmap retrieved successfully! Size: {len(response.content)} bytes")
        return True
    except Exception as e:
        print(f"❌ Heatmap request error: {e}")
        return False

def main():
    print("="*60)
    print("🧪 GRAD-CAM FIX VALIDATION TEST")
    print("="*60)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Test failed at login step")
        return
    
    # Step 2: Upload X-ray
    image_id = upload_xray(token)
    if not image_id:
        print("\n❌ Test failed at upload step")
        return
    
    # Step 3: Analyze (triggers Grad-CAM)
    analysis = analyze_xray(token, image_id)
    if not analysis:
        print("\n❌ Test failed at analysis step - GRAD-CAM ERROR DETECTED")
        print("\n⚠️  CHECK BACKEND LOGS FOR 'BackwardHookFunctionBackward' ERROR")
        print("Live logs available in the background terminal")
        return
    
    print("\n" + "="*60)
    print("✅ TEST PASSED - NO GRAD-CAM ERRORS DETECTED!")
    print("="*60)
    
    # Step 4: Retrieve heatmap
    heatmap_ok = get_heatmap(token, image_id)
    
    if heatmap_ok:
        print("\n🎉 Complete Grad-CAM pipeline working!")
        print("✓ Analysis executed successfully")
        print("✓ Heatmaps generated and saved")
        print("✓ Heatmaps retrievable via API")
    else:
        print("\n⚠️  Analysis works but heatmap retrieval failed")
        print("Check if heatmap files were created in backend/uploads/heatmaps/")
    
    print("\nNext: Verify results in frontend.")

if __name__ == "__main__":
    main()
