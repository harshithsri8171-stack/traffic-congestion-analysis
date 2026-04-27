import { create } from 'zustand'
import { User } from '@/types'
import { api } from '@/services/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (username: string, password: string) => {
    const data = await api.login(username, password)
    localStorage.setItem('token', data.access_token)
    set({ token: data.access_token, isAuthenticated: true })

    // Load user profile
    const user = await api.getProfile()
    set({ user })
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  loadUser: async () => {
    try {
      const user = await api.getProfile()
      set({ user })
    } catch (error) {
      set({ user: null, token: null, isAuthenticated: false })
      localStorage.removeItem('token')
    }
  },
}))
