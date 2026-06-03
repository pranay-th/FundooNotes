import React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import ResetPasswordForm from '@/components/auth/ResetPasswordForm';
import { ROUTES } from '@/utils/constants';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? undefined;

  return (
    <Box minHeight="100vh" display="flex" alignItems="center" justifyContent="center" bgcolor="background.default">
      <Paper elevation={3} sx={{ p: 4, width: '100%', maxWidth: 420 }}>
        <Typography variant="h5" fontWeight={600} mb={1} textAlign="center">
          {token ? 'Set New Password' : 'Reset Password'}
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={3} textAlign="center">
          {token ? 'Enter your new password below.' : 'Enter your email to receive a reset link.'}
        </Typography>
        <ResetPasswordForm token={token} />
        <Typography variant="body2" textAlign="center" mt={2}>
          <Link component={RouterLink} to={ROUTES.LOGIN}>Back to login</Link>
        </Typography>
      </Paper>
    </Box>
  );
}
