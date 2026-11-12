import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, tokenStore } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(tokenStore.get()))

  // Pulihkan sesi login saat halaman dibuka / di-refresh
  useEffect(() => {
    if (!tokenStore.get()) return
    api.get('/auth/me')
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false))
  }, [])

  // Token kedaluwarsa -> otomatis logout
  useEffect(() => {
    const onLogout = () => setUser(null)
    window.addEventListener('safespace-logout', onLogout)
    return () => window.removeEventListener('safespace-logout', onLogout)
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await api.post('/auth/login', { email, password })
    tokenStore.set(data.token)
    setUser(data.user)
  }, [])

  const register = useCallback(async (username, email, password) => {
    const data = await api.post('/auth/register', { username, email, password })
    tokenStore.set(data.token)
    setUser(data.user)
  }, [])

  const logout = useCallback(() => {
    tokenStore.clear()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  return useContext(AuthContext)
}
