import { useEffect, useState } from 'react'
import './App.css'
import { api } from './api'
import { useAuth } from './AuthContext'
import ForumPage from './pages/Forum'
import MyActivity from './pages/MyActivity'
import Moderation from './pages/Moderation'
import Admin from './pages/Admin'

const VIEWS = ['home', 'login', 'register', 'forum', 'activity', 'moderation', 'admin']
const CARD_COLORS = ['peach', 'lavender', 'sage']
const CARD_SYMBOLS = ['✳', '↗', '✦']

function viewFromHash() {
  const v = window.location.hash.replace('#/', '')
  return VIEWS.includes(v) ? v : 'home'
}

function App() {
  const { user, loading, login, register, logout } = useAuth()
  const [view, setView] = useState(viewFromHash)
  const [menuOpen, setMenuOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const [communities, setCommunities] = useState([])
  const [forumCommunity, setForumCommunity] = useState(undefined)

  useEffect(() => {
    const onHash = () => setView(viewFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    api.get('/communities').then(setCommunities).catch(() => {})
  }, [])

  function navigate(next, communityId) {
    setForumCommunity(communityId)
    setMessage('')
    setMenuOpen(false)
    if (window.location.hash === `#/${next}`) setView(next)
    else window.location.hash = `#/${next}`
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function handleAuth(event) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    setBusy(true)
    setMessage('')
    try {
      if (view === 'login') await login(data.get('email'), data.get('password'))
      else await register(data.get('username'), data.get('email'), data.get('password'))
      navigate('forum')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setBusy(false)
    }
  }

  // Halaman yang butuh login / role tertentu
  const protectedRoles = { activity: ['user', 'moderator', 'admin'], moderation: ['moderator', 'admin'], admin: ['admin'] }
  let current = view
  if (protectedRoles[view]) {
    if (loading) current = 'loading'
    else if (!user) current = 'login'
    else if (!protectedRoles[view].includes(user.role)) current = 'forbidden'
  }
  if ((view === 'login' || view === 'register') && user) current = 'forum'

  const cards = communities.slice(0, 3)

  return (
    <div className="site-shell">
      <header className="site-header container">
        <button className="wordmark" onClick={() => navigate('home')} aria-label="SafeSpace home"><span className="mark">✳</span> safespace<span className="wordmark-dot">.</span></button>
        <button className="mobile-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation" aria-expanded={menuOpen}>☰</button>
        <nav className={menuOpen ? 'nav-links open' : 'nav-links'} aria-label="Main navigation">
          <button onClick={() => navigate('home')}>Home</button>
          <button onClick={() => navigate('forum')}>Forum</button>
          {user && <button onClick={() => navigate('activity')}>Aktivitas saya</button>}
          {user && ['moderator', 'admin'].includes(user.role) && <button onClick={() => navigate('moderation')}>Moderasi</button>}
          {user?.role === 'admin' && <button onClick={() => navigate('admin')}>Admin</button>}
          <button onClick={() => { navigate('home'); setTimeout(() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }), 80) }}>About us</button>
        </nav>
        <div className="header-actions">
          {user ? (
            <>
              <span className="user-chip">@{user.username}{user.role !== 'user' ? ` · ${user.role}` : ''}</span>
              <button className="button button-dark button-small" onClick={() => { logout(); navigate('home') }}>Log out</button>
            </>
          ) : (
            <>
              <button className="text-button" onClick={() => navigate('login')}>Log in</button>
              <button className="button button-dark button-small" onClick={() => navigate('register')}>Get started <span>↗</span></button>
            </>
          )}
        </div>
      </header>

      {current === 'loading' ? <main className="container forum"><div className="forum-post">Memuat...</div></main>
        : current === 'forbidden' ? <main className="container forum"><div className="forum-post">Kamu tidak punya akses ke halaman ini.</div></main>
        : current === 'forum' ? <ForumPage key={String(forumCommunity)} navigate={navigate} initialCommunityId={forumCommunity} />
        : current === 'activity' ? <MyActivity />
        : current === 'moderation' ? <Moderation />
        : current === 'admin' ? <Admin />
        : current === 'home' ? <main>
        <section className="hero container">
          <div className="eyebrow"><span className="status-dot"/> YOUR SPACE TO BE YOURSELF</div>
          <h1>Good conversations<br/>start with <em>belonging.</em></h1>
          <p className="hero-subtitle">A thoughtful corner of the internet to share stories, find your people, and feel heard. Come as you are.</p>
          <div className="hero-actions"><button className="button button-dark" onClick={() => navigate(user ? 'forum' : 'register')}>Find your space <span>↗</span></button><button className="button button-outline" onClick={() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })}>Explore SafeSpace <span>↓</span></button></div>
          <div className="hero-art" aria-label="Illustration of community conversations">
            <div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/>
            <div className="floating-note note-left"><span className="note-icon">✺</span><span>little moments,<br/><strong>big connections.</strong></span></div>
            <div className="main-art-card"><div className="art-top"><span>THE COMMUNITY EDIT</span><span>VOL. 01 ↗</span></div><div className="art-center"><span className="art-asterisk">✳</span><div>Here, you<br/>belong<span className="art-period">.</span></div></div><div className="art-bottom"><span>OPEN MINDS. KIND WORDS.</span><span>© SAFESPACE</span></div></div>
            <div className="floating-note note-right"><span className="tiny-avatars"><i>☺</i><i>✿</i><i>☻</i></span><span>There's room<br/>for everyone.</span></div>
          </div>
          <div className="hero-caption"><span>✦ A MORE HUMAN KIND OF SOCIAL SPACE</span><span>SCROLL TO DISCOVER ↓</span></div>
        </section>
        <section className="about-section" id="about"><div className="container about-grid"><div><span className="section-kicker">01 / WHY WE'RE HERE</span><h2>A little more human.<br/><em>A lot more you.</em></h2></div><div className="about-copy"><p>We believe the best communities aren't built on being the loudest in the room. They're built on curiosity, kindness, and the freedom to be yourself.</p><p>SafeSpace brings people together around conversations that matter, with AI-assisted moderation designed to keep the space welcoming.</p><button className="inline-link" onClick={() => navigate(user ? 'forum' : 'register')}>Be part of the conversation <span>↗</span></button></div></div></section>
        <section className="community-section container" id="communities"><div className="section-heading"><div><span className="section-kicker">02 / FIND YOUR PEOPLE</span><h2>There's a conversation<br/>for <em>everyone.</em></h2></div><p>From everyday thoughts to big ideas, find a place where your voice fits right in.</p></div>
          <div className="discussion-grid">{cards.map((item, i) => <article className={`discussion-card ${CARD_COLORS[i % 3]}`} key={item.id}><div className="discussion-top"><span className="card-pill">{item.name}</span><span className="card-arrow">↗</span></div><div className="discussion-symbol">{CARD_SYMBOLS[i % 3]}</div><h3>{item.description || item.name}</h3><div className="discussion-footer"><span>Open community</span><button onClick={() => navigate('forum', item.id)}>Explore ↗</button></div></article>)}</div>
          <button className="button button-dark" style={{ marginTop: 30 }} onClick={() => navigate('forum')}>Open forum ↗</button></section>
        <section className="cta-section container"><div className="cta-inner"><span className="section-kicker">YOUR NEXT CHAPTER STARTS HERE</span><h2>Come for the conversation.<br/><em>Stay for the connection.</em></h2><button className="button button-light" onClick={() => navigate(user ? 'forum' : 'register')}>Join SafeSpace <span>↗</span></button><span className="cta-spark">✳</span></div></section>
      </main> : <main className="auth-section container"><div className="auth-intro"><span className="section-kicker">WELCOME TO SAFESPACE</span><h1>{view === 'login' ? <>Welcome <em>back.</em></> : <>Make yourself<br/><em>at home.</em></>}</h1><p>{view === 'login' ? 'Your conversations are waiting for you.' : 'Create an account to join thoughtful conversations and find your people.'}</p><div className="auth-decoration">✳</div></div><div className="auth-card"><span className="section-kicker">{view === 'login' ? 'LOG IN' : 'CREATE ACCOUNT'}</span><h2>{view === 'login' ? 'Good to see you again.' : 'Let’s get to know you.'}</h2><form onSubmit={handleAuth}>{view === 'register' && <label>Username<input name="username" placeholder="Your username" required minLength={3} maxLength={50} autoComplete="username"/></label>}<label>Email address<input type="email" name="email" placeholder="you@example.com" required autoComplete="email"/></label><label>Password<input type="password" name="password" placeholder="Minimal 8 karakter" required minLength={view === 'register' ? 8 : 1} autoComplete={view === 'login' ? 'current-password' : 'new-password'}/></label><button className="button button-dark auth-submit" type="submit" disabled={busy}>{busy ? 'Mohon tunggu...' : view === 'login' ? 'Log in' : 'Create account'} <span>↗</span></button></form>{message && <p className="form-message" role="alert">{message}</p>}<p className="switch-auth">{view === 'login' ? "Don't have an account?" : 'Already have an account?'} <button onClick={() => navigate(view === 'login' ? 'register' : 'login')}>{view === 'login' ? 'Sign up' : 'Log in'}</button></p></div></main>}

      <footer className="site-footer container"><button className="wordmark" onClick={() => navigate('home')}><span className="mark">✳</span> safespace<span className="wordmark-dot">.</span></button><span>Made for meaningful connections.</span><span>© 2026 SafeSpace</span></footer>
    </div>
  )
}

export default App
