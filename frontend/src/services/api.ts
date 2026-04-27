import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 'Content-Type': 'application/json' },
    })

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token')
      if (token) config.headers.Authorization = `Bearer ${token}`
      return config
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth
  async login(username: string, password: string) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  }

  async register(data: any) {
    const response = await this.client.post('/auth/register', data)
    return response.data
  }

  async getProfile() {
    const response = await this.client.get('/auth/profile')
    return response.data
  }

  async logout() {
    const response = await this.client.post('/auth/logout')
    return response.data
  }

  // Dashboard
  async getDashboardOverview() {
    const response = await this.client.get('/dashboard/overview')
    return response.data
  }

  async getRoadData(roadId: number) {
    const response = await this.client.get(`/dashboard/road/${roadId}`)
    return response.data
  }

  async getTrends(roadId: number, period = 'hourly') {
    const response = await this.client.get('/dashboard/trends', {
      params: { road_id: roadId, period },
    })
    return response.data
  }

  async getHeatmap() {
    const response = await this.client.get('/dashboard/heatmap')
    return response.data
  }

  async getAlerts() {
    const response = await this.client.get('/dashboard/alerts')
    return response.data
  }

  async getPeakHours(roadId?: number) {
    const response = await this.client.get('/dashboard/peak-hours', {
      params: roadId ? { road_id: roadId } : {},
    })
    return response.data
  }

  async compareRoads(road1Id: number, road2Id: number, hours = 24) {
    const response = await this.client.get('/dashboard/comparison', {
      params: { road1_id: road1Id, road2_id: road2Id, hours },
    })
    return response.data
  }

  // Traffic
  async getLiveTraffic(roadId: number) {
    const response = await this.client.get(`/traffic/live/${roadId}`)
    return response.data
  }

  async getTrafficHistory(roadId: number, limit = 100) {
    const response = await this.client.get(`/traffic/history/${roadId}`, {
      params: { limit },
    })
    return response.data
  }

  async uploadVideo(file: File, roadId: number) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('road_id', roadId.toString())
    const response = await this.client.post('/traffic/upload-video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  // Admin
  async addRoad(data: any) {
    const response = await this.client.post('/admin/add-road', data)
    return response.data
  }

  async updateRoad(roadId: number, data: any) {
    const response = await this.client.put(`/admin/update-road/${roadId}`, data)
    return response.data
  }

  async deleteRoad(roadId: number) {
    const response = await this.client.delete(`/admin/delete-road/${roadId}`)
    return response.data
  }

  async listRoads(activeOnly = true) {
    const response = await this.client.get('/admin/roads', {
      params: { active_only: activeOnly },
    })
    return response.data
  }

  async listUsers() {
    const response = await this.client.get('/admin/users')
    return response.data
  }

  async toggleUserActive(userId: number) {
    const response = await this.client.put(`/admin/users/${userId}/toggle-active`)
    return response.data
  }

  async seedData() {
    const response = await this.client.post('/admin/seed')
    return response.data
  }
}

export const api = new ApiService()
