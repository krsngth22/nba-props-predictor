import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,
    },
  },
})

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
            <div className="text-center py-20">
              <h2 className="text-2xl font-bold text-white mb-2">
                Welcome to NBA Props Predictor
              </h2>
              <p className="text-gray-400">
                Player search and predictions coming next!
              </p>
            </div>
          </Layout>
        </ProtectedRoute>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
