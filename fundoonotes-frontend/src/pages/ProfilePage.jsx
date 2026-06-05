import React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { getProfile, updateProfile } from '@/api/authApi';
import { useToast } from '@/context/ToastContext';
import GradientText from '@/components/ui/GradientText';

export default function ProfilePage() {
  const qc = useQueryClient();
  const toast = useToast();
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
  });

  const { register, handleSubmit, setError, formState: { errors, isSubmitting } } =
    useForm({
      values: profile
        ? { username: profile.username, email: profile.email, phone_number: profile.phone_number }
        : undefined,
    });

  const mutation = useMutation({
    mutationFn: (data) => updateProfile(data),
    onSuccess: (updated) => {
      qc.setQueryData(['profile'], updated);
      toast.success('Profile updated successfully.');
    },
    onError: () => {
      toast.error('Failed to update profile.');
    },
  });

  const onSubmit = async (data) => {
    try {
      await mutation.mutateAsync(data);
    } catch (err) {
      const fieldErrors = err?.response?.data?.payload ?? err?.response?.data ?? {};
      Object.keys(fieldErrors).forEach((key) => {
        setError(key, { message: Array.isArray(fieldErrors[key]) ? fieldErrors[key][0] : fieldErrors[key] });
      });
    }
  };

  if (isLoading) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>;

  return (
    <Box maxWidth={480} mx="auto">
      <GradientText variant="h6" duration={0.6} sx={{ mb: 3, fontSize: 15, fontWeight: 600, letterSpacing: 0 }}>
        Profile
      </GradientText>
      <Paper
        elevation={0}
        sx={{
          p: 3,
          borderRadius: 3,
          border: '1px solid',
          borderColor: (theme) =>
            theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.7)',
          backdropFilter: 'blur(16px)',
          bgcolor: (theme) =>
            theme.palette.mode === 'dark' ? 'rgba(30,30,30,0.72)' : 'rgba(255,255,255,0.72)',
        }}
      >
        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField label="Username" {...register('username')} error={Boolean(errors.username)} helperText={errors.username?.message} fullWidth />
          <TextField label="Email" type="email" {...register('email')} error={Boolean(errors.email)} helperText={errors.email?.message} fullWidth />
          <TextField label="Phone Number" {...register('phone_number')} error={Boolean(errors.phone_number)} helperText={errors.phone_number?.message} fullWidth />
          <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth>
            {isSubmitting ? <CircularProgress size={20} /> : 'Save Changes'}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
