import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, User } from 'lucide-react'
import { playerService } from '../api/services'
import type { Player } from '../api/services'
import { useDebounce } from '../hooks/useDebounce'

interface PlayerSearchProps {
  onSelectPlayer: (player: Player) => void
}

export default function PlayerSearch({ onSelectPlayer }: PlayerSearchProps) {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 300)

  const { data: players, isLoading } = useQuery({
    queryKey: ['players', debouncedQuery],
    queryFn: () => playerService.getPlayers(debouncedQuery || undefined, 10),
    enabled: debouncedQuery.length > 0,
  })

  return (
    <div className="relative w-full max-w-xl">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for a player (e.g. Devin Booker)..."
          className="w-full bg-gray-900 text-white pl-10 pr-4 py-3 rounded-xl border border-gray-800 focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      {debouncedQuery.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-gray-800 rounded-xl shadow-xl overflow-hidden z-10">
          {isLoading && (
            <div className="px-4 py-3 text-gray-500 text-sm">Searching...</div>
          )}

          {!isLoading && players?.length === 0 && (
            <div className="px-4 py-3 text-gray-500 text-sm">No players found</div>
          )}

          {!isLoading && players?.map((player) => (
            <button
              key={player.player_id}
              onClick={() => {
                onSelectPlayer(player)
                setQuery('')
              }}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-800 transition-colors text-left"
            >
              <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center">
                <User className="w-4 h-4 text-blue-400" />
              </div>
              <span className="text-white">{player.full_name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
