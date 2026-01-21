'use client';

import { FileText, Download, Eye, AlertTriangle, CheckCircle2, Shield } from 'lucide-react';
import { useState } from 'react';

interface LLMReportsProps {
  data: any;
}

export default function LLMReports({ data }: LLMReportsProps) {
  const [activeReport, setActiveReport] = useState<string | null>(null);

  const reports = [
    {
      id: 'executive',
      title: 'EXECUTIVE BRIEF',
      description: 'Command-level overview for decision makers',
      icon: Shield,
      color: 'amber',
      classification: 'CONFIDENTIAL',
      content: data?.executive_summary || 'No executive summary available.',
    },
    {
      id: 'technical',
      title: 'TECHNICAL ANALYSIS',
      description: 'Detailed methodology breakdown',
      icon: FileText,
      color: 'emerald',
      classification: 'SECRET',
      content: data?.model_decomposition || 'No technical analysis available.',
    },
    {
      id: 'risks',
      title: 'RISK ASSESSMENT',
      description: 'Model limitations and validation',
      icon: AlertTriangle,
      color: 'orange',
      classification: 'RESTRICTED',
      content: data?.risk_and_assumptions || 'No risk analysis available.',
    },
  ];

  const handleDownload = (reportId: string, content: string, title: string) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportId}_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getColorClasses = (color: string) => {
    const colors: Record<string, any> = {
      amber: {
        border: 'border-amber-500/30',
        bg: 'bg-amber-950/20',
        text: 'text-amber-500',
        hover: 'hover:border-amber-500/50',
      },
      emerald: {
        border: 'border-emerald-500/30',
        bg: 'bg-emerald-950/20',
        text: 'text-emerald-500',
        hover: 'hover:border-emerald-500/50',
      },
      orange: {
        border: 'border-orange-500/30',
        bg: 'bg-orange-950/20',
        text: 'text-orange-500',
        hover: 'hover:border-orange-500/50',
      },
    };
    return colors[color] || colors.amber;
  };

  return (
    <div className="space-y-6">
      {/* Reports Overview */}
      <div className="carbon-plate border border-amber-500/30 p-6">
        <div className="flex gap-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 border border-amber-500/50 flex items-center justify-center">
              <FileText className="w-6 h-6 text-amber-500" />
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide">
              AI-GENERATED INTELLIGENCE REPORTS
            </h3>
            <p className="text-xs text-zinc-400 leading-relaxed font-mono">
              LLM interpretation layer has generated classified intelligence reports from attribution data. 
              Each document is tailored for specific clearance levels and operational requirements.
            </p>
          </div>
        </div>
      </div>

      {/* Report Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {reports.map((report) => {
          const colors = getColorClasses(report.color);
          const Icon = report.icon;
          
          return (
            <div
              key={report.id}
              className={`carbon-plate border ${colors.border} ${colors.hover} transition-all`}
            >
              <div className={`${colors.bg} border-b ${colors.border} p-4`}>
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-10 h-10 border ${colors.border} flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${colors.text}`} />
                  </div>
                  <span className={`px-2 py-1 border ${colors.border} ${colors.text} text-xs font-mono tracking-wider`}>
                    {report.classification}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-zinc-100 mb-2 font-mono uppercase tracking-wide">{report.title}</h3>
                <p className="text-xs text-zinc-500 font-mono">{report.description}</p>
              </div>
              
              <div className="p-3 space-y-2">
                <button
                  onClick={() => setActiveReport(activeReport === report.id ? null : report.id)}
                  className={`w-full px-3 py-2 border ${colors.border} ${colors.text} hover:${colors.bg} font-mono text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2`}
                >
                  <Eye className="w-4 h-4" />
                  {activeReport === report.id ? 'CLOSE' : 'VIEW'}
                </button>
                
                <button
                  onClick={() => handleDownload(report.id, report.content, report.title)}
                  className="w-full px-3 py-2 carbon-plate border border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200 transition-all font-mono text-xs uppercase tracking-wider flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  EXPORT
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Report Display */}
      {activeReport && (
        <div className="carbon-plate-deep border border-zinc-800">
          <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950/50 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
                {reports.find(r => r.id === activeReport)?.title}
              </h3>
              <p className="text-xs text-zinc-500 font-mono">
                {reports.find(r => r.id === activeReport)?.description}
              </p>
            </div>
            <button
              onClick={() => setActiveReport(null)}
              className="px-3 py-1 text-xs text-zinc-500 hover:text-zinc-200 border border-zinc-700 hover:border-zinc-500 transition-all font-mono uppercase tracking-wider"
            >
              CLOSE
            </button>
          </div>
          
          <div className="p-6">
            <div className="carbon-plate-deep border border-zinc-800 p-4">
              <pre className="whitespace-pre-wrap font-mono text-xs text-zinc-300 leading-relaxed">
                {reports.find(r => r.id === activeReport)?.content}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Generation Info */}
      <div className="carbon-plate border border-zinc-800 p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 border border-emerald-500/50 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            </div>
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-bold text-zinc-100 mb-3 font-mono uppercase tracking-wide">REPORT GENERATION METADATA</h4>
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="carbon-plate-deep border border-zinc-800 p-3">
                <span className="text-zinc-500 uppercase tracking-wider">IR VERSION</span>
                <div className="text-zinc-100 font-bold mt-1">{data?.ir_version || 'N/A'}</div>
              </div>
              <div className="carbon-plate-deep border border-zinc-800 p-3">
                <span className="text-zinc-500 uppercase tracking-wider">MODEL TYPE</span>
                <div className="text-zinc-100 font-bold mt-1">MARKOV-SHAPLEY</div>
              </div>
              <div className="carbon-plate-deep border border-zinc-800 p-3">
                <span className="text-zinc-500 uppercase tracking-wider">LLM ENGINE</span>
                <div className="text-zinc-100 font-bold mt-1">CLAUDE SONNET 4</div>
              </div>
              <div className="carbon-plate-deep border border-zinc-800 p-3">
                <span className="text-zinc-500 uppercase tracking-wider">GENERATED</span>
                <div className="text-zinc-100 font-bold mt-1">
                  {data?.generated_at ? new Date(data.generated_at).toLocaleString() : 'JUST NOW'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Artifacts */}
      <div className="carbon-plate border border-zinc-800">
        <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950/50">
          <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">ADDITIONAL ARTIFACTS</h3>
          <p className="text-xs text-zinc-500 font-mono mt-1">Visualization specifications and diagram source files</p>
        </div>
        
        <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          <button className="flex items-center gap-4 p-4 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-all text-left">
            <div className="w-10 h-10 border border-zinc-700 flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-zinc-500" />
            </div>
            <div className="flex-1">
              <h4 className="text-xs font-bold text-zinc-100 font-mono uppercase">MERMAID DIAGRAMS</h4>
              <p className="text-xs text-zinc-600 font-mono">Flow charts and visualizations</p>
            </div>
            <Download className="w-4 h-4 text-zinc-600" />
          </button>

          <button className="flex items-center gap-4 p-4 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-all text-left">
            <div className="w-10 h-10 border border-zinc-700 flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-zinc-500" />
            </div>
            <div className="flex-1">
              <h4 className="text-xs font-bold text-zinc-100 font-mono uppercase">VIZ SPECIFICATIONS</h4>
              <p className="text-xs text-zinc-600 font-mono">Chart data and configurations</p>
            </div>
            <Download className="w-4 h-4 text-zinc-600" />
          </button>
        </div>
      </div>
    </div>
  );
}
