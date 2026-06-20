import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import { playerService, predictionService } from '../api/services'
import type { Player } from '../api/services'
import PropCard from '../components/PropCard'

interface PlayerDetailProps {
  player: Player
  onBack: () => void
}

export default function PlayerDetail({ player, onBack }: PlayerDetailProps) {
  const { data: predictions, isLoading: predictionsLoading, isError: predictionsError } = useQuery({
    queryKey: ['predictions', player.player_id],
    queryFn: () => predictionService.getPredictions(player.player_id),
    retry: false,
  })

  const { data: stats, isLoading: statsLoading, isError: statsError } = useQuery({
    queryKey: ['stats', player.player_id],
    queryFn: () => playerService.getPlayerStats(player.player_id, 10),
    retry: false,
  })

  return (
    <div className="space-y-8">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to search
      </button>

      <div>
        <h1 className="text-3xl font-bold text-white">{player.full_name}</h1>
        <p className="text-gray-500 mt-1">Next game predictions</p>
      </div>

      {(predictionsError || statsError) && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-orange-400 flex-shrink-0" />
          <p className="text-orange-200 text-sm">
            No data available for this player yet. Our model currently covers a curated set of 50 active players.
            Try searching for a player like Devin Booker.
          </p>
        </div>
      )}

      {!predictionsError && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <PropCard
            label="Points"
            prediction={predictionsLoading ? null : predictions?.points ?? null}
            icon="points"
          />
          <PropCard
            label="Rebounds"
            prediction={predictionsLoading ? null : predictions?.rebounds ?? null}
            icon="rebounds"
          />
          <PropCard
            label="Assists"
            prediction={predictionsLoading ? null : predictions?.assists ?? null}
            icon="assists"
          />
        </div>
      )}

      {!statsError && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Recent games</h2>
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500">
                  <th className="text-left px-4 py-3 font-medium">Date</th>
                  <th className="text-left px-4 py-3 font-medium">Matchup</th>
                  <th className="text-right px-4 py-3 font-medium">PTS</th>
                  <th className="text-right px-4 py-3 font-medium">REB</th>
                  <th className="text-right px-4 py-3 font-medium">AST</th>
                  <th className="text-right px-4 py-3 font-medium">MIN</th>
                </tr>
              </thead>
              <tbody>
                {statsLoading && (
                  <tr>
                    <td colSpan={6} className="px-4 py-6 text-center text-gray-500">
                      Loading recent games...
                    </td>
                  </tr>
                )}
                {stats?.map((game) => (
                  <tr key={game.game_date} className="border-b border-gray-800/50 text-gray-300 hover:bg-gray-800/30">
                    <td className="px-4 py-3">{new Date(game.game_date).toLocaleDateString()}</td>
                    <td className="px-4 py-3">{game.matchup}</td>
                    <td className="px-4 py-3 text-right font-medium">{game.points}</td>
                    <td className="px-4 py-3 text-right">{game.rebounds}</td>
                    <td className="px-4 py-3 text-right">{game.assists}</td>
                    <td className="px-4 py-3 text-right text-gray-500">{game.minutes_played.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
