import { djangoClient } from './axiosInstances';

export async function getLabels() {
  const { data } = await djangoClient.get('/api/labels/');
  return data.payload;
}

export async function createLabel(title) {
  const { data } = await djangoClient.post('/api/labels/', { title });
  return data.payload;
}

export async function updateLabel(id, title) {
  const { data } = await djangoClient.patch(`/api/labels/${id}/`, { title });
  return data.payload;
}

export async function deleteLabel(id) {
  await djangoClient.delete(`/api/labels/${id}/`);
}
