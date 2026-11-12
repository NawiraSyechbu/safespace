// Backend menyimpan waktu dalam UTC tanpa penanda zona; tambahkan 'Z'.
export function parseUTC(value) {
  if (!value) return null
  const text = String(value)
  return new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(text) ? text : `${text}Z`)
}

export function formatDate(value) {
  const d = parseUTC(value)
  if (!d || isNaN(d)) return ''
  return d.toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })
}

export const STATUS_LABEL = {
  approved: 'Diterbitkan',
  blocked: 'Ditolak sistem',
  pending_review: 'Menunggu moderator',
}

export const APPEAL_LABEL = {
  pending: 'Banding sedang diproses',
  accepted: 'Banding diterima',
  rejected: 'Banding ditolak',
}
