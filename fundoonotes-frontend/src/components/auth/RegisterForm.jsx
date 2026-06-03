import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { registerSchema } from '@/utils/validationSchemas';
import * as authApi from '@/api/authApi';

export default function RegisterForm() {
  const [success, setSuccess] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: yupResolver(registerSchema) });

  const onSubmit = async (data) => {
    try {
      await authApi.register(data);
      setSuccess(true);
    } catch (err) {
      const fieldErrors = err?.response?.data?.payload ?? {};
      Object.keys(fieldErrors).forEach((key) => {
        setError(key, { message: fieldErrors[key]?.[0] });
      });
    }
  };

  if (success) {
    return (
      <Alert severity="success">
        Registration successful! Please check your email to verify your account.
      </Alert>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <TextField label="Username" {...register('username')} error={Boolean(errors.username)} helperText={errors.username?.message} fullWidth />
      <TextField label="Email" type="email" {...register('email')} error={Boolean(errors.email)} helperText={errors.email?.message} fullWidth />
      <TextField label="Phone Number" {...register('phone_number')} error={Boolean(errors.phone_number)} helperText={errors.phone_number?.message} fullWidth />
      <TextField label="Password" type="password" {...register('password')} error={Boolean(errors.password)} helperText={errors.password?.message} fullWidth />
      <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth>
        {isSubmitting ? <CircularProgress size={20} /> : 'Register'}
      </Button>
    </Box>
  );
}
