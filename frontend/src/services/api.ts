
import axios from 'axios'
import { AuthService } from './auth'

const API_BASE = '/api'

const apiClient = axios.create({
  baseURL: API_BASE
})

// Add auth header to all requests
apiClient.interceptors.request.use((config) => {
  const token = AuthService.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export class ApiService {
  static async getAccounts() {
    const response = await apiClient.get('/accounts')
    return response.data
  }

  static async getChats() {
    const response = await apiClient.get('/chats')
    return response.data
  }

  static async getMessages(chatId: string, limit = 50) {
    const response = await apiClient.get(`/chats/${chatId}/messages?limit=${limit}`)
    return response.data
  }

  static async sendMessage(platform: string, accountId: string, chatId: string, text: string) {
    const response = await apiClient.post('/messages/send', {
      platform,
      account_id: accountId,
      chat_id: chatId,
      text
    })
    return response.data
  }

  static async startTelegramAuth(phone: string) {
    const response = await apiClient.post('/auth/telegram/start', { phone })
    return response.data
  }

  static async verifyTelegramAuth(phone: string, code: string) {
    const response = await apiClient.post('/auth/telegram/verify', { phone, code })
    return response.data
  }

  static async getInstagramAuthUrl() {
    const response = await apiClient.get('/auth/instagram/url')
    return response.data
  }

  static async disconnectAccount(accountId: string) {
    const response = await apiClient.delete(`/accounts/${accountId}`)
    return response.data
  }
}
