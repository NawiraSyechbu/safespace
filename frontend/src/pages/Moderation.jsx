/* eslint-disable react-hooks/set-state-in-effect */
import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { Alert } from '../components'
import { formatDate } from '../utils'

function AiBox({ ai, reason }) {
  return (
    <div className="reason-box">
      {reason && <p><strong>Keputusan sistem:</strong> {reason}</p>}
      {ai?.length > 0 && (
        <ul className="ai-list">
          {ai.map((a) => (
            <li key={a.task}>
              <strong>{a.task}</strong>: {a.labels.length ? a.labels.join(', ') : '— (tidak ada label)'}
              <span className="mini-note"> {Object.entries(a.scores).map(([k, v]) => `${k} ${v}`).join(' · ')}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function Pending({ items, onAct }) {
  const [notes, setNotes] = useState({})
  if (!items.length) return <div className="forum-post">Tidak ada konten yang menunggu peninjauan. 🎉</div>

  return items.map((item) => {
    const key = `${item.type}-${item.id}`
    const decide = (status) =>
      onAct(() => api.post('/moderation/review', {
        content_type: item.type, content_id: item.id, new_status: status, notes: notes[key] || null,
      }))
    return (
      <article className="forum-post" key={key}>
        <span className="forum-tag">{item.type === 'post' ? 'Postingan' : 'Komentar'}</span>
        <p className="forum-author">@{item.username} · {formatDate(item.created_at)}</p>
        {item.title && <h2>{item.title}</h2>}
        <p className="post-body">{item.content}</p>
        <AiBox ai={item.ai} reason={item.reason} />
        <input
          className="note-input"
          placeholder="Catatan moderator (opsional)"
          value={notes[key] || ''}
          onChange={(e) => setNotes({ ...notes, [key]: e.target.value })}
        />
        <div className="forum-form-actions">
          <button className="button button-dark button-small" onClick={() => decide('approved')}>Setujui</button>
          <button className="button button-outline button-small" onClick={() => decide('blocked')}>Blokir</button>
        </div>
      </article>
    )
  })
}

function Reports({ items, onAct }) {
  if (!items.length) return <div className="forum-post">Tidak ada laporan terbuka.</div>

  return items.map((r) => (
    <article className="forum-post" key={r.id}>
      <span className="forum-tag">Laporan #{r.id}</span>
      <p className="forum-author">Dilaporkan oleh @{r.reporter} · {formatDate(r.created_at)}</p>
      <p><strong>Alasan:</strong> {r.reason}</p>
      {r.target ? (
        <div className="reason-box">
          <p className="forum-author">{r.content_type === 'post' ? 'Postingan' : 'Komentar'} (status: {r.target.status})</p>
          {r.target.title && <strong>{r.target.title}</strong>}
          <p className="post-body">{r.target.content}</p>
        </div>
      ) : <p className="mini-note">Konten sudah tidak tersedia.</p>}
      <div className="forum-form-actions">
        <button className="button button-outline button-small"
          onClick={() => onAct(() => api.post(`/moderation/reports/${r.id}/resolve`, { action: 'dismiss' }))}>
          Abaikan laporan
        </button>
        <button className="button button-dark button-small"
          onClick={() => onAct(() => api.post(`/moderation/reports/${r.id}/resolve`, { action: 'block' }))}>
          Blokir konten
        </button>
      </div>
    </article>
  ))
}

function Appeals({ items, onAct }) {
  if (!items.length) return <div className="forum-post">Tidak ada banding yang menunggu.</div>

  return items.map((a) => (
    <article className="forum-post" key={a.id}>
      <span className="forum-tag">Banding #{a.id}</span>
      <p className="forum-author">Diajukan @{a.username} · {formatDate(a.created_at)}</p>
      <p><strong>Alasan banding:</strong> {a.reason}</p>
      {a.target && (
        <div className="reason-box">
          {a.target.title && <strong>{a.target.title}</strong>}
          <p className="post-body">{a.target.content}</p>
        </div>
      )}
      <AiBox ai={a.ai} reason={a.ai_reason} />
      <div className="forum-form-actions">
        <button className="button button-dark button-small"
          onClick={() => onAct(() => api.post(`/moderation/appeals/${a.id}/review`, { decision: 'accepted' }))}>
          Terima banding (terbitkan)
        </button>
        <button className="button button-outline button-small"
          onClick={() => onAct(() => api.post(`/moderation/appeals/${a.id}/review`, { decision: 'rejected' }))}>
          Tolak banding
        </button>
      </div>
    </article>
  ))
}

const TABS = [
  ['pending', 'Antrean review', '/moderation/pending'],
  ['reports', 'Laporan', '/moderation/reports'],
  ['appeals', 'Banding', '/moderation/appeals'],
]

export default function Moderation() {
  const [tab, setTab] = useState('pending')
  const [data, setData] = useState({})
  const [msg, setMsg] = useState(null)

  const load = useCallback(async () => {
    try {
      const entries = await Promise.all(TABS.map(async ([key, , path]) => [key, await api.get(path)]))
      setData(Object.fromEntries(entries))
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function act(fn) {
    try {
      const res = await fn()
      setMsg({ kind: 'ok', text: res.message || 'Berhasil.' })
      load()
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    }
  }

  return (
    <main className="forum container">
      <div className="forum-heading">
        <div>
          <span className="section-kicker">MODERASI</span>
          <h1>Ruang <em>moderator.</em></h1>
          <p>Tinjau konten yang ragu-ragu diputuskan AI, laporan pengguna, dan permohonan banding.</p>
        </div>
      </div>

      <div className="tabs">
        {TABS.map(([key, label]) => (
          <button key={key} className={tab === key ? 'tab active' : 'tab'} onClick={() => setTab(key)}>
            {label} {data[key] ? `(${data[key].length})` : ''}
          </button>
        ))}
      </div>

      <Alert kind={msg?.kind}>{msg?.text}</Alert>

      <div className="stack">
        {tab === 'pending' && <Pending items={data.pending || []} onAct={act} />}
        {tab === 'reports' && <Reports items={data.reports || []} onAct={act} />}
        {tab === 'appeals' && <Appeals items={data.appeals || []} onAct={act} />}
      </div>
    </main>
  )
}
