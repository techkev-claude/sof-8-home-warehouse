import client from './client'

export function listImages(itemId) {
  return client.get(`/items/${itemId}/images`).then((r) => r.data)
}

export function uploadImages(itemId, files) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  return client
    .post(`/items/${itemId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export function setPrimaryImage(itemId, imageId) {
  return client
    .patch(`/items/${itemId}/images/${imageId}`, null, { params: { is_primary: true } })
    .then((r) => r.data)
}

export function deleteImage(itemId, imageId) {
  return client.delete(`/items/${itemId}/images/${imageId}`)
}
