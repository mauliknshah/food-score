import json
from typing import Dict, Any
from claude_service import get_claude_client, DEFAULT_MODEL


class GHGEmissionAgent:
    """Agent that uses Claude to calculate greenhouse gas emissions for food items."""

    def __init__(self, api_key: str = None):
        """
        Initialize the agent with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.client = get_claude_client(api_key)

    def calculate_emissions(self, food_items: dict) -> dict:
        """
        Calculate greenhouse gas emissions for food items using Claude API.

        Args:
            food_items: Dictionary with food names as keys and weights in grams as values
                       e.g., {"beef": 100, "rice": 150, "broccoli": 80}

        Returns:
            Dictionary with GHG emission information for each food item
            Format: {
                "food_name": {
                    "co2_equivalent_kg": <number>,
                    "co2_kg": <number>,
                    "methane_kg": <number>,
                    "nitrous_oxide_kg": <number>,
                    "co2e_per_kg_food": <number>,
                    "emission_category": "low|medium|high|very_high"
                }
            }
        """

        prompt = f"""Given the following food items with their weights in grams, calculate the comprehensive greenhouse gas (GHG) emissions for each item, including CO2, methane (CH4), and nitrous oxide (N2O).

Food items:
{json.dumps(food_items, indent=2)}

For each food item, provide:
1. Total CO2 equivalent in kilograms (kg CO2e) for the given weight - this is the overall climate impact
2. CO2 emissions in kilograms (kg CO2) for the given weight - direct carbon dioxide emissions
3. Methane emissions in kilograms (kg CH4) for the given weight - especially significant for ruminant animals
4. Nitrous oxide emissions in kilograms (kg N2O) for the given weight - from fertilizers and manure
5. CO2e per kg of food (emission intensity) - this is the standard emission rate per kilogram of this food type
6. Emission category based on the CO2e per kg of food (NOT the total weight on plate):
   - "low": 0-2 kg CO2e per kg of food (e.g., most vegetables, fruits, legumes)
   - "medium": 2-4 kg CO2e per kg of food (e.g., tofu, dairy, nuts)
   - "high": 4-8 kg CO2e per kg of food (e.g., chicken, pork, fish, eggs, rice)
   - "very_high": > 8 kg CO2e per kg of food (e.g., beef, lamb, cheese)

Return ONLY a JSON object with this exact structure:
{{
  "food_name": {{
    "co2_equivalent_kg": <number for the given weight>,
    "co2_kg": <number for the given weight>,
    "methane_kg": <number for the given weight>,
    "nitrous_oxide_kg": <number for the given weight>,
    "co2e_per_kg_food": <number - emission intensity>,
    "emission_category": "<low|medium|high|very_high based on co2e_per_kg_food>"
  }}
}}

IMPORTANT NOTES:
- Use the exact food names provided in the input as keys in the output JSON
- CO2 equivalent accounts for Global Warming Potential (GWP): Methane has 28x impact of CO2, N2O has 265x impact
- For beef and lamb, methane from enteric fermentation (cow burps) is the largest component
- Include emissions from: production, processing, and packaging (exclude transportation)
- All values should be decimal numbers
- Consider the full lifecycle from farm to consumer
- CRITICAL: The emission category must be based on co2e_per_kg_food (emission intensity), NOT on the plate weight
  Example: 50g of beef should be "very_high" category because beef is ~27 kg CO2e/kg, even though total is only 1.35 kg CO2e

Reference values for common foods (emission intensity per kg) with NEW categories:
- Beef: ~27 kg CO2e/kg food → very_high category (>8)
- Lamb: ~24 kg CO2e/kg food → very_high category (>8)
- Cheese: ~11 kg CO2e/kg food → very_high category (>8)
- Pork: ~7 kg CO2e/kg food → high category (4-8)
- Chicken: ~6 kg CO2e/kg food → high category (4-8)
- Fish (farmed): ~5 kg CO2e/kg food → high category (4-8)
- Eggs: ~4.5 kg CO2e/kg food → high category (4-8)
- Rice: ~4 kg CO2e/kg food → high category (4-8)
- Dairy milk: ~3 kg CO2e/kg food → medium category (2-4)
- Nuts: ~2.5 kg CO2e/kg food → medium category (2-4)
- Tofu: ~2 kg CO2e/kg food → medium category (2-4)
- Beans/Legumes (dry): ~0.9 kg CO2e/kg food → low category (0-2)
- Green beans (fresh): ~0.4 kg CO2e/kg food → low category (0-2)
- Peas: ~0.4 kg CO2e/kg food → low category (0-2)
- Broccoli: ~0.4 kg CO2e/kg food → low category (0-2)
- Tomatoes: ~0.7 kg CO2e/kg food → low category (0-2)
- Lettuce/leafy greens: ~0.3 kg CO2e/kg food → low category (0-2)
- Carrots: ~0.3 kg CO2e/kg food → low category (0-2)
- Potatoes: ~0.3 kg CO2e/kg food → low category (0-2)
- Onions: ~0.3 kg CO2e/kg food → low category (0-2)
- Apples: ~0.4 kg CO2e/kg food → low category (0-2)
- Bananas: ~0.7 kg CO2e/kg food → low category (0-2)
- Most vegetables: ~0.3-1.0 kg CO2e/kg food → low category (0-2)
- Most fruits: ~0.3-1.0 kg CO2e/kg food → low category (0-2)

Be as accurate as possible based on scientific lifecycle assessment (LCA) databases."""

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
            emission_data = json.loads(json_str)
            return emission_data
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse emission data from API response: {e}")


if __name__ == "__main__":
    # Example usage
    agent = GHGEmissionAgent()

    sample_input = {
        "beef": 100,
        "rice": 150,
        "broccoli": 80,
        "chicken": 120
    }

    result = agent.calculate_emissions(sample_input)
    print(json.dumps(result, indent=2))
