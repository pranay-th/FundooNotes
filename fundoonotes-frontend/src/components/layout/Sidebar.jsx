import React, { useState } from 'react';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';
import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import Collapse from '@mui/material/Collapse';
import NoteIcon from '@mui/icons-material/LightbulbOutlined';
import ArchiveIcon from '@mui/icons-material/ArchiveOutlined';
import DeleteIcon from '@mui/icons-material/DeleteOutlined';
import PeopleIcon from '@mui/icons-material/PeopleOutlined';
import LabelIcon from '@mui/icons-material/LabelOutlined';
import EditIcon from '@mui/icons-material/EditOutlined';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import { useNavigate, useLocation } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';
import { useCreateLabel, useUpdateLabel, useDeleteLabel } from '@/hooks/useLabels';

export default function Sidebar({ open, labels, activeLabelId, onLabelClick }) {
  const navigate = useNavigate();
  const location = useLocation();
  const createLabel = useCreateLabel();
  const updateLabel = useUpdateLabel();
  const deleteLabel = useDeleteLabel();

  const [newLabelTitle, setNewLabelTitle] = useState('');
  const [newLabelError, setNewLabelError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [showNewLabel, setShowNewLabel] = useState(false);

  const navItems = [
    { label: 'Notes', icon: <NoteIcon />, path: ROUTES.NOTES },
    { label: 'Archive', icon: <ArchiveIcon />, path: ROUTES.ARCHIVE },
    { label: 'Trash', icon: <DeleteIcon />, path: ROUTES.TRASH },
    { label: 'Shared Notes', icon: <PeopleIcon />, path: ROUTES.SHARED },
  ];

  const handleCreateLabel = async () => {
    if (!newLabelTitle.trim()) return;
    try {
      await createLabel.mutateAsync(newLabelTitle.trim());
      setNewLabelTitle('');
      setNewLabelError('');
      setShowNewLabel(false);
    } catch (err) {
      setNewLabelError(err?.response?.data?.payload?.title?.[0] ?? 'Failed to create label');
    }
  };

  const handleRenameConfirm = async (id) => {
    if (!editingTitle.trim()) return;
    await updateLabel.mutateAsync({ id, title: editingTitle.trim() });
    setEditingId(null);
  };

  const itemSx = {
    borderRadius: '0 24px 24px 0',
    mr: 1,
    pl: open ? 2 : 1.5,
    minHeight: 48,
    '&.Mui-selected': {
      bgcolor: 'action.selected',
      '&:hover': { bgcolor: 'action.selected' },
    },
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', pt: 1 }}>
      <List dense disablePadding>
        {navItems.map((item) => (
          <Tooltip key={item.path} title={open ? '' : item.label} placement="right">
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={itemSx}
            >
              <ListItemIcon sx={{ minWidth: open ? 40 : 'auto', color: 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              {open && (
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{ fontSize: 14, fontWeight: location.pathname === item.path ? 600 : 400 }}
                />
              )}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>

      {open && labels.length > 0 && (
        <>
          <Divider sx={{ my: 1 }} />
          <Box sx={{ px: 2, py: 0.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, textTransform: 'uppercase', letterSpacing: 1 }}>
              Labels
            </Typography>
          </Box>
          <List dense disablePadding sx={{ flex: 1, overflowY: 'auto' }}>
            {labels.map((label) => (
              <ListItemButton
                key={label.id}
                selected={activeLabelId === label.id}
                onClick={() => onLabelClick(label.id)}
                sx={{ ...itemSx, pr: 0.5 }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: 'inherit' }}>
                  <LabelIcon fontSize="small" />
                </ListItemIcon>
                {editingId === label.id ? (
                  <TextField
                    size="small"
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') void handleRenameConfirm(label.id);
                      if (e.key === 'Escape') setEditingId(null);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    autoFocus
                    sx={{ flex: 1, mr: 0.5 }}
                    variant="standard"
                  />
                ) : (
                  <ListItemText
                    primary={label.title}
                    primaryTypographyProps={{ fontSize: 14 }}
                    sx={{ flex: 1 }}
                  />
                )}
                <Box sx={{ display: 'flex', opacity: 0, '.MuiListItemButton-root:hover &': { opacity: 1 } }}>
                  {editingId === label.id ? (
                    <>
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); void handleRenameConfirm(label.id); }}>
                        <CheckIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); setEditingId(null); }}>
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                    </>
                  ) : (
                    <>
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); setEditingId(label.id); setEditingTitle(label.title); }}>
                        <EditIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); void deleteLabel.mutateAsync(label.id); }}>
                        <DeleteIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                    </>
                  )}
                </Box>
              </ListItemButton>
            ))}
          </List>
        </>
      )}

      {open && (
        <Box sx={{ px: 1, pb: 2, mt: 'auto' }}>
          <Collapse in={showNewLabel}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
              <TextField
                size="small"
                fullWidth
                placeholder="New label name"
                value={newLabelTitle}
                onChange={(e) => { setNewLabelTitle(e.target.value); setNewLabelError(''); }}
                onKeyDown={(e) => { if (e.key === 'Enter') void handleCreateLabel(); if (e.key === 'Escape') setShowNewLabel(false); }}
                error={Boolean(newLabelError)}
                helperText={newLabelError}
                autoFocus
                variant="outlined"
              />
              <IconButton size="small" onClick={() => void handleCreateLabel()} color="primary">
                <CheckIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={() => setShowNewLabel(false)}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          </Collapse>
          {!showNewLabel && (
            <ListItemButton onClick={() => setShowNewLabel(true)} sx={{ borderRadius: '0 24px 24px 0', mr: 1 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <AddIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Create new label" primaryTypographyProps={{ fontSize: 14 }} />
            </ListItemButton>
          )}
        </Box>
      )}
    </Box>
  );
}
