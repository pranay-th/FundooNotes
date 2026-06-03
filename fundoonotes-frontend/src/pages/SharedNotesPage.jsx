import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import { useSharedNotes, useUpdateNoteContent } from '@/hooks/useCollab';
import NotesGrid from '@/components/notes/NotesGrid';
import NoteEditor from '@/components/notes/NoteEditor';

function sharedToNote(sn) {
  return {
    id: sn.id,
    title: sn.title,
    content: sn.content,
    color: sn.color,
    is_archived: false,
    is_trashed: false,
    labels: [],
    created_at: '',
    updated_at: '',
  };
}

export default function SharedNotesPage() {
  const { data: sharedNotes = [], isLoading, isError, refetch, error } = useSharedNotes();
  const [selectedShared, setSelectedShared] = useState(undefined);
  const [editorOpen, setEditorOpen] = useState(false);
  const [saveError, setSaveError] = useState('');

  const updateContent = useUpdateNoteContent(selectedShared?.id ?? 0);

  const notes = sharedNotes.map(sharedToNote);

  const handleNoteClick = (note) => {
    const sn = sharedNotes.find((s) => s.id === note.id);
    setSelectedShared(sn);
    setEditorOpen(true);
    setSaveError('');
  };

  const handleSave = async (payload) => {
    if (!selectedShared) return;
    try {
      await updateContent.mutateAsync({
        title: payload.title,
        content: payload.content,
        color: payload.color,
      });
      setEditorOpen(false);
    } catch (err) {
      if (err?.response?.status === 403) {
        setSaveError('You do not have permission to edit this note');
      }
    }
  };

  // Show a helpful message if the collab service is unreachable
  const isNetworkError = isError && error?.code === 'ERR_NETWORK';

  return (
    <Box>
      <Typography variant="h6" mb={2} fontWeight={500}>Shared with me</Typography>
      {saveError && <Alert severity="error" sx={{ mb: 2 }}>{saveError}</Alert>}
      {isNetworkError && (
        <Alert
          severity="warning"
          sx={{ mb: 2 }}
          action={<Button size="small" onClick={() => void refetch()}>Retry</Button>}
        >
          Cannot reach the collaboration service. Make sure it is running on port 8001.
        </Alert>
      )}
      <NotesGrid
        notes={notes}
        isLoading={isLoading}
        isError={isError && !isNetworkError}
        onRetry={() => void refetch()}
        emptyMessage="No notes have been shared with you"
        onNoteClick={handleNoteClick}
        onArchive={() => {}}
        onTrash={() => {}}
        isShared
        getAccessLevel={(note) => sharedNotes.find((s) => s.id === note.id)?.access_level}
      />
      {selectedShared && (
        <NoteEditor
          open={editorOpen}
          note={sharedToNote(selectedShared)}
          readOnly={selectedShared.access_level === 'read'}
          onClose={() => { setEditorOpen(false); setSelectedShared(undefined); }}
          onSave={(p) => void handleSave(p)}
        />
      )}
    </Box>
  );
}
