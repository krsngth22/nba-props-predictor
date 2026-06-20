import { TrendingUp, TrendingDown, Target } from 'lucide-react'
import type { PropPrediction } from '../api/services'

interface PropCardProps {
  label: string
  prediction: PropPrediction | null
  icon: 'points' | 'rebounds' | 'assists'
}

const iconColors = {
  points: 'text-orange-400 bg-orange-400/10',
  rebounds: 'text-purple-400 bg-purple-400/10',
  assists: 'text-emerald-400 bg-emerald-400/10',
}

function getConfidenceLevel(mae: number): { label: string; color: string } {
  if (mae < 1.5) return { label: 'High confidence', color: 'text-emerald-400' }
  if (mae < 3) return { label: 'Medium confidence', color: 'text-yellow-400' }
  return { label: 'Lower confidence', color: 'text-orange-400' }
}

export default function PropCard({ label, prediction, icon }: PropCardProps) {
  if (!prediction) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 animate-pulse">
        <div className="h-4 bg-gray-800 rounded w-20 mb-4" />
        <div className="h-10 bg-gray-800 rounded w-16 mb-2" />
        <div className="h-3 bg-gray-800 rounded w-24" />
      </div>
    )
  }

  const confidence = getConfidenceLevel(prediction.model_mae)
  const lineValue = Math.round(prediction.predicted_value)
  const isOver = prediction.predicted_value > lineValue

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <span className="text-gray-400 text-sm font-medium uppercase tracking-wide">
          {label}
        </span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${iconColors[icon]}`}>
          <Target className="w-4 h-4" />
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-4xl font-bold text-white">
          {prediction.predicted_value.toFixed(1)}
        </span>
        {isOver ? (
          <TrendingUp className="w-5 h-5 text-emerald-400" />
        ) : (
          <TrendingDown className="w-5 h-5 text-red-400" />
        )}
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className={confidence.color}>{confidence.label}</span>
        <span className="text-gray-600">±{prediction.model_mae.toFixed(1)} MAE</span>
      </div>
    </div>
  )
}
