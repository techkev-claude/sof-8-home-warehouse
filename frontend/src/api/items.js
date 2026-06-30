import client from './client'

export function listItems(params = {}) {
  return client.get('/items/', { params }).then((r) => r.data)
}

export function getItem(id) {
  return client.get(`/items/${id}`).then((r) => r.data)
}

export function createItem(data) {
  return client.post('/items/', data).then((r) => r.data)
}

export function updateItem(id, data) {
  return client.patch(`/items/${id}`, data).then((r) => r.data)
}

export function deleteItem(id) {
  return client.delete(`/items/${id}`)
}

export function checkoutItem(id, data) {
  return client.post(`/items/${id}/checkout`, data).then((r) => r.data)
}

export function checkinItem(id, data) {
  return client.post(`/items/${id}/checkin`, data).then((r) => r.data)
}
