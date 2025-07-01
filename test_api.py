from flask import Flask, request, jsonify
import base64
import os

app = Flask(__name__)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "API is running!"})

# Verify student ID via image upload
@app.route('/verify-student-id', methods=['POST'])
def verify_student_id():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Simulate verification (add your own logic here)
    return jsonify({
        "status": "verified",
        "filename": image.filename
    })

# Verify student ID via base64 encoded image
@app.route('/verify-base64', methods=['POST'])
def verify_base64():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        image_bytes = base64.b64decode(data['image'])
        # Simulate verification (add your own logic here)
        return jsonify({"status": "verified", "size": len(image_bytes)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # Replit requires host=0.0.0.0 and port=3000
    app.run(host='0.0.0.0', port=3000)
