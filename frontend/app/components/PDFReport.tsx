'use client';

import { useState } from 'react';
import { Download, FileText, CheckCircle2 } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

interface PDFReportProps {
  results: any;
  chartsRef: React.RefObject<HTMLDivElement>;
}

export default function PDFReport({ results, chartsRef }: PDFReportProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const generatePDF = async () => {
    setIsGenerating(true);
    
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      let yPosition = 20;

      // Helper function to add new page if needed
      const checkPageBreak = (requiredSpace: number) => {
        if (yPosition + requiredSpace > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
          return true;
        }
        return false;
      };

      // Title Page
      pdf.setFontSize(24);
      pdf.setTextColor(255, 215, 0); // Amber color
      pdf.setFont('helvetica', 'bold');
      pdf.text('ATTRIBUTION MATRIX REPORT', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 15;

      pdf.setFontSize(14);
      pdf.setTextColor(200, 200, 200);
      pdf.setFont('helvetica', 'normal');
      pdf.text('First-Principles Attribution Analysis', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 10;

      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Generated: ${new Date().toLocaleString()}`, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 20;

      // Executive Summary
      checkPageBreak(40);
      pdf.setFontSize(16);
      pdf.setTextColor(255, 215, 0);
      pdf.setFont('helvetica', 'bold');
      pdf.text('EXECUTIVE SUMMARY', 20, yPosition);
      yPosition += 15;

      pdf.setFontSize(11);
      pdf.setTextColor(200, 200, 200);
      pdf.setFont('helvetica', 'normal');
      
      const summary = [
        `Total Journeys Analyzed: ${results.ir.total_journeys}`,
        `Total Conversions: ${results.ir.total_conversions}`,
        `Conversion Rate: ${((results.ir.total_conversions / results.ir.total_journeys) * 100).toFixed(1)}%`,
        `Processing Time: ${results.ir.processing_time_ms.toFixed(0)}ms`,
        '',
        'Key Findings:',
        '• Multi-touch attribution reveals hidden channel synergies',
        '• Direct channel receives disproportionate credit in last-touch models',
        '• Social and Search channels show strong assist value'
      ];

      summary.forEach(line => {
        if (line.startsWith('•')) {
          pdf.setFont('helvetica', 'italic');
        }
        pdf.text(line, 25, yPosition);
        yPosition += 7;
        pdf.setFont('helvetica', 'normal');
      });

      // Attribution Results
      checkPageBreak(60);
      yPosition += 10;
      pdf.setFontSize(16);
      pdf.setTextColor(255, 215, 0);
      pdf.setFont('helvetica', 'bold');
      pdf.text('ATTRIBUTION RESULTS', 20, yPosition);
      yPosition += 15;

      // Create attribution table
      const attributions = results.ir.hybrid_result?.channel_attributions || {};
      const channels = Object.keys(attributions);
      const tableStartY = yPosition;
      const tableRowHeight = 8;
      
      // Table headers
      pdf.setFontSize(10);
      pdf.setTextColor(255, 255, 255);
      pdf.setFillColor(50, 50, 50);
      pdf.rect(20, yPosition, 60, tableRowHeight, 'F');
      pdf.rect(80, yPosition, 60, tableRowHeight, 'F');
      pdf.rect(140, yPosition, 40, tableRowHeight, 'F');
      
      pdf.text('Channel', 25, yPosition + 5);
      pdf.text('Attribution %', 85, yPosition + 5);
      pdf.text('Ranking', 145, yPosition + 5);
      yPosition += tableRowHeight;

      // Table data
      const sortedChannels = channels.sort((a, b) => attributions[b] - attributions[a]);
      sortedChannels.forEach((channel, index) => {
        checkPageBreak(tableRowHeight);
        const attribution = attributions[channel];
        const percentage = (attribution * 100).toFixed(1);
        
        pdf.setFillColor(30, 30, 30);
        pdf.rect(20, yPosition, 60, tableRowHeight, 'F');
        pdf.rect(80, yPosition, 60, tableRowHeight, 'F');
        pdf.rect(140, yPosition, 40, tableRowHeight, 'F');
        
        pdf.setTextColor(200, 200, 200);
        pdf.text(channel, 25, yPosition + 5);
        pdf.text(`${percentage}%`, 85, yPosition + 5);
        pdf.text(`#${index + 1}`, 145, yPosition + 5);
        yPosition += tableRowHeight;
      });

      // Methodology
      checkPageBreak(50);
      yPosition += 15;
      pdf.setFontSize(16);
      pdf.setTextColor(255, 215, 0);
      pdf.setFont('helvetica', 'bold');
      pdf.text('METHODOLOGY', 20, yPosition);
      yPosition += 15;

      pdf.setFontSize(11);
      pdf.setTextColor(200, 200, 200);
      pdf.setFont('helvetica', 'normal');
      
      const methodology = [
        `Alpha Parameter: ${results.ir.hybrid_result?.alpha_used || 0.5}`,
        '',
        'Markov-Shapley Hybrid Attribution:',
        '• Markov removal effects for causal attribution',
        '• Shapley values for fair allocation',
        `• ${((results.ir.hybrid_result?.alpha_used || 0.5) * 100).toFixed(0)}% Markov, ${(100 - (results.ir.hybrid_result?.alpha_used || 0.5) * 100).toFixed(0)}% Shapley`,
        '',
        'Uncertainty Quantification:',
        '• Bootstrap resampling for path uncertainty',
        '• Dirichlet posterior for transition uncertainty'
      ];

      methodology.forEach(line => {
        if (line.startsWith('•')) {
          pdf.setFont('helvetica', 'italic');
        }
        pdf.text(line, 25, yPosition);
        yPosition += 7;
        pdf.setFont('helvetica', 'normal');
      });

      // Risk Assessment
      checkPageBreak(40);
      yPosition += 10;
      pdf.setFontSize(16);
      pdf.setTextColor(255, 215, 0);
      pdf.setFont('helvetica', 'bold');
      pdf.text('RISK ASSESSMENT', 20, yPosition);
      yPosition += 15;

      pdf.setFontSize(11);
      pdf.setTextColor(255, 100, 100); // Red for warnings
      pdf.setFont('helvetica', 'bold');
      pdf.text('Limitations:', 25, yPosition);
      yPosition += 8;

      pdf.setTextColor(200, 200, 200);
      pdf.setFont('helvetica', 'normal');
      
      const risks = [
        '• Sample size may limit statistical significance',
        '• Attribution assumes channel independence',
        '• Results sensitive to alpha parameter selection',
        '• Historical data may not predict future behavior',
        '',
        'Recommendations:',
        '• Validate against A/B test holdout groups',
        '• Run sensitivity analysis on alpha parameter',
        '• Combine with qualitative business insights'
      ];

      risks.forEach(line => {
        if (line.startsWith('•')) {
          pdf.setFont('helvetica', 'italic');
        }
        pdf.text(line, 25, yPosition);
        yPosition += 7;
        pdf.setFont('helvetica', 'normal');
      });

      // Add charts as images if available
      if (chartsRef.current) {
        try {
          checkPageBreak(120);
          yPosition += 10;
          pdf.setFontSize(16);
          pdf.setTextColor(255, 215, 0);
          pdf.setFont('helvetica', 'bold');
          pdf.text('VISUALIZATIONS', 20, yPosition);
          yPosition += 20;

          const canvas = await html2canvas(chartsRef.current, {
            scale: 2,
            useCORS: true,
            allowTaint: true
          });

          const imgData = canvas.toDataURL('image/png');
          const imgWidth = pageWidth - 40;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;
          
          if (imgHeight <= pageHeight - yPosition - 20) {
            pdf.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
          } else {
            // Image too large, add as new page
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 20, 20, imgWidth, imgHeight);
          }
        } catch (error) {
          console.warn('Could not capture charts:', error);
          // Add note about missing charts
          yPosition += 10;
          pdf.setFontSize(10);
          pdf.setTextColor(150, 150, 150);
          pdf.setFont('helvetica', 'italic');
          pdf.text('[Charts could not be captured in PDF format]', 25, yPosition);
        }
      }

      // Footer
      const totalPages = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setTextColor(100, 100, 100);
        pdf.text(`Page ${i} of ${totalPages}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
        pdf.text('CLASSIFIED - PRIVACY-FIRST - LOCAL PROCESSING', 20, pageHeight - 10);
      }

      // Save PDF
      pdf.save('attribution-matrix-report.pdf');
      
    } catch (error) {
      console.error('PDF generation failed:', error);
      alert('PDF generation failed. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={generatePDF}
        disabled={isGenerating}
        className="w-full py-3 px-4 carbon-plate border border-amber-500/30 text-amber-500 font-bold hover:bg-amber-950/30 hover:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-mono uppercase tracking-wider text-sm flex items-center justify-center gap-3"
      >
        {isGenerating ? (
          <>
            <div className="w-4 h-4 border-2 border-amber-500/30 border-t-amber-500 animate-spin" />
            GENERATING PDF...
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            DOWNLOAD PDF REPORT
          </>
        )}
      </button>

      <div className="carbon-plate-deep border border-zinc-800 p-4">
        <div className="flex items-start gap-3">
          <FileText className="w-5 h-5 text-amber-500 mt-0.5" />
          <div className="text-xs text-zinc-500 font-mono space-y-1">
            <p>Professional report includes:</p>
            <div className="ml-2 space-y-1">
              <p>• Executive summary with key findings</p>
              <p>• Attribution results with rankings</p>
              <p>• Technical methodology explanation</p>
              <p>• Risk assessment and limitations</p>
              <p>• Charts and visualizations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}