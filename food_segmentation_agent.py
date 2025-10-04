import anthropic
import base64
import json
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class FoodSegmentationAgent:
    """Agent that uses Claude to segment food images and estimate weights."""

    def __init__(self, api_key: str = None):
        """
        Initialize the agent with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set as environment variable")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Encode image to base64.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (base64_string, media_type)
        """
        with open(image_path, 'rb') as image_file:
            image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')

        # Determine media type from extension
        ext = image_path.lower().split('.')[-1]
        media_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        return image_data, media_type

    def encode_image_bytes(self, image_bytes: bytes, filename: str = 'image.jpg') -> tuple[str, str]:
        """
        Encode image bytes to base64.

        Args:
            image_bytes: Image data as bytes
            filename: Filename to determine media type

        Returns:
            Tuple of (base64_string, media_type)
        """
        image_data = base64.standard_b64encode(image_bytes).decode('utf-8')

        ext = filename.lower().split('.')[-1]
        media_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        return image_data, media_type

    def analyze_food_plate(self, image_path: str = None, image_bytes: bytes = None,
                          filename: str = 'image.jpg') -> Dict[str, Any]:
        """
        Analyze a food plate image and segment it into different food items with weight estimates.

        Args:
            image_path: Path to the image file (optional if image_bytes provided)
            image_bytes: Image data as bytes (optional if image_path provided)
            filename: Filename for image_bytes to determine media type

        Returns:
            Dictionary containing segmented food items with details
        """
        if image_path:
            image_data, media_type = self.encode_image(image_path)
        elif image_bytes:
            image_data, media_type = self.encode_image_bytes(image_bytes, filename)
        else:
            raise ValueError("Either image_path or image_bytes must be provided")

        prompt = """Analyze this food plate image and segment it into individual food items. For each food item, provide only:

1. Name of the food item
2. Estimated weight in grams (provide a reasonable estimate based on typical portions)

Please provide your response in JSON format with the following structure:
{
  "items": [
    {
      "food": "<food name>",
      "weight": <estimated weight>
    }
  ]
}

Be as accurate as possible with weight estimates based on standard portion sizes. If the image doesn't contain food, return an empty items array."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # Extract the response text
        response_text = message.content[0].text

        # Try to parse JSON from the response
        try:
            # Look for JSON in the response (might be wrapped in markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text

            result = json.loads(json_str)
            result['raw_response'] = response_text
            return result
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw response
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text
            }

    def analyze_food_plate_structured(self, image_path: str = None, image_bytes: bytes = None,
                                     filename: str = 'image.jpg') -> List[Dict[str, Any]]:
        """
        Analyze food plate and return a simplified list of food items.

        Args:
            image_path: Path to the image file
            image_bytes: Image data as bytes
            filename: Filename for media type detection

        Returns:
            List of dictionaries with food item details
        """
        result = self.analyze_food_plate(image_path, image_bytes, filename)

        if 'error' in result:
            return []

        return result.get('items', [])


if __name__ == '__main__':
    # Example usage
    agent = FoodSegmentationAgent()

    # Test with an image file
    # result = agent.analyze_food_plate(image_path='path/to/food_plate.jpg')
    # print(json.dumps(result, indent=2))

    print("FoodSegmentationAgent initialized successfully!")
    print("Use agent.analyze_food_plate() to analyze food images.")
