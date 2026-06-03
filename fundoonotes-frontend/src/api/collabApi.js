import { collabClient } from './axiosInstances';

export async function getSharedNotes() {
  const { data } = await collabClient.get('/notes/shared');
  return data;
}

export async function getCollaborators(noteId) {
  const { data } = await collabClient.get(`/notes/${noteId}/collaborators`);
  return data;
}

export async function inviteCollaborator(noteId, payload) {
  const { data } = await collabClient.post(`/notes/${noteId}/collaborators`, payload);
  return data;
}

export async function updateCollaborator(noteId, userId, payload) {
  const { data } = await collabClient.patch(
    `/notes/${noteId}/collaborators/${userId}`,
    payload,
  );
  return data;
}

export async function removeCollaborator(noteId, userId) {
  await collabClient.delete(`/notes/${noteId}/collaborators/${userId}`);
}

export async function updateNoteContent(noteId, payload) {
  await collabClient.patch(`/notes/${noteId}/content`, payload);
}
