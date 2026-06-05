import React, { useState } from 'react';
import Box from '@mui/material/Box';
import { useNotes, useUpdateNote } from '@/hooks/useNotes';
import NotesGrid from '@/components/notes/NotesGrid';
import NoteEditor from '@/components/notes/NoteEditor';
import GradientText from '@/components/ui/GradientText';

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
      <GradientText variant="h6" duration={0.6} sx={{ mb: 2, fontSize: 15, fontWeight: 600, letterSpacing: 0 }}>
        Archive
      </GradientText>
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
