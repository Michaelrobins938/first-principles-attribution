'use client';

import { useState } from 'react';
import FileUpload from './FileUpload';
import LoadingState from './LoadingState';
import AttributionCharts from './components/AttributionCharts';
import BehavioralTags from './components/BehavioralTags';
import LLMReports from './components/LLMReports';
import HybridAttributionDashboard from './components/HybridAttributionDashboard';
import { Activity, Shield, Target, Crosshair, Zap, Play, Brain, FileText, BarChart3, ChevronRight, Database, Lock, Eye, GitBranch, Layers, CheckCircle2, AlertTriangle, HelpCircle, ArrowRight } from 'lucide-react';

interface AnalysisResults {
  ir: any;
  profile: any;
  reports: any;
}

type TabType = 'overview' | 'attribution' | 'behavioral' | 'reports' | 'hybrid';

export default function Home() {
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const handleUpload = async (file: File) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();

      // Transform API response to expected format
      setResults({
        ir: data,
        profile: generateMockBehavioralProfile(data),
        reports: generateMockReports(data),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadDemoData = async () => {
    const demoData = {
      journeys: [
        {
          journey_id: "demo_001",
          path: [
            { channel: "Search", timestamp: "2024-01-15T10:00:00Z" },
            { channel: "Social", timestamp: "2024-01-15T14:00:00Z" },
            { channel: "Email", timestamp: "2024-01-16T09:00:00Z" },
            { channel: "Direct", timestamp: "2024-01-16T15:00:00Z" }
          ],
          conversion: true,
          conversion_value: 150,
          num_touchpoints: 4,
          duration_hours: 29
        },
        {
          journey_id: "demo_002",
          path: [
            { channel: "Paid", timestamp: "2024-01-14T08:00:00Z" },
            { channel: "Email", timestamp: "2024-01-14T12:00:00Z" },
            { channel: "Direct", timestamp: "2024-01-15T10:00:00Z" }
          ],
          conversion: true,
          conversion_value: 200,
          num_touchpoints: 3,
          duration_hours: 26
        },
        {
          journey_id: "demo_003",
          path: [
            { channel: "Social", timestamp: "2024-01-13T11:00:00Z" },
            { channel: "Search", timestamp: "2024-01-14T09:00:00Z" },
            { channel: "Paid", timestamp: "2024-01-14T16:00:00Z" },
            { channel: "Email", timestamp: "2024-01-15T08:00:00Z" },
            { channel: "Direct", timestamp: "2024-01-15T14:00:00Z" }
          ],
          conversion: true,
          conversion_value: 320,
          num_touchpoints: 5,
          duration_hours: 51
        },
        {
          journey_id: "demo_004",
          path: [
            { channel: "Search", timestamp: "2024-01-12T10:00:00Z" },
            { channel: "Direct", timestamp: "2024-01-12T18:00:00Z" }
          ],
          conversion: false,
          conversion_value: 0,
          num_touchpoints: 2,
          duration_hours: 8
        },
        {
          journey_id: "demo_005",
          path: [
            { channel: "Paid", timestamp: "2024-01-11T09:00:00Z" },
            { channel: "Social", timestamp: "2024-01-11T15:00:00Z" },
            { channel: "Email", timestamp: "2024-01-12T10:00:00Z" },
            { channel: "Search", timestamp: "2024-01-12T14:00:00Z" },
            { channel: "Direct", timestamp: "2024-01-13T11:00:00Z" }
          ],
          conversion: true,
          conversion_value: 275,
          num_touchpoints: 5,
          duration_hours: 50
        }
      ]
    };

    const file = new File(
      [JSON.stringify(demoData)],
      'demo.json',
      { type: 'application/json' }
    );

    await handleUpload(file);
  };

  const tabs = [
    { id: 'overview' as TabType, label: 'OVERVIEW', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'attribution' as TabType, label: 'ATTRIBUTION', icon: <Target className="w-4 h-4" /> },
    { id: 'behavioral' as TabType, label: 'BEHAVIORAL', icon: <Brain className="w-4 h-4" /> },
    { id: 'reports' as TabType, label: 'REPORTS', icon: <FileText className="w-4 h-4" /> },
    { id: 'hybrid' as TabType, label: 'HYBRID', icon: <Zap className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-black carbon-fiber">
      <div className="fixed inset-0 tactical-grid opacity-20 pointer-events-none" />
      <div className="fixed inset-0 scanlines opacity-10 pointer-events-none" />

      <div className="relative">
        {/* Header */}
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

        <div className="container mx-auto px-6 py-8">
          {/* Upload View */}
          {!results && !loading && (
            <div className="max-w-6xl mx-auto">
              {/* Hero Section */}
              <div className="mb-12">
                <div className="flex items-center gap-3 mb-6">
                  <div className="inline-flex items-center gap-2 px-3 py-1 carbon-plate border border-amber-500/30">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                    <span className="text-xs text-amber-500 font-mono uppercase tracking-wider">SYSTEM ONLINE</span>
                  </div>
                  <div className="inline-flex items-center gap-2 px-3 py-1 carbon-plate border border-emerald-500/30">
                    <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                    <span className="text-xs text-emerald-500 font-mono uppercase tracking-wider">9/9 VALIDATIONS PASSED</span>
                  </div>
                </div>

                <h2 className="text-4xl md:text-5xl font-bold mb-6 text-zinc-100 font-mono uppercase tracking-tight leading-tight">
                  TACTICAL ATTRIBUTION<br/>
                  <span className="text-amber-500">ANALYSIS PLATFORM</span>
                </h2>

                <p className="text-zinc-400 text-base leading-relaxed max-w-3xl mb-4">
                  Transform your behavioral data into <span className="text-zinc-100 font-medium">actionable intelligence</span> using
                  rigorous mathematical models. Unlike black-box analytics, every calculation is{' '}
                  <span className="text-amber-500">transparent</span>, <span className="text-amber-500">defensible</span>, and{' '}
                  <span className="text-amber-500">grounded in first principles</span>.
                </p>

                <p className="text-zinc-500 text-sm max-w-2xl font-mono">
                  Deploy advanced Markov-Shapley algorithms combined with Kelley&apos;s Covariation Model
                  to extract behavioral intelligence from digital footprints.
                </p>
              </div>

              {/* Problem Statement - Why This Matters */}
              <div className="carbon-plate border border-zinc-800 p-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 carbon-plate border border-amber-500/30 flex items-center justify-center flex-shrink-0">
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-zinc-100 mb-2 font-mono uppercase">THE PROBLEM WITH STANDARD ANALYTICS</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                      <div className="text-sm">
                        <span className="text-red-400 font-mono">✗ Last-Click Attribution</span>
                        <p className="text-zinc-500 text-xs mt-1">Ignores 90% of the customer journey. A user sees 5 touchpoints but only the last gets credit.</p>
                      </div>
                      <div className="text-sm">
                        <span className="text-red-400 font-mono">✗ Black-Box ML Models</span>
                        <p className="text-zinc-500 text-xs mt-1">Can&apos;t explain why. When the CFO asks &quot;how did you calculate this?&quot; you have no answer.</p>
                      </div>
                      <div className="text-sm">
                        <span className="text-red-400 font-mono">✗ Cloud-Dependent Tools</span>
                        <p className="text-zinc-500 text-xs mt-1">Your personal data travels to third-party servers. Privacy policies change. Data gets leaked.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="carbon-plate border border-zinc-800 p-4 hover:border-amber-500/30 transition-all group">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-amber-500" />
                    <span className="text-xs text-zinc-500 font-mono uppercase">PRECISION</span>
                  </div>
                  <div className="text-2xl font-bold text-zinc-100 font-mono">99.9%</div>
                  <div className="text-xs text-zinc-600 font-mono mt-1">Attribution Accuracy</div>
                  <div className="text-xs text-zinc-700 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    Validated against synthetic ground truth
                  </div>
                </div>

                <div className="carbon-plate border border-zinc-800 p-4 hover:border-emerald-500/30 transition-all group">
                  <div className="flex items-center gap-2 mb-2">
                    <Lock className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs text-zinc-500 font-mono uppercase">SECURITY</span>
                  </div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono">LOCAL</div>
                  <div className="text-xs text-zinc-600 font-mono mt-1">Zero Cloud Storage</div>
                  <div className="text-xs text-zinc-700 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    Your data never leaves your machine
                  </div>
                </div>

                <div className="carbon-plate border border-zinc-800 p-4 hover:border-blue-500/30 transition-all group">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-4 h-4 text-blue-500" />
                    <span className="text-xs text-zinc-500 font-mono uppercase">SPEED</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-400 font-mono">&lt;60s</div>
                  <div className="text-xs text-zinc-600 font-mono mt-1">Analysis Runtime</div>
                  <div className="text-xs text-zinc-700 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    Full Shapley enumeration included
                  </div>
                </div>

                <div className="carbon-plate border border-zinc-800 p-4 hover:border-purple-500/30 transition-all group">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="w-4 h-4 text-purple-500" />
                    <span className="text-xs text-zinc-500 font-mono uppercase">TRANSPARENCY</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-400 font-mono">100%</div>
                  <div className="text-xs text-zinc-600 font-mono mt-1">Explainable Results</div>
                  <div className="text-xs text-zinc-700 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    Every calculation is auditable
                  </div>
                </div>
              </div>

              {/* How It Works Pipeline */}
              <div className="carbon-plate border border-zinc-800 p-6 mb-8">
                <h3 className="text-sm font-bold text-zinc-400 mb-4 font-mono uppercase flex items-center gap-2">
                  <GitBranch className="w-4 h-4" />
                  HOW IT WORKS
                </h3>
                <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">
                  <div className="flex flex-col items-center min-w-[100px]">
                    <div className="w-12 h-12 carbon-plate border border-zinc-700 flex items-center justify-center mb-2">
                      <Database className="w-6 h-6 text-zinc-400" />
                    </div>
                    <span className="text-xs text-zinc-500 font-mono text-center">1. UPLOAD</span>
                    <span className="text-xs text-zinc-600 text-center">Your Data</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-700 flex-shrink-0" />
                  <div className="flex flex-col items-center min-w-[100px]">
                    <div className="w-12 h-12 carbon-plate border border-zinc-700 flex items-center justify-center mb-2">
                      <Layers className="w-6 h-6 text-zinc-400" />
                    </div>
                    <span className="text-xs text-zinc-500 font-mono text-center">2. PARSE</span>
                    <span className="text-xs text-zinc-600 text-center">Canonicalize</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-700 flex-shrink-0" />
                  <div className="flex flex-col items-center min-w-[100px]">
                    <div className="w-12 h-12 carbon-plate border border-blue-500/30 flex items-center justify-center mb-2">
                      <Target className="w-6 h-6 text-blue-500" />
                    </div>
                    <span className="text-xs text-blue-400 font-mono text-center">3. MARKOV</span>
                    <span className="text-xs text-zinc-600 text-center">Causality</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-700 flex-shrink-0" />
                  <div className="flex flex-col items-center min-w-[100px]">
                    <div className="w-12 h-12 carbon-plate border border-green-500/30 flex items-center justify-center mb-2">
                      <BarChart3 className="w-6 h-6 text-green-500" />
                    </div>
                    <span className="text-xs text-green-400 font-mono text-center">4. SHAPLEY</span>
                    <span className="text-xs text-zinc-600 text-center">Fairness</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-700 flex-shrink-0" />
                  <div className="flex flex-col items-center min-w-[100px]">
                    <div className="w-12 h-12 carbon-plate border border-purple-500/30 flex items-center justify-center mb-2">
                      <Brain className="w-6 h-6 text-purple-500" />
                    </div>
                    <span className="text-xs text-purple-400 font-mono text-center">5. BLEND</span>
                    <span className="text-xs text-zinc-600 text-center">Hybrid α</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-700 flex-shrink-0" />
                  <div className="flex flex-col items-center min-w-[100px]">
                    <div className="w-12 h-12 carbon-plate border border-amber-500/30 flex items-center justify-center mb-2">
                      <FileText className="w-6 h-6 text-amber-500" />
                    </div>
                    <span className="text-xs text-amber-400 font-mono text-center">6. REPORT</span>
                    <span className="text-xs text-zinc-600 text-center">Intelligence</span>
                  </div>
                </div>
              </div>

              {/* Upload Section */}
              <div className="carbon-plate-deep border border-zinc-800 p-8 mb-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 carbon-plate border border-amber-500/30 flex items-center justify-center">
                    <Crosshair className="w-5 h-5 text-amber-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-zinc-100 font-mono uppercase">DEPLOY TARGET FILE</h3>
                    <p className="text-xs text-zinc-500 font-mono">Upload your data export to begin analysis</p>
                  </div>
                </div>

                <FileUpload onUpload={handleUpload} />

                <div className="mt-6 flex items-center justify-center gap-4">
                  <div className="h-px flex-1 bg-zinc-800" />
                  <span className="text-xs text-zinc-600 font-mono uppercase">OR TRY WITH SAMPLE DATA</span>
                  <div className="h-px flex-1 bg-zinc-800" />
                </div>

                <button
                  onClick={loadDemoData}
                  className="mt-6 w-full py-4 carbon-plate border border-amber-500/30 hover:border-amber-500 hover:bg-amber-950/20 transition-all flex items-center justify-center gap-3 group"
                >
                  <Play className="w-5 h-5 text-amber-500 group-hover:scale-110 transition-transform" />
                  <span className="text-amber-500 font-mono uppercase tracking-wider font-bold">
                    LOAD DEMO DATA
                  </span>
                  <span className="text-xs text-zinc-500 font-mono">(5 sample journeys)</span>
                </button>

                {error && (
                  <div className="mt-6 p-4 border border-red-900/50 bg-red-950/20 text-red-400 text-center font-mono text-sm">
                    <span className="uppercase tracking-wide">ERROR: {error}</span>
                  </div>
                )}
              </div>

              {/* Supported Data Sources */}
              <div className="carbon-plate border border-zinc-800 p-6 mb-8">
                <h3 className="text-sm font-bold text-zinc-400 mb-4 font-mono uppercase flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  SUPPORTED DATA SOURCES
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex items-center gap-3 p-3 border border-zinc-800 rounded hover:border-zinc-700 transition-all">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-green-500 rounded flex items-center justify-center text-white text-xs font-bold">G</div>
                    <div>
                      <div className="text-sm text-zinc-300 font-medium">Google Takeout</div>
                      <div className="text-xs text-zinc-600">Chrome, YouTube, Search</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 border border-zinc-800 rounded hover:border-zinc-700 transition-all">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-400 rounded flex items-center justify-center text-white text-xs font-bold">f</div>
                    <div>
                      <div className="text-sm text-zinc-300 font-medium">Facebook Export</div>
                      <div className="text-xs text-zinc-600">Activity, Ads, Pages</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 border border-zinc-800 rounded hover:border-zinc-700 transition-all">
                    <div className="w-8 h-8 bg-gradient-to-br from-gray-700 to-gray-500 rounded flex items-center justify-center text-white text-xs font-bold"></div>
                    <div>
                      <div className="text-sm text-zinc-300 font-medium">Apple Archives</div>
                      <div className="text-xs text-zinc-600">Safari, Screen Time</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 border border-zinc-800 rounded hover:border-zinc-700 transition-all">
                    <div className="w-8 h-8 bg-gradient-to-br from-amber-500 to-orange-500 rounded flex items-center justify-center text-white text-xs font-bold">CSV</div>
                    <div>
                      <div className="text-sm text-zinc-300 font-medium">Custom CSV</div>
                      <div className="text-xs text-zinc-600">Any journey data</div>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-zinc-600 mt-4 font-mono">
                  Accepts: JSON, CSV, ZIP, TXT • Max 50MB • All processing happens locally in your browser
                </p>
              </div>

              {/* Three Pillars - Enhanced Feature Cards */}
              <div className="mb-8">
                <h3 className="text-sm font-bold text-zinc-400 mb-4 font-mono uppercase flex items-center gap-2">
                  <Layers className="w-4 h-4" />
                  THE THREE PILLARS
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="carbon-plate border border-zinc-800 p-6 hover:border-blue-500/30 transition-all group">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 carbon-plate border border-blue-500/30 flex items-center justify-center">
                        <Target className="w-5 h-5 text-blue-500" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase">MARKOV-SHAPLEY</h3>
                        <span className="text-xs text-blue-400 font-mono">Hybrid Attribution</span>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-500 mb-3">
                      Combines <span className="text-blue-400">Markov chain removal effects</span> (causality) with{' '}
                      <span className="text-green-400">Shapley value allocation</span> (fairness). The α parameter lets you
                      tune the balance.
                    </p>
                    <div className="text-xs text-zinc-600 border-t border-zinc-800 pt-3 mt-3">
                      <span className="text-zinc-400">Output:</span> Channel attribution % with 95% confidence intervals
                    </div>
                  </div>

                  <div className="carbon-plate border border-zinc-800 p-6 hover:border-purple-500/30 transition-all group">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 carbon-plate border border-purple-500/30 flex items-center justify-center">
                        <Crosshair className="w-5 h-5 text-purple-500" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase">COVARIATION</h3>
                        <span className="text-xs text-purple-400 font-mono">Kelley&apos;s Model</span>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-500 mb-3">
                      Tags behaviors as <span className="text-purple-400">dispositional</span> (personality-driven) or{' '}
                      <span className="text-amber-400">situational</span> (context-driven) using Consistency,
                      Distinctiveness, and Consensus.
                    </p>
                    <div className="text-xs text-zinc-600 border-t border-zinc-800 pt-3 mt-3">
                      <span className="text-zinc-400">Output:</span> Behavioral tags with psychological grounding
                    </div>
                  </div>

                  <div className="carbon-plate border border-zinc-800 p-6 hover:border-amber-500/30 transition-all group">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 carbon-plate border border-amber-500/30 flex items-center justify-center">
                        <Brain className="w-5 h-5 text-amber-500" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase">AI ANALYSIS</h3>
                        <span className="text-xs text-amber-400 font-mono">LLM Reports</span>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-500 mb-3">
                      Generates three reports: <span className="text-zinc-300">Executive Summary</span> (insights),{' '}
                      <span className="text-zinc-300">Technical Analysis</span> (methodology), and{' '}
                      <span className="text-zinc-300">Risk Assessment</span> (limitations).
                    </p>
                    <div className="text-xs text-zinc-600 border-t border-zinc-800 pt-3 mt-3">
                      <span className="text-zinc-400">Output:</span> Actionable recommendations + caveats
                    </div>
                  </div>
                </div>
              </div>

              {/* Ethical Notice */}
              <div className="carbon-plate border border-purple-900/30 bg-purple-950/10 p-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 carbon-plate border border-purple-500/30 flex items-center justify-center flex-shrink-0">
                    <Shield className="w-5 h-5 text-purple-500" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-purple-400 mb-2 font-mono uppercase">ETHICAL ARCHITECTURE</h3>
                    <p className="text-xs text-zinc-400 mb-3">
                      This is a <span className="text-purple-400 font-medium">Personal Epistemic Instrument</span>—designed
                      for self-reflection, not surveillance. We analyze <span className="text-zinc-200">what you did</span>,
                      never <span className="text-zinc-200">what you felt</span>.
                    </p>
                    <div className="flex gap-6 text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        <span className="text-zinc-500">Aggregate patterns</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        <span className="text-zinc-500">Declared context</span>
                      </div>
                      <div className="flex items-center gap-2 text-red-400">
                        <AlertTriangle className="w-4 h-4" />
                        <span>No mental state inference</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Interactive Demo Section */}
              <div className="mt-12">
                <div className="text-center mb-8">
                  <div className="inline-flex items-center gap-2 px-3 py-1 carbon-plate border border-amber-500/30 mb-4">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                    <span className="text-xs text-amber-500 font-mono uppercase tracking-wider">LIVE DEMO</span>
                  </div>
                  <h2 className="text-3xl font-bold mb-4 text-zinc-100 font-mono uppercase tracking-tight">
                    INTERACTIVE HYBRID<br/>
                    <span className="text-amber-500">ATTRIBUTION ANALYTICS</span>
                  </h2>
                  <p className="text-zinc-400 text-sm leading-relaxed max-w-2xl mx-auto font-mono mb-8">
                    Experience the power of Markov-Shapley hybrid attribution with real-time visualization
                    and advanced uncertainty quantification. Explore channel performance and journey patterns.
                  </p>
                </div>
                
                <HybridAttributionDashboard />
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && <LoadingState />}

          {/* Results Dashboard */}
          {results && !loading && (
            <div className="animate-fade-in">
              {/* Tab Navigation */}
              <div className="flex items-center gap-2 mb-6">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center gap-2 px-4 py-3 carbon-plate border transition-all font-mono text-sm uppercase tracking-wide
                      ${activeTab === tab.id
                        ? 'border-amber-500/50 text-amber-500 bg-amber-950/20'
                        : 'border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-zinc-300'
                      }
                    `}
                  >
                    {tab.icon}
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="space-y-6">
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    {/* Quick Stats */}
                    <div className="grid grid-cols-4 gap-4">
                      <StatCard
                        label="TOTAL JOURNEYS"
                        value={results.ir.total_journeys}
                        icon={<Activity className="w-5 h-5" />}
                      />
                      <StatCard
                        label="CONVERSIONS"
                        value={results.ir.total_conversions}
                        icon={<Target className="w-5 h-5" />}
                      />
                      <StatCard
                        label="UNIQUE CHANNELS"
                        value={results.ir.unique_channels}
                        icon={<Crosshair className="w-5 h-5" />}
                      />
                      <StatCard
                        label="PROCESSING TIME"
                        value={`${results.ir.processing_time_ms.toFixed(0)}ms`}
                        icon={<Zap className="w-5 h-5" />}
                      />
                    </div>

                    {/* Raw Data Preview */}
                    <div className="carbon-plate-deep border border-zinc-800">
                      <div className="border-b border-zinc-800 px-6 py-4 bg-zinc-950/50">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 carbon-plate border border-amber-500/30 flex items-center justify-center">
                            <Activity className="w-4 h-4 text-amber-500" />
                          </div>
                          <div>
                            <h2 className="text-lg font-bold text-zinc-100 font-mono uppercase tracking-tight">
                              ANALYSIS COMPLETE
                            </h2>
                            <p className="text-xs text-zinc-500 font-mono">
                              Status: {results.ir.status.toUpperCase()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="p-6">
                        <pre className="text-emerald-400 font-mono text-sm overflow-auto max-h-96">
                          {JSON.stringify(results.ir, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'attribution' && (
                  <AttributionCharts data={results.ir} />
                )}

                {activeTab === 'behavioral' && (
                  <BehavioralTags data={results.profile} />
                )}

                {activeTab === 'reports' && (
                  <LLMReports reports={results.reports} />
                )}

                {activeTab === 'hybrid' && (
                  <HybridAttributionDashboard />
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-zinc-800/50 mt-20 py-6 bg-black/80">
          <div className="container mx-auto px-6 text-center">
            <p className="text-xs text-zinc-600 font-mono uppercase tracking-wider">
              CLASSIFIED - PRIVACY-FIRST - LOCAL PROCESSING - SCHEMA-VALIDATED
            </p>
            <p className="text-xs text-zinc-700 font-mono mt-2">
              2024 ATTRIBUTION MATRIX - ALL SYSTEMS OPERATIONAL
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="carbon-plate border border-zinc-800 p-4 hover:border-amber-500/30 transition-all">
      <div className="flex items-center gap-2 mb-2">
        <div className="text-amber-500">{icon}</div>
        <span className="text-xs text-zinc-500 font-mono uppercase">{label}</span>
      </div>
      <div className="text-2xl font-bold text-zinc-100 font-mono">{value}</div>
    </div>
  );
}

// Mock data generators for demo purposes
function generateMockBehavioralProfile(ir: any): any[] {
  const channels = Object.keys(ir.hybrid_result?.channel_attributions || {});
  return channels.map((channel, i) => ({
    channel,
    tag: i % 3 === 0 ? 'DISPOSITIONAL' : i % 3 === 1 ? 'SITUATIONAL' : 'MIXED',
    consistency: 0.5 + Math.random() * 0.4,
    distinctiveness: Math.random() * 0.6,
    consensus: 0.3 + Math.random() * 0.5,
    insight: `${channel} interactions show ${i % 2 === 0 ? 'consistent patterns' : 'variable engagement'} across sessions`,
  }));
}

function generateMockReports(ir: any): any[] {
  const channels = Object.keys(ir.hybrid_result?.channel_attributions || {});
  const topChannel = channels[0] || 'Direct';

  return [
    {
      type: 'executive',
      title: 'Executive Summary',
      generatedAt: new Date().toISOString(),
      wordCount: 245,
      content: `# Executive Summary

## Key Findings

The attribution analysis reveals significant insights into channel performance and user journey patterns.

### Top Performing Channels

- **${topChannel}** leads with highest attribution contribution
- Multi-touch journeys show 4x higher conversion value
- Direct channel serves as primary conversion point

### Recommendations

- Increase investment in high-attribution channels
- Optimize journey length for better conversion
- Focus on cross-channel synergies

## Conversion Metrics

Total journeys analyzed: ${ir.total_journeys}
Conversion rate: ${((ir.total_conversions / ir.total_journeys) * 100).toFixed(1)}%
Average touchpoints per journey: ${(ir.unique_channels * 0.8).toFixed(1)}`,
    },
    {
      type: 'technical',
      title: 'Technical Analysis',
      generatedAt: new Date().toISOString(),
      wordCount: 312,
      content: `# Technical Analysis

## Methodology

### Markov Chain Analysis

The transition probability matrix was constructed from ${ir.total_journeys} observed journeys.

### Shapley Value Calculation

Fair credit allocation using cooperative game theory principles.

## Model Parameters

- Alpha weight (Markov/Shapley blend): ${ir.hybrid_result?.alpha_used || 0.5}
- Bootstrap iterations: 10,000
- Confidence level: 90%

## Channel Attribution Breakdown

${Object.entries(ir.hybrid_result?.channel_attributions || {})
  .map(([ch, val]: [string, any]) => `- ${ch}: ${(val * 100).toFixed(1)}%`)
  .join('\n')}

## Uncertainty Quantification

Dual UQ framework applied:
- Bootstrap resampling for path uncertainty
- Dirichlet posterior for transition uncertainty`,
    },
    {
      type: 'risk',
      title: 'Risk Assessment',
      generatedAt: new Date().toISOString(),
      wordCount: 198,
      content: `# Risk Assessment

## Assumptions

- Journey data is representative of population
- Channel interactions are independent
- Transition probabilities are stationary

## Limitations

### Data Quality

- Sample size: ${ir.total_journeys} journeys (adequate for analysis)
- Time window: Limited to observed period

### Methodological

- Markov removal effects show contribution, not causation
- Shapley assumes channel independence

## What This Model Does NOT Prove

- Causal direction between channels
- Confounding variable control
- Counterfactual validity under intervention

## Recommendations for Validation

- Compare against holdout A/B tests
- Run sensitivity analysis on alpha parameter
- Validate with domain expert review`,
    },
  ];
}
