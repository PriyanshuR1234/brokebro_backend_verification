from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from PIL import Image
import io
import base64
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Gemini API
# Make sure to set your API key in environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")
else:
    genai.configure(api_key=GEMINI_API_KEY)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_with_gemini(image_data):
    """Process image with Gemini API for student ID verification"""
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create the prompt for student ID verification
        prompt = """
        Analyze this student ID card image and provide a comprehensive verification report. 
        Please examine the following aspects:

        1. AUTHENTICITY VERIFICATION:
           - Check if this appears to be a genuine student ID card
           - Look for security features, proper formatting, official logos
           - Identify any signs of tampering, editing, or forgery

        2. INFORMATION EXTRACTION:
           - Student Name
           - Student ID/Roll Number
           - Institution/University Name
           - Course/Program
           - Academic Year/Semester
           - Issue Date
           - Expiry Date (if visible)
           - Any other relevant details

        3. COURSE STATUS VERIFICATION:
           - Determine if this appears to be for an ongoing/current course
           - Check if the dates indicate active enrollment
           - Look for current academic year indicators

        4. QUALITY ASSESSMENT:
           - Image clarity and readability
           - Whether all necessary information is visible
           - Overall condition of the ID card

        Please provide your response in the following JSON format:
        {
            "is_authentic": boolean,
            "confidence_score": number (0-100),
            "student_info": {
                "name": "string",
                "student_id": "string",
                "institution": "string",
                "course": "string",
                "academic_year": "string",
                "issue_date": "string",
                "expiry_date": "string"
            },
            "course_status": {
                "is_ongoing": boolean,
                "status_reason": "string"
            },
            "verification_details": {
                "authenticity_indicators": ["list of positive indicators"],
                "red_flags": ["list of concerns or issues"],
                "image_quality": "string (excellent/good/fair/poor)"
            },
            "recommendations": "string"
        }

        If you cannot read the image clearly or if it's not a student ID card, please indicate that in your response.
        """
        
        # Convert image data to PIL Image for Gemini
        image = Image.open(io.BytesIO(image_data))
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        # Try to parse the JSON response
        try:
            # Extract JSON from the response text
            response_text = response.text
            # Find JSON in the response (it might be wrapped in markdown)
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            result = json.loads(json_text)
            return result
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured response
            return {
                "is_authentic": False,
                "confidence_score": 0,
                "student_info": {},
                "course_status": {
                    "is_ongoing": False,
                    "status_reason": "Could not parse verification response"
                },
                "verification_details": {
                    "authenticity_indicators": [],
                    "red_flags": ["Response parsing failed"],
                    "image_quality": "unknown"
                },
                "recommendations": "Please try uploading a clearer image",
                "raw_response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error processing image with Gemini: {str(e)}")
        return {
            "error": f"Failed to process image: {str(e)}",
            "is_authentic": False,
            "confidence_score": 0
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_configured": bool(GEMINI_API_KEY)
    })

@app.route('/verify-student-id', methods=['POST'])
def verify_student_id():
    """Main endpoint for student ID verification"""
    try:
        # Check if API key is configured
        if not GEMINI_API_KEY:
            return jsonify({
                "error": "Gemini API key not configured",
                "success": False
            }), 500

        # Check if file is in request
        if 'image' not in request.files:
            return jsonify({
                "error": "No image file provided",
                "success": False
            }), 400

        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "success": False
            }), 400

        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
                "success": False
            }), 400

        # Read image data
        image_data = file.read()
        
        # Validate image
        try:
            Image.open(io.BytesIO(image_data)).verify()
        except Exception:
            return jsonify({
                "error": "Invalid image file",
                "success": False
            }), 400

        # Process with Gemini
        logger.info(f"Processing student ID verification for file: {file.filename}")
        verification_result = process_image_with_gemini(image_data)
        
        # Add metadata
        verification_result.update({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "filename": secure_filename(file.filename),
            "file_size": len(image_data)
        })

        return jsonify(verification_result)

    except Exception as e:
        logger.error(f"Error in verify_student_id: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.route('/verify-base64', methods=['POST'])
def verify_base64_image():
    """Alternative endpoint for base64 encoded images"""
    try:
        # Check if API key is configured
        if not GEMINI_API_KEY:
            return jsonify({
                "error": "Gemini API key not configured",
                "success": False
            }), 500

        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                "error": "No base64 image data provided",
                "success": False
            }), 400

        try:
            # Decode base64 image
            image_data = base64.b64decode(data['image'])
            
            # Validate image
            Image.open(io.BytesIO(image_data)).verify()
            
        except Exception:
            return jsonify({
                "error": "Invalid base64 image data",
                "success": False
            }), 400

        # Process with Gemini
        logger.info("Processing student ID verification from base64 data")
        verification_result = process_image_with_gemini(image_data)
        
        # Add metadata
        verification_result.update({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "file_size": len(image_data)
        })

        return jsonify(verification_result)

    except Exception as e:
        logger.error(f"Error in verify_base64_image: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "error": "File too large. Maximum size is 16MB",
        "success": False
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "success": False
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "success": False
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
