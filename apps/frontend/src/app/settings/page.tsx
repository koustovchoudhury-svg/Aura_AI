'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Plug, Wrench, Brain, Trash2, Check, X } from 'lucide-react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function authHeaders() {
  const token = localStorage.getItem('aura_token') || ''
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
}

interface Connector {
  platform: string
  connected: boolean
  workspace_id?: string
  token_preview?: string
  connected_at?: string
}

interface AgentInfo {
  name: string
  description: string
  tools: { name: string; description: string; permission: string; cost_tier: string }[]
}

interface MemoryFact {
  id: string
  fact_type: string
  subject?: string
  content: string
  source: string
  created_at: string
}

const PLATFORM_LABELS: Record<string, string> = {
  slack: 'Slack', github: 'GitHub', jira: 'Jira',
  email: 'Email (SMTP)', google_calendar: 'Google Calendar'
}

export default function SettingsPage() {
  const router = useRouter()
  const [tab, setTab] = useState<'connectors' | 'skills' | 'memory'>('connectors')

  const [connectors, setConnectors] = useState<Connector[]>([])
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null)
  const [tokenInput, setTokenInput] = useState('')

  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [disabledTools, setDisabledTools] = useState<string[]>([])

  const [facts, setFacts] = useState<MemoryFact[]>([])
  const [newFact, setNewFact] = useState('')

  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('aura_token')
    if (!token) { router.replace('/login'); return }
    loadConnectors()
    loadSkills()
    loadMemory()
  }, [])

  const loadConnectors = async () => {
    const res = await fetch(`${API}/api/settings/connectors`, { headers: authHeaders() })
    const data = await res.json()
    setConnectors(data.connectors || [])
  }

  const loadSkills = async () => {
    const [agentsRes, skillsRes] = await Promise.all([
      fetch(`${API}/api/agents/`, { headers: authHeaders() }),
      fetch(`${API}/api/settings/skills`, { headers: authHeaders() })
    ])
    const agentsData = await agentsRes.json()
    const skillsData = await skillsRes.json()
    setAgents(agentsData.agents || [])
    setDisabledTools(skillsData.disabled_tools || [])
  }

  const loadMemory = async () => {
    const res = await fetch(`${API}/api/settings/memory`, { headers: authHeaders() })
    const data = await res.json()
    setFacts(data.facts || [])
  }

  const submitConnector = async (platform: string) => {
    if (!tokenInput.trim()) return
    setLoading(true)
    await fetch(`${API}/api/settings/connectors`, {
      method: 'POST', headers: authHeaders(),
      body: JSON.stringify({ platform, access_token: tokenInput })
    })
    setTokenInput('')
    setConnectingPlatform(null)
    await loadConnectors()
    setLoading(false)
  }

  const disconnect = async (platform: string) => {
    setLoading(true)
    await fetch(`${API}/api/settings/connectors/${platform}`, { method: 'DELETE', headers: authHeaders() })
    await loadConnectors()
    setLoading(false)
  }

  const toggleTool = async (toolName: string) => {
    const next = disabledTools.includes(toolName)
      ? disabledTools.filter(t => t !== toolName)
      : [...disabledTools, toolName]
    setDisabledTools(next)
    await fetch(`${API}/api/settings/skills`, {
      method: 'PUT', headers: authHeaders(),
      body: JSON.stringify({ disabled_tools: next })
    })
  }

  const addFact = async () => {
    if (!newFact.trim()) return
    setLoading(true)
    await fetch(`${API}/api/settings/memory`, {
      method: 'POST', headers: authHeaders(),
      body: JSON.stringify({ fact_type: 'note', content: newFact.trim() })
    })
    setNewFact('')
    await loadMemory()
    setLoading(false)
  }

  const removeFact = async (id: string) => {
    setFacts(prev => prev.filter(f => f.id !== id))
    await fetch(`${API}/api/settings/memory/${id}`, { method: 'DELETE', headers: authHeaders() })
  }

  return (
    <div className="flex h-screen bg-[#0a0a18] text-gray-100">
      {/* Sidebar */}
      <div className="w-56 border-r border-[#2a2a4a] flex flex-col p-3">
        <button onClick={() => router.push('/chat')}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 px-2 py-1">
          <ArrowLeft size={14}/> Back to chat
        </button>
        <p className="text-xs text-gray-600 uppercase tracking-wider mb-2 px-2">Settings</p>
        {[
          { id: 'connectors', label: 'Connectors', icon: Plug },
          { id: 'skills', label: 'Skills & Tools', icon: Wrench },
          { id: 'memory', label: 'Memory', icon: Brain },
        ].map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setTab(id as any)}
            className={`flex items-center gap-2 px-2 py-2 rounded-lg text-sm transition-colors
              ${tab === id ? 'bg-purple-600/20 text-purple-300' : 'text-gray-400 hover:text-white hover:bg-[#0f0f23]'}`}>
            <Icon size={14}/> {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8 max-w-3xl">
        {tab === 'connectors' && (
          <div>
            <h1 className="text-xl font-semibold text-white mb-1">Connectors</h1>
            <p className="text-sm text-gray-500 mb-6">
              Connect external accounts so AURA's agents can act on your behalf (Slack, GitHub, Jira, Email, Calendar).
            </p>
            <div className="space-y-3">
              {connectors.map(c => (
                <div key={c.platform} className="border border-[#2a2a4a] rounded-xl p-4 bg-[#0f0f23]">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">{PLATFORM_LABELS[c.platform] || c.platform}</p>
                      {c.connected ? (
                        <p className="text-xs text-green-400 mt-0.5 flex items-center gap-1">
                          <Check size={11}/> Connected {c.token_preview ? `· ${c.token_preview}` : ''}
                        </p>
                      ) : (
                        <p className="text-xs text-gray-600 mt-0.5">Not connected</p>
                      )}
                    </div>
                    {c.connected ? (
                      <button onClick={() => disconnect(c.platform)} disabled={loading}
                        className="text-xs px-3 py-1.5 rounded-lg border border-[#2a2a4a] text-gray-400 hover:text-red-400 hover:border-red-500/40">
                        Disconnect
                      </button>
                    ) : (
                      <button onClick={() => setConnectingPlatform(connectingPlatform === c.platform ? null : c.platform)}
                        className="text-xs px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white">
                        Connect
                      </button>
                    )}
                  </div>
                  {connectingPlatform === c.platform && (
                    <div className="mt-3 flex items-center gap-2">
                      <input
                        value={tokenInput}
                        onChange={e => setTokenInput(e.target.value)}
                        placeholder={`Paste ${PLATFORM_LABELS[c.platform] || c.platform} API token / app password`}
                        type="password"
                        className="flex-1 bg-[#1a1a2e] border border-[#2a2a4a] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-purple-500/50"
                      />
                      <button onClick={() => submitConnector(c.platform)} disabled={loading || !tokenInput.trim()}
                        className="text-xs px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white">
                        Save
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'skills' && (
          <div>
            <h1 className="text-xl font-semibold text-white mb-1">Skills &amp; Tools</h1>
            <p className="text-sm text-gray-500 mb-6">
              Enable or disable individual tools per agent. Disabled tools will be refused by AURA.
            </p>
            <div className="space-y-4">
              {agents.map(a => (
                <div key={a.name} className="border border-[#2a2a4a] rounded-xl p-4 bg-[#0f0f23]">
                  <p className="text-sm font-medium text-white">{a.name}</p>
                  <p className="text-xs text-gray-500 mb-3">{a.description}</p>
                  <div className="space-y-1.5">
                    {a.tools.length === 0 && (
                      <p className="text-xs text-gray-700">No discrete tools (uses direct LLM reasoning)</p>
                    )}
                    {a.tools.map(t => {
                      const isDisabled = disabledTools.includes(t.name)
                      return (
                        <div key={t.name} className="flex items-center justify-between px-2 py-1.5 rounded-lg hover:bg-[#1a1a2e]">
                          <div>
                            <p className="text-xs text-gray-300">{t.name}</p>
                            <p className="text-xs text-gray-600">{t.description} · {t.permission}</p>
                          </div>
                          <button onClick={() => toggleTool(t.name)}
                            className={`relative w-9 h-5 rounded-full transition-colors shrink-0
                              ${!isDisabled ? 'bg-purple-600' : 'bg-gray-700'}`}>
                            <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform
                              ${!isDisabled ? 'translate-x-4' : ''}`}/>
                          </button>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'memory' && (
          <div>
            <h1 className="text-xl font-semibold text-white mb-1">Memory</h1>
            <p className="text-sm text-gray-500 mb-6">
              Facts AURA remembers about you across sessions. Add things you want it to always know, or remove what it's learned.
            </p>
            <div className="flex items-center gap-2 mb-4">
              <input
                value={newFact}
                onChange={e => setNewFact(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addFact()}
                placeholder="e.g. I prefer concise answers, my timezone is IST..."
                className="flex-1 bg-[#1a1a2e] border border-[#2a2a4a] rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-purple-500/50"
              />
              <button onClick={addFact} disabled={loading || !newFact.trim()}
                className="text-xs px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white">
                Add
              </button>
            </div>
            <div className="space-y-2">
              {facts.length === 0 && <p className="text-xs text-gray-700">No memories yet</p>}
              {facts.map(f => (
                <div key={f.id} className="flex items-center justify-between px-3 py-2 rounded-lg border border-[#2a2a4a] bg-[#0f0f23]">
                  <div>
                    <p className="text-sm text-gray-200">{f.content}</p>
                    <p className="text-xs text-gray-600 mt-0.5">{f.fact_type} · {f.source} · {new Date(f.created_at).toLocaleString()}</p>
                  </div>
                  <button onClick={() => removeFact(f.id)} className="text-gray-600 hover:text-red-400 shrink-0 ml-2">
                    <Trash2 size={14}/>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
