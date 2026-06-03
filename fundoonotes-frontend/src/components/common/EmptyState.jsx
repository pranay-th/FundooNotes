import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import NoteAltOutlinedIcon from '@mui/icons-material/NoteAltOutlined';

export default function EmptyState({ message, icon }) {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      py={8}
      gap={2}
      color="text.secondary"
    >
      {icon ?? <NoteAltOutlinedIcon sx={{ fontSize: 64, opacity: 0.4 }} />}
      <Typography variant="body1" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );
}
