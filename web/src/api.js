const BASE = '/api'

export async function checkHealth() {
  const res = await fetch('/health')
  return res.json()
}

export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || '上传失败')
  }
  return res.json()
}

export async function getDocuments() {
  const res = await fetch(`${BASE}/documents`)
  return res.json()
}

export async function deleteDocument(filename) {
  const res = await fetch(`${BASE}/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('删除失败')
  return res.json()
}

export async function getSessions() {
  const res = await fetch(`${BASE}/sessions`)
  return res.json()
}

export async function getSessionMessages(sessionId) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/messages`)
  return res.json()
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${BASE}/sessions/${sessionId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('删除失败')
  return res.json()
}

/**
 * 流式 Agent 对话，通过 SSE 逐 token 回调
 * @param {string} query
 * @param {string} sessionId
 * @param {(token: string) => void} onToken
 * @param {() => void} onDone
 */
export async function streamChat(query, sessionId, onToken, onDone) {
  const res = await fetch(`${BASE}/agent/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId }),
  })

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() // 保留不完整的行

    for (const line of lines) {
      if (line.startsWith('event: done')) {
        onDone?.()
        return
      }
      if (line.startsWith('data: ')) {
        const payload = line.slice(6)
        if (payload === '[DONE]') {
          onDone?.()
          return
        }
        try {
          const token = JSON.parse(payload)
          onToken?.(token)
        } catch {}
      }
    }
  }
  onDone?.()
}
