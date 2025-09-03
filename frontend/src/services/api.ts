import axios from 'axios'
import { AuthService } from './auth'

const API_BASE = '/api'

const apiClient = axios.create({
  baseURL: API_BASE
})

// Add API request/response logging
apiClient.interceptors.request.use((config) => {
  console.log(`🌐 API REQUEST: ${config.method?.toUpperCase()} ${config.url}`, config.data);
  const token = AuthService.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Log responses and errors
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API RESPONSE: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error(`❌ API ERROR: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

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