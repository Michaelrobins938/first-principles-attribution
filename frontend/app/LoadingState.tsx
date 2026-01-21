'use client';

import { Activity, Target, Shield, Zap, CheckCircle2 } from 'lucide-react';

export default function LoadingState() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="carbon-plate-deep border border-zinc-800">
        <div className="p-12">
          {/* Main Loading Animation */}
          <div className="flex flex-col items-center justify-center mb-12">
            <div className="relative w-32 h-32 mb-8">
              {/* Outer tactical ring */}
              <div className="absolute inset-0 border-2 border-amber-500/20 animate-pulse-tactical"></div>
              
              {/* Middle crosshair */}
              <div className="absolute inset-4 border-2 border-amber-500/40">
                <div className="absolute top-1/2 left-0 right-0 h-px bg-amber-500/60"></div>
                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-amber-500/60"></div>
              </div>
              
              {/* Inner core */}
              <div className="absolute inset-8 carbon-plate border border-amber-500 flex items-center justify-center">
                <Activity className="w-12 h-12 text-amber-500 animate-pulse" />
              </div>
              
              {/* Corner markers */}
              <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-amber-500"></div>
              <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-amber-500"></div>
              <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-amber-500"></div>
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-amber-500"></div>
            </div>

            <h2 className="text-2xl font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide">
              ANALYSIS IN PROGRESS
            </h2>
            <p className="text-zinc-500 text-center max-w-md font-mono text-sm">
              EXECUTING MARKOV-SHAPLEY ATTRIBUTION • BEHAVIORAL COVARIATION • AI INTELLIGENCE GENERATION
            </p>
          </div>

          {/* Progress Steps */}
          <div className="space-y-3 mb-8">
            <div className="flex items-center gap-4 p-4 carbon-plate border border-emerald-900/50 bg-emerald-950/20">
              <div className="flex-shrink-0 w-8 h-8 border border-emerald-500 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              </div>
              <div className="flex-1">
                <p className="font-bold text-zinc-100 font-mono uppercase text-sm tracking-wide">DATA INGESTION</p>
                <p className="text-xs text-zinc-500 font-mono">Multi-source event normalization complete</p>
              </div>
              <div className="text-xs text-emerald-500 font-mono">COMPLETE</div>
            </div>

            <div className="flex items-center gap-4 p-4 carbon-plate border border-amber-500/50 bg-amber-950/20 animate-shimmer-tactical">
              <div className="flex-shrink-0 w-8 h-8 border border-amber-500 flex items-center justify-center">
                <Target className="w-5 h-5 text-amber-500 animate-pulse" />
              </div>
              <div className="flex-1">
                <p className="font-bold text-zinc-100 font-mono uppercase text-sm tracking-wide">ATTRIBUTION ENGINE</p>
                <p className="text-xs text-zinc-500 font-mono">Computing Markov chains and Shapley values...</p>
              </div>
              <div className="flex-shrink-0">
                <div className="w-5 h-5 border-2 border-amber-500/30 border-t-amber-500 animate-spin"></div>
              </div>
            </div>

            <div className="flex items-center gap-4 p-4 carbon-plate border border-zinc-800">
              <div className="flex-shrink-0 w-8 h-8 border border-zinc-700 flex items-center justify-center">
                <Shield className="w-5 h-5 text-zinc-600" />
              </div>
              <div className="flex-1">
                <p className="font-bold text-zinc-600 font-mono uppercase text-sm tracking-wide">COVARIATION ANALYSIS</p>
                <p className="text-xs text-zinc-700 font-mono">Kelley&apos;s model pending...</p>
              </div>
              <div className="text-xs text-zinc-700 font-mono">QUEUED</div>
            </div>

            <div className="flex items-center gap-4 p-4 carbon-plate border border-zinc-800">
              <div className="flex-shrink-0 w-8 h-8 border border-zinc-700 flex items-center justify-center">
                <Zap className="w-5 h-5 text-zinc-600" />
              </div>
              <div className="flex-1">
                <p className="font-bold text-zinc-600 font-mono uppercase text-sm tracking-wide">AI REPORT GENERATION</p>
                <p className="text-xs text-zinc-700 font-mono">LLM interpretation pending...</p>
              </div>
              <div className="text-xs text-zinc-700 font-mono">QUEUED</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between text-xs text-zinc-500 font-mono mb-2">
              <span className="uppercase">MISSION PROGRESS</span>
              <span>45%</span>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 h-3 relative overflow-hidden">
              <div 
                className="h-full bg-amber-500 relative"
                style={{ width: '45%' }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer-tactical"></div>
              </div>
            </div>
          </div>

          {/* Tactical Stats */}
          <div className="grid grid-cols-3 gap-4 pt-6 border-t border-zinc-800">
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-500 font-mono">3</div>
              <p className="text-xs text-zinc-600 font-mono uppercase">ENGINES ACTIVE</p>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-500 font-mono">5</div>
              <p className="text-xs text-zinc-600 font-mono uppercase">REPORTS QUEUED</p>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-500 font-mono">~45s</div>
              <p className="text-xs text-zinc-600 font-mono uppercase">ETA REMAINING</p>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="carbon-plate border border-zinc-800 p-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-zinc-500 font-mono uppercase">SECURITY</span>
          </div>
          <div className="text-sm font-bold text-zinc-100 font-mono">ENCRYPTED</div>
        </div>
        
        <div className="carbon-plate border border-zinc-800 p-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-zinc-500 font-mono uppercase">PRIVACY</span>
          </div>
          <div className="text-sm font-bold text-zinc-100 font-mono">LOCAL ONLY</div>
        </div>
        
        <div className="carbon-plate border border-zinc-800 p-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-zinc-500 font-mono uppercase">STATUS</span>
          </div>
          <div className="text-sm font-bold text-zinc-100 font-mono">PROCESSING</div>
        </div>
      </div>
    </div>
  );
}
