import client from './client'

export function login(username, password) {
  return client.post('/auth/login', { username, password }).then((r) => r.data)
}

export function fetchMe() {
  return client.get('/auth/me').then((r) => r.data)
}
