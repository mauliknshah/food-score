import json
from typing import Dict, Any
from claude_service import get_claude_client, DEFAULT_MODEL


class CompassionScoreAgent:
    """Agent that calculates compassion scores based on animal welfare and environmental impact."""

    def __init__(self, api_key: str = None):
        """
        Initialize the agent with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.client = get_claude_client(api_key)

    def calculate_scores(self, food_items: dict) -> dict:
        """
        Calculate compassion scores for food items.

        Args:
            food_items: Dictionary with food names as keys and weights in grams as values
                       e.g., {"beef": 100, "milk": 200, "broccoli": 150}

        Returns:
            Dictionary with compassion score information for each food item
            Format: {
                "food_name": {
                    "compassion_score": <number between -7 and 2>,
                    "category": "killed_animal|animal_product|plant_based",
                    "reasoning": "<brief explanation>"
                }
            }
        """

        prompt = f"""Given the following food items with their weights in grams, calculate a compassion score for each item based on animal welfare and environmental ethics.

Food items:
{json.dumps(food_items, indent=2)}

SCORING SYSTEM:

1. KILLED ANIMALS (score: -5 to -7):
   - Score based on animal intelligence and sentience
   - Highly intelligent animals (pigs, octopus, cows): -7
   - Intelligent animals (chickens, turkeys, fish): -6
   - Less complex animals (shellfish, insects): -5

2. DAIRY & ANIMAL-DERIVED PRODUCTS (score: -2 to -1):
   - Products requiring animal exploitation but not killing
   - Dairy products (milk, cheese, yogurt, butter): -2
   - Eggs: -2
   - Honey: -1

3. PLANT-BASED FOODS (score: 1 to 2):
   - Score based on environmental impact (lower impact = higher score)
   - Very low impact (most vegetables, fruits, legumes): 2
   - Moderate impact (grains, nuts, processed plant foods): 1.5
   - Higher impact plant foods (water-intensive crops, imported): 1

COMPASSION CATEGORIES (for overall meal score):
- LOW (negative impact): < -3
- MEDIUM (needs improvement): -3 to 0
- POSITIVE (compassionate choice): >= 1

For each food item, provide:
1. Compassion score (between -7 and 2)
2. Category: "killed_animal", "animal_product", or "plant_based"
3. Brief reasoning (one sentence)

Return ONLY a JSON object with this exact structure:
{{
  "food_name": {{
    "compassion_score": <number>,
    "category": "<killed_animal|animal_product|plant_based>",
    "reasoning": "<brief explanation>"
  }}
}}

IMPORTANT NOTES:
- Use the exact food names provided in the input as keys in the output JSON
- Compassion score must be a number (integer or decimal) between -7 and 2
- Consider the inherent nature of the food, not the quantity
- The weight will be used as a multiplying factor in the final calculation
- Be consistent with scoring across similar food items

Examples:
- Beef: {{"compassion_score": -7, "category": "killed_animal", "reasoning": "Cattle are highly intelligent, sentient animals"}}
- Pork: {{"compassion_score": -7, "category": "killed_animal", "reasoning": "Pigs are extremely intelligent and emotionally complex"}}
- Chicken: {{"compassion_score": -6, "category": "killed_animal", "reasoning": "Chickens are sentient birds with social behaviors"}}
- Fish (salmon): {{"compassion_score": -6, "category": "killed_animal", "reasoning": "Fish are sentient creatures capable of pain"}}
- Shrimp: {{"compassion_score": -5, "category": "killed_animal", "reasoning": "Crustaceans have simpler nervous systems but still sentient"}}
- Milk: {{"compassion_score": -2, "category": "animal_product", "reasoning": "Dairy industry involves animal exploitation"}}
- Eggs: {{"compassion_score": -2, "category": "animal_product", "reasoning": "Egg production involves chicken exploitation"}}
- Honey: {{"compassion_score": -1, "category": "animal_product", "reasoning": "Bee exploitation but minimal harm"}}
- Beans: {{"compassion_score": 2, "category": "plant_based", "reasoning": "Low environmental impact, highly sustainable"}}
- Broccoli: {{"compassion_score": 2, "category": "plant_based", "reasoning": "Very low environmental footprint"}}
- Spinach: {{"compassion_score": 2, "category": "plant_based", "reasoning": "Nutrient-dense with minimal environmental cost"}}
- Rice: {{"compassion_score": 1.5, "category": "plant_based", "reasoning": "Moderate environmental impact from water use"}}
- Almonds: {{"compassion_score": 1, "category": "plant_based", "reasoning": "Higher water use and often imported"}}

Be as accurate as possible based on animal sentience research and environmental data."""

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
            compassion_data = json.loads(json_str)
            return compassion_data
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse compassion score data from API response: {e}")


if __name__ == "__main__":
    # Example usage
    agent = CompassionScoreAgent()

    sample_input = {
        "beef": 100,
        "chicken": 120,
        "milk": 200,
        "eggs": 50,
        "broccoli": 150,
        "rice": 200
    }

    result = agent.calculate_scores(sample_input)
    print(json.dumps(result, indent=2))
