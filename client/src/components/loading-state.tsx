import { Card, CardContent } from "@/components/ui/card";
import { Utensils } from "lucide-react";

export function LoadingState() {
  return (
    <Card className="shadow-sm border border-border">
      <CardContent className="p-8 text-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-border border-t-primary rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Utensils className="text-primary" size={20} />
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">Analyzing Your Meal</h3>
            <p className="text-sm text-muted-foreground mt-1">AI is identifying food items and dietary information...</p>
          </div>
          <div className="w-full max-w-xs bg-secondary rounded-full h-2">
            <div className="bg-primary h-2 rounded-full transition-all duration-1000 ease-in-out w-2/3"></div>
          </div>
          <p className="text-xs text-muted-foreground">This usually takes 5-10 seconds</p>
        </div>
      </CardContent>
    </Card>
  );
}
