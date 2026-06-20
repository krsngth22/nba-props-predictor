import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import PlayerSearch from './components/PlayerSearch'
import PlayerDetail from './pages/PlayerDetail'
import type { Player } from './api/services'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,
    },
  },
})

function Dashboard() {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null)

  if (selectedPlayer) {
    return (
      <PlayerDetail
        player={selectedPlayer}
        onBack={() => setSelectedPlayer(null)}
      />
    )
  }

  return (
    <div className="flex flex-col items-center pt-12">
      <h1 className="text-3xl font-bold text-white mb-2">
        NBA Player Prop Predictor
      </h1>
      <p className="text-gray-500 mb-8">
        Search any player to see ML-powered predictions for their next game
      </p>
      <PlayerSearch onSelectPlayer={setSelectedPlayer} />
    </div>
  )
}

function App() {
  const isLoginPage = window.location.pathname === '/login'

  if (isLoginPage) {
    return (
      <AuthProvider>
        <Login />
      </AuthProvider>
    )
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
