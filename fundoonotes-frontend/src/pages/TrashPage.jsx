import React, { useState } from 'react';
import Box from '@mui/material/Box';
import { useNotes, useUpdateNote } from '@/hooks/useNotes';
import { djangoClient } from '@/api/axiosInstances';
import NotesGrid from '@/components/notes/NotesGrid';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import { useQueryClient } from '@tanstack/react-query';
import GradientText from '@/components/ui/GradientText';

export default function TrashPage() {
  const { data: notes = [], isLoading, isError, refetch } = useNotes();
  const updateNote = useUpdateNote();
  const qc = useQueryClient();
  const [confirmId, setConfirmId] = useState(null);

  const trashed = notes.filter((n) => n.is_trashed);

  const handleRestore = (id) => {
    updateNote.mutate({ id, payload: { is_trashed: false } });
  };

  const handlePermanentDelete = async (id) => {
    await djangoClient.delete(`/api/notes/${id}/permanent/`);
    void qc.invalidateQueries({ queryKey: ['notes'] });
    setConfirmId(null);
  };

  return (
    <Box>
      <GradientText variant="h6" duration={0.6} sx={{ mb: 2, fontSize: 15, fontWeight: 600, letterSpacing: 0 }}>
        Trash
      </GradientText>
      <NotesGrid
        notes={trashed}
        isLoading={isLoading}
        isError={isError}
        onRetry={() => void refetch()}
        emptyMessage="Trash is empty"
        onNoteClick={() => {}}
        onArchive={handleRestore}
        onTrash={(id) => setConfirmId(id)}
      />
      <ConfirmDialog
        open={confirmId !== null}
        title="Delete permanently?"
        message="This note will be permanently deleted and cannot be recovered."
        confirmLabel="Delete"
        onConfirm={() => { if (confirmId !== null) void handlePermanentDelete(confirmId); }}
        onCancel={() => setConfirmId(null)}
      />
    </Box>
  );
}
