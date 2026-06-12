'use client'
import { useState, useEffect, useRef, useCallback } from 'react'
import { Send, Mic, MicOff, Upload, Settings, Zap, LogOut, Plus, Volume2, VolumeX, AudioLines, Square,
         Wrench, MessageSquare, FileText, Search, Pin, X } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface Message {
  id:      string
  role:    'user' | 'assistant' | 'status' | 'error'
  content: string
  ts:      Date
}

interface LocalSession {
  id:     string
  title:  string
  ts:     number
  pinned: boolean
}

export default function ChatPage() {
  const router     = useRouter()
  const [messages, setMessages]     = useState<Message[]>([])
  const [input,    setInput]        = useState('')
  const [loading,  setLoading]      = useState(false)
  const [status,   setStatus]       = useState('Ready')
  const [recording, setRecording]   = useState(false)
  const [voiceMode, setVoiceModeState] = useState(false)
  const setVoiceMode = (v: boolean) => {
    voiceModeRef.current = v
    setVoiceModeState(v)
    if (!v && typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
  }
  const [transcribing, setTranscribing] = useState(false)
  const [convoActive, setConvoActive] = useState(false)
  const wsRef      = useRef<WebSocket | null>(null)
  const bottomRef  = useRef<HTMLDivElement>(null)
  const fileRef    = useRef<HTMLInputElement>(null)
  const sessionId  = useRef(`sess_${Date.now()}`)
  const mediaRef   = useRef<MediaRecorder | null>(null)
  const chunksRef  = useRef<Blob[]>([])
  const voiceModeRef = useRef(false)
  const convoActiveRef = useRef(false)
  const loadingRef = useRef(false)
  const recognitionRef = useRef<any>(null)

  // Hermes-style sidebar: sessions, search, skills/artifacts panels
  const [localSessions, setLocalSessions] = useState<LocalSession[]>([])
  const [sessionSearch, setSessionSearch] = useState('')
  const [panel, setPanel] = useState<'none' | 'skills' | 'artifacts'>('none')
  const [agentsList, setAgentsList] = useState<any[]>([])
  const [docsList, setDocsList] = useState<any[]>([])
  const [panelLoading, setPanelLoading] = useState(false)

  useEffect(() => {
    try {
      const raw = localStorage.getItem('aura_local_sessions')
      if (raw) setLocalSessions(JSON.parse(raw))
    } catch {}
  }, [])

  const persistSessions = (list: LocalSession[]) => {
    setLocalSessions(list)
    localStorage.setItem('aura_local_sessions', JSON.stringify(list))
  }

  const recordSession = useCallback((firstMessage: string) => {
    setLocalSessions(prev => {
      if (prev.some(s => s.id === sessionId.current)) return prev
      const next = [{ id: sessionId.current, title: firstMessage.slice(0, 40), ts: Date.now(), pinned: false }, ...prev]
      localStorage.setItem('aura_local_sessions', JSON.stringify(next))
      return next
    })
  }, [])

  const togglePin = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    persistSessions(localSessions.map(s => s.id === id ? { ...s, pinned: !s.pinned } : s))
  }

  const removeSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    persistSessions(localSessions.filter(s => s.id !== id))
  }

  const switchSession = (id: string) => {
    if (id === sessionId.current) return
    sessionId.current = id
    setMessages([])
    wsRef.current?.close()
    connectWS()
  }

  const openPanel = async (which: 'skills' | 'artifacts') => {
    setPanel(which)
    setPanelLoading(true)
    const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const token = localStorage.getItem('aura_token') || ''
    try {
      if (which === 'skills') {
        const res = await fetch(`${API}/api/agents/`, { headers: { Authorization: `Bearer ${token}` } })
        const data = await res.json()
        setAgentsList(data.agents || [])
      } else {
        const res = await fetch(`${API}/api/knowledge/documents`, { headers: { Authorization: `Bearer ${token}` } })
        const data = await res.json()
        setDocsList(data.documents || [])
      }
    } catch {
      // ignore - panel will show empty state
    } finally {
      setPanelLoading(false)
    }
  }

  const connectWS = useCallback(() => {
    const WS_URL  = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    const token   = localStorage.getItem('aura_token') || ''
    const url     = `${WS_URL}/api/chat/ws/${sessionId.current}?token=${token}`
    const ws      = new WebSocket(url)

    ws.onopen  = () => setStatus('Connected')
    ws.onclose = () => setStatus('Reconnecting...')
    ws.onerror = () => setStatus('Connection error')

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      switch (data.type) {
        case 'token':
          setMessages(prev => {
            const last = prev[prev.length - 1]
            if (last?.role === 'assistant') {
              return [...prev.slice(0, -1),
                { ...last, content: last.content + data.content }]
            }
            return [...prev, { id: Date.now().toString(), role: 'assistant',
                               content: data.content, ts: new Date() }]
          })
          break
        case 'status':
          setStatus(`Processing: ${data.node}`)
          break
        case 'done':
          setLoading(false)
          loadingRef.current = false
          setStatus('Ready')
          if (voiceModeRef.current && typeof window !== 'undefined' && window.speechSynthesis) {
            setMessages(prev => {
              const last = prev[prev.length - 1]
              if (last?.role === 'assistant' && last.content) {
                const utter = new SpeechSynthesisUtterance(last.content)
                utter.onend = () => {
                  if (convoActiveRef.current) startRecognition()
                }
                window.speechSynthesis.cancel()
                window.speechSynthesis.speak(utter)
              } else if (convoActiveRef.current) {
                startRecognition()
              }
              return prev
            })
          } else if (convoActiveRef.current) {
            startRecognition()
          }
          break
        case 'approval_required':
          setMessages(prev => [...prev, {
            id: Date.now().toString(), role: 'status',
            content: `⚠️ Approval needed\n${data.reason || ''}`, ts: new Date()
          }])
          setLoading(false)
          loadingRef.current = false
          setStatus('Awaiting approval')
          convoActiveRef.current = false
          setConvoActive(false)
          break
        case 'error':
          setMessages(prev => [...prev, {
            id: Date.now().toString(), role: 'error',
            content: `Error: ${data.message}`, ts: new Date()
          }])
          setLoading(false)
          loadingRef.current = false
          setStatus('Ready')
          if (convoActiveRef.current) startRecognition()
          break
      }
    }
    wsRef.current = ws
    return ws
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('aura_token')
    if (!token) { router.replace('/login'); return }
    const ws = connectWS()
    return () => ws.close()
  }, [connectWS, router])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = useCallback((text?: string) => {
    const content = (text ?? input).trim()
    if (!content || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    const userId = localStorage.getItem('aura_user_id') || ''
    setMessages(prev => [...prev, {
      id: Date.now().toString(), role: 'user', content, ts: new Date()
    }])
    recordSession(content)
    setLoading(true)
    loadingRef.current = true
    setStatus('Thinking...')
    wsRef.current.send(JSON.stringify({ message: content, user_id: userId }))
    setInput('')
  }, [input])

  const startRecognition = useCallback(() => {
    if (typeof window === 'undefined') return
    const SR: any = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(), role: 'error',
        content: 'Voice conversation requires a browser with speech recognition support (e.g. Chrome/Edge)',
        ts: new Date()
      }])
      convoActiveRef.current = false
      setConvoActive(false)
      return
    }
    if (recognitionRef.current) {
      try { recognitionRef.current.stop() } catch {}
    }
    const recognition = new SR()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onresult = (e: any) => {
      const text = e.results?.[0]?.[0]?.transcript?.trim()
      if (text) sendMessage(text)
    }
    recognition.onerror = (e: any) => {
      if (e.error === 'no-speech' || e.error === 'aborted') return
      setMessages(prev => [...prev, {
        id: Date.now().toString(), role: 'error',
        content: `Voice recognition error: ${e.error}`, ts: new Date()
      }])
    }
    recognition.onend = () => {
      if (convoActiveRef.current && !loadingRef.current &&
          !(typeof window !== 'undefined' && window.speechSynthesis?.speaking)) {
        setTimeout(() => {
          if (convoActiveRef.current && !loadingRef.current) startRecognition()
        }, 300)
      }
    }

    recognitionRef.current = recognition
    setStatus('Listening...')
    try { recognition.start() } catch {}
  }, [sendMessage])

  const toggleConversation = () => {
    if (convoActive) {
      convoActiveRef.current = false
      setConvoActive(false)
      if (recognitionRef.current) {
        try { recognitionRef.current.stop() } catch {}
        recognitionRef.current = null
      }
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
      setStatus('Ready')
    } else {
      convoActiveRef.current = true
      setConvoActive(true)
      setVoiceMode(true)
      startRecognition()
    }
  }

  const handleApprove = (approved: boolean) => {
    if (!wsRef.current) return
    wsRef.current.send(JSON.stringify({ type: 'approval_response', approved }))
    setStatus(approved ? 'Executing...' : 'Cancelled')
    setLoading(approved)
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const API   = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const token = localStorage.getItem('aura_token') || ''
    const form  = new FormData()
    form.append('file', file)
    try {
      await fetch(`${API}/api/knowledge/ingest`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: form
      })
      setMessages(prev => [...prev, {
        id: Date.now().toString(), role: 'status',
        content: `📄 "${file.name}" queued for ingestion`, ts: new Date()
      }])
    } catch {
      setMessages(prev => [...prev, {
        id: Date.now().toString(), role: 'error',
        content: 'File upload failed', ts: new Date()
      }])
    }
    e.target.value = ''
  }

  const toggleRecording = async () => {
    if (recording) {
      mediaRef.current?.stop()
      setRecording(false)
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : MediaRecorder.isTypeSupported('audio/mp4')
          ? 'audio/mp4'
          : ''
      const mr = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream)
      const usedType = mr.mimeType || 'audio/webm'
      chunksRef.current = []
      mr.ondataavailable = e => { if (e.data && e.data.size > 0) chunksRef.current.push(e.data) }
      mr.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunksRef.current, { type: usedType })
        if (blob.size === 0) {
          setMessages(prev => [...prev, {
            id: Date.now().toString(), role: 'error',
            content: 'No audio captured — please try again', ts: new Date()
          }])
          return
        }
        const ext   = usedType.includes('mp4') ? 'm4a' : 'webm'
        const API   = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const token = localStorage.getItem('aura_token') || ''
        const form  = new FormData()
        form.append('audio', blob, `recording.${ext}`)
        setTranscribing(true)
        setStatus('Transcribing...')
        try {
          const res = await fetch(`${API}/api/voice/transcribe`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: form
          })
          if (!res.ok) {
            const errText = await res.text().catch(() => '')
            throw new Error(errText || `Transcription failed (${res.status})`)
          }
          const data = await res.json()
          const text = (data.transcript || '').trim()
          if (text) {
            if (voiceModeRef.current) {
              sendMessage(text)
            } else {
              setInput(text)
            }
          } else {
            setMessages(prev => [...prev, {
              id: Date.now().toString(), role: 'error',
              content: 'No speech detected — please try again', ts: new Date()
            }])
          }
          setStatus('Ready')
        } catch (err: any) {
          setMessages(prev => [...prev, {
            id: Date.now().toString(), role: 'error',
            content: `Voice transcription failed: ${err?.message || err}`, ts: new Date()
          }])
          setStatus('Ready')
        } finally {
          setTranscribing(false)
        }
      }
      mr.start()
      mediaRef.current = mr
      setRecording(true)
    } catch (err: any) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(), role: 'error',
        content: `Microphone access denied: ${err?.message || err}`, ts: new Date()
      }])
    }
  }

  const handleLogout = () => {
    localStorage.clear()
    wsRef.current?.close()
    router.replace('/login')
  }

  const newChat = () => {
    sessionId.current = `sess_${Date.now()}`
    setMessages([])
    wsRef.current?.close()
    connectWS()
  }

  const userName = typeof window !== 'undefined'
    ? localStorage.getItem('aura_name') || 'User' : 'User'

  return (
    <div className="flex h-screen bg-[#0f0f23]">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <div className="w-64 bg-[#1a1a2e] border-r border-[#2a2a4a] flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-[#2a2a4a]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <Zap size={16} className="text-white"/>
            </div>
            <div>
              <div className="font-bold text-white text-sm">AURA AI-OS</div>
              <div className="text-xs text-gray-600">v1.0</div>
            </div>
          </div>
        </div>

        {/* New Chat */}
        <div className="p-3">
          <button
            onClick={newChat}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg
                       border border-[#2a2a4a] hover:border-purple-500/50
                       text-gray-400 hover:text-white text-sm transition-all"
          >
            <Plus size={14}/> New session
          </button>
        </div>

        {/* Nav: Skills & Tools / Messaging / Artifacts */}
        <div className="px-3 pb-2 space-y-0.5">
          <button onClick={() => openPanel('skills')}
            className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors
              ${panel === 'skills' ? 'bg-purple-600/20 text-purple-300' : 'text-gray-400 hover:text-white hover:bg-[#0f0f23]'}`}>
            <Wrench size={14}/> Skills &amp; Tools
          </button>
          <button onClick={() => setPanel('none')}
            className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors
              ${panel === 'none' ? 'bg-purple-600/20 text-purple-300' : 'text-gray-400 hover:text-white hover:bg-[#0f0f23]'}`}>
            <MessageSquare size={14}/> Messaging
          </button>
          <button onClick={() => openPanel('artifacts')}
            className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors
              ${panel === 'artifacts' ? 'bg-purple-600/20 text-purple-300' : 'text-gray-400 hover:text-white hover:bg-[#0f0f23]'}`}>
            <FileText size={14}/> Artifacts
          </button>
          <button onClick={() => router.push('/settings')}
            className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors
              text-gray-400 hover:text-white hover:bg-[#0f0f23]">
            <Settings size={14}/> Connectors &amp; Skills
          </button>
        </div>

        {/* Search */}
        <div className="px-3 pb-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-[#0f0f23] border border-[#2a2a4a]">
            <Search size={12} className="text-gray-600"/>
            <input
              value={sessionSearch}
              onChange={e => setSessionSearch(e.target.value)}
              placeholder="Search sessions..."
              className="bg-transparent text-xs text-gray-300 placeholder-gray-600 outline-none flex-1"
            />
          </div>
        </div>

        {/* Sessions */}
        <div className="px-3 flex-1 overflow-y-auto">
          {(() => {
            const filtered = localSessions.filter(s =>
              s.title.toLowerCase().includes(sessionSearch.toLowerCase()))
            const pinned = filtered.filter(s => s.pinned)
            const rest   = filtered.filter(s => !s.pinned)
            const renderItem = (s: LocalSession) => (
              <div key={s.id} onClick={() => switchSession(s.id)}
                className={`group flex items-center gap-2 px-2 py-1.5 rounded-lg cursor-pointer text-xs
                  ${s.id === sessionId.current ? 'bg-purple-600/20 text-purple-300' : 'text-gray-500 hover:text-gray-300 hover:bg-[#0f0f23]'}`}>
                <span className="truncate flex-1">{s.title || 'New chat'}</span>
                <button onClick={e => togglePin(s.id, e)} title={s.pinned ? 'Unpin' : 'Pin'}
                  className={`shrink-0 ${s.pinned ? 'text-purple-400' : 'text-gray-700 group-hover:text-gray-400'}`}>
                  <Pin size={11}/>
                </button>
                <button onClick={e => removeSession(s.id, e)} title="Remove"
                  className="shrink-0 text-gray-700 group-hover:text-gray-400 hover:text-red-400">
                  <X size={11}/>
                </button>
              </div>
            )
            return (
              <>
                {pinned.length > 0 && (
                  <>
                    <p className="text-xs text-gray-600 uppercase tracking-wider mb-1 px-1 mt-1">Pinned</p>
                    {pinned.map(renderItem)}
                  </>
                )}
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-1 px-1 mt-2">
                  Sessions {filtered.length ? `(${filtered.length})` : ''}
                </p>
                {rest.length === 0 && pinned.length === 0 && (
                  <p className="text-xs text-gray-700 px-2 py-1">Shift-click pin to save a chat</p>
                )}
                {rest.map(renderItem)}
              </>
            )
          })()}
        </div>

        {/* User */}
        <div className="p-3 border-t border-[#2a2a4a]">
          <div className="flex items-center justify-between px-2">
            <div>
              <p className="text-xs text-white font-medium">{userName}</p>
              <p className="text-xs text-gray-600">Self-hosted</p>
            </div>
            <button onClick={handleLogout}
              className="text-gray-600 hover:text-red-400 transition-colors">
              <LogOut size={14}/>
            </button>
          </div>
        </div>
      </div>

      {/* ── Skills/Artifacts Panel ─────────────────────────── */}
      {panel !== 'none' && (
        <div className="w-72 border-r border-[#2a2a4a] bg-[#0f0f23] flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a2a4a]">
            <span className="text-sm font-medium text-white">
              {panel === 'skills' ? 'Skills & Tools' : 'Artifacts'}
            </span>
            <button onClick={() => setPanel('none')} className="text-gray-500 hover:text-white">
              <X size={14}/>
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {panelLoading && <p className="text-xs text-gray-600 px-1">Loading...</p>}
            {!panelLoading && panel === 'skills' && agentsList.length === 0 && (
              <p className="text-xs text-gray-600 px-1">No agents found</p>
            )}
            {!panelLoading && panel === 'skills' && agentsList.map((a, i) => (
              <div key={i} className="px-3 py-2 rounded-lg border border-[#2a2a4a] bg-[#1a1a2e]">
                <div className="flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 rounded-full ${a.enabled ? 'bg-green-400' : 'bg-gray-600'}`}/>
                  <span className="text-sm text-white font-medium">{a.name}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{a.description}</p>
              </div>
            ))}
            {!panelLoading && panel === 'artifacts' && docsList.length === 0 && (
              <p className="text-xs text-gray-600 px-1">No documents ingested yet</p>
            )}
            {!panelLoading && panel === 'artifacts' && docsList.map((d, i) => (
              <div key={i} className="px-3 py-2 rounded-lg border border-[#2a2a4a] bg-[#1a1a2e]">
                <div className="flex items-center gap-2">
                  <FileText size={12} className="text-purple-400"/>
                  <span className="text-sm text-white truncate">{d.filename}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{d.doc_type} · {d.chunk_count} chunks</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Main Chat ──────────────────────────────────────── */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3
                        border-b border-[#2a2a4a] bg-[#0f0f23]">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              status === 'Ready' || status === 'Connected'
                ? 'bg-green-400' : 'bg-yellow-400 animate-pulse'
            }`}/>
            <span className="text-xs text-gray-500">{status}</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setVoiceMode(!voiceMode)}
              title={voiceMode ? 'Voice mode on (responses spoken aloud)' : 'Enable voice mode'}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs transition-colors
                ${voiceMode
                  ? 'bg-purple-600/20 text-purple-300 border border-purple-500/40'
                  : 'text-gray-600 hover:text-gray-300 border border-transparent hover:border-[#2a2a4a]'}`}>
              {voiceMode ? <Volume2 size={14}/> : <VolumeX size={14}/>}
              Voice Mode
            </button>
            <Settings size={16} className="text-gray-600 cursor-pointer hover:text-white"/>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center
                            animate-fade-in pb-20">
              <div className="w-16 h-16 rounded-2xl bg-purple-600/20 border border-purple-500/30
                              flex items-center justify-center mb-4">
                <Zap size={28} className="text-purple-400"/>
              </div>
              <h2 className="text-xl font-bold text-white mb-2">
                Hello, I&apos;m AURA
              </h2>
              <p className="text-gray-500 max-w-md text-sm leading-relaxed">
                Your Personal AI Operating System. I can help you plan your day,
                analyse meetings, write code, manage infrastructure, create content,
                and automate almost anything.
              </p>
              <div className="grid grid-cols-2 gap-2 mt-6 w-full max-w-md">
                {[
                  '📋 Summarise my last meeting',
                  '💻 Write a Python function to...',
                  '🚀 Debug my Kubernetes pods',
                  '✉️ Draft an email to my team'
                ].map(s => (
                  <button key={s}
                    onClick={() => setInput(s.slice(3).trim())}
                    className="text-left text-xs text-gray-500 border border-[#2a2a4a]
                               rounded-xl px-3 py-2 hover:border-purple-500/50
                               hover:text-gray-300 transition-all bg-[#1a1a2e]">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}
                          animate-slide-up`}>
              {msg.role === 'status' ? (
                <div className="max-w-xl mx-auto text-center">
                  <div className="inline-block text-xs text-amber-400 bg-amber-900/20
                                  border border-amber-800/40 rounded-xl px-4 py-2 whitespace-pre-wrap">
                    {msg.content}
                    {msg.content.includes('Approval needed') && (
                      <div className="flex gap-2 justify-center mt-2">
                        <button onClick={() => handleApprove(true)}
                          className="px-3 py-1 bg-green-600 hover:bg-green-500
                                     rounded-lg text-white text-xs font-medium">
                          Approve
                        </button>
                        <button onClick={() => handleApprove(false)}
                          className="px-3 py-1 bg-red-700 hover:bg-red-600
                                     rounded-lg text-white text-xs font-medium">
                          Deny
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : msg.role === 'error' ? (
                <div className="text-xs text-red-400 bg-red-900/20 border border-red-800/40
                                rounded-xl px-4 py-2 max-w-xl">
                  {msg.content}
                </div>
              ) : (
                <div className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed
                  ${msg.role === 'user'
                    ? 'bg-purple-600 text-white rounded-br-sm'
                    : 'bg-[#1a1a2e] border border-[#2a2a4a] text-gray-100 rounded-bl-sm'
                  }`}>
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                    {msg.content}
                  </pre>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-[#1a1a2e] border border-[#2a2a4a] px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex gap-1 items-center">
                  <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce"/>
                  <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:0.15s]"/>
                  <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:0.3s]"/>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef}/>
        </div>

        {/* Input */}
        <div className="p-4 border-t border-[#2a2a4a]">
          <div className="flex items-end gap-2 bg-[#1a1a2e] border border-[#2a2a4a]
                          rounded-2xl px-4 py-3 focus-within:border-purple-500/50 transition-colors">
            <textarea
              className="flex-1 bg-transparent text-white resize-none outline-none
                         text-sm leading-relaxed max-h-40 min-h-[24px] placeholder-gray-600"
              placeholder="Ask AURA anything... (Enter to send, Shift+Enter for newline)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault(); sendMessage()
                }
              }}
              rows={1}
            />
            <div className="flex items-center gap-1.5 pb-0.5">
              <input ref={fileRef} type="file" className="hidden"
                accept=".pdf,.docx,.md,.txt,.py,.js,.ts,.xlsx,.csv,.eml"
                onChange={handleFileUpload}/>
              <button
                onClick={() => fileRef.current?.click()}
                title="Upload document"
                className="p-1.5 text-gray-600 hover:text-gray-300 transition-colors rounded-lg
                           hover:bg-[#0f0f23]">
                <Upload size={16}/>
              </button>
              <button
                onClick={toggleRecording}
                disabled={transcribing || convoActive}
                title={recording ? 'Stop recording' : 'Voice input'}
                className={`p-1.5 rounded-lg transition-colors disabled:opacity-50
                  ${recording
                    ? 'text-red-400 bg-red-900/20 animate-pulse'
                    : 'text-gray-600 hover:text-gray-300 hover:bg-[#0f0f23]'}`}>
                {recording ? <MicOff size={16}/> : <Mic size={16}/>}
              </button>
              <button
                onClick={toggleConversation}
                disabled={recording || transcribing}
                title={convoActive ? 'Stop voice conversation' : 'Start voice conversation'}
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all disabled:opacity-50
                  ${convoActive
                    ? 'bg-red-600 hover:bg-red-500 animate-pulse'
                    : 'bg-purple-600 hover:bg-purple-500'}`}>
                {convoActive ? <Square size={13} className="text-white"/> : <AudioLines size={15} className="text-white"/>}
              </button>
              <button
                onClick={sendMessage}
                disabled={!input.trim() || loading}
                className="w-8 h-8 bg-purple-600 hover:bg-purple-500 disabled:opacity-30
                           disabled:cursor-not-allowed rounded-xl flex items-center
                           justify-center transition-all">
                <Send size={13} className="text-white"/>
              </button>
            </div>
          </div>
          <p className="text-center text-xs text-gray-700 mt-2">
            AURA AI-OS v1.0 · Privacy-first · Self-hosted · All data stays local
          </p>
        </div>
      </div>
    </div>
  )
}
