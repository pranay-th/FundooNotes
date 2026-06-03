import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useNotes, useUpdateNote } from '@/hooks/useNotes';
import { djangoClient } from '@/api/axiosInstances';
import NotesGrid from '@/components/notes/NotesGrid';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import { useQueryClient } from '@tanstack/react-query';

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
      <Typography variant="h6" mb={2}>Trash</Typography>
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
