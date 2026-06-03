import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Link from '@mui/material/Link';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import * as authApi from '@/api/authApi';
import { ROUTES } from '@/utils/constants';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    if (!token) { setStatus('error'); return; }
    authApi.verifyEmail(token)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'));
  }, [token]);

  return (
    <Box minHeight="100vh" display="flex" alignItems="center" justifyContent="center" bgcolor="background.default">
      <Paper elevation={3} sx={{ p: 4, maxWidth: 420, width: '100%', textAlign: 'center' }}>
        <Typography variant="h5" fontWeight={600} mb={3}>Email Verification</Typography>
        {status === 'loading' && <CircularProgress />}
        {status === 'success' && (
          <Alert severity="success">
            Your email has been verified. <Link component={RouterLink} to={ROUTES.LOGIN}>Sign in</Link>
          </Alert>
        )}
        {status === 'error' && (
          <Alert severity="error">
            The verification link is invalid or expired.{' '}
            <Link component={RouterLink} to={ROUTES.LOGIN}>Request a new one</Link>
          </Alert>
        )}
      </Paper>
    </Box>
  );
}
