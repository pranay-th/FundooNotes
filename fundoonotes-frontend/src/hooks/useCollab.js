import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getSharedNotes,
  getCollaborators,
  inviteCollaborator,
  updateCollaborator,
  removeCollaborator,
  updateNoteContent,
} from '@/api/collabApi';

export function useSharedNotes() {
  return useQuery({
    queryKey: ['shared-notes'],
    queryFn: getSharedNotes,
    staleTime: 30_000,
  });
}

export function useCollaborators(noteId) {
  return useQuery({
    queryKey: ['collaborators', noteId],
    queryFn: () => getCollaborators(noteId),
    enabled: noteId > 0,
  });
}

export function useInviteCollaborator(noteId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload) => inviteCollaborator(noteId, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['collaborators', noteId] });
    },
  });
}

export function useUpdateCollaborator(noteId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }) => updateCollaborator(noteId, userId, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['collaborators', noteId] });
    },
  });
}

export function useRemoveCollaborator(noteId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId) => removeCollaborator(noteId, userId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['collaborators', noteId] });
    },
  });
}

export function useUpdateNoteContent(noteId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload) => updateNoteContent(noteId, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['collaborators', noteId] });
      void qc.invalidateQueries({ queryKey: ['shared-notes'] });
    },
  });
}
