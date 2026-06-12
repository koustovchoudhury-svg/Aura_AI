import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: API_URL })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('aura_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

export const knowledgeAPI = {
  query:     (query: string, top_k = 5) => api.post('/api/knowledge/query', { query, top_k }),
  documents: ()                          => api.get('/api/knowledge/documents'),
  delete:    (id: string)                => api.delete(`/api/knowledge/documents/${id}`),
}

export const meetingsAPI = {
  list:   ()                  => api.get('/api/meetings/'),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/meetings/upload', form)
  }
}

export const agentsAPI = {
  list:   () => api.get('/api/agents/'),
  health: () => api.get('/api/agents/health'),
}
