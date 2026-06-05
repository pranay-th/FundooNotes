import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { loginSchema } from '@/utils/validationSchemas';
import * as authApi from '@/api/authApi';
import { useToast } from '@/context/ToastContext';

export default function LoginForm({ onSuccess }) {
  const [showPassword, setShowPassword] = useState(false);
  const toast = useToast();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: yupResolver(loginSchema) });

  const onSubmit = async (data) => {
    try {
      await authApi.login(data);
      toast.success('OTP sent — check your inbox');
      onSuccess(data.email);
    } catch (err) {
      const errData = err?.response?.data;
      const msg =
        errData?.payload?.non_field_errors?.[0] ??
        errData?.payload?.username?.[0] ??
        errData?.message ??
        'Invalid credentials';
      setError('password', { message: msg });
      toast.error(msg);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <TextField
        label="Email"
        type="email"
        autoComplete="email"
        {...register('email')}
        error={Boolean(errors.email)}
        helperText={errors.email?.message}
        fullWidth
      />

      <TextField
        label="Password"
        type={showPassword ? 'text' : 'password'}
        autoComplete="current-password"
        {...register('password')}
        error={Boolean(errors.password)}
        helperText={errors.password?.message}
        fullWidth
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                onClick={() => setShowPassword((v) => !v)}
                edge="end"
                size="small"
              >
                {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth sx={{ mt: 0.5 }}>
        {isSubmitting ? <CircularProgress size={20} /> : 'Continue'}
      </Button>
    </Box>
  );
}
