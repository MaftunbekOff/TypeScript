
import React, { useState, useEffect } from 'react'
import { AuthService } from './services/auth'
import { ApiService } from './services/api'
import { WebSocketService } from './services/websocket'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = AuthService.getToken()
    if (token) {
      try {
        // Verify token by making a test API call
        await ApiService.getAccounts()
        setIsAuthenticated(true)
      } catch (error) {
        AuthService.logout()
      }
    }
    setLoading(false)
  }

  const handleLogin = (token: string) => {
    AuthService.setToken(token)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    AuthService.logout()
    setIsAuthenticated(false)
    WebSocketService.disconnect()
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading CrossMessenger...</p>
      </div>
    )
  }

  return (
    <div className="app">
      {isAuthenticated ? (
        <Dashboard onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  )
}

export default App
