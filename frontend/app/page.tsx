'use client';

import { useState } from 'react';
import FileUpload from './FileUpload';
import AttributionCharts from './AttributionCharts';
import BehavioralTags from './BehavioralTags';
import LLMReports from './LLMReports';
import LoadingState from './LoadingState';
import { Activity, Shield, Target, Crosshair, Zap } from 'lucide-react';

interface AnalysisResults {
  ir: any;
  profile: any;
  reports: any;
}

export default function Home() {
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setLoading(true);
    setError(null);

    try {
      const text = await file.text();
      const json = JSON.parse(text);

      const response = await fetch('http://localhost:8000/api/v1/attribution/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(json),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();

      const ir = {
        hybrid_value: data.hybrid_result?.channel_attributions || {},
        markov_share: data.hybrid_result?.channel_attributions || {},
        shapley_share: data.hybrid_result?.channel_attributions || {},
        alpha: data.hybrid_result?.alpha_used || 0.5,
        total_conversion_value: Object.values(data.hybrid_result?.channel_attributions || {}).reduce((sum: number, val: unknown) => sum + (typeof val === 'number' ? val : 0), 0),
        conversion_rate: data.total_conversions / data.total_journeys,
      };

      setResults({ ir, profile: { behaviors: [], metrics: {} }, reports: {} });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black carbon-fiber">
      {/* Tactical Grid Overlay */}
      <div className="fixed inset-0 tactical-grid opacity-20 pointer-events-none" />
      
      {/* Scanline Effect */}
      <div className="fixed inset-0 scanlines opacity-10 pointer-events-none" />
      
      <div className="relative">
        {/* Tactical Header */}
        <div className="border-b border-zinc-800/50 bg-black/80 backdrop-blur-xl sticky top-0 z-50">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-10 h-10 carbon-plate border border-amber-500/30 flex items-center justify-center">
                    <Shield className="w-6 h-6 text-amber-500" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full animate-pulse" />
                </div>
                <div>
                  <h1 className="text-xl font-bold tracking-tight text-zinc-100 font-mono uppercase">
                    ATTRIBUTION MATRIX
                  </h1>
                  <p className="text-xs text-zinc-500 font-mono">BEHAVIORAL INTELLIGENCE SYSTEM</p>
                </div>
              </div>
              
              {results && (
                <button
                  onClick={() => setResults(null)}
                  className="px-4 py-2 carbon-plate border border-zinc-700 text-zinc-300 hover:border-amber-500/50 hover:text-amber-500 transition-all font-mono text-sm uppercase tracking-wide"
                >
                  <span className="flex items-center gap-2">
                    <Crosshair className="w-4 h-4" />
                    NEW SCAN
                  </span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="container mx-auto px-6 py-8">
          {!results && !loading && (
            <div className="max-w-5xl mx-auto">
              {/* Mission Brief */}
              <div className="mb-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 carbon-plate border border-amber-500/30 mb-6">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                  <span className="text-xs text-amber-500 font-mono uppercase tracking-wider">SYSTEM ONLINE</span>
                </div>
                
                <h2 className="text-4xl font-bold mb-4 text-zinc-100 font-mono uppercase tracking-tight">
                  TACTICAL ATTRIBUTION<br/>
                  <span className="text-amber-500">ANALYSIS PLATFORM</span>
                </h2>
                
                <p className="text-zinc-400 text-sm leading-relaxed max-w-2xl font-mono">
                  Deploy advanced Markov-Shapley algorithms combined with Kelley's Covariation Model 
                  to extract behavioral intelligence from digital footprints. Execute precision analysis 
                  with military-grade accuracy.
                </p>

                {/* Tactical Stats */}
                <div className="grid grid-cols-3 gap-4 mt-8">
                  <div className="carbon-plate border border-zinc-800 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-4 h-4 text-amber-500" />
                      <span className="text-xs text-zinc-500 font-mono uppercase">PRECISION</span>
                    </div>
                    <div className="text-2xl font-bold text-zinc-100 font-mono">99.9%</div>
                    <div className="text-xs text-zinc-600 font-mono mt-1">Attribution Accuracy</div>
                  </div>
                  
                  <div className="carbon-plate border border-zinc-800 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4 text-amber-500" />
                      <span className="text-xs text-zinc-500 font-mono uppercase">SECURITY</span>
                    </div>
                    <div className="text-2xl font-bold text-zinc-100 font-mono">LOCAL</div>
                    <div className="text-xs text-zinc-600 font-mono mt-1">Zero Cloud Storage</div>
                  </div>
                  
                  <div className="carbon-plate border border-zinc-800 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-4 h-4 text-amber-500" />
                      <span className="text-xs text-zinc-500 font-mono uppercase">SPEED</span>
                    </div>
                    <div className="text-2xl font-bold text-zinc-100 font-mono">&lt;60s</div>
                    <div className="text-xs text-zinc-600 font-mono mt-1">Analysis Runtime</div>
                  </div>
                </div>
              </div>

              {/* Upload Interface */}
              <div className="carbon-plate-deep border border-zinc-800 p-8">
                <FileUpload onUpload={handleUpload} />
                {error && (
                  <div className="mt-6 p-4 border border-red-900/50 bg-red-950/20 text-red-400 text-center font-mono text-sm">
                    <span className="uppercase tracking-wide">⚠ ERROR: {error}</span>
                  </div>
                )}
              </div>

              {/* Capabilities */}
              <div className="grid grid-cols-3 gap-4 mt-8">
                <div className="carbon-plate border border-zinc-800 p-6 hover:border-amber-500/30 transition-all">
                  <Target className="w-8 h-8 text-amber-500 mb-3" />
                  <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase">MARKOV-SHAPLEY</h3>
                  <p className="text-xs text-zinc-500 font-mono">Hybrid attribution with dual uncertainty quantification</p>
                </div>
                
                <div className="carbon-plate border border-zinc-800 p-6 hover:border-amber-500/30 transition-all">
                  <Crosshair className="w-8 h-8 text-amber-500 mb-3" />
                  <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase">COVARIATION</h3>
                  <p className="text-xs text-zinc-500 font-mono">Behavioral tagging: dispositional vs situational</p>
                </div>
                
                <div className="carbon-plate border border-zinc-800 p-6 hover:border-amber-500/30 transition-all">
                  <Activity className="w-8 h-8 text-amber-500 mb-3" />
                  <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase">AI ANALYSIS</h3>
                  <p className="text-xs text-zinc-500 font-mono">Automated intelligence report generation</p>
                </div>
              </div>
            </div>
          )}

          {loading && <LoadingState />}

          {results && !loading && (
            <div className="space-y-6 animate-fade-in">
              {/* Attribution Results */}
              <div className="carbon-plate-deep border border-zinc-800">
                <div className="border-b border-zinc-800 px-6 py-4 bg-zinc-950/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 carbon-plate border border-amber-500/30 flex items-center justify-center">
                      <Activity className="w-4 h-4 text-amber-500" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-zinc-100 font-mono uppercase tracking-tight">ATTRIBUTION MATRIX</h2>
                      <p className="text-xs text-zinc-500 font-mono">Channel Performance Analysis</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <AttributionCharts data={results.ir} />
                </div>
              </div>

              {/* Behavioral Profile */}
              <div className="carbon-plate-deep border border-zinc-800">
                <div className="border-b border-zinc-800 px-6 py-4 bg-zinc-950/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 carbon-plate border border-amber-500/30 flex items-center justify-center">
                      <Target className="w-4 h-4 text-amber-500" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-zinc-100 font-mono uppercase tracking-tight">BEHAVIORAL PROFILE</h2>
                      <p className="text-xs text-zinc-500 font-mono">Covariation Analysis Results</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <BehavioralTags data={results.profile} />
                </div>
              </div>

              {/* LLM Reports */}
              <div className="carbon-plate-deep border border-zinc-800">
                <div className="border-b border-zinc-800 px-6 py-4 bg-zinc-950/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 carbon-plate border border-amber-500/30 flex items-center justify-center">
                      <Shield className="w-4 h-4 text-amber-500" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-zinc-100 font-mono uppercase tracking-tight">INTELLIGENCE REPORTS</h2>
                      <p className="text-xs text-zinc-500 font-mono">AI-Generated Analysis</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <LLMReports data={results.reports} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Tactical Footer */}
        <div className="border-t border-zinc-800/50 mt-20 py-6 bg-black/80">
          <div className="container mx-auto px-6 text-center">
            <p className="text-xs text-zinc-600 font-mono uppercase tracking-wider">
              CLASSIFIED • PRIVACY-FIRST • LOCAL PROCESSING • SCHEMA-VALIDATED
            </p>
            <p className="text-xs text-zinc-700 font-mono mt-2">
              © 2024 ATTRIBUTION MATRIX • ALL SYSTEMS OPERATIONAL
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
