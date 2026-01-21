'use client';

import { Shield, Target, Zap, AlertTriangle, Activity, Users } from 'lucide-react';

interface BehavioralTagsProps {
  data: any;
}

export default function BehavioralTags({ data }: BehavioralTagsProps) {
  const behaviors = data?.behaviors || [];
  const metrics = data?.metrics || {};
  
  const dispositionalBehaviors = behaviors.filter((b: any) => b.tag === 'DISPOSITIONAL');
  const situationalBehaviors = behaviors.filter((b: any) => b.tag === 'SITUATIONAL');
  const mixedBehaviors = behaviors.filter((b: any) => b.tag === 'MIXED');

  const getTagColor = (tag: string) => {
    switch (tag) {
      case 'DISPOSITIONAL':
        return 'amber';
      case 'SITUATIONAL':
        return 'emerald';
      case 'MIXED':
        return 'zinc';
      default:
        return 'zinc';
    }
  };

  const getTagIcon = (tag: string) => {
    switch (tag) {
      case 'DISPOSITIONAL':
        return <Shield className="w-5 h-5" />;
      case 'SITUATIONAL':
        return <Target className="w-5 h-5" />;
      default:
        return <Zap className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Explanation Banner */}
      <div className="carbon-plate border border-amber-500/30 p-6">
        <div className="flex gap-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 border border-amber-500/50 flex items-center justify-center">
              <Shield className="w-6 h-6 text-amber-500" />
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide">
              KELLEY'S COVARIATION MODEL
            </h3>
            <p className="text-xs text-zinc-400 leading-relaxed font-mono">
              Classification system distinguishes <span className="text-amber-500 font-bold">CORE PERSONALITY TRAITS</span> (dispositional) 
              from <span className="text-emerald-500 font-bold">ENVIRONMENTAL REACTIONS</span> (situational) using three-dimensional 
              analysis: Consistency, Distinctiveness, Consensus.
            </p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="carbon-plate border border-amber-500/30 p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-amber-500/50 flex items-center justify-center">
              <Shield className="w-5 h-5 text-amber-500" />
            </div>
            <span className="text-3xl font-bold text-amber-500 font-mono">
              {dispositionalBehaviors.length}
            </span>
          </div>
          <h4 className="text-xs font-bold text-zinc-100 mb-1 font-mono uppercase tracking-wider">DISPOSITIONAL</h4>
          <p className="text-xs text-zinc-600 font-mono">Core personality traits</p>
        </div>

        <div className="carbon-plate border border-emerald-500/30 p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-emerald-500/50 flex items-center justify-center">
              <Target className="w-5 h-5 text-emerald-500" />
            </div>
            <span className="text-3xl font-bold text-emerald-500 font-mono">
              {situationalBehaviors.length}
            </span>
          </div>
          <h4 className="text-xs font-bold text-zinc-100 mb-1 font-mono uppercase tracking-wider">SITUATIONAL</h4>
          <p className="text-xs text-zinc-600 font-mono">Environmental reactions</p>
        </div>

        <div className="carbon-plate border border-zinc-700 p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-zinc-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-zinc-500" />
            </div>
            <span className="text-3xl font-bold text-zinc-500 font-mono">
              {mixedBehaviors.length}
            </span>
          </div>
          <h4 className="text-xs font-bold text-zinc-100 mb-1 font-mono uppercase tracking-wider">MIXED</h4>
          <p className="text-xs text-zinc-600 font-mono">Context-dependent</p>
        </div>
      </div>

      {/* Dispositional Behaviors */}
      {dispositionalBehaviors.length > 0 && (
        <div className="carbon-plate border border-zinc-800">
          <div className="border-b border-zinc-800 px-4 py-3 bg-amber-950/20">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border border-amber-500/50 flex items-center justify-center">
                <Shield className="w-4 h-4 text-amber-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">DISPOSITIONAL BEHAVIORS</h3>
                <p className="text-xs text-zinc-500 font-mono">Core personality traits consistent across contexts</p>
              </div>
            </div>
          </div>
          <div className="p-4 space-y-3">
            {dispositionalBehaviors.map((behavior: any, index: number) => (
              <div key={index} className="carbon-plate-deep border border-amber-500/20 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide text-sm">{behavior.channel || behavior.name}</h4>
                    <p className="text-xs text-zinc-400 font-mono leading-relaxed">{behavior.description || behavior.insight}</p>
                  </div>
                  <span className="px-3 py-1 border border-amber-500 text-amber-500 text-xs font-mono uppercase tracking-wider">
                    DISPOSITIONAL
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-3 mt-4">
                  <div className="carbon-plate border border-zinc-800 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-3 h-3 text-amber-500" />
                      <span className="text-xs font-mono text-zinc-500 uppercase">CONSISTENCY</span>
                    </div>
                    <div className="text-lg font-bold text-zinc-100 font-mono">
                      {((behavior.consistency || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="carbon-plate border border-zinc-800 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-3 h-3 text-amber-500" />
                      <span className="text-xs font-mono text-zinc-500 uppercase">DISTINCT</span>
                    </div>
                    <div className="text-lg font-bold text-zinc-100 font-mono">
                      {((behavior.distinctiveness || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="carbon-plate border border-zinc-800 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-3 h-3 text-amber-500" />
                      <span className="text-xs font-mono text-zinc-500 uppercase">CONSENSUS</span>
                    </div>
                    <div className="text-lg font-bold text-zinc-100 font-mono">
                      {((behavior.consensus || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Situational Behaviors */}
      {situationalBehaviors.length > 0 && (
        <div className="carbon-plate border border-zinc-800">
          <div className="border-b border-zinc-800 px-4 py-3 bg-emerald-950/20">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 border border-emerald-500/50 flex items-center justify-center">
                <Target className="w-4 h-4 text-emerald-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">SITUATIONAL BEHAVIORS</h3>
                <p className="text-xs text-zinc-500 font-mono">Environmental reactions driven by specific contexts</p>
              </div>
            </div>
          </div>
          <div className="p-4 space-y-3">
            {situationalBehaviors.map((behavior: any, index: number) => (
              <div key={index} className="carbon-plate-deep border border-emerald-500/20 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide text-sm">{behavior.channel || behavior.name}</h4>
                    <p className="text-xs text-zinc-400 font-mono leading-relaxed">{behavior.description || behavior.insight}</p>
                  </div>
                  <span className="px-3 py-1 border border-emerald-500 text-emerald-500 text-xs font-mono uppercase tracking-wider">
                    SITUATIONAL
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-3 mt-4">
                  <div className="carbon-plate border border-zinc-800 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-3 h-3 text-emerald-500" />
                      <span className="text-xs font-mono text-zinc-500 uppercase">CONSISTENCY</span>
                    </div>
                    <div className="text-lg font-bold text-zinc-100 font-mono">
                      {((behavior.consistency || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="carbon-plate border border-zinc-800 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-3 h-3 text-emerald-500" />
                      <span className="text-xs font-mono text-zinc-500 uppercase">DISTINCT</span>
                    </div>
                    <div className="text-lg font-bold text-zinc-100 font-mono">
                      {((behavior.distinctiveness || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="carbon-plate border border-zinc-800 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-3 h-3 text-emerald-500" />
                      <span className="text-xs font-mono text-zinc-500 uppercase">CONSENSUS</span>
                    </div>
                    <div className="text-lg font-bold text-zinc-100 font-mono">
                      {((behavior.consensus || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {behaviors.length === 0 && (
        <div className="carbon-plate border border-zinc-800 p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-4 border border-zinc-700 flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-zinc-600" />
          </div>
          <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide">
            NO BEHAVIORAL DATA
          </h3>
          <p className="text-xs text-zinc-500 font-mono">
            Insufficient data for covariation analysis. Requires additional behavioral samples.
          </p>
        </div>
      )}
    </div>
  );
}
