import React, { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import InputBase from '@mui/material/InputBase';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import { useTheme as useMuiTheme } from '@mui/material/styles';
import NoteColorPicker from './NoteColorPicker';
import LabelPicker from './LabelPicker';
import { useLabels } from '@/hooks/useLabels';
import { NOTE_COLORS } from '@/theme/colors';

export default function NoteEditor({ open, note, readOnly = false, onClose, onSave }) {
  const muiTheme = useMuiTheme();
  const isDark = muiTheme.palette.mode === 'dark';
  const { data: labels = [] } = useLabels();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [color, setColor] = useState('default');
  const [selectedLabelIds, setSelectedLabelIds] = useState([]);

  useEffect(() => {
    if (open) {
      setTitle(note?.title ?? '');
      setContent(note?.content ?? '');
      setColor(note?.color ?? 'default');
      setSelectedLabelIds(note?.labels.map((l) => l.id) ?? []);
    }
  }, [open, note]);

  const colorDef = NOTE_COLORS.find((c) => c.value === color);
  const bgColor = colorDef && color !== 'default'
    ? (isDark ? colorDef.dark : colorDef.light)
    : muiTheme.palette.background.paper;

  const handleSave = () => {
    onSave({ title, content, color, label_ids: selectedLabelIds });
    onClose();
  };

  const selectedLabels = labels.filter((l) => selectedLabelIds.includes(l.id));

  return (
    <Dialog
      open={open}
      onClose={readOnly ? onClose : handleSave}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: bgColor,
          transition: 'background-color 0.2s',
          borderRadius: 2,
          boxShadow: 8,
        },
      }}
    >
      <DialogContent sx={{ p: 2, pb: 0 }}>
        <InputBase
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={readOnly}
          fullWidth
          multiline
          sx={{
            fontSize: 18,
            fontWeight: 500,
            mb: 1,
            '& .MuiInputBase-input': { p: 0 },
          }}
          inputProps={{ 'aria-label': 'note title' }}
        />
        <InputBase
          placeholder="Take a note…"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={readOnly}
          fullWidth
          multiline
          minRows={3}
          sx={{
            fontSize: 14,
            '& .MuiInputBase-input': { p: 0 },
          }}
          inputProps={{ 'aria-label': 'note content' }}
        />

        {/* Label chips */}
        {selectedLabels.length > 0 && (
          <Box display="flex" flexWrap="wrap" gap={0.5} mt={1.5}>
            {selectedLabels.map((l) => (
              <Chip
                key={l.id}
                label={l.title}
                size="small"
                onDelete={readOnly ? undefined : () =>
                  setSelectedLabelIds((ids) => ids.filter((id) => id !== l.id))
                }
                sx={{ height: 22, fontSize: 12, bgcolor: 'action.hover' }}
              />
            ))}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 2, py: 1, justifyContent: 'space-between' }}>
        {!readOnly ? (
          <Box display="flex" alignItems="center" gap={0.5}>
            <NoteColorPicker value={color} onChange={setColor} />
            <LabelPicker
              labels={labels}
              selectedIds={selectedLabelIds}
              onChange={setSelectedLabelIds}
            />
          </Box>
        ) : (
          <Box />
        )}
        <Button
          onClick={readOnly ? onClose : handleSave}
          size="small"
          sx={{ textTransform: 'none', fontWeight: 500 }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}
