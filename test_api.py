import requests
import base64
import json
import os

class StudentIDVerifier:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def verify_image_file(self, image_path):
        """Verify student ID using file upload"""
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f"{self.base_url}/verify-student-id", files=files)
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def verify_base64_image(self, image_path):
        """Verify student ID using base64 encoded image"""
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            data = {"image": image_data}
            response = requests.post(
                f"{self.base_url}/verify-base64",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    verifier = StudentIDVerifier()
    
    # Test health check
    print("Testing health check...")
    health = verifier.health_check()
    print(json.dumps(health, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test with an image file (you'll need to provide an actual image path)
    image_path = input("Enter path to student ID image (or press Enter to skip): ").strip()
    
    if image_path and os.path.exists(image_path):
        print("Testing file upload verification...")
        result = verifier.verify_image_file(image_path)
        print(json.dumps(result, indent=2))
        print("\n" + "="*50 + "\n")
        
        print("Testing base64 verification...")
        result = verifier.verify_base64_image(image_path)
        print(json.dumps(result, indent=2))
    else:
        print("No valid image path provided. Skipping image verification tests.")

if __name__ == "__main__":
    main()
