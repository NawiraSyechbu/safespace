/* eslint-disable react-hooks/set-state-in-effect */
import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../AuthContext'
import { Alert, DeleteButton, moderationAlert } from '../components'
import { formatDate } from '../utils'

/* ---------- Tombol lapor ---------- */
function ReportButton({ contentType, contentId, navigate }) {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState('')
  const [msg, setMsg] = useState(null)

  async function submit(e) {
    e.preventDefault()
    try {
      await api.post('/reports', { content_type: contentType, content_id: contentId, reason })
      setMsg({ kind: 'ok', text: 'Laporan terkirim. Terima kasih.' })
      setOpen(false)
      setReason('')
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    }
  }

  if (msg?.kind === 'ok') return <span className="mini-note">{msg.text}</span>

  return (
    <span className="report-wrap">
      <button
        className="link-btn"
        onClick={() => (user ? setOpen(!open) : navigate('login'))}
      >
        Laporkan
      </button>
      {open && (
        <form className="inline-form" onSubmit={submit}>
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Alasan laporan..."
            required
            maxLength={1000}
          />
          <button className="button button-dark button-small" type="submit">Kirim</button>
        </form>
      )}
      <Alert kind={msg?.kind}>{msg?.text}</Alert>
    </span>
  )
}

/* ---------- Form komentar ---------- */
function CommentForm({ postId, parentId = null, onPosted, onCancel, navigate }) {
  const { user } = useAuth()
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState(null)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setMsg(null)
    try {
      const res = await api.post(`/posts/${postId}/comments`, {
        content: text,
        parent_comment_id: parentId,
      })
      const info = moderationAlert(res, 'Komentar')
      setMsg(info)
      if (res.moderation_status !== 'blocked') {
        setText('') // ditolak -> teks dipertahankan supaya bisa diedit
        onPosted?.()
      }
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    } finally {
      setBusy(false)
    }
  }

  if (!user) {
    return (
      <p className="forum-small">
        <button className="link-btn" onClick={() => navigate('login')}>Log in</button> untuk ikut berkomentar.
      </p>
    )
  }

  return (
    <form className="comment-form" onSubmit={submit}>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={parentId ? 2 : 3}
        placeholder={parentId ? 'Tulis balasan...' : 'Tulis komentar...'}
        required
        maxLength={2000}
      />
      <div className="forum-form-actions">
        <button className="button button-dark button-small" disabled={busy} type="submit">
          {busy ? 'Memeriksa dengan AI...' : parentId ? 'Balas' : 'Kirim komentar'}
        </button>
        {onCancel && (
          <button type="button" className="button button-outline button-small" onClick={onCancel}>
            Batal
          </button>
        )}
      </div>
      <Alert kind={msg?.kind}>{msg?.text}</Alert>
    </form>
  )
}

/* ---------- Satu komentar + balasannya ---------- */
function CommentNode({ comment, childrenMap, postId, reload, depth, navigate }) {
  const [replying, setReplying] = useState(false)
  const replies = childrenMap[comment.id] || []

  return (
    <div className={`comment ${depth > 0 ? 'comment-reply' : ''}`}>
      <p className="forum-author">
        <strong>@{comment.username}</strong> · {formatDate(comment.created_at)}
      </p>
      <p className="comment-body">{comment.content}</p>
      <div className="comment-actions">
        <button className="link-btn" onClick={() => setReplying(!replying)}>Balas</button>
        <ReportButton contentType="comment" contentId={comment.id} navigate={navigate} />
        <DeleteButton kind="comment" id={comment.id} ownerId={comment.user_id} onDeleted={reload} />
      </div>
      {replying && (
        <CommentForm
          postId={postId}
          parentId={comment.id}
          navigate={navigate}
          onPosted={() => { setReplying(false); reload() }}
          onCancel={() => setReplying(false)}
        />
      )}
      {replies.map((r) => (
        <CommentNode
          key={r.id}
          comment={r}
          childrenMap={childrenMap}
          postId={postId}
          reload={reload}
          depth={Math.min(depth + 1, 3)}
          navigate={navigate}
        />
      ))}
    </div>
  )
}

/* ---------- Detail postingan ---------- */
function PostDetail({ postId, onBack, navigate }) {
  const [post, setPost] = useState(null)
  const [comments, setComments] = useState([])
  const [error, setError] = useState('')

  const loadComments = useCallback(async () => {
    try {
      setComments(await api.get(`/posts/${postId}/comments`))
    } catch (err) {
      setError(err.message)
    }
  }, [postId])

  useEffect(() => {
    api.get(`/posts/${postId}`).then(setPost).catch((err) => setError(err.message))
    loadComments()
  }, [postId, loadComments])

  if (error) return <div className="forum-post"><Alert kind="error">{error}</Alert><button className="forum-back" onClick={onBack}>← Kembali</button></div>
  if (!post) return <div className="forum-post">Memuat...</div>

  const childrenMap = {}
  const roots = []
  comments.forEach((c) => {
    if (c.parent_comment_id) (childrenMap[c.parent_comment_id] ||= []).push(c)
    else roots.push(c)
  })

  return (
    <article className="forum-post">
      <button className="forum-back" onClick={onBack}>← Kembali ke feed</button>
      <span className="forum-tag">{post.community_name}</span>
      <h2>{post.title}</h2>
      <p className="forum-author">
        Oleh @{post.username} · {formatDate(post.created_at)}
      </p>
      <p className="post-body">{post.content}</p>
      <ReportButton contentType="post" contentId={post.id} navigate={navigate} />
      <DeleteButton kind="post" id={post.id} ownerId={post.user_id} onDeleted={onBack} />

      <div className="forum-comments">
        <h3>Komentar ({comments.length})</h3>
        <CommentForm postId={post.id} onPosted={loadComments} navigate={navigate} />
        {roots.length === 0 && <p className="forum-small">Belum ada komentar.</p>}
        {roots.map((c) => (
          <CommentNode
            key={c.id}
            comment={c}
            childrenMap={childrenMap}
            postId={post.id}
            reload={loadComments}
            depth={0}
            navigate={navigate}
          />
        ))}
      </div>
    </article>
  )
}

/* ---------- Form buat postingan ---------- */
function Compose({ communities, defaultCommunityId, onClose, onPublished }) {
  const [communityId, setCommunityId] = useState(defaultCommunityId || communities[0]?.id || '')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState(null)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setMsg(null)
    try {
      const res = await api.post('/posts', {
        community_id: Number(communityId || communities[0]?.id),
        title,
        content,
      })
      const info = moderationAlert(res, 'Postingan')
      if (res.moderation_status === 'blocked') {
        setMsg(info) // form tetap terbuka agar pengguna bisa mengedit
      } else {
        onPublished(info)
      }
    } catch (err) {
      setMsg({ kind: 'error', text: err.message })
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="forum-compose" onSubmit={submit}>
      <h2>Diskusi baru</h2>
      <label>
        Komunitas
        <select value={communityId} onChange={(e) => setCommunityId(e.target.value)}>
          {communities.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </label>
      <label>
        Judul
        <input value={title} onChange={(e) => setTitle(e.target.value)} required maxLength={200} />
      </label>
      <label>
        Isi postingan
        <textarea value={content} onChange={(e) => setContent(e.target.value)} required rows={6} maxLength={5000} />
      </label>
      <div className="forum-form-actions">
        <button type="button" className="button button-outline" onClick={onClose}>Batal</button>
        <button className="button button-dark" type="submit" disabled={busy}>
          {busy ? 'Memeriksa dengan AI...' : 'Terbitkan'}
        </button>
      </div>
      <Alert kind={msg?.kind}>{msg?.text}</Alert>
      <p className="forum-small">
        Setiap postingan diperiksa otomatis oleh model AI sebelum tampil di forum.
      </p>
    </form>
  )
}

/* ---------- Halaman forum ---------- */
export default function ForumPage({ navigate, initialCommunityId }) {
  const { user } = useAuth()
  const [communities, setCommunities] = useState([])
  const [joined, setJoined] = useState(new Set())
  const [communityId, setCommunityId] = useState(initialCommunityId ?? 'all')
  const [posts, setPosts] = useState([])
  const [search, setSearch] = useState('')
  const [creating, setCreating] = useState(false)
  const [selectedId, setSelectedId] = useState(null)
  const [notice, setNotice] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/communities').then(setCommunities).catch((e) => setNotice({ kind: 'error', text: e.message }))
  }, [])

  useEffect(() => {
    if (!user) return
    api.get('/me/communities').then((list) => setJoined(new Set(list.map((c) => c.id)))).catch(() => {})
  }, [user])

  const loadPosts = useCallback(async () => {
    setLoading(true)
    try {
      const q = communityId === 'all' ? '' : `?community_id=${communityId}`
      setPosts(await api.get(`/posts${q}`))
    } catch (err) {
      setNotice({ kind: 'error', text: err.message })
    } finally {
      setLoading(false)
    }
  }, [communityId])

  useEffect(() => { loadPosts() }, [loadPosts])

  async function join() {
    try {
      await api.post(`/communities/${communityId}/join`)
      setJoined(new Set([...joined, communityId]))
    } catch (err) {
      setNotice({ kind: 'error', text: err.message })
    }
  }

  const visible = posts.filter((p) =>
    `${p.title} ${p.content}`.toLowerCase().includes(search.toLowerCase()),
  )
  const activeCommunity = communities.find((c) => c.id === communityId)

  return (
    <main className="forum container">
      <div className="forum-heading">
        <div>
          <span className="section-kicker">COMMUNITY</span>
          <h1>Find your <em>conversation.</em></h1>
          <p>Jelajahi diskusi dan sampaikan pendapatmu. Setiap postingan dan komentar diperiksa AI sebelum terbit.</p>
        </div>
        <button
          className="button button-dark"
          onClick={() => {
            if (!user) return navigate('login')
            setCreating(true)
            setSelectedId(null)
          }}
        >
          Buat postingan +
        </button>
      </div>

      <div className="forum-layout">
        <aside className="forum-sidebar">
          <h2>Komunitas</h2>
          <button
            className={communityId === 'all' ? 'forum-filter active' : 'forum-filter'}
            onClick={() => { setCommunityId('all'); setSelectedId(null) }}
          >
            Semua
          </button>
          {communities.map((c) => (
            <button
              key={c.id}
              className={communityId === c.id ? 'forum-filter active' : 'forum-filter'}
              onClick={() => { setCommunityId(c.id); setSelectedId(null) }}
            >
              {c.name}
            </button>
          ))}
          {activeCommunity && (
            <>
              <p className="forum-small">{activeCommunity.description}</p>
              {user && !joined.has(activeCommunity.id) && (
                <button className="button button-outline button-small" onClick={join}>Gabung</button>
              )}
              {user && joined.has(activeCommunity.id) && <p className="forum-small">✓ Kamu sudah bergabung</p>}
            </>
          )}
        </aside>

        <section className="forum-main">
          {!selectedId && (
            <label className="forum-search">
              Cari diskusi
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Cari berdasarkan judul atau isi..." />
            </label>
          )}

          <Alert kind={notice?.kind}>{notice?.text}</Alert>

          {creating && (
            <Compose
              communities={communities}
              defaultCommunityId={typeof communityId === 'number' ? communityId : undefined}
              onClose={() => setCreating(false)}
              onPublished={(info) => { setCreating(false); setNotice(info); loadPosts() }}
            />
          )}

          {selectedId ? (
            <PostDetail postId={selectedId} onBack={() => { setSelectedId(null); loadPosts() }} navigate={navigate} />
          ) : loading ? (
            <div className="forum-post">Memuat diskusi...</div>
          ) : visible.length ? (
            visible.map((post) => (
              <article className="forum-post" key={post.id}>
                <span className="forum-tag">{post.community_name}</span>
                <p className="forum-author">
                  Oleh @{post.username} · {formatDate(post.created_at)} · {post.comment_count} komentar
                </p>
                <h2>{post.title}</h2>
                <p>{post.content.length > 240 ? `${post.content.slice(0, 240)}…` : post.content}</p>
                <button className="forum-read" onClick={() => { setSelectedId(post.id); setCreating(false) }}>
                  Baca diskusi →
                </button>
              </article>
            ))
          ) : (
            <div className="forum-post">Belum ada diskusi yang cocok. Jadilah yang pertama memulai!</div>
          )}
        </section>
      </div>
    </main>
  )
}
