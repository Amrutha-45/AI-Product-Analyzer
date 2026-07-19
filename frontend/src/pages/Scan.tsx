import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Image as ImageIcon, X } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { scanService } from '../services/api/scanService';

export const Scan = () => {
  const navigate = useNavigate();
  const [frontImage, setFrontImage] = useState<File | null>(null);
  const [backImage, setBackImage] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>, setter: (f: File) => void) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setter(e.dataTransfer.files[0]);
    }
  };

  const handleScan = async () => {
    if (!frontImage || !backImage) return;
    setIsScanning(true);
    try {
      const result = await scanService.submitScan(frontImage, backImage);
      // Pass the full result via router state to avoid a second Supabase fetch
      navigate(`/scan/${result.scan_id}`, { state: { result } });
    } catch (error: any) {
      console.error("Scan failed", error);
      alert(error?.message || "Failed to process scan. Check that the backend is running.");
    } finally {
      setIsScanning(false);
    }
  };

  const ImageDropzone = React.useCallback(({ 
    label, 
    file, 
    onFileSet, 
    onClear 
  }: { 
    label: string, 
    file: File | null, 
    onFileSet: (f: File) => void,
    onClear: () => void 
  }) => {
    // We use a regular variable for the object URL, and clean it up in an effect below
    // However, since this component is defined inline (or via useCallback), using an img tag
    // directly with URL.createObjectURL(file) is the simplest approach for this scope.
    return (
    <Card className="relative overflow-hidden group p-0">
      {file ? (
        <div className="relative aspect-[3/4] w-full rounded-lg overflow-hidden bg-base-900 flex items-center justify-center">
          <img 
            src={URL.createObjectURL(file)} 
            alt={file.name} 
            className="w-full h-full object-cover" 
            onLoad={(e) => URL.revokeObjectURL((e.target as HTMLImageElement).src)}
          />
          <button 
            onClick={onClear}
            className="absolute top-2 right-2 p-1.5 bg-black/50 hover:bg-black/80 text-white rounded-full transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="absolute bottom-0 inset-x-0 p-3 bg-gradient-to-t from-black/80 to-transparent">
            <p className="text-sm text-white truncate">{file.name}</p>
          </div>
        </div>
      ) : (
        <div 
          className="aspect-[3/4] w-full border-2 border-dashed border-base-700 hover:border-primary/50 rounded-lg flex flex-col items-center justify-center p-6 text-center transition-colors cursor-pointer"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => handleDrop(e, onFileSet)}
          onClick={() => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/jpeg,image/png,image/webp';
            input.onchange = (e) => {
              const target = e.target as HTMLInputElement;
              if (target.files && target.files[0]) onFileSet(target.files[0]);
            };
            input.click();
          }}
        >
          <div className="w-12 h-12 bg-base-800 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <UploadCloud className="w-6 h-6 text-text-secondary group-hover:text-primary transition-colors" />
          </div>
          <p className="text-white font-medium mb-1">{label}</p>
          <p className="text-sm text-text-secondary">Drag & drop or click</p>
        </div>
      )}
    </Card>
    );
  }, []);

  return (
    <div className="min-h-screen bg-base-900 pt-24 pb-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-white mb-3">Scan a Product</h1>
          <p className="text-text-secondary">Upload clear photos of the front label and the back ingredient list.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <ImageDropzone 
            label="Front Label" 
            file={frontImage} 
            onFileSet={setFrontImage} 
            onClear={() => setFrontImage(null)} 
          />
          <ImageDropzone 
            label="Back Label (Ingredients)" 
            file={backImage} 
            onFileSet={setBackImage} 
            onClear={() => setBackImage(null)} 
          />
        </div>

        <div className="flex justify-center">
          <Button 
            size="lg" 
            className="w-full md:w-auto md:min-w-[200px]"
            disabled={!frontImage || !backImage}
            isLoading={isScanning}
            onClick={handleScan}
          >
            {isScanning ? 'Analyzing...' : 'Analyze Product'}
          </Button>
        </div>

      </div>
    </div>
  );
};
