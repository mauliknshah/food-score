import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ImageUploadZone } from "@/components/image-upload-zone";
import { FoodAnalysisResults } from "@/components/food-analysis-results";
import { LoadingState } from "@/components/loading-state";
import { Card, CardContent } from "@/components/ui/card";
import { Utensils, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/queryClient";
import type { AnalysisResponse } from "@shared/schema";

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);

  const analyzeImageMutation = useMutation({
    mutationFn: async (imageData: string): Promise<AnalysisResponse> => {
      const response = await apiRequest("POST", "/api/analyze-food", {
        image: imageData,
      });
      return response.json();
    },
    onSuccess: (result) => {
      setAnalysisResult(result);
    },
    onError: (error) => {
      console.error("Analysis failed:", error);
      setAnalysisResult({
        success: false,
        food_items: [],
        overall_confidence: 0,
        error: "Failed to analyze image. Please try again.",
      });
    },
  });

  const handleImageSelect = (imageData: string) => {
    setSelectedImage(imageData);
    setAnalysisResult(null);
    analyzeImageMutation.mutate(imageData);
  };

  const handleAnalyzeNew = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <Utensils className="text-primary-foreground" size={20} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">Food Score</h1>
                <p className="text-xs text-muted-foreground">AI Meal Recognition</p>
              </div>
            </div>
            <Button
              variant="secondary"
              size="icon"
              className="w-10 h-10"
              data-testid="button-settings"
            >
              <Settings size={16} />
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        {/* Upload Section */}
        {!selectedImage && !analyzeImageMutation.isPending && (
          <ImageUploadZone onImageSelect={handleImageSelect} />
        )}

        {/* Legend Section */}
        <div className="bg-card rounded-lg shadow-sm border border-border p-4 mb-6">
          <h3 className="text-sm font-semibold text-foreground mb-3">Dietary Classification</h3>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full" style={{ backgroundColor: "hsl(var(--vegan))" }}></div>
              <span className="text-sm text-foreground">Vegan</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full" style={{ backgroundColor: "hsl(var(--vegetarian))" }}></div>
              <span className="text-sm text-foreground">Vegetarian</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full" style={{ backgroundColor: "hsl(var(--meat))" }}></div>
              <span className="text-sm text-foreground">Contains Meat</span>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {analyzeImageMutation.isPending && <LoadingState />}

        {/* Results Section */}
        {selectedImage && analysisResult && !analyzeImageMutation.isPending && (
          <FoodAnalysisResults
            imageData={selectedImage}
            analysisResult={analysisResult}
            onAnalyzeNew={handleAnalyzeNew}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-8 border-t border-border bg-muted/30">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>© 2024 Food Score</span>
              <span>•</span>
              <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
              <span>•</span>
              <a href="#" className="hover:text-foreground transition-colors">Terms</a>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-xs text-muted-foreground">Powered by Anthropic Claude</span>
              <div className="flex space-x-2">
                <a href="#" className="w-8 h-8 bg-secondary hover:bg-accent rounded-full flex items-center justify-center transition-colors">
                  <span className="text-secondary-foreground text-sm">𝕏</span>
                </a>
                <a href="#" className="w-8 h-8 bg-secondary hover:bg-accent rounded-full flex items-center justify-center transition-colors">
                  <span className="text-secondary-foreground text-sm">GH</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
