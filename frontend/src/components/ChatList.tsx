
import React from 'react'

interface Chat {
  id: string
  chat_id: string
  title: string
  platform: string
  last_message_at: string
}

interface ChatListProps {
  chats: Chat[]
  selectedChat: Chat | null
  onSelectChat: (chat: Chat) => void
}

const ChatList: React.FC<ChatListProps> = ({ chats, selectedChat, onSelectChat }) => {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 24 * 60 * 60 * 1000) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else {
      return date.toLocaleDateString()
    }
  }

  return (
    <div className="chat-list">
      <h3>Chats ({chats.length})</h3>
      <div className="chat-items">
        {chats.map((chat) => (
          <div
            key={`${chat.platform}_${chat.chat_id}`}
            className={`chat-item ${selectedChat?.chat_id === chat.chat_id ? 'selected' : ''}`}
            onClick={() => onSelectChat(chat)}
          >
            <div className="chat-info">
              <div className="chat-header">
                <span className={`platform-badge ${chat.platform}`}>
                  {chat.platform.charAt(0).toUpperCase()}
                </span>
                <span className="chat-title">{chat.title}</span>
              </div>
              <div className="chat-time">
                {formatTime(chat.last_message_at)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChatList
