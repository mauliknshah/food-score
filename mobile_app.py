from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

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
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const cameraBtn = document.getElementById('cameraBtn');
        const previewArea = document.getElementById('previewArea');
        const previewImage = document.getElementById('previewImage');
        const fileInfo = document.getElementById('fileInfo');

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

            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewArea.classList.add('show');

                const sizeKB = (file.size / 1024).toFixed(2);
                fileInfo.textContent = `${file.name} (${sizeKB} KB)`;
            };
            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Here you can add your image processing logic
    return jsonify({'message': 'Image uploaded successfully', 'filename': file.filename})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
