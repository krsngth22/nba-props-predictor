import type { ReactNode } from 'react'
import { useAuth } from '../context/AuthContext'
import { BarChart2 } from 'lucide-react'

export default function Layout({ children }: { children: ReactNode }) {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="bg-gray-900 border-b border-gray-800 px-4 md:px-6 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-blue-400" />
            <span className="text-lg font-bold text-white">NBA Props</span>
            <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full hidden sm:inline">
              ML
            </span>
          </div>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-white text-sm transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-800"
          >
            Sign out
          </button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8">
        {children}
      </main>
    </div>
  )
}
