import { djangoClient } from './axiosInstances';

export async function getNotes() {
  const { data } = await djangoClient.get('/api/notes/');
  return data.payload;
}

export async function createNote(payload) {
  const { data } = await djangoClient.post('/api/notes/', payload);
  return data.payload;
}

export async function updateNote(id, payload) {
  const { data } = await djangoClient.patch(`/api/notes/${id}/`, payload);
  return data.payload;
}

export async function deleteNote(id) {
  await djangoClient.delete(`/api/notes/${id}/`);
}
