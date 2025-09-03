
import React, { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  sender_name: string
  text: string
  timestamp: string
  platform: string
}

interface Chat {
  chat_id: string
  title: string
  platform: string
}

interface Account {
  id: string
  platform: string
}

interface MessageViewProps {
  chat: Chat
  messages: Message[]
  accounts: Account[]
  onSendMessage: (platform: string, accountId: string, chatId: string, text: string) => void
}

const MessageView: React.FC<MessageViewProps> = ({ chat, messages, accounts, onSendMessage }) => {
  const [newMessage, setNewMessage] = useState('')
  const [selectedAccount, setSelectedAccount] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Auto-select account for the current chat platform
    const matchingAccount = accounts.find(acc => acc.platform === chat.platform)
    if (matchingAccount) {
      setSelectedAccount(matchingAccount.id)
    }
  }, [chat, accounts])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = () => {
    if (!newMessage.trim() || !selectedAccount) return

    const account = accounts.find(acc => acc.id === selectedAccount)
    if (!account) return

    onSendMessage(account.platform, selectedAccount, chat.chat_id, newMessage)
    setNewMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="message-view">
      <div className="chat-header">
        <span className={`platform-badge ${chat.platform}`}>
          {chat.platform.charAt(0).toUpperCase()}
        </span>
        <h2>{chat.title}</h2>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className="message">
            <div className="message-header">
              <span className="sender-name">{message.sender_name}</span>
              <span className="message-time">{formatTime(message.timestamp)}</span>
            </div>
            <div className="message-text">{message.text}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="message-composer">
        <div className="composer-controls">
          <select 
            value={selectedAccount} 
            onChange={(e) => setSelectedAccount(e.target.value)}
            className="account-selector"
          >
            <option value="">Select account...</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.platform} Account
              </option>
            ))}
          </select>
        </div>
        
        <div className="composer-input">
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            rows={1}
          />
          <button 
            onClick={handleSend} 
            disabled={!newMessage.trim() || !selectedAccount}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default MessageView
