'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, DollarSign, Target, Award } from 'lucide-react';

interface AttributionChartsProps {
  data: any;
}

const TACTICAL_COLORS = ['#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7', '#fffbeb'];

export default function AttributionCharts({ data }: AttributionChartsProps) {
  // Transform data for charts
  const hybridData = data?.hybrid_value 
    ? Object.entries(data.hybrid_value).map(([channel, value]) => ({
        channel,
        value: typeof value === 'number' ? value : 0,
        markov: data.markov_share?.[channel] ? data.markov_share[channel] * 100 : 0,
        shapley: data.shapley_share?.[channel] ? data.shapley_share[channel] * 100 : 0,
      })).sort((a, b) => b.value - a.value)
    : [];

  const pieData = hybridData.map((item, index) => ({
    name: item.channel,
    value: item.value,
    color: TACTICAL_COLORS[index % TACTICAL_COLORS.length],
  }));

  const topChannel = hybridData[0];
  const totalValue = data?.total_conversion_value || 0;
  const conversionRate = data?.conversion_rate || 0;
  const avgPerChannel = hybridData.length > 0 ? totalValue / hybridData.length : 0;

  return (
    <div className="space-y-6">
      {/* KPI Cards - Tactical */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="carbon-plate border border-zinc-800 p-5 hover:border-amber-500/30 transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-amber-500/30 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-2xl font-bold text-amber-500 font-mono">${totalValue.toFixed(0)}</div>
          </div>
          <p className="text-xs text-zinc-500 font-mono uppercase tracking-wider">TOTAL REVENUE</p>
        </div>

        <div className="carbon-plate border border-zinc-800 p-5 hover:border-amber-500/30 transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-amber-500/30 flex items-center justify-center">
              <Award className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-xl font-bold text-amber-500 font-mono">{topChannel?.channel || 'N/A'}</div>
          </div>
          <p className="text-xs text-zinc-500 font-mono uppercase tracking-wider">PRIMARY TARGET</p>
        </div>

        <div className="carbon-plate border border-zinc-800 p-5 hover:border-amber-500/30 transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-amber-500/30 flex items-center justify-center">
              <Target className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-2xl font-bold text-amber-500 font-mono">{(conversionRate * 100).toFixed(1)}%</div>
          </div>
          <p className="text-xs text-zinc-500 font-mono uppercase tracking-wider">HIT RATE</p>
        </div>

        <div className="carbon-plate border border-zinc-800 p-5 hover:border-amber-500/30 transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 border border-amber-500/30 flex items-center justify-center">
              <Activity className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-2xl font-bold text-amber-500 font-mono">${avgPerChannel.toFixed(0)}</div>
          </div>
          <p className="text-xs text-zinc-500 font-mono uppercase tracking-wider">AVG PER CHANNEL</p>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hybrid Attribution Bar Chart */}
        <div className="carbon-plate border border-zinc-800">
          <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950/50">
            <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
              HYBRID ATTRIBUTION ($)
            </h3>
          </div>
          <div className="p-4">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={hybridData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis 
                  dataKey="channel" 
                  tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }}
                  stroke="#3f3f46"
                />
                <YAxis 
                  tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }}
                  stroke="#3f3f46"
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#09090b',
                    border: '1px solid #27272a',
                    borderRadius: '0',
                    fontFamily: 'monospace',
                    fontSize: '12px'
                  }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'VALUE']}
                  labelStyle={{ color: '#f59e0b', textTransform: 'uppercase' }}
                />
                <Bar 
                  dataKey="value" 
                  fill="#f59e0b"
                  radius={[0, 0, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue Share Pie Chart */}
        <div className="carbon-plate border border-zinc-800">
          <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950/50">
            <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
              DISTRIBUTION MAP
            </h3>
          </div>
          <div className="p-4">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  style={{ fontSize: '11px', fontFamily: 'monospace', fill: '#a1a1aa' }}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#18181b" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#09090b',
                    border: '1px solid #27272a',
                    borderRadius: '0',
                    fontFamily: 'monospace',
                    fontSize: '12px'
                  }}
                  formatter={(value: number) => `$${value.toFixed(2)}`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Markov vs Shapley Comparison */}
      <div className="carbon-plate border border-zinc-800">
        <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950/50">
          <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
            MARKOV VS SHAPLEY ATTRIBUTION SHARES (%)
          </h3>
        </div>
        <div className="p-4">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hybridData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis 
                dataKey="channel" 
                tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }}
                stroke="#3f3f46"
              />
              <YAxis 
                tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'monospace' }}
                stroke="#3f3f46"
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#09090b',
                  border: '1px solid #27272a',
                  borderRadius: '0',
                  fontFamily: 'monospace',
                  fontSize: '12px'
                }}
                formatter={(value: number) => `${value.toFixed(1)}%`}
              />
              <Legend 
                wrapperStyle={{ fontFamily: 'monospace', fontSize: '11px' }}
                iconType="square"
              />
              <Bar dataKey="markov" fill="#f59e0b" name="MARKOV (CAUSAL)" radius={[0, 0, 0, 0]} />
              <Bar dataKey="shapley" fill="#fbbf24" name="SHAPLEY (FAIR)" radius={[0, 0, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 p-4 carbon-plate-deep border border-zinc-800">
            <p className="text-xs text-zinc-500 font-mono leading-relaxed">
              <span className="text-amber-500 font-bold">ANALYSIS:</span> Markov displays causal contribution (removal effects), 
              Shapley ensures fair allocation. Hybrid model (α={data?.alpha || 0.5}) balances both methodologies.
            </p>
          </div>
        </div>
      </div>

      {/* Channel Details Table */}
      <div className="carbon-plate border border-zinc-800">
        <div className="border-b border-zinc-800 px-4 py-3 bg-zinc-950/50">
          <h3 className="text-sm font-bold text-zinc-100 font-mono uppercase tracking-wide">
            DETAILED ATTRIBUTION BREAKDOWN
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-xs">
            <thead className="bg-zinc-950/50 border-b border-zinc-800">
              <tr>
                <th className="px-4 py-3 text-left text-zinc-500 uppercase tracking-wider">
                  CHANNEL
                </th>
                <th className="px-4 py-3 text-right text-zinc-500 uppercase tracking-wider">
                  HYBRID VALUE
                </th>
                <th className="px-4 py-3 text-right text-zinc-500 uppercase tracking-wider">
                  MARKOV SHARE
                </th>
                <th className="px-4 py-3 text-right text-zinc-500 uppercase tracking-wider">
                  SHAPLEY SHARE
                </th>
                <th className="px-4 py-3 text-right text-zinc-500 uppercase tracking-wider">
                  % OF TOTAL
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {hybridData.map((item, index) => (
                <tr key={item.channel} className="hover:bg-zinc-950/30 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-2 h-2 border border-zinc-700"
                        style={{ backgroundColor: TACTICAL_COLORS[index % TACTICAL_COLORS.length] }}
                      />
                      <span className="text-zinc-100 font-bold uppercase tracking-wide">{item.channel}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right font-bold text-amber-500">
                    ${item.value.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-zinc-400">
                    {item.markov.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-zinc-400">
                    {item.shapley.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-zinc-400">
                    {((item.value / totalValue) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
