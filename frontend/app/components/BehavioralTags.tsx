'use client';

import { useState } from 'react';
import { Brain, Zap, Users, TrendingUp, ChevronDown, ChevronUp, Fingerprint } from 'lucide-react';

interface BehaviorAnalysis {
  channel: string;
  tag: 'DISPOSITIONAL' | 'SITUATIONAL' | 'MIXED';
  consistency: number;
  distinctiveness: number;
  consensus: number;
  insight: string;
}

interface BehavioralTagsProps {
  data: BehaviorAnalysis[];
}

export default function BehavioralTags({ data }: BehavioralTagsProps) {
  const [expandedChannel, setExpandedChannel] = useState<string | null>(null);

  const dispositionalCount = data.filter(d => d.tag === 'DISPOSITIONAL').length;
  const situationalCount = data.filter(d => d.tag === 'SITUATIONAL').length;
  const mixedCount = data.filter(d => d.tag === 'MIXED').length;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard
          icon={<Fingerprint className="w-5 h-5" />}
          label="DISPOSITIONAL"
          value={dispositionalCount}
          color="purple"
          description="Core personality traits"
        />
        <MetricCard
          icon={<Zap className="w-5 h-5" />}
          label="SITUATIONAL"
          value={situationalCount}
          color="blue"
          description="Environment-driven"
        />
        <MetricCard
          icon={<Brain className="w-5 h-5" />}
          label="MIXED"
          value={mixedCount}
          color="amber"
          description="Context-dependent"
        />
      </div>

      {/* Behavior Cards */}
      <div className="space-y-3">
        {data.map((behavior) => (
          <BehaviorCard
            key={behavior.channel}
            behavior={behavior}
            isExpanded={expandedChannel === behavior.channel}
            onToggle={() => setExpandedChannel(
              expandedChannel === behavior.channel ? null : behavior.channel
            )}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="carbon-plate border border-zinc-800 p-4">
        <h4 className="text-xs text-zinc-500 font-mono uppercase tracking-wide mb-3">
          KELLEY&apos;S COVARIATION MODEL
        </h4>
        <div className="grid grid-cols-3 gap-4 text-xs font-mono">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-3 h-3 text-amber-500" />
              <span className="text-zinc-400 uppercase">Consistency</span>
            </div>
            <p className="text-zinc-600">Does this happen every time?</p>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Fingerprint className="w-3 h-3 text-purple-500" />
              <span className="text-zinc-400 uppercase">Distinctiveness</span>
            </div>
            <p className="text-zinc-600">Unique to this channel?</p>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Users className="w-3 h-3 text-blue-500" />
              <span className="text-zinc-400 uppercase">Consensus</span>
            </div>
            <p className="text-zinc-600">Does everyone do this?</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value, color, description }: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: 'purple' | 'blue' | 'amber';
  description: string;
}) {
  const colorClasses = {
    purple: 'text-purple-500 border-purple-500/30 bg-purple-950/20',
    blue: 'text-blue-500 border-blue-500/30 bg-blue-950/20',
    amber: 'text-amber-500 border-amber-500/30 bg-amber-950/20',
  };

  return (
    <div className={`carbon-plate border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 mb-2">
        <div className={colorClasses[color].split(' ')[0]}>{icon}</div>
        <span className="text-xs text-zinc-500 font-mono uppercase">{label}</span>
      </div>
      <div className={`text-3xl font-bold font-mono ${colorClasses[color].split(' ')[0]}`}>
        {value}
      </div>
      <div className="text-xs text-zinc-600 font-mono mt-1">{description}</div>
    </div>
  );
}

function BehaviorCard({ behavior, isExpanded, onToggle }: {
  behavior: BehaviorAnalysis;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const tagStyles = {
    DISPOSITIONAL: {
      bg: 'bg-purple-950/30',
      border: 'border-purple-500/30',
      text: 'text-purple-400',
      badge: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    },
    SITUATIONAL: {
      bg: 'bg-blue-950/30',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      badge: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    },
    MIXED: {
      bg: 'bg-amber-950/30',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
      badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    },
  };

  const style = tagStyles[behavior.tag];

  return (
    <div className={`carbon-plate border ${style.border} ${style.bg} overflow-hidden transition-all`}>
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-zinc-900/30 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 carbon-plate-deep border border-zinc-700 flex items-center justify-center">
            <span className="text-amber-500 font-mono font-bold text-sm">
              {behavior.channel.charAt(0)}
            </span>
          </div>
          <div className="text-left">
            <h4 className="text-sm font-bold text-zinc-100 font-mono uppercase">
              {behavior.channel}
            </h4>
            <p className="text-xs text-zinc-500 font-mono mt-0.5">{behavior.insight}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 text-xs font-mono uppercase border ${style.badge}`}>
            [{behavior.tag}]
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-zinc-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-zinc-500" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 animate-fade-in">
          <div className="h-px bg-zinc-800" />

          {/* Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <MetricBar
              label="Consistency"
              value={behavior.consistency}
              color="amber"
            />
            <MetricBar
              label="Distinctiveness"
              value={behavior.distinctiveness}
              color="purple"
            />
            <MetricBar
              label="Consensus"
              value={behavior.consensus}
              color="blue"
            />
          </div>

          {/* Analysis Logic */}
          <div className="carbon-plate-deep border border-zinc-800 p-3">
            <p className="text-xs text-zinc-500 font-mono uppercase mb-2">Analysis Logic</p>
            <div className="flex flex-wrap gap-2 text-xs font-mono">
              <LogicChip
                label="Consistency"
                value={behavior.consistency}
                threshold={0.7}
                highMeaning="Regular pattern"
                lowMeaning="Variable behavior"
              />
              <LogicChip
                label="Distinctiveness"
                value={behavior.distinctiveness}
                threshold={0.3}
                highMeaning="Channel-specific"
                lowMeaning="Cross-channel"
                invertLogic
              />
              <LogicChip
                label="Consensus"
                value={behavior.consensus}
                threshold={0.3}
                highMeaning="Common behavior"
                lowMeaning="Unique to you"
                invertLogic
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricBar({ label, value, color }: {
  label: string;
  value: number;
  color: 'amber' | 'purple' | 'blue';
}) {
  const colorClasses = {
    amber: 'bg-amber-500',
    purple: 'bg-purple-500',
    blue: 'bg-blue-500',
  };

  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-xs text-zinc-500 font-mono uppercase">{label}</span>
        <span className="text-xs text-zinc-300 font-mono">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-2 bg-zinc-800 rounded-sm overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  );
}

function LogicChip({ label, value, threshold, highMeaning, lowMeaning, invertLogic }: {
  label: string;
  value: number;
  threshold: number;
  highMeaning: string;
  lowMeaning: string;
  invertLogic?: boolean;
}) {
  const isHigh = invertLogic ? value < threshold : value > threshold;
  const meaning = isHigh ? highMeaning : lowMeaning;
  const color = isHigh ? 'text-emerald-500' : 'text-zinc-500';

  return (
    <span className={`px-2 py-1 carbon-plate border border-zinc-700 ${color}`}>
      {label}: {meaning}
    </span>
  );
}
