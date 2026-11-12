/* eslint-disable react-refresh/only-export-components */
import { api } from './api'
import { useAuth } from './AuthContext'
import { STATUS_LABEL } from './utils'

export function Alert({ kind = 'ok', children }) {
  if (!children) return null
  return <p className={`alert alert-${kind}`} role="status">{children}</p>
}

export function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{STATUS_LABEL[status] || status}</span>
}

// Hasil dari POST /posts atau /comments -> pesan untuk pengguna
export function moderationAlert(result, noun) {
  if (result.moderation_status === 'approved') {
    return { kind: 'ok', text: `${noun} berhasil diterbitkan.` }
  }
  if (result.moderation_status === 'blocked') {
    return {
      kind: 'error',
      text: `${noun} ditolak oleh sistem moderasi AI. ${result.reason || ''} Silakan ubah isinya, atau ajukan banding dari menu "Aktivitas saya".`,
    }
  }
  return {
    kind: 'warn',
    text: `${noun} ditahan dan menunggu peninjauan moderator. Statusnya bisa kamu lihat di "Aktivitas saya".`,
  }
}

export function DeleteButton({ kind, id, ownerId, onDeleted }) {
  const { user } = useAuth()
  const allowed =
    user && (user.id === ownerId || ['moderator', 'admin'].includes(user.role))
  if (!allowed) return null

  async function remove() {
    if (!window.confirm('Hapus permanen? Jika ini postingan, semua komentarnya ikut terhapus.')) return
    try {
      await api.delete(`/${kind}s/${id}`)
      onDeleted()
    } catch (err) {
      window.alert(err.message)
    }
  }

  return <button className="link-btn" onClick={remove}>Hapus</button>
}