import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

export default function ErrorState({ message = 'Something went wrong', onRetry }) {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      py={8}
      gap={2}
    >
      <ErrorOutlineIcon sx={{ fontSize: 48, color: 'error.main' }} />
      <Typography variant="body1" color="text.secondary">
        {message}
      </Typography>
      <Button variant="outlined" onClick={onRetry}>
        Retry
      </Button>
    </Box>
  );
}
