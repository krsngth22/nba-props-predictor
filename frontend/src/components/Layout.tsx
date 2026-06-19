import { ReactNode } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }: { children: ReactNode }) {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-white">NBA Props</span>
            <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">ML</span>
          </div>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-white text-sm transition-colors"
          >
            Sign out
          </button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  )
}
