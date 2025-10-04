from flask import Flask, render_template_string, request, jsonify
import os
import concurrent.futures
from food_segmentation_agent import FoodSegmentationAgent
from nutrition_agent import NutritionAgent
from ingredient_agent import IngredientAgent
from ghg_emission_agent import GHGEmissionAgent

app = Flask(__name__)

# Initialize the food segmentation agent
try:
    segmentation_agent = FoodSegmentationAgent()
    print("Food Segmentation Agent initialized successfully!")
except ValueError as e:
    print(f"Warning: Could not initialize segmentation agent - {e}")
    print("Set ANTHROPIC_API_KEY environment variable to enable food analysis")
    segmentation_agent = None

# Initialize the nutrition agent
try:
    nutrition_agent = NutritionAgent()
    print("Nutrition Agent initialized successfully!")
except ValueError as e:
    print(f"Warning: Could not initialize nutrition agent - {e}")
    nutrition_agent = None

# Initialize the ingredient agent
try:
    ingredient_agent = IngredientAgent()
    print("Ingredient Agent initialized successfully!")
except ValueError as e:
    print(f"Warning: Could not initialize ingredient agent - {e}")
    ingredient_agent = None

# Initialize the GHG emission agent
try:
    ghg_agent = GHGEmissionAgent()
    print("GHG Emission Agent initialized successfully!")
except ValueError as e:
    print(f"Warning: Could not initialize GHG emission agent - {e}")
    ghg_agent = None

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

        .summary-section {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .summary-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }

        .summary-ghg {
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            color: white;
            text-align: center;
        }

        .summary-ghg.ghg-low {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }

        .summary-ghg.ghg-medium {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        }

        .summary-ghg.ghg-high {
            background: linear-gradient(135deg, #fd7e14 0%, #dc3545 100%);
        }

        .summary-ghg.ghg-very-high {
            background: linear-gradient(135deg, #dc3545 0%, #bd2130 100%);
        }

        .summary-ghg-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .summary-ghg-value {
            font-size: 1.8rem;
            font-weight: 700;
        }

        .summary-ghg-breakdown {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-top: 10px;
            font-size: 0.85rem;
        }

        .summary-nutrition {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }

        .summary-nutrient {
            background: #f8f9ff;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }

        .summary-nutrient-label {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 4px;
        }

        .summary-nutrient-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #667eea;
        }

        .details-section {
            margin-top: 20px;
        }

        .details-header {
            background: #667eea;
            color: white;
            padding: 12px 15px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            user-select: none;
        }

        .details-header:hover {
            background: #5568d3;
        }

        .details-arrow {
            transition: transform 0.3s ease;
        }

        .details-arrow.open {
            transform: rotate(180deg);
        }

        .details-content {
            margin-top: 10px;
            display: none;
        }

        .details-content.show {
            display: block;
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
            margin-bottom: 12px;
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

        .ghg-emission {
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }

        .ghg-emission.ghg-low {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        }

        .ghg-emission.ghg-medium {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        }

        .ghg-emission.ghg-high {
            background: linear-gradient(135deg, #ffe8d1 0%, #ffd7ba 100%);
        }

        .ghg-emission.ghg-very-high {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        }

        .ghg-total {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .ghg-label {
            font-size: 0.9rem;
            font-weight: 600;
        }

        .ghg-emission.ghg-low .ghg-label {
            color: #155724;
        }

        .ghg-emission.ghg-medium .ghg-label {
            color: #856404;
        }

        .ghg-emission.ghg-high .ghg-label {
            color: #8b4513;
        }

        .ghg-emission.ghg-very-high .ghg-label {
            color: #721c24;
        }

        .ghg-value {
            font-size: 1rem;
            font-weight: 700;
        }

        .ghg-emission.ghg-low .ghg-value {
            color: #155724;
        }

        .ghg-emission.ghg-medium .ghg-value {
            color: #856404;
        }

        .ghg-emission.ghg-high .ghg-value {
            color: #8b4513;
        }

        .ghg-emission.ghg-very-high .ghg-value {
            color: #721c24;
        }

        .ghg-breakdown {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }

        .ghg-component {
            text-align: center;
            font-size: 0.75rem;
        }

        .ghg-component-label {
            color: #777;
            display: block;
            margin-bottom: 2px;
        }

        .ghg-component-value {
            font-weight: 600;
            color: #333;
        }

        .nutrition-info {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }

        .calories {
            font-size: 0.95rem;
            color: #ff6b6b;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .daily-values {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            font-size: 0.85rem;
        }

        .nutrient {
            display: flex;
            justify-content: space-between;
            padding: 4px 8px;
            background: #f8f9ff;
            border-radius: 4px;
        }

        .nutrient-name {
            color: #666;
            text-transform: capitalize;
        }

        .nutrient-value {
            color: #667eea;
            font-weight: 600;
        }

        .diet-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .diet-vegan {
            background: #d4edda;
            color: #155724;
        }

        .diet-vegetarian {
            background: #fff3cd;
            color: #856404;
        }

        .diet-pescatarian {
            background: #d1ecf1;
            color: #0c5460;
        }

        .diet-meat {
            background: #f8d7da;
            color: #721c24;
        }

        .ingredients-section {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }

        .ingredients-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 6px;
        }

        .ingredients-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .ingredient-tag {
            background: #f0f3ff;
            color: #667eea;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
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

            // Calculate totals
            let totalCO2e = 0;
            let totalCO2 = 0;
            let totalMethane = 0;
            let totalN2O = 0;
            let totalCalories = 0;
            let avgCO2ePerKg = 0;
            let itemCount = 0;

            const nutrients = {
                protein: 0, fat: 0, carbohydrates: 0, fiber: 0, sugar: 0,
                sodium: 0, potassium: 0, vitamin_a: 0, vitamin_c: 0,
                vitamin_d: 0, calcium: 0, iron: 0, vitamin_b12: 0
            };

            data.items.forEach(item => {
                if (item.ghg_emission) {
                    totalCO2e += item.ghg_emission.co2_equivalent_kg || 0;
                    totalCO2 += item.ghg_emission.co2_kg || 0;
                    totalMethane += item.ghg_emission.methane_kg || 0;
                    totalN2O += item.ghg_emission.nitrous_oxide_kg || 0;
                    if (item.ghg_emission.co2e_per_kg_food) {
                        avgCO2ePerKg += item.ghg_emission.co2e_per_kg_food;
                        itemCount++;
                    }
                }
                if (item.nutrition) {
                    totalCalories += item.nutrition.calories || 0;
                    if (item.nutrition.daily_value_percentages) {
                        Object.keys(nutrients).forEach(key => {
                            nutrients[key] += item.nutrition.daily_value_percentages[key] || 0;
                        });
                    }
                }
            });

            // Calculate average CO2e per kg and determine category
            avgCO2ePerKg = itemCount > 0 ? avgCO2ePerKg / itemCount : 0;
            let ghgCategory = 'low';
            if (avgCO2ePerKg > 8) ghgCategory = 'very-high';
            else if (avgCO2ePerKg > 4) ghgCategory = 'high';
            else if (avgCO2ePerKg > 2) ghgCategory = 'medium';

            // Build summary section
            let html = `
                <div class="summary-section">
                    <div class="summary-title">📊 Overall Impact Summary</div>

                    <div class="summary-ghg ghg-${ghgCategory}">
                        <div class="summary-ghg-label">🌍 Total Greenhouse Gas Emissions</div>
                        <div class="summary-ghg-value">${totalCO2e.toFixed(3)} kg CO₂e</div>
                        <div style="font-size: 0.85rem; opacity: 0.9; margin-top: 4px;">
                            Average: ${avgCO2ePerKg.toFixed(1)} kg CO₂e/kg
                        </div>
                        <div class="summary-ghg-breakdown">
                            <div>CO₂: ${totalCO2.toFixed(3)} kg</div>
                            <div>CH₄: ${totalMethane.toFixed(4)} kg</div>
                            <div>N₂O: ${totalN2O.toFixed(5)} kg</div>
                        </div>
                    </div>

                    <div class="summary-nutrition">
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">🔥 Calories</div>
                            <div class="summary-nutrient-value">${totalCalories.toFixed(0)} kcal</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Protein</div>
                            <div class="summary-nutrient-value">${nutrients.protein.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Fat</div>
                            <div class="summary-nutrient-value">${nutrients.fat.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Carbs</div>
                            <div class="summary-nutrient-value">${nutrients.carbohydrates.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Fiber</div>
                            <div class="summary-nutrient-value">${nutrients.fiber.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Sugar</div>
                            <div class="summary-nutrient-value">${nutrients.sugar.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Sodium</div>
                            <div class="summary-nutrient-value">${nutrients.sodium.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Potassium</div>
                            <div class="summary-nutrient-value">${nutrients.potassium.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Vitamin A</div>
                            <div class="summary-nutrient-value">${nutrients.vitamin_a.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Vitamin C</div>
                            <div class="summary-nutrient-value">${nutrients.vitamin_c.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Vitamin D</div>
                            <div class="summary-nutrient-value">${nutrients.vitamin_d.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Calcium</div>
                            <div class="summary-nutrient-value">${nutrients.calcium.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Iron</div>
                            <div class="summary-nutrient-value">${nutrients.iron.toFixed(0)}%</div>
                        </div>
                        <div class="summary-nutrient">
                            <div class="summary-nutrient-label">Vitamin B12</div>
                            <div class="summary-nutrient-value">${nutrients.vitamin_b12.toFixed(0)}%</div>
                        </div>
                    </div>
                </div>

                <div class="details-section">
                    <div class="details-header" onclick="toggleDetails()">
                        <span>📋 Details (${data.items.length} items)</span>
                        <span class="details-arrow" id="detailsArrow">▼</span>
                    </div>
                    <div class="details-content" id="detailsContent">
            `;

            // Add individual food items
            data.items.forEach(item => {
                html += `
                    <div class="food-item">
                        <div class="food-item-header">
                            <div class="food-name">${item.food}</div>
                            <div class="food-weight">${item.weight}g</div>
                        </div>
                `;

                // Add GHG emission as the first item (if available)
                if (item.ghg_emission) {
                    const co2e = item.ghg_emission.co2_equivalent_kg;
                    const co2 = item.ghg_emission.co2_kg;
                    const methane = item.ghg_emission.methane_kg;
                    const n2o = item.ghg_emission.nitrous_oxide_kg;
                    const co2ePerKg = item.ghg_emission.co2e_per_kg_food;
                    const category = item.ghg_emission.emission_category;
                    const categoryClass = `ghg-${category.replace('_', '-')}`;

                    html += `
                        <div class="ghg-emission ${categoryClass}">
                            <div class="ghg-total">
                                <span class="ghg-label">🌍 Total GHG Impact:</span>
                                <span class="ghg-value">${co2e.toFixed(3)} kg CO₂e</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #666; margin-bottom: 6px;">
                                (${co2ePerKg.toFixed(1)} kg CO₂e per kg of food)
                            </div>
                            <div class="ghg-breakdown">
                                <div class="ghg-component">
                                    <span class="ghg-component-label">CO₂</span>
                                    <span class="ghg-component-value">${co2.toFixed(3)} kg</span>
                                </div>
                                <div class="ghg-component">
                                    <span class="ghg-component-label">Methane (CH₄)</span>
                                    <span class="ghg-component-value">${methane.toFixed(4)} kg</span>
                                </div>
                                <div class="ghg-component">
                                    <span class="ghg-component-label">N₂O</span>
                                    <span class="ghg-component-value">${n2o.toFixed(5)} kg</span>
                                </div>
                            </div>
                        </div>
                    `;
                }

                // Add diet badge if ingredients info is available
                if (item.ingredients_info && item.ingredients_info.diet) {
                    const dietType = item.ingredients_info.diet.toLowerCase();
                    const dietEmojis = {
                        'vegan': '🌱',
                        'vegetarian': '🥬',
                        'pescatarian': '🐟',
                        'meat': '🍖'
                    };
                    const emoji = dietEmojis[dietType] || '';
                    html += `<div class="diet-badge diet-${dietType}">${emoji} ${item.ingredients_info.diet}</div>`;
                }

                // Add nutrition information if available
                if (item.nutrition) {
                    html += `<div class="nutrition-info">`;

                    // Calories
                    if (item.nutrition.calories) {
                        html += `<div class="calories">🔥 ${item.nutrition.calories} kcal</div>`;
                    }

                    // Daily value percentages
                    if (item.nutrition.daily_value_percentages) {
                        html += `<div class="daily-values">`;

                        const dvp = item.nutrition.daily_value_percentages;
                        const nutrients = [
                            { key: 'protein', label: 'Protein' },
                            { key: 'fat', label: 'Fat' },
                            { key: 'carbohydrates', label: 'Carbs' },
                            { key: 'fiber', label: 'Fiber' },
                            { key: 'sugar', label: 'Sugar' },
                            { key: 'sodium', label: 'Sodium' },
                            { key: 'potassium', label: 'Potassium' },
                            { key: 'vitamin_a', label: 'Vit A' },
                            { key: 'vitamin_c', label: 'Vit C' },
                            { key: 'vitamin_d', label: 'Vit D' },
                            { key: 'calcium', label: 'Calcium' },
                            { key: 'iron', label: 'Iron' },
                            { key: 'vitamin_b12', label: 'Vit B12' }
                        ];

                        nutrients.forEach(nutrient => {
                            if (dvp[nutrient.key] !== undefined) {
                                html += `
                                    <div class="nutrient">
                                        <span class="nutrient-name">${nutrient.label}</span>
                                        <span class="nutrient-value">${dvp[nutrient.key]}%</span>
                                    </div>
                                `;
                            }
                        });

                        html += `</div>`;
                    }

                    html += `</div>`;
                }

                // Add ingredients section if available
                if (item.ingredients_info && item.ingredients_info.ingredients) {
                    html += `
                        <div class="ingredients-section">
                            <div class="ingredients-title">Ingredients:</div>
                            <div class="ingredients-list">
                    `;

                    item.ingredients_info.ingredients.forEach(ingredient => {
                        html += `<span class="ingredient-tag">${ingredient}</span>`;
                    });

                    html += `
                            </div>
                        </div>
                    `;
                }

                html += `</div>`;
            });

            // Close details section
            html += `
                    </div>
                </div>
            `;

            resultsContent.innerHTML = html;
        }

        function toggleDetails() {
            const detailsContent = document.getElementById('detailsContent');
            const detailsArrow = document.getElementById('detailsArrow');

            if (detailsContent.classList.contains('show')) {
                detailsContent.classList.remove('show');
                detailsArrow.classList.remove('open');
            } else {
                detailsContent.classList.add('show');
                detailsArrow.classList.add('open');
            }
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
    if not segmentation_agent:
        return jsonify({'error': 'Food analysis agent not initialized. Please set ANTHROPIC_API_KEY environment variable.'}), 500

    if not nutrition_agent:
        return jsonify({'error': 'Nutrition agent not initialized. Please set ANTHROPIC_API_KEY environment variable.'}), 500

    if not ingredient_agent:
        return jsonify({'error': 'Ingredient agent not initialized. Please set ANTHROPIC_API_KEY environment variable.'}), 500

    if not ghg_agent:
        return jsonify({'error': 'GHG emission agent not initialized. Please set ANTHROPIC_API_KEY environment variable.'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read image bytes
        image_bytes = file.read()

        # Step 1: Analyze the food plate using segmentation agent
        segmentation_result = segmentation_agent.analyze_food_plate(
            image_bytes=image_bytes,
            filename=file.filename
        )

        if 'error' in segmentation_result:
            return jsonify(segmentation_result), 500

        # Step 2: Get nutrition and ingredient information for each food item
        food_items = segmentation_result.get('items', [])

        if not food_items:
            return jsonify(segmentation_result)

        # Prepare inputs for agents
        nutrition_input = {item['food']: item['weight'] for item in food_items}
        ingredient_input = [item['food'] for item in food_items]
        ghg_input = {item['food']: item['weight'] for item in food_items}

        # Call all three agents in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            nutrition_future = executor.submit(nutrition_agent.estimate_nutrition, nutrition_input)
            ingredient_future = executor.submit(ingredient_agent.analyze_ingredients, ingredient_input)
            ghg_future = executor.submit(ghg_agent.calculate_emissions, ghg_input)

            # Get results
            nutrition_data = nutrition_future.result()
            ingredient_data = ingredient_future.result()
            ghg_data = ghg_future.result()

        # Combine segmentation, nutrition, ingredient, and GHG data
        for item in food_items:
            food_name = item['food']
            if food_name in nutrition_data:
                item['nutrition'] = nutrition_data[food_name]
            if food_name in ingredient_data:
                item['ingredients_info'] = ingredient_data[food_name]
            if food_name in ghg_data:
                item['ghg_emission'] = ghg_data[food_name]

        return jsonify(segmentation_result)

    except Exception as e:
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
