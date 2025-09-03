
import React, { useState } from 'react'
import { ApiService } from '../services/api'

interface AccountConnectorProps {
  onClose: () => void
  onAccountConnected: () => void
}

const AccountConnector: React.FC<AccountConnectorProps> = ({ onClose, onAccountConnected }) => {
  const [platform, setPlatform] = useState<'telegram' | 'instagram'>('telegram')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState<'select' | 'phone' | 'code' | 'instagram'>('select')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleTelegramStart = async () => {
    setLoading(true)
    setError('')
    
    try {
      await ApiService.startTelegramAuth(phone)
      setStep('code')
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to send code')
    } finally {
      setLoading(false)
    }
  }

  const handleTelegramVerify = async () => {
    setLoading(true)
    setError('')
    
    try {
      await ApiService.verifyTelegramAuth(phone, code)
      onAccountConnected()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Invalid code')
    } finally {
      setLoading(false)
    }
  }

  const handleInstagramConnect = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.getInstagramAuthUrl()
      window.open(response.auth_url, '_blank')
      // Note: In a real app, you'd handle the callback properly
      setError('Please complete Instagram OAuth in the new window, then refresh this page')
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to get Instagram auth URL')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Connect Account</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="modal-content">
          {step === 'select' && (
            <div className="platform-selector">
              <h3>Choose Platform</h3>
              <div className="platform-options">
                <button 
                  onClick={() => { setPlatform('telegram'); setStep('phone'); }}
                  className="platform-btn telegram"
                >
                  <span className="platform-icon">T</span>
                  Telegram
                </button>
                <button 
                  onClick={() => { setPlatform('instagram'); setStep('instagram'); }}
                  className="platform-btn instagram"
                >
                  <span className="platform-icon">I</span>
                  Instagram
                </button>
              </div>
            </div>
          )}

          {step === 'phone' && (
            <div className="telegram-auth">
              <h3>Connect Telegram</h3>
              <div className="form-group">
                <label>Phone Number:</label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1234567890"
                  required
                />
              </div>
              <button onClick={handleTelegramStart} disabled={loading || !phone}>
                {loading ? 'Sending...' : 'Send Code'}
              </button>
            </div>
          )}

          {step === 'code' && (
            <div className="telegram-verify">
              <h3>Enter Verification Code</h3>
              <p>We sent a code to {phone}</p>
              <div className="form-group">
                <label>Verification Code:</label>
                <input
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="12345"
                  required
                />
              </div>
              <button onClick={handleTelegramVerify} disabled={loading || !code}>
                {loading ? 'Verifying...' : 'Verify'}
              </button>
              <button onClick={() => setStep('phone')} className="back-btn">
                Back
              </button>
            </div>
          )}

          {step === 'instagram' && (
            <div className="instagram-auth">
              <h3>Connect Instagram</h3>
              <p>You'll be redirected to Instagram to authorize the connection.</p>
              <button onClick={handleInstagramConnect} disabled={loading}>
                {loading ? 'Opening...' : 'Connect Instagram'}
              </button>
              <p className="note">
                Note: Instagram DM access is limited. This demo shows mock data.
              </p>
            </div>
          )}

          {error && <div className="error">{error}</div>}
        </div>
      </div>
    </div>
  )
}

export default AccountConnector
