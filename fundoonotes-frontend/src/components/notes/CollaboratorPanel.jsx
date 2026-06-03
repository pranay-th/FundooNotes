import React, { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import IconButton from '@mui/material/IconButton';
import Alert from '@mui/material/Alert';
import Typography from '@mui/material/Typography';
import DeleteIcon from '@mui/icons-material/Delete';

export default function CollaboratorPanel({ collaborators, onInvite, onUpdateAccess, onRemove }) {
  const [email, setEmail] = useState('');
  const [accessLevel, setAccessLevel] = useState('read');
  const [inviteError, setInviteError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInvite = async () => {
    if (!email.trim()) return;
    setLoading(true);
    setInviteError('');
    try {
      await onInvite({ collaborator_email: email.trim(), access_level: accessLevel });
      setEmail('');
    } catch (err) {
      const status = err?.response?.status;
      if (status === 404) setInviteError('No user found with that email address');
      else if (status === 400) setInviteError('You cannot invite yourself as a collaborator');
      else setInviteError(err?.response?.data?.message ?? 'Failed to invite collaborator');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>Share with others</Typography>

      <Box display="flex" gap={1} mb={1} flexWrap="wrap">
        <TextField
          size="small"
          label="Email address"
          value={email}
          onChange={(e) => { setEmail(e.target.value); setInviteError(''); }}
          sx={{ flex: 1, minWidth: 180 }}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Access</InputLabel>
          <Select
            value={accessLevel}
            label="Access"
            onChange={(e) => setAccessLevel(e.target.value)}
          >
            <MenuItem value="read">Read</MenuItem>
            <MenuItem value="read_write">Read & Write</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" size="small" onClick={handleInvite} disabled={loading}>
          Invite
        </Button>
      </Box>

      {inviteError && <Alert severity="error" sx={{ mb: 1 }}>{inviteError}</Alert>}

      {collaborators.length > 0 && (
        <List dense>
          {collaborators.map((c) => (
            <ListItem key={c.user_id} disablePadding>
              <ListItemText
                primary={c.username}
                secondary={c.email}
              />
              <Box display="flex" alignItems="center" gap={1}>
                <Select
                  size="small"
                  value={c.access_level}
                  onChange={(e) =>
                    void onUpdateAccess(c.user_id, { access_level: e.target.value })
                  }
                  sx={{ minWidth: 120 }}
                >
                  <MenuItem value="read">Read</MenuItem>
                  <MenuItem value="read_write">Read & Write</MenuItem>
                </Select>
                <ListItemSecondaryAction>
                  <IconButton size="small" onClick={() => void onRemove(c.user_id)} aria-label="remove collaborator">
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </ListItemSecondaryAction>
              </Box>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}
