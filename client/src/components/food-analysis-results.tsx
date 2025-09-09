import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Share, RotateCcw, CheckCircle, Sparkles } from "lucide-react";
import type { FoodItem, AnalysisResponse } from "@shared/schema";
import { cn } from "@/lib/utils";

interface FoodAnalysisResultsProps {
  imageData: string;
  analysisResult: AnalysisResponse;
  onAnalyzeNew: () => void;
}

export function FoodAnalysisResults({ 
  imageData, 
  analysisResult, 
  onAnalyzeNew 
}: FoodAnalysisResultsProps) {
  const [selectedItem, setSelectedItem] = useState<FoodItem | null>(null);

  const getDietaryColor = (classification: string) => {
    switch (classification) {
      case "vegan":
        return "hsl(var(--vegan))";
      case "vegetarian":
        return "hsl(var(--vegetarian))";
      case "meat":
        return "hsl(var(--meat))";
      default:
        return "hsl(var(--muted))";
    }
  };

  const getDietaryDescription = (classification: string) => {
    switch (classification) {
      case "vegan":
        return "Vegan friendly";
      case "vegetarian":
        return "Vegetarian friendly";
      case "meat":
        return "Contains meat ingredients";
      default:
        return "Unknown dietary classification";
    }
  };

  const handleExportResults = () => {
    const exportData = {
      analysis_date: new Date().toISOString(),
      food_items: analysisResult.food_items,
      overall_confidence: analysisResult.overall_confidence,
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `food-analysis-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Food Analysis Results",
          text: `Found ${analysisResult.food_items.length} food items with ${analysisResult.overall_confidence}% confidence`,
        });
      } catch (error) {
        console.log("Share failed:", error);
      }
    } else {
      // Fallback: copy to clipboard
      const shareText = `Food Analysis Results:\n${analysisResult.food_items
        .map(item => `• ${item.name} (${item.dietary_classification})`)
        .join("\n")}`;
      
      navigator.clipboard.writeText(shareText);
      alert("Analysis results copied to clipboard!");
    }
  };

  if (!analysisResult.success) {
    return (
      <Card className="shadow-sm border border-border">
        <CardContent className="p-6 text-center">
          <div className="text-destructive mb-4">
            <h3 className="text-lg font-semibold">Analysis Failed</h3>
            <p className="text-sm mt-2">{analysisResult.error}</p>
          </div>
          <Button onClick={onAnalyzeNew} variant="outline" data-testid="button-try-again">
            <RotateCcw size={16} className="mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm border border-border overflow-hidden" data-testid="analysis-results">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">Analysis Results</h3>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Sparkles size={16} />
            <span>AI Powered</span>
          </div>
        </div>
      </div>
      
      {/* Image with Annotations */}
      <div className="relative bg-muted">
        <img 
          src={imageData} 
          alt="Analyzed meal plate" 
          className="w-full h-auto max-h-96 object-contain"
          data-testid="analyzed-image"
        />
        
        {/* Annotation Overlays */}
        <svg 
          className="absolute inset-0 w-full h-full pointer-events-none" 
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          {analysisResult.food_items.map((item, index) => (
            item.position && (
              <g key={index}>
                {/* Annotation line */}
                <line
                  x1={item.position.x}
                  y1={item.position.y}
                  x2={item.position.x + (index % 2 === 0 ? -10 : 10)}
                  y2={item.position.y - 10}
                  stroke={getDietaryColor(item.dietary_classification)}
                  strokeWidth="0.5"
                  strokeDasharray="2,2"
                />
                {/* Annotation point */}
                <circle
                  cx={item.position.x}
                  cy={item.position.y}
                  r="1"
                  fill={getDietaryColor(item.dietary_classification)}
                />
              </g>
            )
          ))}
        </svg>
        
        {/* Food Labels */}
        {analysisResult.food_items.slice(0, 4).map((item, index) => {
          const positions = [
            { top: "4px", left: "4px" },
            { top: "4px", right: "4px" },
            { bottom: "4px", right: "4px" },
            { bottom: "4px", left: "4px" },
          ];
          const position = positions[index] || positions[0];

          return (
            <div
              key={index}
              className="absolute food-badge rounded-lg px-3 py-2 shadow-lg cursor-pointer hover:scale-105 transition-transform"
              style={position}
              onClick={() => setSelectedItem(selectedItem?.name === item.name ? null : item)}
              data-testid={`food-label-${index}`}
            >
              <div className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getDietaryColor(item.dietary_classification) }}
                ></div>
                <span className="text-sm font-medium">{item.name}</span>
              </div>
            </div>
          );
        })}
        
        {/* Confidence indicator */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 food-badge rounded-full px-3 py-1 shadow-lg">
          <div className="flex items-center space-x-1">
            <CheckCircle className="text-green-500" size={12} />
            <span className="text-xs font-medium">{analysisResult.overall_confidence}% Confidence</span>
          </div>
        </div>
      </div>
      
      {/* Detected Items List */}
      <div className="p-4">
        <h4 className="text-sm font-semibold text-foreground mb-3">
          Detected Food Items ({analysisResult.food_items.length})
        </h4>
        <div className="space-y-3">
          {analysisResult.food_items.map((item, index) => (
            <div
              key={index}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg transition-all cursor-pointer",
                selectedItem?.name === item.name ? "bg-accent" : "bg-secondary hover:bg-accent"
              )}
              onClick={() => setSelectedItem(selectedItem?.name === item.name ? null : item)}
              data-testid={`food-item-${index}`}
            >
              <div className="flex items-center space-x-3">
                <div
                  className="w-6 h-6 rounded-full"
                  style={{ backgroundColor: getDietaryColor(item.dietary_classification) }}
                ></div>
                <div>
                  <p className="text-sm font-medium text-foreground">{item.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {getDietaryDescription(item.dietary_classification)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">Confidence</div>
                <div className="text-sm font-medium text-foreground">{item.confidence}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="p-4 border-t border-border bg-muted/50">
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            className="flex-1 flex items-center justify-center space-x-2"
            onClick={handleExportResults}
            data-testid="button-export"
          >
            <Download size={16} />
            <span>Export Results</span>
          </Button>
          <Button
            variant="secondary"
            className="flex-1 flex items-center justify-center space-x-2"
            onClick={handleShare}
            data-testid="button-share"
          >
            <Share size={16} />
            <span>Share Analysis</span>
          </Button>
          <Button
            variant="outline"
            className="px-4 py-2 flex items-center justify-center space-x-2"
            onClick={onAnalyzeNew}
            data-testid="button-analyze-new"
          >
            <RotateCcw size={16} />
            <span>Analyze New</span>
          </Button>
        </div>
      </div>
    </Card>
  );
}
