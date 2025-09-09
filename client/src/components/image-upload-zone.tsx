import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Camera, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

interface ImageUploadZoneProps {
  onImageSelect: (imageData: string) => void;
  isLoading?: boolean;
}

export function ImageUploadZone({ onImageSelect, isLoading = false }: ImageUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert("File size must be less than 10MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      if (result) {
        onImageSelect(result);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card className="shadow-sm border border-border">
      <CardContent className="p-6">
        <div className="text-center mb-4">
          <h2 className="text-2xl font-semibold text-foreground mb-2">Analyze Your Meal</h2>
          <p className="text-muted-foreground">Upload a photo to identify ingredients and dietary information</p>
        </div>
        
        <div className="relative">
          <div className="upload-zone absolute inset-0 rounded-lg"></div>
          <div
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer bg-card relative z-10 transition-all duration-300",
              isDragOver ? "border-primary bg-primary/5" : "border-border hover:border-primary",
              isLoading && "pointer-events-none opacity-50"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleChooseFile}
            data-testid="upload-zone"
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                <Camera className="text-primary text-2xl" size={32} />
              </div>
              <div>
                <p className="text-lg font-medium text-foreground">Drop your meal photo here</p>
                <p className="text-sm text-muted-foreground mt-1">or click to browse files</p>
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  className="px-6 py-2 flex items-center space-x-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleChooseFile();
                  }}
                  disabled={isLoading}
                  data-testid="button-choose-file"
                >
                  <Upload size={16} />
                  <span>Choose File</span>
                </Button>
                <Button
                  variant="secondary"
                  className="px-6 py-2 flex items-center space-x-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    // In a real app, this would open camera capture
                    handleChooseFile();
                  }}
                  disabled={isLoading}
                  data-testid="button-take-photo"
                >
                  <Camera size={16} />
                  <span>Take Photo</span>
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">Supports JPG, PNG up to 10MB</p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept="image/*"
              onChange={handleFileInputChange}
              data-testid="input-file"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
