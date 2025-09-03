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
      console.log(`🔌 WEBSOCKET: Connecting to ${wsUrl}`);
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('✅ WEBSOCKET: Connected successfully')
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('📨 WEBSOCKET MESSAGE:', message);
          this.messageHandler?.(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('🔌 WEBSOCKET: Disconnected')
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (this.messageHandler) {
            this.connect(this.messageHandler)
          }
        }, 3000)
      }

      this.ws.onerror = (error) => {
        console.error('❌ WEBSOCKET ERROR:', error)
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