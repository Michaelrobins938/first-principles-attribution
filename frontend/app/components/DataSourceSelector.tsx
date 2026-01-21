'use client';

import { useState } from 'react';
import {
  Database,
  Chrome,
  Facebook,
  FileSpreadsheet,
  Globe,
  Upload,
  CheckCircle,
  Info,
  ChevronRight,
  Smartphone,
  Monitor,
  Apple
} from 'lucide-react';

interface DataSource {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  formats: string[];
  instructions: string[];
  color: string;
}

interface DataSourceSelectorProps {
  onSourceSelect: (sourceId: string) => void;
  onFileUpload: (file: File, sourceId: string) => void;
  selectedSource: string | null;
}

const DATA_SOURCES: DataSource[] = [
  {
    id: 'google_analytics',
    name: 'Google Analytics 4',
    description: 'BigQuery export or GA4 data',
    icon: <Globe className="w-6 h-6" />,
    formats: ['JSON', 'CSV'],
    instructions: [
      'Export from BigQuery or GA4 Admin',
      'Include events with timestamps',
      'Ensure user_pseudo_id is present'
    ],
    color: 'amber'
  },
  {
    id: 'facebook',
    name: 'Facebook Export',
    description: 'Your Facebook data download',
    icon: <Facebook className="w-6 h-6" />,
    formats: ['JSON', 'ZIP'],
    instructions: [
      'Download from Facebook Settings',
      'Select JSON format',
      'Include activity and ads data'
    ],
    color: 'blue'
  },
  {
    id: 'browser_history',
    name: 'Browser History',
    description: 'Chrome, Firefox, Safari exports',
    icon: <Chrome className="w-6 h-6" />,
    formats: ['JSON', 'CSV', 'SQLite'],
    instructions: [
      'Export from browser settings',
      'Or use history export extension',
      'Include timestamps and URLs'
    ],
    color: 'emerald'
  },
  {
    id: 'csv',
    name: 'Custom CSV',
    description: 'Your own journey data',
    icon: <FileSpreadsheet className="w-6 h-6" />,
    formats: ['CSV'],
    instructions: [
      'Required: user_id, channel, timestamp',
      'Optional: conversion, value',
      'See template for format'
    ],
    color: 'purple'
  },
  {
    id: 'apple',
    name: 'Apple Privacy',
    description: 'Apple data privacy export',
    icon: <Apple className="w-6 h-6" />,
    formats: ['JSON', 'ZIP'],
    instructions: [
      'Request from privacy.apple.com',
      'Include app activity data',
      'May take 1-7 days to receive'
    ],
    color: 'zinc'
  },
  {
    id: 'multi_source',
    name: 'Multi-Source',
    description: 'Combine multiple data sources',
    icon: <Database className="w-6 h-6" />,
    formats: ['Multiple'],
    instructions: [
      'Upload files from different sources',
      'System auto-detects format',
      'Unified event schema applied'
    ],
    color: 'rose'
  }
];

export default function DataSourceSelector({
  onSourceSelect,
  onFileUpload,
  selectedSource
}: DataSourceSelectorProps) {
  const [hoveredSource, setHoveredSource] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<{name: string, size: number}[]>([]);

  const selectedSourceData = DATA_SOURCES.find(s => s.id === selectedSource);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0] && selectedSource) {
      const file = e.dataTransfer.files[0];
      setUploadedFiles(prev => [...prev, { name: file.name, size: file.size }]);
      onFileUpload(file, selectedSource);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0] && selectedSource) {
      const file = e.target.files[0];
      setUploadedFiles(prev => [...prev, { name: file.name, size: file.size }]);
      onFileUpload(file, selectedSource);
    }
  };

  const getColorClasses = (color: string, isSelected: boolean) => {
    const colors: Record<string, { border: string; bg: string; text: string }> = {
      amber: {
        border: isSelected ? 'border-amber-500' : 'border-amber-500/30',
        bg: 'bg-amber-950/20',
        text: 'text-amber-500'
      },
      blue: {
        border: isSelected ? 'border-blue-500' : 'border-blue-500/30',
        bg: 'bg-blue-950/20',
        text: 'text-blue-500'
      },
      emerald: {
        border: isSelected ? 'border-emerald-500' : 'border-emerald-500/30',
        bg: 'bg-emerald-950/20',
        text: 'text-emerald-500'
      },
      purple: {
        border: isSelected ? 'border-purple-500' : 'border-purple-500/30',
        bg: 'bg-purple-950/20',
        text: 'text-purple-500'
      },
      zinc: {
        border: isSelected ? 'border-zinc-400' : 'border-zinc-500/30',
        bg: 'bg-zinc-900/50',
        text: 'text-zinc-400'
      },
      rose: {
        border: isSelected ? 'border-rose-500' : 'border-rose-500/30',
        bg: 'bg-rose-950/20',
        text: 'text-rose-500'
      }
    };
    return colors[color] || colors.amber;
  };

  return (
    <div className="space-y-6">
      {/* Source Grid */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-4 h-4 text-amber-500" />
          <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
            SELECT DATA SOURCE
          </h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {DATA_SOURCES.map((source) => {
            const isSelected = selectedSource === source.id;
            const isHovered = hoveredSource === source.id;
            const colors = getColorClasses(source.color, isSelected);

            return (
              <button
                key={source.id}
                onClick={() => onSourceSelect(source.id)}
                onMouseEnter={() => setHoveredSource(source.id)}
                onMouseLeave={() => setHoveredSource(null)}
                className={`
                  relative p-4 carbon-plate border transition-all text-left group
                  ${colors.border}
                  ${isSelected ? colors.bg : 'hover:bg-zinc-900/50'}
                `}
              >
                {isSelected && (
                  <div className="absolute top-2 right-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                  </div>
                )}

                <div className={`mb-3 ${colors.text}`}>
                  {source.icon}
                </div>

                <h4 className="text-sm font-bold text-zinc-100 font-mono uppercase mb-1">
                  {source.name}
                </h4>
                <p className="text-xs text-zinc-500 font-mono">
                  {source.description}
                </p>

                <div className="flex flex-wrap gap-1 mt-3">
                  {source.formats.map((format) => (
                    <span
                      key={format}
                      className="px-2 py-0.5 text-xs font-mono bg-zinc-800 text-zinc-400 border border-zinc-700"
                    >
                      {format}
                    </span>
                  ))}
                </div>

                {(isHovered || isSelected) && (
                  <ChevronRight className={`absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 ${colors.text} transition-transform ${isSelected ? 'translate-x-0' : '-translate-x-1'}`} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Upload Zone */}
      {selectedSource && selectedSourceData && (
        <div className="animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <Upload className="w-4 h-4 text-amber-500" />
            <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
              UPLOAD {selectedSourceData.name.toUpperCase()} DATA
            </h3>
          </div>

          {/* Instructions */}
          <div className="carbon-plate border border-zinc-800 p-4 mb-4">
            <div className="flex items-start gap-2">
              <Info className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-zinc-500 font-mono uppercase mb-2">
                  How to export your data:
                </p>
                <ul className="space-y-1">
                  {selectedSourceData.instructions.map((instruction, i) => (
                    <li key={i} className="text-xs text-zinc-400 font-mono flex items-center gap-2">
                      <span className="w-4 h-4 carbon-plate-deep border border-zinc-700 flex items-center justify-center text-amber-500">
                        {i + 1}
                      </span>
                      {instruction}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`
              relative border-2 border-dashed p-8 transition-all cursor-pointer
              ${dragActive
                ? 'border-amber-500 bg-amber-950/20'
                : 'border-zinc-700 hover:border-amber-500/50 hover:bg-zinc-950/50'
              }
            `}
          >
            <input
              type="file"
              onChange={handleFileInput}
              accept={selectedSourceData.formats.map(f => `.${f.toLowerCase()}`).join(',')}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />

            <div className="text-center space-y-3">
              <div className="w-12 h-12 mx-auto carbon-plate border border-amber-500/30 flex items-center justify-center">
                <Upload className={`w-6 h-6 ${dragActive ? 'text-amber-500 animate-bounce' : 'text-amber-500'}`} />
              </div>
              <div>
                <p className="text-sm font-semibold text-zinc-100 font-mono uppercase">
                  {dragActive ? 'DROP FILE HERE' : 'DRAG & DROP OR CLICK'}
                </p>
                <p className="text-xs text-zinc-500 font-mono mt-1">
                  Supported: {selectedSourceData.formats.join(', ')}
                </p>
              </div>
            </div>
          </div>

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-xs text-zinc-500 font-mono uppercase">Uploaded Files:</p>
              {uploadedFiles.map((file, i) => (
                <div key={i} className="flex items-center gap-3 p-3 carbon-plate border border-emerald-500/30 bg-emerald-950/10">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm text-zinc-100 font-mono">{file.name}</span>
                  <span className="text-xs text-zinc-500 font-mono ml-auto">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Device Icons */}
          <div className="flex items-center justify-center gap-6 mt-6 pt-4 border-t border-zinc-800">
            <div className="flex items-center gap-2 text-zinc-600">
              <Monitor className="w-4 h-4" />
              <span className="text-xs font-mono">Desktop</span>
            </div>
            <div className="flex items-center gap-2 text-zinc-600">
              <Smartphone className="w-4 h-4" />
              <span className="text-xs font-mono">Mobile</span>
            </div>
            <div className="flex items-center gap-2 text-zinc-600">
              <Chrome className="w-4 h-4" />
              <span className="text-xs font-mono">Browser</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
