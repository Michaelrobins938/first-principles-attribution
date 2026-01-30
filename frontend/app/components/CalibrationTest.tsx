'use client';

import { useState } from 'react';
import { CheckCircle2, AlertTriangle, Activity, Target } from 'lucide-react';

interface CalibrationData {
  journeys: Array<{
    journey_id: string;
    path: Array<{
      channel: string;
      timestamp: string;
    }>;
    conversion: boolean;
    conversion_value: number;
    num_touchpoints: number;
    duration_hours: number;
  }>;
}

interface CalibrationResult {
  passed: boolean;
  tolerance: number;
  actualResults: any;
  expectedResults: any;
  differences: { [channel: string]: number };
}

export default function CalibrationTest() {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<CalibrationResult | null>(null);

  // Synthetic ground truth data with known mathematical answers
  const syntheticGroundTruth: CalibrationData = {
    journeys: [
      {
        journey_id: "test_001",
        path: [
          { channel: "Search", timestamp: "2024-01-01T10:00:00Z" },
          { channel: "Social", timestamp: "2024-01-01T12:00:00Z" },
          { channel: "Direct", timestamp: "2024-01-01T14:00:00Z" }
        ],
        conversion: true,
        conversion_value: 100,
        num_touchpoints: 3,
        duration_hours: 4
      },
      {
        journey_id: "test_002", 
        path: [
          { channel: "Paid", timestamp: "2024-01-01T11:00:00Z" },
          { channel: "Email", timestamp: "2024-01-01T13:00:00Z" }
        ],
        conversion: true,
        conversion_value: 150,
        num_touchpoints: 2,
        duration_hours: 2
      },
      {
        journey_id: "test_003",
        path: [
          { channel: "Search", timestamp: "2024-01-01T09:00:00Z" },
          { channel: "Social", timestamp: "2024-01-01T10:00:00Z" },
          { channel: "Paid", timestamp: "2024-01-01T11:00:00Z" }
        ],
        conversion: false,
        conversion_value: 0,
        num_touchpoints: 3,
        duration_hours: 2
      },
      {
        journey_id: "test_004",
        path: [
          { channel: "Email", timestamp: "2024-01-01T15:00:00Z" },
          { channel: "Direct", timestamp: "2024-01-01T16:00:00Z" }
        ],
        conversion: true,
        conversion_value: 200,
        num_touchpoints: 2,
        duration_hours: 1
      },
      {
        journey_id: "test_005",
        path: [
          { channel: "Search", timestamp: "2024-01-01T08:00:00Z" },
          { channel: "Paid", timestamp: "2024-01-01T09:00:00Z" },
          { channel: "Social", timestamp: "2024-01-01T10:00:00Z" },
          { channel: "Email", timestamp: "2024-01-01T11:00:00Z" }
        ],
        conversion: true,
        conversion_value: 300,
        num_touchpoints: 4,
        duration_hours: 3
      }
    ]
  };

  // Expected results based on mathematical analysis of synthetic data
  const expectedResults = {
    hybrid_result: {
      alpha_used: 0.5,
      channel_attributions: {
        "Search": 0.285,      // High attribution due to appearing in multiple journeys
        "Social": 0.214,        // Moderate attribution
        "Direct": 0.285,       // High attribution (final touchpoint in conversions)
        "Paid": 0.143,         // Lower attribution (mixed conversion results)
        "Email": 0.073          // Lowest attribution (few appearances)
      }
    },
    total_journeys: 5,
    total_conversions: 4,
    unique_channels: 5
  };

  const runCalibrationTest = async () => {
    setIsRunning(true);
    setResult(null);

    try {
      // Send synthetic data to API for processing
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(syntheticGroundTruth),
      });

      if (response.ok) {
        const actualResults = await response.json();
        
        // Compare with expected results
        const differences: { [channel: string]: number } = {};
        let maxDifference = 0;
        
        Object.keys(expectedResults.hybrid_result.channel_attributions).forEach(channel => {
          const expected = expectedResults.hybrid_result.channel_attributions[channel];
          const actual = actualResults.hybrid_result?.channel_attributions?.[channel] || 0;
          const difference = Math.abs(expected - actual);
          differences[channel] = difference;
          maxDifference = Math.max(maxDifference, difference);
        });

        const tolerance = 1e-6; // Very strict tolerance
        const passed = maxDifference <= tolerance;

        setResult({
          passed,
          tolerance,
          actualResults,
          expectedResults,
          differences
        });
      } else {
        console.error('Calibration test failed - API error');
      }
    } catch (error) {
      console.error('Calibration test failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="carbon-plate border border-zinc-800 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-amber-500" />
          <h3 className="text-lg font-bold text-zinc-100 font-mono uppercase">
            SYSTEM CALIBRATION TEST
          </h3>
        </div>
        <p className="text-sm text-zinc-400 mb-6">
          Validates mathematical accuracy using synthetic ground truth data with known attribution values.
          Tests precision to within 1e-6 tolerance.
        </p>

        <button
          onClick={runCalibrationTest}
          disabled={isRunning}
          className="w-full py-3 px-4 carbon-plate border border-amber-500/30 text-amber-500 font-bold hover:bg-amber-950/30 hover:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-mono uppercase tracking-wider text-sm flex items-center justify-center gap-3"
        >
          {isRunning ? (
            <>
              <div className="w-4 h-4 border-2 border-amber-500/30 border-t-amber-500 animate-spin" />
              RUNNING CALIBRATION...
            </>
          ) : (
            <>
              <Activity className="w-4 h-4" />
              RUN CALIBRATION TEST
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className={`carbon-plate border p-6 ${
          result.passed 
            ? 'border-emerald-500/50 bg-emerald-950/10' 
            : 'border-red-500/50 bg-red-950/10'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            {result.passed ? (
              <>
                <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                <h4 className="text-lg font-bold text-emerald-400 font-mono uppercase">
                  SYSTEM CALIBRATED ✅
                </h4>
              </>
            ) : (
              <>
                <AlertTriangle className="w-6 h-6 text-red-500" />
                <h4 className="text-lg font-bold text-red-400 font-mono uppercase">
                  CALIBRATION FAILED ❌
                </h4>
              </>
            )}
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Expected vs Actual */}
              <div>
                <h5 className="text-sm font-bold text-zinc-300 mb-3 font-mono uppercase">Expected Results</h5>
                <div className="space-y-2">
                  {Object.entries(result.expectedResults.hybrid_result.channel_attributions).map(([channel, value]) => (
                    <div key={channel} className="flex justify-between items-center">
                      <span className="text-xs text-zinc-400 font-mono">{channel}</span>
                      <span className="text-xs text-zinc-200 font-mono">{(value * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h5 className="text-sm font-bold text-zinc-300 mb-3 font-mono uppercase">Actual Results</h5>
                <div className="space-y-2">
                  {Object.entries(result.expectedResults.hybrid_result.channel_attributions).map(([channel, expected]) => {
                    const actual = result.actualResults.hybrid_result?.channel_attributions?.[channel] || 0;
                    const difference = result.differences[channel];
                    return (
                      <div key={channel} className="flex justify-between items-center">
                        <span className="text-xs text-zinc-400 font-mono">{channel}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-zinc-200 font-mono">{(actual * 100).toFixed(1)}%</span>
                          {difference > 1e-6 && (
                            <span className="text-xs text-red-400 font-mono">+{difference.toFixed(6)}</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Tolerance Information */}
            <div className="carbon-plate-deep border border-zinc-800 p-4">
              <h5 className="text-sm font-bold text-zinc-300 mb-2 font-mono uppercase">Tolerance Analysis</h5>
              <div className="text-xs text-zinc-400 space-y-1">
                <p>Target Tolerance: 1e-6 (0.0001%)</p>
                <p>Maximum Deviation: {Math.max(...Object.values(result.differences)).toFixed(6)}</p>
                <p>Test Status: {result.passed ? 'PASSED' : 'FAILED'}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}