import React, { useState } from 'react';
import Popover from '@mui/material/Popover';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import LabelIcon from '@mui/icons-material/Label';

export default function LabelPicker({ labels, selectedIds, onChange }) {
  const [anchor, setAnchor] = useState(null);

  const toggle = (id) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((x) => x !== id));
    } else {
      onChange([...selectedIds, id]);
    }
  };

  return (
    <>
      <Tooltip title="Labels">
        <IconButton size="small" onClick={(e) => setAnchor(e.currentTarget)} aria-label="pick labels">
          <LabelIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Popover
        open={Boolean(anchor)}
        anchorEl={anchor}
        onClose={() => setAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <List dense sx={{ minWidth: 180, maxHeight: 300, overflowY: 'auto' }}>
          {labels.length === 0 && (
            <ListItemButton disabled>
              <ListItemText primary="No labels yet" />
            </ListItemButton>
          )}
          {labels.map((label) => (
            <ListItemButton key={label.id} onClick={() => toggle(label.id)}>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked={selectedIds.includes(label.id)}
                  tabIndex={-1}
                  disableRipple
                  size="small"
                />
              </ListItemIcon>
              <ListItemText primary={label.title} />
            </ListItemButton>
          ))}
        </List>
      </Popover>
    </>
  );
}
