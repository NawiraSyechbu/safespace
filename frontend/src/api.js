// Semua komunikasi ke backend lewat file ini.
// Default '/api' (satu alamat dengan backend / lewat proxy Vite).
const BASE = import.meta.env.VITE_API_URL || '/api'
const TOKEN_KEY = 'safespace_token'

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

async function request(path, { method = 'GET', body } = {}) {
  const token = tokenStore.get()
  let res
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: {
        ...(body !== undefined && { 'Content-Type': 'application/json' }),
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new Error('Tidak bisa terhubung ke server. Pastikan backend sudah berjalan.')
  }

  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    if (res.status === 401 && token) {
      tokenStore.clear()
      window.dispatchEvent(new Event('safespace-logout'))
    }
    const detail = data.detail
    throw new Error(
      typeof detail === 'string' ? detail : 'Terjadi kesalahan pada server.',
    )
  }
  return data
}

export const api = {
  get: (path) => request(path),
  post: (path, body = {}) => request(path, { method: 'POST', body }),
    delete: (path) => request(path, { method: 'DELETE' }),
  patch: (path, body = {}) => request(path, { method: 'PATCH', body }),
}
