import client from './client'

export function listLocations() {
  return client.get('/locations/').then((r) => r.data)
}

export function getLocationTree() {
  return client.get('/locations/tree').then((r) => r.data)
}

export function createLocation(data) {
  return client.post('/locations/', data).then((r) => r.data)
}

export function updateLocation(id, data) {
  return client.patch(`/locations/${id}`, data).then((r) => r.data)
}

export function deleteLocation(id) {
  return client.delete(`/locations/${id}`)
}
