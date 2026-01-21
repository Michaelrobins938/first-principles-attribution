'use client';

import { useState } from 'react';
import { FileText, Download, Eye, Clock, Cpu, CheckCircle, AlertTriangle } from 'lucide-react';

interface Report {
  type: 'executive' | 'technical' | 'risk';
  title: string;
  content: string;
  generatedAt: string;
  wordCount: number;
}

interface LLMReportsProps {
  reports: Report[];
}

export default function LLMReports({ reports }: LLMReportsProps) {
  const [activeReport, setActiveReport] = useState<string>(reports[0]?.type || 'executive');
  const [viewMode, setViewMode] = useState<'preview' | 'full'>('preview');

  const currentReport = reports.find(r => r.type === activeReport);

  const reportIcons = {
    executive: <FileText className="w-4 h-4" />,
    technical: <Cpu className="w-4 h-4" />,
    risk: <AlertTriangle className="w-4 h-4" />,
  };

  const reportDescriptions = {
    executive: 'Stakeholder-ready summary with key insights',
    technical: 'Detailed methodology and model decomposition',
    risk: 'Assumptions, limitations, and caveats',
  };

  const handleDownload = (report: Report) => {
    const blob = new Blob([report.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.type}_summary.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Report Tabs */}
      <div className="flex items-center gap-2">
        {reports.map((report) => (
          <button
            key={report.type}
            onClick={() => setActiveReport(report.type)}
            className={`
              flex items-center gap-2 px-4 py-3 carbon-plate border transition-all font-mono text-sm uppercase tracking-wide
              ${activeReport === report.type
                ? 'border-amber-500/50 text-amber-500 bg-amber-950/20'
                : 'border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-zinc-300'
              }
            `}
          >
            {reportIcons[report.type]}
            <span>{report.title}</span>
            <CheckCircle className="w-3 h-3 text-emerald-500" />
          </button>
        ))}
      </div>

      {/* Report Content */}
      {currentReport && (
        <div className="carbon-plate-deep border border-zinc-800">
          {/* Report Header */}
          <div className="border-b border-zinc-800 px-6 py-4 bg-zinc-950/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 carbon-plate border border-amber-500/30 flex items-center justify-center">
                  <span className="text-amber-500">{reportIcons[currentReport.type]}</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-zinc-100 font-mono uppercase tracking-tight">
                    {currentReport.title}
                  </h3>
                  <p className="text-xs text-zinc-500 font-mono">
                    {reportDescriptions[currentReport.type]}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-4 text-xs text-zinc-500 font-mono">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(currentReport.generatedAt).toLocaleTimeString()}
                  </span>
                  <span>{currentReport.wordCount} words</span>
                </div>
                <button
                  onClick={() => setViewMode(viewMode === 'preview' ? 'full' : 'preview')}
                  className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
                  title={viewMode === 'preview' ? 'Expand' : 'Collapse'}
                >
                  <Eye className="w-4 h-4 text-zinc-400" />
                </button>
                <button
                  onClick={() => handleDownload(currentReport)}
                  className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
                  title="Download"
                >
                  <Download className="w-4 h-4 text-zinc-400" />
                </button>
              </div>
            </div>
          </div>

          {/* Report Body */}
          <div className={`p-6 overflow-auto transition-all ${viewMode === 'full' ? 'max-h-[600px]' : 'max-h-[300px]'}`}>
            <div className="prose prose-invert prose-sm max-w-none">
              <MarkdownRenderer content={currentReport.content} />
            </div>
          </div>

          {/* Report Footer */}
          <div className="border-t border-zinc-800 px-6 py-3 bg-zinc-950/30">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-zinc-600">
                Generated via LLM Scaffold Layer
              </span>
              <span className="text-emerald-500 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Schema Validated
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Generation Info */}
      <div className="carbon-plate border border-zinc-800 p-4">
        <h4 className="text-xs text-zinc-500 font-mono uppercase tracking-wide mb-3">
          ANALYSIS ARTIFACTS
        </h4>
        <div className="grid grid-cols-5 gap-3">
          {[
            { name: 'executive_summary.md', status: 'complete' },
            { name: 'model_decomposition.md', status: 'complete' },
            { name: 'diagrams.mmd', status: 'complete' },
            { name: 'viz_spec.json', status: 'complete' },
            { name: 'risk_assessment.md', status: 'complete' },
          ].map((artifact) => (
            <div
              key={artifact.name}
              className="carbon-plate-deep border border-zinc-800 p-3 text-center"
            >
              <FileText className="w-4 h-4 text-amber-500 mx-auto mb-2" />
              <p className="text-xs text-zinc-400 font-mono truncate" title={artifact.name}>
                {artifact.name}
              </p>
              <span className="text-xs text-emerald-500 font-mono uppercase">
                {artifact.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MarkdownRenderer({ content }: { content: string }) {
  // Simple markdown rendering for demo
  const lines = content.split('\n');

  return (
    <div className="space-y-3">
      {lines.map((line, i) => {
        if (line.startsWith('# ')) {
          return (
            <h1 key={i} className="text-xl font-bold text-amber-500 font-mono uppercase mt-4">
              {line.replace('# ', '')}
            </h1>
          );
        }
        if (line.startsWith('## ')) {
          return (
            <h2 key={i} className="text-lg font-bold text-zinc-100 font-mono uppercase mt-3">
              {line.replace('## ', '')}
            </h2>
          );
        }
        if (line.startsWith('### ')) {
          return (
            <h3 key={i} className="text-sm font-bold text-zinc-200 font-mono uppercase mt-2">
              {line.replace('### ', '')}
            </h3>
          );
        }
        if (line.startsWith('- ')) {
          return (
            <li key={i} className="text-zinc-300 font-mono text-sm ml-4 list-disc">
              {line.replace('- ', '')}
            </li>
          );
        }
        if (line.startsWith('**') && line.endsWith('**')) {
          return (
            <p key={i} className="text-zinc-100 font-mono text-sm font-bold">
              {line.replace(/\*\*/g, '')}
            </p>
          );
        }
        if (line.trim() === '') {
          return <div key={i} className="h-2" />;
        }
        return (
          <p key={i} className="text-zinc-400 font-mono text-sm leading-relaxed">
            {line}
          </p>
        );
      })}
    </div>
  );
}
