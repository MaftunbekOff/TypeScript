
export class WebSocketService {
  private static ws: WebSocket | null = null
  private static messageHandler: ((message: any) => void) | null = null

  static connect(onMessage: (message: any) => void) {
    this.messageHandler = onMessage
    
    // Get user ID from token (simplified)
    const token = localStorage.getItem('access_token')
    if (!token) return

    try {
      // Parse JWT to get user ID (simplified - in production use proper JWT library)
      const payload = JSON.parse(atob(token.split('.')[1]))
      const userId = payload.user_id

      const wsUrl = `ws://${window.location.host}/ws/${userId}`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.messageHandler?.(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (this.messageHandler) {
            this.connect(this.messageHandler)
          }
        }, 3000)
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error connecting WebSocket:', error)
    }
  }

  static disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.messageHandler = null
  }

  static send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }
}
