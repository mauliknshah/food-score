import type { Express } from "express";
import { createServer, type Server } from "http";
import { analysisRequestSchema } from "@shared/schema";
import { foodAnalysisService } from "./services/foodAnalysis";

export async function registerRoutes(app: Express): Promise<Server> {
  // Food analysis endpoint
  app.post("/api/analyze-food", async (req, res) => {
    try {
      const validatedData = analysisRequestSchema.parse(req.body);
      
      // Validate base64 image format
      if (!validatedData.image.startsWith("data:image/")) {
        return res.status(400).json({
          success: false,
          food_items: [],
          overall_confidence: 0,
          error: "Invalid image format. Please upload a valid image file.",
        });
      }

      // Extract base64 data (remove data:image/jpeg;base64, prefix)
      const base64Data = validatedData.image.split(",")[1];
      
      if (!base64Data) {
        return res.status(400).json({
          success: false,
          food_items: [],
          overall_confidence: 0,
          error: "Invalid image data format.",
        });
      }

      const result = await foodAnalysisService.analyzeImage(base64Data);
      
      res.json(result);
      
    } catch (error) {
      console.error("API error:", error);
      res.status(500).json({
        success: false,
        food_items: [],
        overall_confidence: 0,
        error: "Server error occurred while analyzing the image.",
      });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
