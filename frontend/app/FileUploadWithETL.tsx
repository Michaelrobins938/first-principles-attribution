'use client';

import { useState, useCallback } from 'react';
import { Upload, File, X, CheckCircle2, Crosshair, ChevronDown } from 'lucide-react';
import { parseAutoDetect, parseGoogleTakeout, parseFacebookAds, parseShopifyOrders, parseGA4 } from '../lib/parsers';

interface FileUploadProps {
  onUpload: (file: File) => void;
  disabled?: boolean;
}

export default function FileUpload({ onUpload, disabled }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dataSource, setDataSource] = useState('auto');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        setSelectedFile(files[0]);
      }
    },
    [disabled]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (selectedFile && !disabled) {
      setIsProcessing(true);
      
      try {
        // Handle different file types
        let processedFile = selectedFile;
        
        if (selectedFile.name.endsWith('.csv')) {
          // Parse CSV and transform to our format
          const text = await selectedFile.text();
          let result;
          
          switch (dataSource) {
            case 'google':
              result = parseGoogleTakeout(text);
              break;
            case 'facebook':
              result = parseFacebookAds(text);
              break;
            case 'shopify':
              result = parseShopifyOrders(text);
              break;
            case 'ga4':
              result = parseGA4(text);
              break;
            default:
              result = parseAutoDetect(text);
          }
          
          if (result.success && result.data) {
            // Convert back to File object in correct format
            const jsonStr = JSON.stringify(result.data, null, 2);
            const blob = new Blob([jsonStr], { type: 'application/json' });
            processedFile = new File([blob], `processed_${selectedFile.name.replace('.csv', '.json')}`, { type: 'application/json' });
          } else {
            console.error('Parsing failed:', result.error);
            // Continue with original file as fallback
          }
        }
        
        onUpload(processedFile);
      } catch (error) {
        console.error('File processing failed:', error);
        onUpload(selectedFile); // Fallback to original file
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed p-12 transition-all duration-300 ${
          isDragging
            ? 'border-amber-500 bg-amber-950/20 scale-[1.01]'
            : selectedFile
            ? 'border-emerald-500/50 bg-emerald-950/10'
            : 'border-zinc-700 hover:border-amber-500/50 hover:bg-zinc-950/50'
        } ${disabled || isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <input
          type="file"
          onChange={handleFileSelect}
          disabled={disabled || isProcessing}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept=".json,.csv,.zip,.txt"
        />

        <div className="text-center space-y-4">
          {selectedFile ? (
            <>
              <div className="w-16 h-16 mx-auto carbon-plate border border-emerald-500/50 flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              </div>
              <div>
                <p className="text-base font-semibold text-zinc-100 mb-2 font-mono uppercase tracking-wide">
                  FILE LOADED
                </p>
                <div className="inline-flex items-center gap-3 px-4 py-3 carbon-plate border border-zinc-700 mt-2">
                  <File className="w-5 h-5 text-zinc-400" />
                  <div className="text-left">
                    <p className="text-sm font-medium text-zinc-200 max-w-xs truncate font-mono">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-zinc-500 font-mono">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                    className="p-1.5 hover:bg-zinc-800 border border-transparent hover:border-red-900/50 transition-all"
                  >
                    <X className="w-4 h-4 text-zinc-500 hover:text-red-500" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 mx-auto carbon-plate border border-amber-500/30 flex items-center justify-center">
                <Upload className="w-8 h-8 text-amber-500" />
              </div>
              <div>
                <p className="text-base font-semibold text-zinc-100 mb-2 font-mono uppercase tracking-wide">
                  DEPLOY TARGET FILE
                </p>
                <p className="text-sm text-zinc-500 font-mono">
                  DROP FILE OR CLICK TO SELECT FROM SYSTEM
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 text-xs text-zinc-600 font-mono">
                <span className="px-3 py-1 carbon-plate border border-zinc-800">JSON</span>
                <span className="px-3 py-1 carbon-plate border border-zinc-800">CSV</span>
                <span className="px-3 py-1 carbon-plate border border-zinc-800">ZIP</span>
                <span className="px-3 py-1 carbon-plate border border-zinc-800">TXT</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Data Source Selector */}
      {!isProcessing && (
        <div className="carbon-plate border border-zinc-800 p-4">
          <div className="flex items-center gap-3 mb-3">
            <ChevronDown className="w-4 h-4 text-zinc-400" />
            <span className="text-xs text-zinc-500 font-mono uppercase">DATA SOURCE TYPE</span>
          </div>
          <select
            value={dataSource}
            onChange={(e) => setDataSource(e.target.value)}
            className="w-full px-3 py-2 bg-black border border-zinc-700 text-zinc-100 font-mono text-sm focus:border-amber-500 focus:outline-none"
          >
            <option value="auto">Auto-Detect</option>
            <option value="google">Google Takeout</option>
            <option value="facebook">Facebook Ads</option>
            <option value="shopify">Shopify Orders</option>
            <option value="ga4">GA4 Export</option>
          </select>
        </div>
      )}

      {selectedFile && (
        <button
          onClick={handleAnalyze}
          disabled={disabled || isProcessing}
          className="w-full py-4 px-6 carbon-plate border border-amber-500/50 text-amber-500 font-bold hover:bg-amber-950/30 hover:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-all font-mono uppercase tracking-wider text-sm flex items-center justify-center gap-3 relative overflow-hidden group"
        >
          {disabled || isProcessing ? (
            <>
              <div className="w-5 h-5 border-2 border-amber-500/30 border-t-amber-500 animate-spin" />
              {isProcessing ? 'PROCESSING DATA...' : 'ANALYZING TARGET...'}
            </>
          ) : (
            <>
              <Crosshair className="w-5 h-5" />
              INITIATE ANALYSIS
              <div className="absolute inset-0 bg-amber-500/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
            </>
          )}
        </button>
      )}

      {/* Mission Brief */}
      <div className="text-xs text-zinc-600 font-mono text-center space-y-1">
        <p className="uppercase tracking-wide">SUPPORTED DATA SOURCES</p>
        <p className="text-zinc-700">Google Takeout • Facebook Export • Apple Archives • Browser History</p>
      </div>
    </div>
  );
}