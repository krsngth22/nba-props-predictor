import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Cell, ResponsiveContainer
} from 'recharts'
import { useQuery } from '@tanstack/react-query'
import { shapService } from '../api/services'

interface ShapChartProps {
  playerId: number
  target: 'points' | 'rebounds' | 'assists'
}

function formatFeatureName(name: string): string {
  return name
    .replace(/_roll_/g, ' (')
    .replace(/_lag_/g, ' lag ')
    .replace(/_/g, ' ')
    .replace(/(\d+)$/, '$1)')
    .replace(/pct/g, '%')
    .trim()
}

export default function ShapChart({ playerId, target }: ShapChartProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['shap', playerId, target],
    queryFn: () => shapService.getExplanation(playerId, target),
    retry: false,
  })

  if (isLoading) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 animate-pulse">
        <div className="h-4 bg-gray-800 rounded w-48 mb-6" />
        <div className="h-40 bg-gray-800 rounded" />
      </div>
    )
  }

  if (isError || !data) {
    return null
  }

  const chartData = data.features.map(f => ({
    feature: formatFeatureName(f.feature),
    impact: parseFloat(f.shap_value.toFixed(3)),
  }))

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-white font-semibold">
          Why this {target} prediction?
        </h3>
        <span className="text-gray-500 text-sm">Top 10 factors</span>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 0, right: 20, left: 120, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            tickFormatter={v => v > 0 ? `+${v}` : `${v}`}
          />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            width={115}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
            labelStyle={{ color: '#9ca3af' }}
            formatter={(value: number) => [value > 0 ? `+${value}` : value, 'Impact']}
          />
          <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.impact >= 0 ? '#10b981' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-gray-600 text-xs mt-4">
        Green bars push the prediction higher. Red bars push it lower.
      </p>
    </div>
  )
}
