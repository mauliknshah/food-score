# Food-Score 🍽️

A comprehensive food analysis application that evaluates your meals across multiple dimensions: nutrition, environmental impact, animal welfare, and dietary preferences. Using AI-powered agents, Food-Score provides detailed insights to help you make informed, sustainable, and compassionate food choices.

## Features

### 📊 Multi-Dimensional Food Analysis

1. **Food Segmentation** 📸
   - AI-powered image recognition to identify food items
   - Automatic weight estimation for each item

2. **Nutritional Analysis** 🔥
   - Complete nutrition breakdown for all 14 key nutrients
   - Daily value percentages based on 2000 calorie diet
   - Total meal calorie count

3. **Greenhouse Gas Emissions** 🌍
   - Comprehensive GHG impact including CO₂, CH₄, and N₂O
   - Color-coded categories based on emission intensity
   - Both total and per-kg emission rates

4. **Compassion Score** 💚
   - Animal welfare impact scoring (-7 to 2)
   - Categorized by impact level (Low/Medium/Positive)
   - Weighted by food quantity

5. **Dietary Classification** 🌱
   - Automatic diet type identification (Vegan, Vegetarian, Pescatarian, Meat)
   - Complete ingredient breakdown for each food item

### 🎯 Key Highlights

- **Overall Impact Summary**: See total GHG emissions, compassion score, and complete nutritional profile at a glance
- **Detailed Item View**: Expandable section with per-item breakdowns
- **Color-Coded Categories**: Visual indicators for quick understanding
- **Mobile-Friendly**: Responsive design optimized for all devices
- **Real-Time Analysis**: Fast parallel processing of multiple AI agents

## Technology Stack

- **Backend**: Flask (Python)
- **AI/ML**: Anthropic Claude (Sonnet 4.5)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Concurrent Processing**: Python ThreadPoolExecutor for parallel agent execution

## Architecture

The application uses a multi-agent architecture where specialized agents handle different aspects of food analysis:

```
Food Image → Segmentation Agent → [Nutrition Agent + GHG Agent + Ingredient Agent + Compassion Agent] → Combined Results
```

All agents leverage Claude AI with carefully crafted prompts for accurate analysis.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Anthropic API key

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd food-score
```

### Step 2 Set Up Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add your Anthropic API key to the `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
```

To get an Anthropic API key:
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### Step 3 Run the Application

```bash
python mobile_app.py
```

The application will start on `http://0.0.0.0:8000`