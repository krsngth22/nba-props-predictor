import { createContext, useContext, useState, ReactNode } from 'react'
import { authService } from '../api/services'

interface AuthContextType {
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(
    authService.isAuthenticated()
  )

  const login = async (username: string, password: string) => {
    const token = await authService.login(username, password)
    localStorage.setItem('token', token)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
