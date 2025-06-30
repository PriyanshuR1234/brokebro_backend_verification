# Student ID Verification Backend

A Python Flask backend service that uses Google's Gemini AI to verify student ID cards for authenticity and validate ongoing course enrollment.

## Features

- **Image Upload Support**: Accepts various image formats (PNG, JPG, JPEG, GIF, BMP, WebP)
- **Gemini AI Integration**: Uses Google's Gemini 1.5 Flash model for intelligent image analysis
- **Student ID Verification**: Analyzes authenticity, extracts information, and validates course status
- **RESTful API**: Clean REST endpoints with JSON responses
- **Error Handling**: Comprehensive error handling and logging
- **File Size Limits**: 16MB maximum file size with proper validation

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and paste it in your `.env` file

### 4. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```
Returns server health status and configuration info.

### Verify Student ID (File Upload)
```
POST /verify-student-id
Content-Type: multipart/form-data
```
Upload an image file of a student ID card.

**Parameters:**
- `image`: Image file (required)

### Verify Student ID (Base64)
```
POST /verify-base64
Content-Type: application/json
```
Send a base64 encoded image.

**Body:**
```json
{
    "image": "base64_encoded_image_data"
}
```

## API Response Format

```json
{
    "success": true,
    "is_authentic": true,
    "confidence_score": 85,
    "student_info": {
        "name": "John Doe",
        "student_id": "12345678",
        "institution": "XYZ University",
        "course": "Computer Science",
        "academic_year": "2024-2025",
        "issue_date": "2024-08-01",
        "expiry_date": "2025-07-31"
    },
    "course_status": {
        "is_ongoing": true,
        "status_reason": "Valid academic year and active enrollment period"
    },
    "verification_details": {
        "authenticity_indicators": [
            "Official university logo present",
            "Proper card formatting",
            "Security features visible"
        ],
        "red_flags": [],
        "image_quality": "good"
    },
    "recommendations": "ID appears authentic and valid",
    "timestamp": "2024-12-30T10:30:00",
    "filename": "student_id.jpg",
    "file_size": 245760
}
```

## Testing the API

Use the provided test script:

```bash
python test_api.py
```

Or test manually with curl:

```bash
# Health check
curl http://localhost:5000/health

# Upload image
curl -X POST -F "image=@student_id.jpg" http://localhost:5000/verify-student-id
```

## Error Handling

The API provides detailed error messages for:
- Missing or invalid API key
- Unsupported file formats
- File size too large (>16MB)
- Invalid image data
- Network or processing errors

## Security Considerations

- File type validation
- File size limits
- Input sanitization
- Error message sanitization
- CORS configuration for web integration

## Integration Examples

### JavaScript/Web
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:5000/verify-student-id', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python
```python
import requests

with open('student_id.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/verify-student-id', files=files)
    result = response.json()
    print(result)
```

## Deployment

For production deployment:

1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Set up proper logging and monitoring
4. Configure SSL/HTTPS
5. Set up rate limiting if needed

## Troubleshooting

### Common Issues

1. **"Gemini API key not configured"**
   - Ensure your API key is set in the `.env` file
   - Check that the `.env` file is in the same directory as `app.py`

2. **"Invalid image file"**
   - Check file format is supported
   - Ensure file is not corrupted
   - Verify file size is under 16MB

3. **"Module not found" errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're using the correct Python environment

4. **Gemini API errors**
   - Verify your API key is valid and active
   - Check your API quota and billing settings
   - Ensure stable internet connection

## License

This project is for educational and development purposes.
