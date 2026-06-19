import { ReactNode } from 'react'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    window.location.href = '/login'
    return null
  }

  return <>{children}</>
}
