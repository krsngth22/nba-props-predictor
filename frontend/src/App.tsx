import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
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

function Main() {
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
    <div className="space-y-10">
      <div className="flex justify-center pt-4">
        <PlayerSearch onSelectPlayer={setSelectedPlayer} />
      </div>
      <Dashboard onSelectPlayer={setSelectedPlayer} />
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
            <Main />
          </Layout>
        </ProtectedRoute>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
