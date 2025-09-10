import { useState, useRef, useEffect } from "react";
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
  const [scale, setScale] = useState(1);
  const [translateX, setTranslateX] = useState(0);
  const [translateY, setTranslateY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [lastTouchDistance, setLastTouchDistance] = useState(0);
  const [lastTouchCenter, setLastTouchCenter] = useState({ x: 0, y: 0 });
  const [lastTouchTime, setLastTouchTime] = useState(0);
  const imageContainerRef = useRef<HTMLDivElement>(null);

  const getDietaryColor = (classification: string) => {
    switch (classification) {
      case "vegan":
        return "#00AA00"; // Bright green
      case "vegetarian":
        return "#AAFF00"; // Bright lime
      case "meat":
        return "#FF0000"; // Bright red
      default:
        return "#888888"; // Gray for unknown
    }
  };

  const getDietaryDescription = (classification: string) => {
    switch (classification) {
      case "vegan":
        return "Vegan";
      case "vegetarian":
        return "Vegetarian";
      case "meat":
        return "Contains meat ingredients";
      default:
        return "Unknown dietary classification";
    }
  };

  // Touch and zoom handling functions
  const getTouchDistance = (touches: React.TouchList) => {
    if (touches.length < 2) return 0;
    const touch1 = touches[0];
    const touch2 = touches[1];
    return Math.sqrt(
      Math.pow(touch2.clientX - touch1.clientX, 2) + 
      Math.pow(touch2.clientY - touch1.clientY, 2)
    );
  };

  const getTouchCenter = (touches: React.TouchList) => {
    if (touches.length < 2) return { x: touches[0].clientX, y: touches[0].clientY };
    const touch1 = touches[0];
    const touch2 = touches[1];
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    };
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    const now = Date.now();
    
    if (e.touches.length === 1) {
      // Check for double tap
      if (now - lastTouchTime < 300) {
        handleDoubleTap();
        return;
      }
      setLastTouchTime(now);
      setIsDragging(true);
      const touch = e.touches[0];
      setLastTouchCenter({ x: touch.clientX, y: touch.clientY });
    } else if (e.touches.length === 2) {
      // Start pinch gesture
      setIsDragging(false);
      const distance = getTouchDistance(e.touches);
      const center = getTouchCenter(e.touches);
      setLastTouchDistance(distance);
      setLastTouchCenter(center);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    e.preventDefault();
    
    if (e.touches.length === 1 && isDragging && scale > 1) {
      // Pan gesture
      const touch = e.touches[0];
      const deltaX = touch.clientX - lastTouchCenter.x;
      const deltaY = touch.clientY - lastTouchCenter.y;
      
      setTranslateX(prev => prev + deltaX);
      setTranslateY(prev => prev + deltaY);
      setLastTouchCenter({ x: touch.clientX, y: touch.clientY });
    } else if (e.touches.length === 2) {
      // Pinch gesture
      const distance = getTouchDistance(e.touches);
      const center = getTouchCenter(e.touches);
      
      if (lastTouchDistance > 0) {
        const deltaScale = distance / lastTouchDistance;
        const newScale = Math.min(5, Math.max(0.5, scale * deltaScale));
        
        // Adjust translation to zoom towards touch center
        const rect = imageContainerRef.current?.getBoundingClientRect();
        if (rect) {
          const centerX = center.x - rect.left - rect.width / 2;
          const centerY = center.y - rect.top - rect.height / 2;
          
          setScale(newScale);
          setTranslateX(prev => prev + centerX * (deltaScale - 1));
          setTranslateY(prev => prev + centerY * (deltaScale - 1));
        }
      }
      
      setLastTouchDistance(distance);
      setLastTouchCenter(center);
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    setLastTouchDistance(0);
  };

  const handleDoubleTap = () => {
    if (scale === 1) {
      setScale(2);
    } else {
      resetZoom();
    }
  };

  const resetZoom = () => {
    setScale(1);
    setTranslateX(0);
    setTranslateY(0);
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
      <div className="relative bg-muted overflow-hidden touch-none" 
           ref={imageContainerRef}
           onTouchStart={handleTouchStart}
           onTouchMove={handleTouchMove}
           onTouchEnd={handleTouchEnd}>
        <div
          className="transition-transform duration-100 ease-out"
          style={{
            transform: `scale(${scale}) translate(${translateX / scale}px, ${translateY / scale}px)`,
            transformOrigin: 'center center'
          }}
        >
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
          {analysisResult.food_items.map((item, index) => {
            if (!item.position) return null;
            
            return (
              <div
                key={index}
                className="absolute rounded-full w-8 h-8 shadow-lg cursor-pointer hover:scale-110 transition-transform flex items-center justify-center"
                style={{
                  left: `${item.position.x}%`,
                  top: `${item.position.y}%`,
                  transform: 'translate(-50%, -50%)',
                  backgroundColor: getDietaryColor(item.dietary_classification),
                  border: '2px solid white',
                }}
                onClick={() => setSelectedItem(selectedItem?.name === item.name ? null : item)}
                data-testid={`food-label-${index}`}
              >
                <span className="text-sm font-bold text-white">{index + 1}</span>
              </div>
            );
          })}
        </div>
        
        {/* Confidence indicator and zoom controls */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 food-badge rounded-full px-3 py-1 shadow-lg">
          <div className="flex items-center space-x-1">
            <CheckCircle className="text-green-500" size={12} />
            <span className="text-xs font-medium">{analysisResult.overall_confidence}% Confidence</span>
          </div>
        </div>
        
        {scale > 1 && (
          <Button
            size="sm"
            variant="secondary"
            className="absolute top-4 right-4 bg-black/50 hover:bg-black/70 text-white border-0"
            onClick={resetZoom}
            data-testid="button-reset-zoom"
          >
            Reset Zoom
          </Button>
        )}
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
                  <p className="text-sm font-medium text-foreground">
                    <span className="inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold text-white mr-2" 
                          style={{ backgroundColor: getDietaryColor(item.dietary_classification) }}>
                      {index + 1}
                    </span>
                    {item.name}
                  </p>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                    <span>{getDietaryDescription(item.dietary_classification)}</span>
                    {item.weight_grams && (
                      <>
                        <span>•</span>
                        <span className="font-medium">{item.weight_grams}g</span>
                      </>
                    )}
                  </div>
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
