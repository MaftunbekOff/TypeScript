import React, { useState } from 'react'
import { AuthService } from '../services/auth'

interface LoginProps {
  onLogin: (token: string) => void
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log(`🎯 FORM SUBMIT: ${isLogin ? 'Login' : 'Register'} attempt for ${email}`);
    setError('')
    setLoading(true)

    try {
      let response
      if (isLogin) {
        console.log('📝 Calling login service...');
        response = await AuthService.login(email, password)
      } else {
        console.log('📝 Calling register service...');
        response = await AuthService.register(email, password)
      }

      onLogin(response.access_token)
      console.log('🎉 Authentication successful, redirecting...');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Authentication failed';
      console.error('💥 Authentication error:', errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>CrossMessenger</h1>
        <p className="subtitle">Connect Telegram, Instagram & Internal Chat</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <p className="switch-mode">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            type="button" 
            className="link-button"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  )
}

export default Login