// Note: This file is not currently used in the application architecture.
// All OpenAI API calls are handled server-side for security reasons.
// The actual implementation is in server/services/foodAnalysis.ts

import OpenAI from "openai";

/*
This client-side OpenAI integration is provided for reference but is NOT used
in the current application. All OpenAI API calls happen server-side to:
1. Keep API keys secure
2. Avoid CORS issues
3. Better error handling and rate limiting

The actual food analysis happens in server/services/foodAnalysis.ts
*/

// the newest OpenAI model is "gpt-5" which was released August 7, 2025. do not change this unless explicitly requested by the user
const openai = new OpenAI({ 
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Not recommended for production
});

// This function would be used if we wanted client-side OpenAI calls
// However, the current app uses server-side calls for security
export async function analyzeImageClientSide(base64Image: string): Promise<{
  food_items: Array<{
    name: string;
    dietary_classification: "vegan" | "vegetarian" | "meat";
    confidence: number;
    position?: { x: number; y: number };
  }>;
  overall_confidence: number;
}> {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-5",
      messages: [
        {
          role: "system",
          content: `You are an expert food identification AI. Analyze the uploaded meal photo and identify all visible food items. For each food item, provide:
1. The specific name of the food item
2. Dietary classification: "vegan" (plant-based only), "vegetarian" (may contain dairy/eggs but no meat), or "meat" (contains any animal protein)
3. Confidence score (0-100) for the identification
4. Approximate position in the image (x,y coordinates as percentages 0-100)

Respond with JSON in this exact format:
{
  "food_items": [
    {
      "name": "Food item name",
      "dietary_classification": "vegan|vegetarian|meat",
      "confidence": 95,
      "position": {"x": 50, "y": 30}
    }
  ],
  "overall_confidence": 90
}

Be accurate with dietary classifications:
- Vegan: Only plant-based ingredients (fruits, vegetables, grains, legumes, nuts, seeds)
- Vegetarian: Plant-based + dairy/eggs but NO meat, poultry, fish, or seafood
- Meat: Contains any animal protein including meat, poultry, fish, seafood, or meat-derived ingredients`
        },
        {
          role: "user",
          content: [
            {
              type: "text",
              text: "Please analyze this meal photo and identify all the food items with their dietary classifications and positions."
            },
            {
              type: "image_url",
              image_url: {
                url: `data:image/jpeg;base64,${base64Image}`
              }
            }
          ],
        },
      ],
      response_format: { type: "json_object" },
      max_tokens: 1000,
    });

    const result = JSON.parse(response.choices[0].message.content || "{}");
    
    return {
      food_items: (result.food_items || []).map((item: any) => ({
        name: item.name || "Unknown Food Item",
        dietary_classification: ["vegan", "vegetarian", "meat"].includes(item.dietary_classification) 
          ? item.dietary_classification 
          : "vegan",
        confidence: Math.min(100, Math.max(0, item.confidence || 0)),
        position: item.position || { x: 50, y: 50 },
      })),
      overall_confidence: Math.min(100, Math.max(0, result.overall_confidence || 0)),
    };

  } catch (error) {
    console.error("Client-side food analysis error:", error);
    throw new Error(error instanceof Error ? error.message : "Analysis failed");
  }
}

// Export the openai instance for potential future use
export { openai };
