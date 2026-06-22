import apiClient from './client'

export interface Player {
  player_id: number
  full_name: string
  is_active: boolean
}

export interface GameStat {
  game_date: string
  matchup: string
  home_away: string
  points: number
  rebounds: number
  assists: number
  minutes_played: number
  opponent_abbr: string | null
}

export interface PropPrediction {
  player_id: number
  full_name: string
  target: string
  predicted_value: number
  model_mae: number
}

export interface PredictionResponse {
  player_id: number
  full_name: string
  points: PropPrediction | null
  rebounds: PropPrediction | null
  assists: PropPrediction | null
}

export interface HealthResponse {
  status: string
  database: string
  models_loaded: boolean
  version: string
}

export const authService = {
  login: async (username: string, password: string): Promise<string> => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await apiClient.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data.access_token
  },

  logout: () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('token')
  },
}

export const playerService = {
  getPlayers: async (search?: string, limit = 50): Promise<Player[]> => {
    const params: Record<string, string | number> = { limit }
    if (search) params.search = search
    const response = await apiClient.get('/players', { params })
    return response.data
  },

  getPlayer: async (playerId: number): Promise<Player> => {
    const response = await apiClient.get(`/players/${playerId}`)
    return response.data
  },

  getPlayerStats: async (playerId: number, limit = 20): Promise<GameStat[]> => {
    const response = await apiClient.get(`/players/${playerId}/stats`, {
      params: { limit },
    })
    return response.data
  },
}

export const predictionService = {
  getPredictions: async (playerId: number): Promise<PredictionResponse> => {
    const response = await apiClient.get(`/predictions/${playerId}`)
    return response.data
  },
}

export const healthService = {
  getHealth: async (): Promise<HealthResponse> => {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export interface ShapFeature {
  feature: string
  shap_value: number
  value: number
}

export interface ShapResponse {
  player_id: number
  full_name: string
  target: string
  prediction: number
  features: ShapFeature[]
}

export const shapService = {
  getExplanation: async (playerId: number, target: string): Promise<ShapResponse> => {
    const response = await apiClient.get(`/predictions/${playerId}/explain/${target}`)
    return response.data
  },
}
