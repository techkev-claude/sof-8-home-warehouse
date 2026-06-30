import client from './client'

export function listUsagePurposes() {
  return client.get('/usage-purposes/').then((r) => r.data)
}

export function createUsagePurpose(data) {
  return client.post('/usage-purposes/', data).then((r) => r.data)
}

export function updateUsagePurpose(id, data) {
  return client.patch(`/usage-purposes/${id}`, data).then((r) => r.data)
}

export function deleteUsagePurpose(id) {
  return client.delete(`/usage-purposes/${id}`)
}
