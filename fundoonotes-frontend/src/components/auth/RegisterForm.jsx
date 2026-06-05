import React, { useState } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { registerSchema } from '@/utils/validationSchemas';
import * as authApi from '@/api/authApi';
import { useToast } from '@/context/ToastContext';

/** Returns 0–4 based on password complexity. */
function getPasswordStrength(password) {
  if (!password) return 0;
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return score;
}

const STRENGTH_LABELS = ['', 'Weak', 'Fair', 'Good', 'Strong'];
const STRENGTH_COLORS = ['', 'error', 'warning', 'info', 'success'];

function PasswordStrengthBar({ password }) {
  const strength = getPasswordStrength(password);
  // Don't render until there's something typed, and strength must be ≥1
  if (!password || strength === 0) return null;

  return (
    <Box sx={{ mt: -0.5 }}>
      <LinearProgress
        variant="determinate"
        value={(strength / 4) * 100}
        color={STRENGTH_COLORS[strength]}
        sx={{ borderRadius: 1, height: 4 }}
      />
      <Typography
        variant="caption"
        color={`${STRENGTH_COLORS[strength]}.main`}
        sx={{ mt: 0.25, display: 'block' }}
      >
        {STRENGTH_LABELS[strength]}
      </Typography>
    </Box>
  );
}

export default function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false);
  const toast = useToast();

  const {
    register,
    handleSubmit,
    setError,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: yupResolver(registerSchema) });

  // Watch password live for the strength bar — coerce undefined to ''
  const passwordValue = useWatch({ control, name: 'password', defaultValue: '' }) ?? '';

  const onSubmit = async (data) => {
    try {
      await authApi.register(data);
      reset();
      toast.success('Account created! Check your email to verify your account.');
    } catch (err) {
      const fieldErrors = err?.response?.data?.payload ?? {};
      const keys = Object.keys(fieldErrors);

      if (keys.length > 0) {
        keys.forEach((key) => {
          setError(key, { message: fieldErrors[key]?.[0] });
        });
        // Surface the first field error as a toast too
        toast.error(fieldErrors[keys[0]]?.[0] ?? 'Registration failed');
      } else {
        const msg = err?.response?.data?.message ?? 'Registration failed. Please try again.';
        toast.error(msg);
      }
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
        label="Username"
        autoComplete="username"
        {...register('username')}
        error={Boolean(errors.username)}
        helperText={errors.username?.message}
        fullWidth
      />

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
        label="Phone Number"
        type="tel"
        autoComplete="tel"
        placeholder="+91XXXXXXXXXX"
        {...register('phone_number')}
        error={Boolean(errors.phone_number)}
        helperText={errors.phone_number?.message ?? 'Include country code, e.g. +91…'}
        fullWidth
      />

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
        <TextField
          label="Password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
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
        <PasswordStrengthBar password={passwordValue} />
      </Box>

      <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth sx={{ mt: 0.5 }}>
        {isSubmitting ? <CircularProgress size={20} /> : 'Create account'}
      </Button>
    </Box>
  );
}
