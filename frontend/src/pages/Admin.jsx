/* eslint-disable react-hooks/set-state-in-effect */
import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../AuthContext'
import { Alert } from '../components'
import { formatDate } from '../utils'

function Stat({ label, value }) {
  return (
    <div className="stat-card">
      <span className="stat-value">{value ?? '-'}</span>
      <span className="stat-label">{label}</span>
    </div>
  )
}

function StatusLine({ title, counts = {} }) {
  return (
    <p className="forum-small">
      <strong>{title}:</strong> diterbitkan {counts.approved || 0} · ditolak {counts.blocked || 0} · menunggu {counts.pending_review || 0}
    </p>
  )
}

export default function Admin() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [msg, setMsg] = useState(null)

  const load = useCallback(async () => {
    try {
      const [s, u] = await Promise.all([api.get('/admin/stats'), api.get('/admin/users')])
      setStats(s)
      setUsers(u)
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function changeRole(id, role) {
    try {
      const res = await api.patch(`/admin/users/${id}/role`, { role })
      setMsg({ kind: 'ok', text: res.message })
      load()
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    }
  }

  return (
    <main className="forum container">
      <div className="forum-heading">
        <div>
          <span className="section-kicker">ADMIN</span>
          <h1>Dashboard <em>moderasi.</em></h1>
          <p>Ringkasan aktivitas forum, hasil moderasi AI, dan pengelolaan pengguna.</p>
        </div>
      </div>

      <Alert kind={msg?.kind}>{msg?.text}</Alert>

      {stats && (
        <>
          <div className="stat-grid">
            <Stat label="Pengguna" value={stats.total_users} />
            <Stat label="Postingan" value={stats.total_posts} />
            <Stat label="Komentar" value={stats.total_comments} />
            <Stat label="Prediksi AI tersimpan" value={stats.total_predictions} />
            <Stat label="Menunggu review" value={stats.pending_posts + stats.pending_comments} />
            <Stat label="Laporan terbuka" value={stats.open_reports} />
            <Stat label="Banding terbuka" value={stats.open_appeals} />
            <Stat label="Total laporan" value={stats.total_reports} />
          </div>
          <div className="forum-post">
            <StatusLine title="Postingan" counts={stats.posts_by_status} />
            <StatusLine title="Komentar" counts={stats.comments_by_status} />
          </div>
        </>
      )}

      <div className="forum-post table-wrap">
        <h2>Pengguna</h2>
        <table className="table">
          <thead>
            <tr><th>Username</th><th>Email</th><th>Bergabung</th><th>Role</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.email}</td>
                <td>{formatDate(u.created_at)}</td>
                <td>
                  <select
                    value={u.role}
                    disabled={u.id === user.id}
                    onChange={(e) => changeRole(u.id, e.target.value)}
                  >
                    <option value="user">user</option>
                    <option value="moderator">moderator</option>
                    <option value="admin">admin</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  )
}
