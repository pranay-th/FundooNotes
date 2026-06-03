import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import Popover from '@mui/material/Popover';
import IconButton from '@mui/material/IconButton';
import CheckIcon from '@mui/icons-material/Check';
import PaletteOutlinedIcon from '@mui/icons-material/PaletteOutlined';
import { NOTE_COLORS } from '@/theme/colors';
import { useTheme as useMuiTheme } from '@mui/material/styles';

export default function NoteColorPicker({ value, onChange }) {
  const muiTheme = useMuiTheme();
  const isDark = muiTheme.palette.mode === 'dark';
  const [anchor, setAnchor] = useState(null);

  return (
    <>
      <Tooltip title="Background options">
        <IconButton
          size="small"
          onClick={(e) => setAnchor(e.currentTarget)}
          aria-label="change note color"
        >
          <PaletteOutlinedIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Popover
        open={Boolean(anchor)}
        anchorEl={anchor}
        onClose={() => setAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <Box display="flex" flexWrap="wrap" gap={0.5} sx={{ maxWidth: 220 }}>
          {NOTE_COLORS.map((c) => (
            <Tooltip key={c.value} title={c.label}>
              <Box
                component="button"
                type="button"
                onClick={() => { onChange(c.value); setAnchor(null); }}
                aria-label={c.label}
                sx={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  bgcolor: isDark ? c.dark : c.light,
                  border: value === c.value ? '2px solid' : '2px solid transparent',
                  borderColor: value === c.value ? 'primary.main' : 'divider',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  p: 0,
                  outline: 'none',
                  transition: 'transform 0.1s',
                  '&:hover': { transform: 'scale(1.15)' },
                }}
              >
                {value === c.value && (
                  <CheckIcon sx={{ fontSize: 14, color: 'text.primary' }} />
                )}
              </Box>
            </Tooltip>
          ))}
        </Box>
      </Popover>
    </>
  );
}
