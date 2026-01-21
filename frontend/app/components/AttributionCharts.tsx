'use client';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Target, TrendingUp, Percent, DollarSign } from 'lucide-react';

interface AttributionData {
  status: string;
  processing_time_ms: number;
  total_journeys: number;
  total_conversions: number;
  unique_channels: number;
  hybrid_result?: {
    channel_attributions: Record<string, number>;
    alpha_used: number;
  };
  channels_summary?: Record<string, number>;
}

interface AttributionChartsProps {
  data: AttributionData;
}

const TACTICAL_COLORS = [
  '#f59e0b', // amber-500
  '#fbbf24', // amber-400
  '#d97706', // amber-600
  '#92400e', // amber-800
  '#78350f', // amber-900
  '#10b981', // emerald-500
];

export default function AttributionCharts({ data }: AttributionChartsProps) {
  const channelAttributions = data.hybrid_result?.channel_attributions || {};
  const channelsSummary = data.channels_summary || {};

  // Prepare data for charts
  const barData = Object.entries(channelAttributions).map(([channel, value]) => ({
    channel,
    attribution: (value * 100).toFixed(1),
    touchpoints: channelsSummary[channel] || 0,
  }));

  const pieData = Object.entries(channelAttributions).map(([name, value]) => ({
    name,
    value: parseFloat((value * 100).toFixed(1)),
  }));

  const conversionRate = data.total_journeys > 0
    ? ((data.total_conversions / data.total_journeys) * 100).toFixed(1)
    : '0';

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard
          icon={<Target className="w-5 h-5" />}
          label="TOTAL JOURNEYS"
          value={data.total_journeys.toLocaleString()}
          subtext="Analyzed paths"
        />
        <KPICard
          icon={<TrendingUp className="w-5 h-5" />}
          label="CONVERSIONS"
          value={data.total_conversions.toLocaleString()}
          subtext={`${conversionRate}% rate`}
        />
        <KPICard
          icon={<Percent className="w-5 h-5" />}
          label="ALPHA WEIGHT"
          value={data.hybrid_result?.alpha_used?.toFixed(2) || '0.50'}
          subtext="Markov vs Shapley"
        />
        <KPICard
          icon={<DollarSign className="w-5 h-5" />}
          label="PROCESSING"
          value={`${data.processing_time_ms.toFixed(0)}ms`}
          subtext="Analysis time"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="carbon-plate-deep border border-zinc-800 p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
            <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
              CHANNEL ATTRIBUTION
            </h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} layout="vertical">
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#3f3f46' }}
                  tickFormatter={(v) => `${v}%`}
                />
                <YAxis
                  type="category"
                  dataKey="channel"
                  tick={{ fill: '#a1a1aa', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#3f3f46' }}
                  width={80}
                />
                <Tooltip
                  content={<CustomTooltip />}
                  cursor={{ fill: 'rgba(245, 158, 11, 0.1)' }}
                />
                <Bar
                  dataKey="attribution"
                  fill="#f59e0b"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="carbon-plate-deep border border-zinc-800 p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
            <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
              ATTRIBUTION DISTRIBUTION
            </h3>
          </div>
          <div className="h-64 flex items-center">
            <ResponsiveContainer width="60%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={index} fill={TACTICAL_COLORS[index % TACTICAL_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              {pieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-sm"
                    style={{ backgroundColor: TACTICAL_COLORS[index % TACTICAL_COLORS.length] }}
                  />
                  <span className="text-xs text-zinc-400 font-mono uppercase">{entry.name}</span>
                  <span className="text-xs text-zinc-100 font-mono ml-auto">{entry.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Channel Details Table */}
      <div className="carbon-plate-deep border border-zinc-800 p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
          <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
            CHANNEL BREAKDOWN
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left py-3 px-4 text-xs text-zinc-500 font-mono uppercase">Channel</th>
                <th className="text-right py-3 px-4 text-xs text-zinc-500 font-mono uppercase">Attribution</th>
                <th className="text-right py-3 px-4 text-xs text-zinc-500 font-mono uppercase">Touchpoints</th>
                <th className="text-right py-3 px-4 text-xs text-zinc-500 font-mono uppercase">Efficiency</th>
              </tr>
            </thead>
            <tbody>
              {barData.map((row, i) => {
                const efficiency = row.touchpoints > 0
                  ? (parseFloat(row.attribution) / row.touchpoints).toFixed(2)
                  : '0';
                return (
                  <tr key={row.channel} className="border-b border-zinc-800/50 hover:bg-zinc-900/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: TACTICAL_COLORS[i % TACTICAL_COLORS.length] }}
                        />
                        <span className="text-sm text-zinc-100 font-mono uppercase">{row.channel}</span>
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 text-sm text-amber-500 font-mono font-bold">
                      {row.attribution}%
                    </td>
                    <td className="text-right py-3 px-4 text-sm text-zinc-400 font-mono">
                      {row.touchpoints}
                    </td>
                    <td className="text-right py-3 px-4 text-sm text-emerald-500 font-mono">
                      {efficiency}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function KPICard({ icon, label, value, subtext }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtext: string;
}) {
  return (
    <div className="carbon-plate border border-zinc-800 p-4 hover:border-amber-500/30 transition-all">
      <div className="flex items-center gap-2 mb-2">
        <div className="text-amber-500">{icon}</div>
        <span className="text-xs text-zinc-500 font-mono uppercase">{label}</span>
      </div>
      <div className="text-2xl font-bold text-zinc-100 font-mono">{value}</div>
      <div className="text-xs text-zinc-600 font-mono mt-1">{subtext}</div>
    </div>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="carbon-plate border border-amber-500/30 p-3">
        <p className="text-amber-500 font-mono text-sm font-bold uppercase">{data.channel}</p>
        <p className="text-zinc-100 font-mono text-xs mt-1">
          Attribution: <span className="text-amber-500">{data.attribution}%</span>
        </p>
        <p className="text-zinc-400 font-mono text-xs">
          Touchpoints: {data.touchpoints}
        </p>
      </div>
    );
  }
  return null;
}

function PieTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="carbon-plate border border-amber-500/30 p-3">
        <p className="text-amber-500 font-mono text-sm font-bold uppercase">{payload[0].name}</p>
        <p className="text-zinc-100 font-mono text-xs mt-1">
          Share: <span className="text-amber-500">{payload[0].value}%</span>
        </p>
      </div>
    );
  }
  return null;
}
