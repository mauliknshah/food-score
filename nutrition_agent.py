import json
from typing import Dict, Any
from claude_service import get_claude_client, DEFAULT_MODEL


class NutritionAgent:
    """Agent that uses Claude to estimate nutritional information for food items."""

    def __init__(self, api_key: str = None):
        """
        Initialize the agent with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.client = get_claude_client(api_key)

    def estimate_nutrition(self, food_items: dict) -> dict:
        """
        Estimate nutritional information for food items using Claude API.

        Args:
            food_items: Dictionary with food names as keys and weights in grams as values
                       e.g., {"bread": 22, "meat": 100, "tomato": 50, "cheese": 23}

        Returns:
            Dictionary with nutritional information for each food item
        """

        prompt = f"""Given the following food items with their weights in grams, provide the daily value percentages for each item.

Food items:
{json.dumps(food_items, indent=2)}

For each food item, provide:
1. Calories (in kcal)
2. Daily value percentages for main nutritions: protein, fat, carbohydrates, fiber, sugar, sodium, potassium
3. Daily value percentages for vitamins and minerals: vitamin_a, vitamin_c, vitamin_d, calcium, iron, vitamin_b12

Return ONLY a JSON object with this exact structure:
{{
  "food_name": {{
    "calories": <number>,
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

IMPORTANT: Daily value percentages should be whole numbers representing the percentage of recommended daily intake based on a 2000 calorie diet.
Calories should be in kcal.
Be as accurate as possible based on standard nutritional databases."""

        message = self.client.messages.create(
            model=DEFAULT_MODEL,
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
    agent = NutritionAgent()

    sample_input = {
        "bread": 22,
        "meat": 100,
        "tomato": 50,
        "cheese": 23
    }

    result = agent.estimate_nutrition(sample_input)
    print(json.dumps(result, indent=2))
