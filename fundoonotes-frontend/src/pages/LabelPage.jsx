import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useParams } from 'react-router-dom';
import { useNotes, useUpdateNote, useDeleteNote } from '@/hooks/useNotes';
import { useLabels } from '@/hooks/useLabels';
import NotesGrid from '@/components/notes/NotesGrid';
import NoteEditor from '@/components/notes/NoteEditor';

export default function LabelPage() {
  const { labelId } = useParams();
  const id = Number(labelId);
  const { data: notes = [], isLoading, isError, refetch } = useNotes();
  const { data: labels = [] } = useLabels();
  const updateNote = useUpdateNote();
  const deleteNote = useDeleteNote();
  const [selectedNote, setSelectedNote] = useState(undefined);
  const [editorOpen, setEditorOpen] = useState(false);

  const label = labels.find((l) => l.id === id);
  const filtered = notes.filter(
    (n) => !n.is_archived && !n.is_trashed && n.labels.some((l) => l.id === id),
  );

  return (
    <Box>
      <Typography variant="h6" mb={2}>
        {label?.title ?? 'Label'}
      </Typography>
      <NotesGrid
        notes={filtered}
        isLoading={isLoading}
        isError={isError}
        onRetry={() => void refetch()}
        emptyMessage="No notes with this label"
        onNoteClick={(note) => { setSelectedNote(note); setEditorOpen(true); }}
        onArchive={(noteId) => updateNote.mutate({ id: noteId, payload: { is_archived: true } })}
        onTrash={(noteId) => deleteNote.mutate(noteId)}
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
