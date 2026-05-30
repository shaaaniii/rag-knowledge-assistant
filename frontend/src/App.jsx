import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_URL    = 'http://localhost:8000'
const SESSION_ID = 'session_' + Math.random().toString(36).substr(2, 9)

export default function App() {
  const [messages, setMessages]         = useState([])
  const [input, setInput]               = useState('')
  const [loading, setLoading]           = useState(false)
  const [uploading, setUploading]       = useState(false)
  const [uploadMsg, setUploadMsg]       = useState('')
  const [documents, setDocuments]       = useState([])
  const [selectedDocs, setSelectedDocs] = useState([])
  const [sidebarOpen, setSidebarOpen]   = useState(true)
  const [chatStarted, setChatStarted]   = useState(false)
  const bottomRef                       = useRef(null)
  const fileRef                         = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => { fetchDocuments() }, [])

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${API_URL}/upload-doc/list`)
      setDocuments(res.data.documents)
    } catch (e) {}
  }

  const toggleDocSelection = (filename) => {
    setSelectedDocs(prev =>
      prev.includes(filename)
        ? prev.filter(d => d !== filename)
        : [...prev, filename]
    )
  }

  const selectAllDocs = () => setSelectedDocs([])
  const isAllSelected = selectedDocs.length === 0

  const deleteDocument = async (filename, e) => {
    e.stopPropagation()
    if (!window.confirm(`Delete "${filename}"? This cannot be undone.`)) return

    try {
      await axios.delete(`${API_URL}/upload-doc/${encodeURIComponent(filename)}`)
      setDocuments(prev => prev.filter(d => d.filename !== filename))
      setSelectedDocs(prev => prev.filter(d => d !== filename))
      setUploadMsg(`✅ "${filename}" deleted`)
      setTimeout(() => setUploadMsg(''), 3000)
    } catch (err) {
      setUploadMsg(`❌ Delete failed`)
      setTimeout(() => setUploadMsg(''), 3000)
    }
  }

  const sendMessageWithText = async (text) => {
    if (!text.trim() || loading) return

    setInput('')
    setChatStarted(true)
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    try {
      const res = await axios.post(`${API_URL}/ask/`, {
        query:              text,
        session_id:         SESSION_ID,
        role:               'employee',
        k:                  5,
        selected_documents: selectedDocs.length > 0 ? selectedDocs : null
      })

      setMessages(prev => [...prev, {
        role:       'assistant',
        content:    res.data.answer,
        sources:    res.data.sources,
        confidence: res.data.confidence
      }])
    } catch (err) {
      const detail = err.response?.data?.detail || 'Something went wrong.'
      setMessages(prev => [...prev, {
        role: 'assistant', content: `Error: ${detail}`, error: true
      }])
    }

    setLoading(false)
  }

  const sendMessage = () => sendMessageWithText(input.trim())

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setUploadMsg(`Uploading ${file.name}...`)

    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post(`${API_URL}/upload-doc/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadMsg(`✅ ${file.name} uploaded!`)
      setTimeout(async () => {
        setUploadMsg('')
        await fetchDocuments()
      }, 4000)
    } catch (err) {
      setUploadMsg(`❌ ${err.response?.data?.detail || 'Upload failed'}`)
      setTimeout(() => setUploadMsg(''), 4000)
    }

    setUploading(false)
    fileRef.current.value = ''
  }

  const clearChat = () => setMessages([]) && setChatStarted(false)

  const newChat = () => {
    setMessages([])
    setChatStarted(false)
  }

  const suggestions = [
    'Give me a professional summary of this document',
    'What are the key points and main findings?',
    'What action items or decisions are mentioned?',
    'Explain the most important section in detail',
  ]

  // Format message with bullet points rendered properly
  const formatMessage = (text) => {
    return text.split('\n').map((line, i) => {
      if (line.startsWith('**') && line.endsWith('**')) {
        return <div key={i} className="msg-heading">{line.replace(/\*\*/g, '')}</div>
      }
      if (line.match(/^\*\*.*\*\*/)) {
        const formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        return <div key={i} dangerouslySetInnerHTML={{ __html: formatted }} />
      }
      if (line.startsWith('• ') || line.startsWith('- ')) {
        return <div key={i} className="msg-bullet">• {line.slice(2)}</div>
      }
      if (line.trim() === '') return <div key={i} className="msg-spacer" />
      return <div key={i}>{line}</div>
    })
  }

  return (
    <div className={`app ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>

      {/* ── SIDEBAR ─────────────────────────────── */}
      <div className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <span className="brand-icon">⚡</span>
            <span className="brand-name">KnowledgeAI</span>
          </div>
        </div>

        {/* New Chat */}
        <button className="new-chat-btn" onClick={newChat}>
          + New Chat
        </button>

        {/* Upload */}
        <div className="sidebar-section-label">Upload Document</div>
        <button
          className="upload-btn"
          onClick={() => fileRef.current.click()}
          disabled={uploading}
        >
          {uploading ? '⏳ Uploading...' : '📎 Upload File'}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleUpload}
          style={{ display: 'none' }}
        />
        {uploadMsg && <div className="upload-msg">{uploadMsg}</div>}

        {/* Document list with multi-select + delete */}
        <div className="sidebar-section-label">Select Documents</div>
        <div className="doc-list">

          {/* All documents toggle */}
          <div
            className={`doc-item ${isAllSelected ? 'doc-selected' : ''}`}
            onClick={selectAllDocs}
          >
            <div className="doc-checkbox">
              {isAllSelected ? '☑' : '☐'}
            </div>
            <div className="doc-info">
              <div className="doc-name">🌐 All Documents</div>
              <div className="doc-meta">Search everything</div>
            </div>
          </div>

          {documents.length === 0
            ? <div className="doc-empty">No documents yet</div>
            : documents.map((doc, i) => (
              <div
                key={i}
                className={`doc-item ${selectedDocs.includes(doc.filename) ? 'doc-selected' : ''}`}
                onClick={() => toggleDocSelection(doc.filename)}
              >
                <div className="doc-checkbox">
                  {selectedDocs.includes(doc.filename) ? '☑' : '☐'}
                </div>
                <div className="doc-info">
                  <div className="doc-name">📄 {doc.filename}</div>
                  <div className="doc-meta">{doc.num_chunks} chunks</div>
                </div>
                <button
                  className="doc-delete"
                  onClick={(e) => deleteDocument(doc.filename, e)}
                  title="Delete document"
                >
                  🗑
                </button>
              </div>
            ))
          }
        </div>

        <div className="sidebar-footer">
          <div className="session-label">
            Session: {SESSION_ID.slice(-6)}
          </div>
        </div>
      </div>

      {/* ── MAIN AREA ────────────────────────────── */}
      <div className="main">

        {/* Top bar */}
        <div className="topbar">
          <button
            className="hamburger"
            onClick={() => setSidebarOpen(p => !p)}
          >
            ☰
          </button>
          <div className="topbar-title">Enterprise Knowledge Assistant</div>
          <div className="topbar-doc">
            {selectedDocs.length > 0
              ? `📄 ${selectedDocs.length} doc${selectedDocs.length > 1 ? 's' : ''} selected`
              : '🌐 All Documents'}
          </div>
        </div>

        {/* Chat area */}
        <div className="chat-area">

          {/* Welcome screen */}
          {!chatStarted && (
            <div className="welcome">
              <div className="welcome-greeting">Hi 👋</div>
              <div className="welcome-title">
                I am your Personal Knowledge Assistant
              </div>
              <div className="welcome-sub">How can I help you?</div>

              {documents.length > 0 && (
                <div className="suggestions">
                  {suggestions.map((s, i) => (
                    <button
                      key={i}
                      className="suggestion"
                      onClick={() => sendMessageWithText(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}

              {documents.length === 0 && (
                <div className="welcome-hint">
                  Upload a document from the sidebar to get started
                </div>
              )}
            </div>
          )}

          {/* Messages */}
          {chatStarted && (
            <div className="messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <div className="msg-avatar">
                    {msg.role === 'user' ? '👤' : '⚡'}
                  </div>
                  <div className="msg-body">
                    <div className={`bubble ${msg.role} ${msg.error ? 'error' : ''}`}>
                      {formatMessage(msg.content)}
                    </div>

                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources">
                        📎&nbsp;
                        {msg.sources.map((s, j) => (
                          <span key={j} className="source-tag">
                            {s.source} p.{s.page}
                          </span>
                        ))}
                        <span className={`confidence ${msg.confidence}`}>
                          {msg.confidence}
                        </span>
                      </div>
                    )}

                    {msg.role === 'assistant' && !msg.error && (
                      <div className="feedback">
                        {msg.feedback ? (
                          <span className="feedback-done">
                            {msg.feedback === 'helpful' ? '👍 Thanks!' : '👎 Noted'}
                          </span>
                        ) : (
                          <>
                            <span className="feedback-label">Helpful?</span>
                            <button className="fb-btn"
                              onClick={async () => {
                                await axios.post(`${API_URL}/feedback/`, {
                                  session_id: SESSION_ID,
                                  message_index: i,
                                  rating: 'helpful',
                                  comment: null
                                })
                                setMessages(prev => prev.map((m, idx) =>
                                  idx === i ? { ...m, feedback: 'helpful' } : m
                                ))
                              }}>👍</button>
                            <button className="fb-btn"
                              onClick={async () => {
                                await axios.post(`${API_URL}/feedback/`, {
                                  session_id: SESSION_ID,
                                  message_index: i,
                                  rating: 'not_helpful',
                                  comment: null
                                })
                                setMessages(prev => prev.map((m, idx) =>
                                  idx === i ? { ...m, feedback: 'not_helpful' } : m
                                ))
                              }}>👎</button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message assistant">
                  <div className="msg-avatar">⚡</div>
                  <div className="msg-body">
                    <div className="bubble assistant loading">
                      <span className="dot" />
                      <span className="dot" />
                      <span className="dot" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-box">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask your knowledge assistant..."
              rows={1}
              className="input"
            />
            <button
              className={`send-btn ${loading ? 'disabled' : ''}`}
              onClick={sendMessage}
              disabled={loading}
            >
              {loading ? '⏳' : '➤'}
            </button>
          </div>
          <div className="input-hint">
            {selectedDocs.length > 0
              ? `Searching: ${selectedDocs.join(', ')}`
              : 'Searching all documents'} · Enter to send
          </div>
        </div>
      </div>
    </div>
  )
}