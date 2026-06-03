import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getLabels,
  createLabel,
  updateLabel,
  deleteLabel,
} from '@/api/labelsApi';

export function useLabels() {
  return useQuery({
    queryKey: ['labels'],
    queryFn: getLabels,
    staleTime: 60_000,
  });
}

export function useCreateLabel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (title) => createLabel(title),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['labels'] });
    },
  });
}

export function useUpdateLabel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, title }) => updateLabel(id, title),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['labels'] });
    },
  });
}

export function useDeleteLabel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => deleteLabel(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['labels'] });
    },
  });
}
