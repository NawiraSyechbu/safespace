import { useState } from 'react'
import './App.css'

const discussions = [
  { tag: 'Everyday life', title: 'What is something small that made your week better?', replies: '24 conversations', color: 'peach', symbol: '✳' },
  { tag: 'Personal growth', title: 'Learning to take things one step at a time.', replies: '18 conversations', color: 'lavender', symbol: '↗' },
  { tag: 'Creative corner', title: 'Share something you made just for yourself.', replies: '32 conversations', color: 'sage', symbol: '✦' },
]


const starterPosts = [
  { id: 1, community: 'Everyday life', author: 'community_member', title: 'What is one small thing that made your week better?', body: 'A space to share the little moments that matter.', replies: 12 },
  { id: 2, community: 'Personal growth', author: 'another_member', title: 'How do you stay motivated when learning something new?', body: 'I would love to hear different approaches.', replies: 8 },
  { id: 3, community: 'Creative corner', author: 'creative_member', title: 'What are you working on lately?', body: 'Share your ideas, sketches, projects, or anything you are learning.', replies: 5 },
]

function ForumPreview() {
  const [posts, setPosts] = useState(starterPosts)
  const [community, setCommunity] = useState('All')
  const [search, setSearch] = useState('')
  const [creating, setCreating] = useState(false)
  const [selected, setSelected] = useState(null)
  const [notice, setNotice] = useState('')
  const communities = ['All', 'Everyday life', 'Personal growth', 'Creative corner']
  const visible = posts.filter(p => (community === 'All' || p.community === community) && `${p.title} ${p.body}`.toLowerCase().includes(search.toLowerCase()))
  function addPost(event) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const title = String(data.get('title') || '').trim()
    const body = String(data.get('body') || '').trim()
    if (!title || !body) return
    setPosts(current => [{ id: Date.now(), community: String(data.get('community')), author: 'you (demo)', title, body, replies: 0 }, ...current])
    setCreating(false)
    setCommunity('All')
    setNotice('Demo post added locally. It was NOT checked by AI or saved to the backend.')
  }
  return <main className="forum container">
    <div className="forum-heading"><div><span className="section-kicker">COMMUNITY / FRONTEND DEMO</span><h1>Find your <em>conversation.</em></h1><p>Explore discussions and share your thoughts. This preview uses sample data only.</p></div><button className="button button-dark" onClick={() => {setCreating(true);setSelected(null)}}>Create post +</button></div>
    <div className="forum-layout"><aside className="forum-sidebar"><h2>Communities</h2>{communities.map(c => <button key={c} className={community === c ? 'forum-filter active' : 'forum-filter'} onClick={() => {setCommunity(c);setSelected(null)}}>{c}</button>)}<p className="forum-small">Real communities and membership will be loaded from the Python backend later.</p></aside>
    <section className="forum-main"><label className="forum-search">Search discussions<input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by title or content..." /></label>{notice && <p className="forum-notice" role="status">{notice}</p>}
      {creating && <form className="forum-compose" onSubmit={addPost}><h2>New discussion</h2><label>Community<select name="community">{communities.filter(c => c !== 'All').map(c => <option key={c}>{c}</option>)}</select></label><label>Title<input name="title" required maxLength={120} /></label><label>Your post<textarea name="body" required rows={5} /></label><div className="forum-form-actions"><button type="button" className="button button-outline" onClick={() => setCreating(false)}>Cancel</button><button className="button button-dark" type="submit">Add demo post</button></div><p className="forum-small">This is a UI-only demo. No AI moderation or server submission occurs.</p></form>}
      {selected ? <article className="forum-post"><button className="forum-back" onClick={() => setSelected(null)}>← Back to feed</button><span className="forum-tag">{selected.community}</span><h2>{selected.title}</h2><p className="forum-author">Posted by {selected.author}</p><p>{selected.body}</p><div className="forum-comments"><h3>Comments</h3><p>Comment threads will appear here after we connect the backend. No sample comments are presented as real users.</p></div></article> : visible.length ? visible.map(post => <article className="forum-post" key={post.id}><span className="forum-tag">{post.community}</span><p className="forum-author">Posted by {post.author} · Sample content</p><h2>{post.title}</h2><p>{post.body}</p><button className="forum-read" onClick={() => setSelected(post)}>Read discussion →</button></article>) : <div className="forum-post">No discussions match your search.</div>}
    </section></div>
  </main>
}

function App() {
  const [view, setView] = useState('home')
  const [menuOpen, setMenuOpen] = useState(false)
  const [message, setMessage] = useState('')

  function navigate(next) {
    setView(next)
    setMessage('')
    setMenuOpen(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function handleAuth(event) {
    event.preventDefault()
    setMessage('This is a frontend preview. Login and registration will work after we connect the Python API.')
  }

  return (
    <div className="site-shell">
      <header className="site-header container">
        <button className="wordmark" onClick={() => navigate('home')} aria-label="SafeSpace home"><span className="mark">✳</span> safespace<span className="wordmark-dot">.</span></button>
        <button className="mobile-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation" aria-expanded={menuOpen}>☰</button>
        <nav className={menuOpen ? 'nav-links open' : 'nav-links'} aria-label="Main navigation">
          <button onClick={() => navigate('home')}>Home</button><button onClick={() => navigate('forum')}>Forum demo</button>
          <button onClick={() => { navigate('home'); setTimeout(() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }), 50) }}>About us</button>
          <button onClick={() => { navigate('home'); setTimeout(() => document.getElementById('communities')?.scrollIntoView({ behavior: 'smooth' }), 50) }}>Communities</button>
        </nav>
        <div className="header-actions"><button className="text-button" onClick={() => navigate('login')}>Log in</button><button className="button button-dark button-small" onClick={() => navigate('register')}>Get started <span>↗</span></button></div>
      </header>

      {view === 'forum' ? <ForumPreview /> : view === 'home' ? <main>
        <section className="hero container">
          <div className="eyebrow"><span className="status-dot"/> YOUR SPACE TO BE YOURSELF</div>
          <h1>Good conversations<br/>start with <em>belonging.</em></h1>
          <p className="hero-subtitle">A thoughtful corner of the internet to share stories, find your people, and feel heard. Come as you are.</p>
          <div className="hero-actions"><button className="button button-dark" onClick={() => navigate('register')}>Find your space <span>↗</span></button><button className="button button-outline" onClick={() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })}>Explore SafeSpace <span>↓</span></button></div>
          <div className="hero-art" aria-label="Illustration of community conversations">
            <div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/>
            <div className="floating-note note-left"><span className="note-icon">✺</span><span>little moments,<br/><strong>big connections.</strong></span></div>
            <div className="main-art-card"><div className="art-top"><span>THE COMMUNITY EDIT</span><span>VOL. 01 ↗</span></div><div className="art-center"><span className="art-asterisk">✳</span><div>Here, you<br/>belong<span className="art-period">.</span></div></div><div className="art-bottom"><span>OPEN MINDS. KIND WORDS.</span><span>© SAFESPACE</span></div></div>
            <div className="floating-note note-right"><span className="tiny-avatars"><i>☺</i><i>✿</i><i>☻</i></span><span>There's room<br/>for everyone.</span></div>
          </div>
          <div className="hero-caption"><span>✦ A MORE HUMAN KIND OF SOCIAL SPACE</span><span>SCROLL TO DISCOVER ↓</span></div>
        </section>
        <section className="about-section" id="about"><div className="container about-grid"><div><span className="section-kicker">01 / WHY WE'RE HERE</span><h2>A little more human.<br/><em>A lot more you.</em></h2></div><div className="about-copy"><p>We believe the best communities aren't built on being the loudest in the room. They're built on curiosity, kindness, and the freedom to be yourself.</p><p>SafeSpace brings people together around conversations that matter, with thoughtful moderation designed to keep the space welcoming.</p><button className="inline-link" onClick={() => navigate('register')}>Be part of the conversation <span>↗</span></button></div></div></section>
        <section className="community-section container" id="communities"><div className="section-heading"><div><span className="section-kicker">02 / FIND YOUR PEOPLE</span><h2>There's a conversation<br/>for <em>everyone.</em></h2></div><p>From everyday thoughts to big ideas, find a place where your voice fits right in.</p></div><div className="discussion-grid">{discussions.map((item) => <article className={`discussion-card ${item.color}`} key={item.tag}><div className="discussion-top"><span className="card-pill">{item.tag}</span><span className="card-arrow">↗</span></div><div className="discussion-symbol">{item.symbol}</div><h3>{item.title}</h3><div className="discussion-footer"><span>{item.replies}</span><button onClick={() => navigate('register')}>Explore ↗</button></div></article>)}</div><p className="sample-note">Illustrative community previews — real communities will appear when the backend is connected.</p><button className="button button-dark" onClick={() => navigate('forum')}>Open forum demo ↗</button></section>
        <section className="cta-section container"><div className="cta-inner"><span className="section-kicker">YOUR NEXT CHAPTER STARTS HERE</span><h2>Come for the conversation.<br/><em>Stay for the connection.</em></h2><button className="button button-light" onClick={() => navigate('register')}>Join SafeSpace <span>↗</span></button><span className="cta-spark">✳</span></div></section>
      </main> : <main className="auth-section container"><div className="auth-intro"><span className="section-kicker">WELCOME TO SAFESPACE</span><h1>{view === 'login' ? <>Welcome <em>back.</em></> : <>Make yourself<br/><em>at home.</em></>}</h1><p>{view === 'login' ? 'Your conversations are waiting for you.' : 'Create an account to join thoughtful conversations and find your people.'}</p><div className="auth-decoration">✳</div></div><div className="auth-card"><span className="section-kicker">{view === 'login' ? 'LOG IN' : 'CREATE ACCOUNT'}</span><h2>{view === 'login' ? 'Good to see you again.' : 'Let’s get to know you.'}</h2><form onSubmit={handleAuth}>{view === 'register' && <label>Username<input name="username" placeholder="Your username" required autoComplete="username"/></label>}<label>Email address<input type="email" name="email" placeholder="you@example.com" required autoComplete="email"/></label><label>Password<input type="password" name="password" placeholder="Enter your password" required minLength={6} autoComplete={view === 'login' ? 'current-password' : 'new-password'}/></label><button className="button button-dark auth-submit" type="submit">{view === 'login' ? 'Log in' : 'Create account'} <span>↗</span></button></form>{message && <p className="form-message" role="status">{message}</p>}<p className="switch-auth">{view === 'login' ? "Don't have an account?" : 'Already have an account?'} <button onClick={() => navigate(view === 'login' ? 'register' : 'login')}>{view === 'login' ? 'Sign up' : 'Log in'}</button></p></div></main>}
      <footer className="site-footer container"><button className="wordmark" onClick={() => navigate('home')}><span className="mark">✳</span> safespace<span className="wordmark-dot">.</span></button><span>Made for meaningful connections.</span><span>© 2026 SafeSpace</span></footer>
    </div>
  )
}

export default App
