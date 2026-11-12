import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { Alert, DeleteButton, StatusBadge } from '../components'
import { APPEAL_LABEL, formatDate } from '../utils'
import { useAuth } from '../AuthContext'

function AppealForm({ item, onDone }) {
  const [reason, setReason] = useState('')
  const [msg, setMsg] = useState(null)

  async function submit(e) {
    e.preventDefault()
    try {
      await api.post('/appeals', {
        content_type: item.content_type,
        content_id: item.content_id,
        reason,
      })
      onDone()
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    }
  }

  return (
    <form className="inline-form" onSubmit={submit}>
      <input
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="Jelaskan mengapa menurutmu konten ini tidak melanggar..."
        required
        maxLength={1000}
      />
      <button className="button button-dark button-small" type="submit">Ajukan banding</button>
      <Alert kind={msg?.kind}>{msg?.text}</Alert>
    </form>
  )
}

export default function MyActivity() {
  const { user } = useAuth()
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    api.get('/me/content').then(setItems).catch((e) => setError(e.message))
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <main className="forum container">
      <div className="forum-heading">
        <div>
          <span className="section-kicker">AKTIVITAS SAYA</span>
          <h1>Riwayat <em>kontenmu.</em></h1>
          <p>Lihat status moderasi setiap postingan dan komentarmu. Konten yang ditolak AI bisa diajukan banding ke moderator.</p>
        </div>
      </div>

      <Alert kind="error">{error}</Alert>
      {!items && !error && <div className="forum-post">Memuat...</div>}
      {items?.length === 0 && <div className="forum-post">Kamu belum membuat postingan atau komentar.</div>}

      <div className="stack">
        {items?.map((item) => (
          <article className="forum-post" key={`${item.content_type}-${item.content_id}`}>
            <div className="row-between">
              <span className="forum-tag">{item.content_type === 'post' ? 'Postingan' : 'Komentar'}</span>
              <StatusBadge status={item.status} />
            </div>
            {item.title && <h2>{item.title}</h2>}
            <p className="post-body">{item.content}</p>
            <p className="forum-author">{formatDate(item.created_at)}</p>

            {item.reason && item.status !== 'approved' && (
              <p className="reason-box"><strong>Alasan sistem:</strong> {item.reason}</p>
            )}

            {item.ai && item.status !== 'approved' && (
              <div className="reason-box">
                <p><strong>Skor deteksi AI</strong></p>
                {Object.entries(item.ai.scores).map(([label, score]) => {
                  const limit = item.ai.thresholds?.[label]
                  const flagged = limit !== undefined && score >= limit
                  return (
                    <p key={label}>
                      {label === 'HS' ? 'Hate speech' : label}:{' '}
                      <strong>{(score * 100).toFixed(1)}%</strong>
                      {limit !== undefined && (
                        <span className="mini-note"> (batas deteksi {(limit * 100).toFixed(0)}%)</span>
                      )}
                      {flagged && ' ⚠ terdeteksi'}
                    </p>
                  )
                })}
              </div>
            )}

            {item.appeal_status && <p className="mini-note">{APPEAL_LABEL[item.appeal_status]}</p>}

            {item.status === 'blocked' && !item.appeal_status && (
              <AppealForm item={item} onDone={load} />
            )}
            
            <DeleteButton kind={item.content_type} id={item.content_id} ownerId={user.id} onDeleted={load} />

          </article>
        ))}
      </div>
    </main>
  )
}
