import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import { otpSchema } from '@/utils/validationSchemas';
import * as authApi from '@/api/authApi';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';
import { useToast } from '@/context/ToastContext';

export default function OtpForm({ email }) {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [readyToNavigate, setReadyToNavigate] = useState(false);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: yupResolver(otpSchema) });

  // Navigate only after isAuthenticated has updated in context
  useEffect(() => {
    if (readyToNavigate && isAuthenticated) {
      navigate(ROUTES.NOTES, { replace: true });
    }
  }, [isAuthenticated, readyToNavigate, navigate]);

  const onSubmit = async (data) => {
    try {
      const tokens = await authApi.verifyOtp({ email, otp: data.otp });
      // Build a minimal user object from what we know — full profile loads later
      const minimalUser = {
        username: email.split('@')[0],
        email,
        phone_number: '',
        is_verified: true,
      };
      // Store tokens immediately so subsequent requests are authenticated
      login(tokens, minimalUser);
      // Then fetch the real profile in the background and update
      authApi.getProfileWithToken(tokens.access)
        .then((user) => login(tokens, user))
        .catch(() => { /* non-critical — minimal user is sufficient */ });
      toast.success('Welcome to FundooNotes!');
      setReadyToNavigate(true);
    } catch (err) {
      console.error('OTP submit error:', err);
      const errData = err?.response?.data;
      const msg =
        errData?.payload?.non_field_errors?.[0] ??
        errData?.payload?.otp?.[0] ??
        errData?.message ??
        'Invalid or expired OTP';
      setError('otp', { message: msg });
      toast.error(msg);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Typography variant="body2" color="text.secondary">
        Enter the OTP sent to <strong>{email}</strong>
      </Typography>
      <TextField
        label="One-Time Password"
        {...register('otp')}
        error={Boolean(errors.otp)}
        helperText={errors.otp?.message}
        fullWidth
        inputProps={{ maxLength: 6 }}
      />
      <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth>
        {isSubmitting ? <CircularProgress size={20} /> : 'Verify'}
      </Button>
    </Box>
  );
}
