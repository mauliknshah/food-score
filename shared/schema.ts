import { z } from "zod";

export const foodItemSchema = z.object({
  name: z.string(),
  dietary_classification: z.enum(["vegan", "vegetarian", "meat"]),
  confidence: z.number().min(0).max(100),
  weight_grams: z.number().optional(),
  position: z.object({
    x: z.number(),
    y: z.number(),
  }).optional(),
});

export const analysisRequestSchema = z.object({
  image: z.string(), // base64 encoded image
});

export const analysisResponseSchema = z.object({
  success: z.boolean(),
  food_items: z.array(foodItemSchema),
  overall_confidence: z.number().min(0).max(100),
  error: z.string().optional(),
});

export type FoodItem = z.infer<typeof foodItemSchema>;
export type AnalysisRequest = z.infer<typeof analysisRequestSchema>;
export type AnalysisResponse = z.infer<typeof analysisResponseSchema>;
