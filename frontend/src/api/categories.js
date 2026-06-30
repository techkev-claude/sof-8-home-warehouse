import client from './client'

export function listCategories() {
  return client.get('/categories/').then((r) => r.data)
}

export function createCategory(data) {
  return client.post('/categories/', data).then((r) => r.data)
}

export function updateCategory(id, data) {
  return client.patch(`/categories/${id}`, data).then((r) => r.data)
}

export function deleteCategory(id) {
  return client.delete(`/categories/${id}`)
}
