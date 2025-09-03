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
    console.log('🔑 FRONTEND: Attempting login for', email);
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        email,
        password
      })
      localStorage.setItem('access_token', response.data.access_token);
      console.log('✅ FRONTEND: Login successful for', email);
      return response.data
    } catch (error) {
      console.error('❌ FRONTEND: Login failed for', email, error);
      throw error;
    }
  }

  static async register(email: string, password: string) {
    console.log('🔐 FRONTEND: Attempting registration for', email);
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, {
        email,
        password
      })
      localStorage.setItem('access_token', response.data.access_token);
      console.log('✅ FRONTEND: Registration successful for', email);
      return response.data
    } catch (error) {
      console.error('❌ FRONTEND: Registration failed for', email, error);
      throw error;
    }
  }

  static getAuthHeaders() {
    const token = this.getToken()
    return token ? { Authorization: `Bearer ${token}` } : {}
  }
}