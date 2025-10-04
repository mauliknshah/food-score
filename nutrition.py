import anthropic
import json
import os


def estimate_nutrition(food_items: dict) -> dict:
    """
    Estimate nutritional information for food items using Claude API.

    Args:
        food_items: Dictionary with food names as keys and weights in grams as values
                   e.g., {"bread": 22, "meat": 100, "tomato": 50, "cheese": 23}

    Returns:
        Dictionary with nutritional information for each food item
    """
    client = anthropic.Anthropic(api_key="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")

    prompt = f"""Given the following food items with their weights in grams, provide exact nutritional information for each item.

Food items:
{json.dumps(food_items, indent=2)}

For each food item, provide:
1. Calories (in kcal)
2. Main nutritions (in grams): protein, fat, carbohydrates, fiber, sugar, sodium, potassium
3. Other nutritions: vitamins and minerals with their amounts
4. Daily value percentages for each nutrient

Return ONLY a JSON object with this exact structure:
{{
  "food_name": {{
    "calories": <number>,
    "main_nutritions": {{
      "protein": <number>,
      "fat": <number>,
      "carbohydrates": <number>,
      "fiber": <number>,
      "sugar": <number>,
      "sodium": <number>,
      "potassium": <number>
    }},
    "other_nutritions": {{
      "vitamin_a": <number>,
      "vitamin_c": <number>,
      "vitamin_d": <number>,
      "calcium": <number>,
      "iron": <number>,
      "vitamin_b12": <number>
    }},
    "daily_value_percentages": {{
      "protein": <number>,
      "fat": <number>,
      "carbohydrates": <number>,
      "fiber": <number>,
      "sugar": <number>,
      "sodium": <number>,
      "potassium": <number>,
      "vitamin_a": <number>,
      "vitamin_c": <number>,
      "vitamin_d": <number>,
      "calcium": <number>,
      "iron": <number>,
      "vitamin_b12": <number>
    }}
  }}
}}

IMPORTANT: ALL nutrition values MUST be numeric values in grams (g), including vitamins and minerals. Do NOT use units like mg, mcg, IU, etc. Convert everything to grams. For example, 240 IU of vitamin A should be converted to grams (approximately 0.000072 g), 184 mg calcium should be 0.184 g, 0.1 mcg vitamin D should be 0.0000001 g.
Calories should be in kcal.
Daily value percentages should be whole numbers representing the percentage of recommended daily intake.
Be as accurate as possible based on standard nutritional databases."""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract JSON from response
    response_text = message.content[0].text

    # Try to parse JSON from the response
    try:
        # Look for JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        nutrition_data = json.loads(json_str)
        return nutrition_data
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse nutrition data from API response: {e}")


if __name__ == "__main__":
    # Example usage
    sample_input = {
        "bread": 22,
        "meat": 100,
        "tomato": 50,
        "cheese": 23
    }

    result = estimate_nutrition(sample_input)
    print(json.dumps(result, indent=2))
