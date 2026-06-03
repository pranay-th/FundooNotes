import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useNotes, useUpdateNote } from '@/hooks/useNotes';
import NotesGrid from '@/components/notes/NotesGrid';
import NoteEditor from '@/components/notes/NoteEditor';

export default function ArchivePage() {
  const { data: notes = [], isLoading, isError, refetch } = useNotes();
  const updateNote = useUpdateNote();
  const [selectedNote, setSelectedNote] = useState(undefined);
  const [editorOpen, setEditorOpen] = useState(false);

  const archived = notes.filter((n) => n.is_archived && !n.is_trashed);

  const handleUnarchive = (id) => {
    updateNote.mutate({ id, payload: { is_archived: false } });
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}>Archive</Typography>
      <NotesGrid
        notes={archived}
        isLoading={isLoading}
        isError={isError}
        onRetry={() => void refetch()}
        emptyMessage="No archived notes"
        onNoteClick={(note) => { setSelectedNote(note); setEditorOpen(true); }}
        onArchive={handleUnarchive}
        onTrash={() => {}}
      />
      <NoteEditor
        open={editorOpen}
        note={selectedNote}
        onClose={() => { setEditorOpen(false); setSelectedNote(undefined); }}
        onSave={(payload) => {
          if (selectedNote) updateNote.mutate({ id: selectedNote.id, payload });
          setEditorOpen(false);
        }}
      />
    </Box>
  );
}
