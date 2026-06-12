export type WSMessage =
  | { type: 'token';             content: string }
  | { type: 'status';            node: string }
  | { type: 'done' }
  | { type: 'error';             message: string }
  | { type: 'approval_required'; reason: string }

export class AuraWebSocket {
  private ws: WebSocket | null = null
  private sessionId: string
  private onMessage: (msg: WSMessage) => void

  constructor(sessionId: string, onMessage: (msg: WSMessage) => void) {
    this.sessionId = sessionId
    this.onMessage = onMessage
  }

  connect() {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    const token  = localStorage.getItem('aura_token') || ''
    this.ws      = new WebSocket(`${WS_URL}/api/chat/ws/${this.sessionId}?token=${token}`)
    this.ws.onmessage = e => this.onMessage(JSON.parse(e.data))
    return this
  }

  send(message: string, userId: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ message, user_id: userId }))
    }
  }

  sendApproval(approved: boolean) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'approval_response', approved }))
    }
  }

  close() { this.ws?.close() }
}
