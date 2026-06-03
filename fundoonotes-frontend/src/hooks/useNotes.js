import {
  useQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';
import {
  getNotes,
  createNote,
  updateNote,
  deleteNote,
} from '@/api/notesApi';

export function useNotes() {
  return useQuery({
    queryKey: ['notes'],
    queryFn: getNotes,
    staleTime: 60_000,
  });
}

export function useCreateNote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload) => createNote(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}

export function useUpdateNote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }) => updateNote(id, payload),
    onMutate: async ({ id, payload }) => {
      await qc.cancelQueries({ queryKey: ['notes'] });
      const snapshot = qc.getQueryData(['notes']);
      qc.setQueryData(['notes'], (old) =>
        old?.map((n) => (n.id === id ? { ...n, ...payload } : n)) ?? [],
      );
      return { snapshot };
    },
    onError: (_err, _vars, context) => {
      if (context?.snapshot) {
        qc.setQueryData(['notes'], context.snapshot);
      }
    },
    onSettled: () => {
      void qc.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}

export function useDeleteNote() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => deleteNote(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}
