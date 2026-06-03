import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { loginSchema } from '@/utils/validationSchemas';
import * as authApi from '@/api/authApi';

export default function LoginForm({ onSuccess }) {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: yupResolver(loginSchema) });

  const onSubmit = async (data) => {
    try {
      await authApi.login(data);
      onSuccess(data.email);
    } catch (err) {
      const errData = err?.response?.data;
      // Backend: { message, payload: { non_field_errors: [...] }, status }
      const msg =
        errData?.payload?.non_field_errors?.[0] ??
        errData?.payload?.username?.[0] ??
        errData?.message ??
        'Invalid credentials';
      setError('password', { message: msg });
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <TextField label="Email" type="email" {...register('email')} error={Boolean(errors.email)} helperText={errors.email?.message} fullWidth />
      <TextField label="Password" type="password" {...register('password')} error={Boolean(errors.password)} helperText={errors.password?.message} fullWidth />
      <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth>
        {isSubmitting ? <CircularProgress size={20} /> : 'Continue'}
      </Button>
    </Box>
  );
}
