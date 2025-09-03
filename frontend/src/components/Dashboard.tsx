
import React, { useState, useEffect } from 'react'
import { ApiService } from '../services/api'
import { WebSocketService } from '../services/websocket'
import AccountConnector from './AccountConnector'
import ChatList from './ChatList'
import MessageView from './MessageView'

interface DashboardProps {
  onLogout: () => void
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [accounts, setAccounts] = useState([])
  const [chats, setChats] = useState([])
  const [selectedChat, setSelectedChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [showConnector, setShowConnector] = useState(false)

  useEffect(() => {
    loadAccounts()
    loadChats()
    
    // Connect WebSocket
    WebSocketService.connect((message) => {
      if (message.type === 'message:new') {
        // Refresh messages if it's for the current chat
        if (selectedChat && message.chat_id === selectedChat.chat_id) {
          loadMessages(selectedChat.chat_id)
        }
        // Refresh chat list to update last message time
        loadChats()
      }
    })

    return () => {
      WebSocketService.disconnect()
    }
  }, [])

  useEffect(() => {
    if (selectedChat) {
      loadMessages(selectedChat.chat_id)
    }
  }, [selectedChat])

  const loadAccounts = async () => {
    try {
      const response = await ApiService.getAccounts()
      setAccounts(response.accounts)
    } catch (error) {
      console.error('Error loading accounts:', error)
    }
  }

  const loadChats = async () => {
    try {
      const response = await ApiService.getChats()
      setChats(response.chats)
    } catch (error) {
      console.error('Error loading chats:', error)
    }
  }

  const loadMessages = async (chatId: string) => {
    try {
      const response = await ApiService.getMessages(chatId)
      setMessages(response.messages)
    } catch (error) {
      console.error('Error loading messages:', error)
    }
  }

  const handleSendMessage = async (platform: string, accountId: string, chatId: string, text: string) => {
    try {
      await ApiService.sendMessage(platform, accountId, chatId, text)
      // Refresh messages
      loadMessages(chatId)
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const handleAccountConnected = () => {
    loadAccounts()
    loadChats()
    setShowConnector(false)
  }

  const handleDisconnectAccount = async (accountId: string) => {
    try {
      await ApiService.disconnectAccount(accountId)
      loadAccounts()
      loadChats()
    } catch (error) {
      console.error('Error disconnecting account:', error)
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>CrossMessenger</h1>
        <div className="header-actions">
          <button onClick={() => setShowConnector(true)}>
            Connect Account
          </button>
          <button onClick={onLogout}>Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="sidebar">
          <div className="accounts-section">
            <h3>Connected Accounts ({accounts.length})</h3>
            {accounts.map((account: any) => (
              <div key={account.id} className="account-item">
                <span className={`platform-icon ${account.platform}`}>
                  {account.platform.charAt(0).toUpperCase()}
                </span>
                <span>{account.platform}</span>
                <button 
                  onClick={() => handleDisconnectAccount(account.id)}
                  className="disconnect-btn"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          
          <ChatList 
            chats={chats}
            selectedChat={selectedChat}
            onSelectChat={setSelectedChat}
          />
        </div>

        <div className="main-content">
          {selectedChat ? (
            <MessageView
              chat={selectedChat}
              messages={messages}
              accounts={accounts}
              onSendMessage={handleSendMessage}
            />
          ) : (
            <div className="welcome-screen">
              <h2>Welcome to CrossMessenger</h2>
              <p>Select a chat to start messaging</p>
              {accounts.length === 0 && (
                <button onClick={() => setShowConnector(true)}>
                  Connect Your First Account
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {showConnector && (
        <AccountConnector
          onClose={() => setShowConnector(false)}
          onAccountConnected={handleAccountConnected}
        />
      )}
    </div>
  )
}

export default Dashboard
