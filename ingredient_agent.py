import json
from typing import Dict, List, Any
from claude_service import get_claude_client, DEFAULT_MODEL


class IngredientAgent:
    """Agent that uses Claude to identify ingredients and categorize food by diet type."""

    def __init__(self, api_key: str = None):
        """
        Initialize the agent with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.client = get_claude_client(api_key)

    def analyze_ingredients(self, food_items: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze food items to identify ingredients and categorize by diet type.

        Args:
            food_items: List of food names
                       e.g., ["grilled chicken", "caesar salad", "pasta"]

        Returns:
            Dictionary with food names as keys and their ingredient info as values
            Format: {
                "food_name": {
                    "diet": "vegan|vegetarian|pescatarian|meat",
                    "ingredients": ["ingredient1", "ingredient2", ...]
                }
            }
        """

        prompt = f"""Given the following food items, identify all the ingredients used in making each food and categorize each food item by diet type.

Food items:
{json.dumps(food_items, indent=2)}

For each food item, provide:
1. Diet category (choose ONE that best fits):
   - "vegan": Contains no animal products (no meat, fish, dairy, eggs, honey)
   - "vegetarian": Contains no meat or fish, but may contain dairy, eggs
   - "pescatarian": Contains fish/seafood but no other meat
   - "meat": Contains meat (chicken, beef, pork, lamb, etc.)

2. Complete list of ingredients typically used to make this food

Return ONLY a JSON object with this exact structure:
{{
  "food_name": {{
    "diet": "<vegan|vegetarian|pescatarian|meat>",
    "ingredients": ["ingredient1", "ingredient2", "ingredient3"]
  }}
}}

IMPORTANT:
- Use the exact food names provided in the input as keys in the output JSON
- Be comprehensive with ingredients - include all major components
- Choose the most restrictive diet category (e.g., if food has chicken, it's "meat" not "pescatarian")
- List ingredients in order of prominence/quantity
- Be specific with ingredient names (e.g., "all-purpose flour" not just "flour")"""

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
            ingredient_data = json.loads(json_str)
            return ingredient_data
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse ingredient data from API response: {e}")


if __name__ == "__main__":
    # Example usage
    agent = IngredientAgent()

    sample_input = [
        "grilled chicken",
        "caesar salad",
        "vegetable stir fry",
        "salmon sushi"
    ]

    result = agent.analyze_ingredients(sample_input)
    print(json.dumps(result, indent=2))
