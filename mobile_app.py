from flask import Flask, render_template_string, request, jsonify
import os
from food_segmentation_agent import FoodSegmentationAgent

app = Flask(__name__)

# Initialize the food segmentation agent
try:
    agent = FoodSegmentationAgent()
    print("Food Segmentation Agent initialized successfully!")
except ValueError as e:
    print(f"Warning: Could not initialize agent - {e}")
    print("Set ANTHROPIC_API_KEY environment variable to enable food analysis")
    agent = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Food-Score</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }

        h1 {
            color: white;
            font-size: 2.5rem;
            margin: 20px 0 40px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }

        .upload-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }

        .upload-area.dragover {
            background: #f0f3ff;
            border-color: #764ba2;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }

        .upload-text {
            color: #667eea;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 10px;
        }

        .upload-hint {
            color: #888;
            font-size: 0.9rem;
        }

        input[type="file"] {
            display: none;
        }

        .camera-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .camera-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .camera-btn:active {
            transform: translateY(0);
        }

        .preview-area {
            margin-top: 20px;
            display: none;
        }

        .preview-area.show {
            display: block;
        }

        .preview-image {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }

        .file-info {
            color: #666;
            font-size: 0.9rem;
            margin-top: 10px;
            text-align: center;
        }

        .analyze-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-top: 15px;
            display: none;
        }

        .analyze-btn.show {
            display: block;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(17, 153, 142, 0.4);
        }

        .analyze-btn:active {
            transform: translateY(0);
        }

        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .results-area {
            margin-top: 20px;
            display: none;
            background: #f8f9ff;
            border-radius: 10px;
            padding: 20px;
        }

        .results-area.show {
            display: block;
        }

        .results-title {
            color: #667eea;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
        }

        .food-item {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .food-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .food-name {
            font-weight: 600;
            color: #333;
            font-size: 1.1rem;
        }

        .food-weight {
            color: #667eea;
            font-weight: 600;
            font-size: 1rem;
        }


        .loading {
            text-align: center;
            color: #667eea;
            font-size: 1rem;
            padding: 20px;
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }

        @media (max-width: 480px) {
            h1 {
                font-size: 2rem;
            }

            .container {
                padding: 20px;
            }

            .upload-area {
                padding: 30px 15px;
            }
        }
    </style>
</head>
<body>
    <h1>Food-Score</h1>

    <div class="container">
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📸</div>
            <div class="upload-text">Tap to upload an image</div>
            <div class="upload-hint">or drag and drop here</div>
            <input type="file" id="fileInput" accept="image/*">
        </div>

        <button class="camera-btn" id="cameraBtn">
            <span>📷</span>
            <span>Take a Photo</span>
        </button>

        <div class="preview-area" id="previewArea">
            <img id="previewImage" class="preview-image" alt="Preview">
            <div class="file-info" id="fileInfo"></div>
            <button class="analyze-btn" id="analyzeBtn">
                <span>🔍</span>
                <span>Analyze Food</span>
            </button>
        </div>

        <div class="results-area" id="resultsArea">
            <div class="results-title">Food Analysis Results</div>
            <div id="resultsContent"></div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const cameraBtn = document.getElementById('cameraBtn');
        const previewArea = document.getElementById('previewArea');
        const previewImage = document.getElementById('previewImage');
        const fileInfo = document.getElementById('fileInfo');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const resultsArea = document.getElementById('resultsArea');
        const resultsContent = document.getElementById('resultsContent');

        let currentFile = null;

        // Upload area click
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            handleFile(e.target.files[0]);
        });

        // Camera button
        cameraBtn.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.capture = 'environment';
            input.addEventListener('change', (e) => {
                handleFile(e.target.files[0]);
            });
            input.click();
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        // Handle file
        function handleFile(file) {
            if (!file || !file.type.startsWith('image/')) {
                alert('Please select a valid image file');
                return;
            }

            currentFile = file;
            resultsArea.classList.remove('show');

            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewArea.classList.add('show');
                analyzeBtn.classList.add('show');

                const sizeKB = (file.size / 1024).toFixed(2);
                fileInfo.textContent = `${file.name} (${sizeKB} KB)`;
            };
            reader.readAsDataURL(file);
        }

        // Analyze button click
        analyzeBtn.addEventListener('click', async () => {
            if (!currentFile) return;

            analyzeBtn.disabled = true;
            resultsContent.innerHTML = '<div class="loading">🔄 Analyzing your food plate...</div>';
            resultsArea.classList.add('show');

            const formData = new FormData();
            formData.append('image', currentFile);

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.error) {
                    resultsContent.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                } else {
                    displayResults(data);
                }
            } catch (error) {
                resultsContent.innerHTML = `<div class="error">❌ Failed to analyze image: ${error.message}</div>`;
            } finally {
                analyzeBtn.disabled = false;
            }
        });

        function displayResults(data) {
            if (!data.items || data.items.length === 0) {
                resultsContent.innerHTML = '<div class="error">No food items detected in the image.</div>';
                return;
            }

            let html = '';
            data.items.forEach(item => {
                html += `
                    <div class="food-item">
                        <div class="food-item-header">
                            <div class="food-name">${item.name}</div>
                            <div class="food-weight">${item.weight_grams}g</div>
                        </div>
                    </div>
                `;
            });

            resultsContent.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded food image using Claude."""
    if not agent:
        return jsonify({'error': 'Food analysis agent not initialized. Please set ANTHROPIC_API_KEY environment variable.'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read image bytes
        image_bytes = file.read()

        # Analyze the food plate
        result = agent.analyze_food_plate(
            image_bytes=image_bytes,
            filename=file.filename
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
