import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import * as authApi from '@/api/authApi';

export default function ResetPasswordForm({ token }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authApi.resetPassword(email);
      setMessage('If this email is registered, a reset link has been sent.');
    } catch {
      setMessage('If this email is registered, a reset link has been sent.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      await authApi.resetPasswordConfirm(token, password);
      setMessage('Password reset successful. You can now log in.');
    } catch (err) {
      setError(err?.response?.data?.message ?? 'Invalid or expired reset token.');
    } finally {
      setLoading(false);
    }
  };

  if (message) return <Alert severity="success">{message}</Alert>;

  if (token) {
    return (
      <Box component="form" onSubmit={handleConfirmReset} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="New Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required fullWidth />
        <Button type="submit" variant="contained" disabled={loading} fullWidth>
          {loading ? <CircularProgress size={20} /> : 'Reset Password'}
        </Button>
      </Box>
    );
  }

  return (
    <Box component="form" onSubmit={handleRequestReset} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <TextField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required fullWidth />
      <Button type="submit" variant="contained" disabled={loading} fullWidth>
        {loading ? <CircularProgress size={20} /> : 'Send Reset Link'}
      </Button>
    </Box>
  );
}
