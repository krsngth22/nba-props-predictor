import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Database, Cpu, Activity } from 'lucide-react'
import { healthService, playerService, predictionService } from '../api/services'
import type { Player } from '../api/services'

interface StatCardProps {
  label: string
  value: string
  icon: React.ReactNode
  color: string
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-gray-500 text-sm">{label}</p>
        <p className="text-white font-semibold text-lg">{value}</p>
      </div>
    </div>
  )
}

interface TopPredictionCardProps {
  player: Player
  onSelect: (player: Player) => void
}

function TopPredictionCard({ player, onSelect }: TopPredictionCardProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['predictions', player.player_id],
    queryFn: () => predictionService.getPredictions(player.player_id),
    retry: false,
  })

  if (isLoading || !data?.points) return null

  return (
    <button
      onClick={() => onSelect(player)}
      className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-4 text-left transition-colors w-full"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-white font-medium text-sm">{player.full_name}</span>
        <TrendingUp className="w-4 h-4 text-blue-400" />
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="text-orange-400 font-bold text-lg">
            {data.points?.predicted_value.toFixed(1)}
          </p>
          <p className="text-gray-600 text-xs">PTS</p>
        </div>
        <div>
          <p className="text-purple-400 font-bold text-lg">
            {data.rebounds?.predicted_value.toFixed(1)}
          </p>
          <p className="text-gray-600 text-xs">REB</p>
        </div>
        <div>
          <p className="text-emerald-400 font-bold text-lg">
            {data.assists?.predicted_value.toFixed(1)}
          </p>
          <p className="text-gray-600 text-xs">AST</p>
        </div>
      </div>
    </button>
  )
}

interface DashboardProps {
  onSelectPlayer: (player: Player) => void
}

const FEATURED_PLAYERS = [1628389, 203078, 1631128, 1630175, 1626164]

export default function Dashboard({ onSelectPlayer }: DashboardProps) {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthService.getHealth,
  })

  const { data: players } = useQuery({
    queryKey: ['featured-players'],
    queryFn: async () => {
      const results = await Promise.allSettled(
        FEATURED_PLAYERS.map(id => playerService.getPlayer(id))
      )
      return results
        .filter(r => r.status === 'fulfilled')
        .map(r => (r as PromiseFulfilledResult<Player>).value)
    },
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-500 mt-1">NBA player prop predictions powered by XGBoost</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="API Status"
          value={health?.status === 'ok' ? 'Online' : 'Offline'}
          icon={<Activity className="w-5 h-5" />}
          color="bg-emerald-400/10 text-emerald-400"
        />
        <StatCard
          label="Database"
          value={health?.database === 'connected' ? 'Connected' : 'Disconnected'}
          icon={<Database className="w-5 h-5" />}
          color="bg-blue-400/10 text-blue-400"
        />
        <StatCard
          label="ML Models"
          value={health?.models_loaded ? '3 Loaded' : 'Not loaded'}
          icon={<Cpu className="w-5 h-5" />}
          color="bg-purple-400/10 text-purple-400"
        />
        <StatCard
          label="Version"
          value={health?.version ?? '—'}
          icon={<TrendingUp className="w-5 h-5" />}
          color="bg-orange-400/10 text-orange-400"
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Featured players</h2>
          <span className="text-gray-600 text-sm">Click to see full predictions</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {players?.map(player => (
            <TopPredictionCard
              key={player.player_id}
              player={player}
              onSelect={onSelectPlayer}
            />
          ))}
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-2">Model performance</h2>
        <p className="text-gray-500 text-sm mb-4">Backtest results on holdout data</p>
        <div className="grid grid-cols-3 gap-6">
          {[
            { label: 'Points', mae: '2.06', within5: '90.9%', bet: '91.5%', color: 'text-orange-400' },
            { label: 'Rebounds', mae: '2.16', within5: '92.3%', bet: '76.4%', color: 'text-purple-400' },
            { label: 'Assists', mae: '0.65', within5: '99.3%', bet: '85.0%', color: 'text-emerald-400' },
          ].map(stat => (
            <div key={stat.label}>
              <p className={`font-semibold ${stat.color} mb-2`}>{stat.label}</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">MAE</span>
                  <span className="text-white">{stat.mae}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Within 5</span>
                  <span className="text-white">{stat.within5}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Bet accuracy</span>
                  <span className="text-white">{stat.bet}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
