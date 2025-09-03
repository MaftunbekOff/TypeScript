
import axios from 'axios'

const API_BASE = '/api'

export class AuthService {
  static getToken(): string | null {
    return localStorage.getItem('access_token')
  }

  static setToken(token: string): void {
    localStorage.setItem('access_token', token)
  }

  static logout(): void {
    localStorage.removeItem('access_token')
  }

  static async login(email: string, password: string) {
    const response = await axios.post(`${API_BASE}/auth/login`, {
      email,
      password
    })
    return response.data
  }

  static async register(email: string, password: string) {
    const response = await axios.post(`${API_BASE}/auth/register`, {
      email,
      password
    })
    return response.data
  }

  static getAuthHeaders() {
    const token = this.getToken()
    return token ? { Authorization: `Bearer ${token}` } : {}
  }
}
