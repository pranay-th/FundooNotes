import React, { useState, useRef } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import InputBase from '@mui/material/InputBase';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Collapse from '@mui/material/Collapse';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import CloseIcon from '@mui/icons-material/Close';
import { useNotes, useCreateNote, useUpdateNote, useDeleteNote } from '@/hooks/useNotes';
import { useLabels } from '@/hooks/useLabels';
import { useCollaborators, useInviteCollaborator, useUpdateCollaborator, useRemoveCollaborator } from '@/hooks/useCollab';
import { useUI } from '@/context/UIContext';
import { filterNotesByQuery } from '@/utils/searchFilter';
import NotesGrid from '@/components/notes/NotesGrid';
import NoteEditor from '@/components/notes/NoteEditor';
import NoteColorPicker from '@/components/notes/NoteColorPicker';
import LabelPicker from '@/components/notes/LabelPicker';
import CollaboratorPanel from '@/components/notes/CollaboratorPanel';
import GradientText from '@/components/ui/GradientText';

// ── Collaborator dialog wrapper ───────────────────────────────────────────────
function CollaboratorDialog({ note, onClose }) {
  const { data: collaborators = [] } = useCollaborators(note.id);
  const invite = useInviteCollaborator(note.id);
  const updateAccess = useUpdateCollaborator(note.id);
  const remove = useRemoveCollaborator(note.id);

  return (
    <Dialog open onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        Share "{note.title || 'Note'}"
        <IconButton size="small" onClick={onClose}><CloseIcon fontSize="small" /></IconButton>
      </DialogTitle>
      <DialogContent>
        <CollaboratorPanel
          noteId={note.id}
          collaborators={collaborators}
          onInvite={async (p) => { await invite.mutateAsync(p); }}
          onUpdateAccess={async (userId, p) => { await updateAccess.mutateAsync({ userId, payload: p }); }}
          onRemove={async (userId) => { await remove.mutateAsync(userId); }}
        />
      </DialogContent>
    </Dialog>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function NotesPage() {
  const { data: notes = [], isLoading, isError, refetch } = useNotes();
  const { data: labels = [] } = useLabels();
  const { searchQuery } = useUI();
  const createNote = useCreateNote();
  const updateNote = useUpdateNote();
  const deleteNote = useDeleteNote();

  // Inline creator state
  const [expanded, setExpanded] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newColor, setNewColor] = useState('default');
  const [newLabelIds, setNewLabelIds] = useState([]);
  const creatorRef = useRef(null);

  // Editor state
  const [editorOpen, setEditorOpen] = useState(false);
  const [selectedNote, setSelectedNote] = useState(undefined);

  // Collaborator dialog state
  const [collabNote, setCollabNote] = useState(undefined);

  const activeNotes = notes.filter((n) => !n.is_archived && !n.is_trashed);
  const filtered = filterNotesByQuery(activeNotes, searchQuery);

  const handleClose = () => {
    if (newTitle.trim() || newContent.trim()) {
      createNote.mutate({ title: newTitle, content: newContent, color: newColor, label_ids: newLabelIds });
    }
    setExpanded(false);
    setNewTitle('');
    setNewContent('');
    setNewColor('default');
    setNewLabelIds([]);
  };

  const handleNoteClick = (note) => {
    setSelectedNote(note);
    setEditorOpen(true);
  };

  const handleShareClick = (note) => {
    setCollabNote(note);
  };

  const handleSave = (payload) => {
    if (selectedNote) {
      updateNote.mutate({ id: selectedNote.id, payload });
    }
    setSelectedNote(undefined);
  };

  return (
    <Box>
      {/* ── Section heading ── */}
      <Box sx={{ maxWidth: 600, mx: 'auto', mb: 2, px: 0.5 }}>
        <GradientText variant="h6" duration={0.6} sx={{ fontSize: 15, fontWeight: 600, letterSpacing: 0 }}>
          My Notes
        </GradientText>
      </Box>

      {/* ── Inline note creator ── */}
      <Box sx={{ maxWidth: 600, mx: 'auto', mb: 4 }}>
        <Paper
          ref={creatorRef}
          elevation={0}
          sx={{
            borderRadius: 3,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: (theme) => expanded
              ? 'primary.main'
              : (theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.12)' : 'rgba(255,255,255,0.7)'),
            boxShadow: expanded
              ? '0 4px 24px rgba(26,115,232,0.2)'
              : '0 2px 8px rgba(0,0,0,0.08)',
            backdropFilter: 'blur(16px) saturate(160%)',
            bgcolor: (theme) =>
              theme.palette.mode === 'dark'
                ? 'rgba(30,30,30,0.72)'
                : 'rgba(255,255,255,0.72)',
            transition: 'border-color 0.2s, box-shadow 0.2s',
          }}
        >
          {!expanded && (
            <Box
              sx={{ px: 2, py: 1.5, cursor: 'text', display: 'flex', alignItems: 'center' }}
              onClick={() => setExpanded(true)}
            >
              <InputBase placeholder="Take a note…" readOnly fullWidth sx={{ fontSize: 15, cursor: 'text' }} />
            </Box>
          )}
          <Collapse in={expanded}>
            <Box sx={{ px: 2, pt: 1.5 }}>
              <InputBase
                placeholder="Title"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                fullWidth
                autoFocus
                sx={{ fontSize: 15, fontWeight: 600, mb: 0.5 }}
                inputProps={{ 'aria-label': 'note title' }}
              />
              <InputBase
                placeholder="Take a note…"
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
                fullWidth
                multiline
                minRows={2}
                sx={{ fontSize: 14 }}
                inputProps={{ 'aria-label': 'note content' }}
              />
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', px: 1, pb: 1, justifyContent: 'space-between' }}>
              <Box display="flex" alignItems="center">
                <NoteColorPicker value={newColor} onChange={setNewColor} />
                <LabelPicker labels={labels} selectedIds={newLabelIds} onChange={setNewLabelIds} />
              </Box>
              <Tooltip title="Close">
                <IconButton size="small" onClick={handleClose} aria-label="close note creator">
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Collapse>
        </Paper>
      </Box>

      {/* ── Notes grid ── */}
      <NotesGrid
        notes={filtered}
        isLoading={isLoading}
        isError={isError}
        onRetry={() => void refetch()}
        emptyMessage={searchQuery ? 'No notes match your search' : 'Your notes will appear here'}
        onNoteClick={handleNoteClick}
        onArchive={(id) => updateNote.mutate({ id, payload: { is_archived: true } })}
        onTrash={(id) => deleteNote.mutate(id)}
        onShare={handleShareClick}
      />

      {/* ── Edit note dialog ── */}
      <NoteEditor
        open={editorOpen}
        note={selectedNote}
        onClose={() => { setEditorOpen(false); setSelectedNote(undefined); }}
        onSave={handleSave}
      />

      {/* ── Collaborator dialog ── */}
      {collabNote && (
        <CollaboratorDialog
          note={collabNote}
          onClose={() => setCollabNote(undefined)}
        />
      )}
    </Box>
  );
}
