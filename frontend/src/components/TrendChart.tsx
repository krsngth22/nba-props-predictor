import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ReferenceLine, ResponsiveContainer
} from 'recharts'
import type { GameStat } from '../api/services'

interface TrendChartProps {
  stats: GameStat[]
  target: 'points' | 'rebounds' | 'assists'
  prediction: number
}

const targetColors = {
  points: '#f97316',
  rebounds: '#a855f7',
  assists: '#10b981',
}

const targetLabels = {
  points: 'Points',
  rebounds: 'Rebounds',
  assists: 'Assists',
}

function computeRolling(data: number[], window: number): (number | null)[] {
  return data.map((_, i) => {
    if (i < window - 1) return null
    const slice = data.slice(i - window + 1, i + 1)
    return slice.reduce((a, b) => a + b, 0) / window
  })
}

export default function TrendChart({ stats, target, prediction }: TrendChartProps) {
  const reversed = [...stats].reverse()
  const values = reversed.map(g => g[target])
  const rolling5 = computeRolling(values, 5)

  const chartData = reversed.map((game, i) => ({
    date: new Date(game.game_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    actual: game[target],
    rolling5: rolling5[i] !== null ? parseFloat(rolling5[i]!.toFixed(1)) : null,
    prediction,
  }))

  const color = targetColors[target]

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-white font-semibold mb-6">
        {targetLabels[target]} — Last {stats.length} games
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
            labelStyle={{ color: '#9ca3af' }}
            itemStyle={{ color: '#e5e7eb' }}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }}
          />
          <ReferenceLine
            y={prediction}
            stroke="#3b82f6"
            strokeDasharray="6 3"
            label={{ value: `Pred: ${prediction}`, fill: '#3b82f6', fontSize: 11 }}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke={color}
            strokeWidth={2}
            dot={{ fill: color, r: 3 }}
            name="Actual"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="rolling5"
            stroke="#60a5fa"
            strokeWidth={2}
            strokeDasharray="4 2"
            dot={false}
            name="5-game avg"
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
