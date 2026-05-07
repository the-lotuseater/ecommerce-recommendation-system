import { useState, useRef, useEffect } from 'react'
import './App.css'

const SUGGESTIONS = [
  'Best gaming headset under $50?',
  'Top rated PS5 games?',
  'Most durable Xbox controller?',
  'Good open world games?',
]

function Message({ role, text }) {
  return (
    <div className={`message ${role}`}>
      {role === 'assistant' && <div className="avatar">S</div>}
      <div className="content">{text}</div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (text) => {
    if (!text.trim() || loading) return
    setMessages(prev => [...prev, { role: 'user', text }])
    setInput('')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('msg', text)
      const res = await fetch('/chat', { method: 'POST', body: fd })
      const reply = await res.text()
      setMessages(prev => [...prev, { role: 'assistant', text: reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) }
  }

  const empty = messages.length === 0

  return (
    <div className="app">
      <main className="main">
        {empty ? (
          <div className="landing">
            <h1>What can I help with?</h1>
            <div className="input-box">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything"
                rows={1}
                autoFocus
              />
              <button onClick={() => send(input)} disabled={!input.trim()} className="send">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
              </button>
            </div>
            <div className="chips">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="chip" onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        ) : (
          <>
            <div className="thread">
              {messages.map((m, i) => <Message key={i} {...m} />)}
              {loading && (
                <div className="message assistant">
                  <div className="avatar">S</div>
                  <div className="content thinking"><span /><span /><span /></div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
            <div className="bottom-bar">
              <div className="input-box">
                <textarea
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask anything"
                  rows={1}
                  disabled={loading}
                  autoFocus
                />
                <button onClick={() => send(input)} disabled={!input.trim() || loading} className="send">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
              </div>
              <p className="disclaimer">Made with RAG & LLM by Abhishek Birhade</p>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
