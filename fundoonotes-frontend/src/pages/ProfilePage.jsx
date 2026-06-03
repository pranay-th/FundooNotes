import React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { getProfile, updateProfile } from '@/api/authApi';

export default function ProfilePage() {
  const qc = useQueryClient();
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
    },
  });

  const onSubmit = async (data) => {
    try {
      await mutation.mutateAsync(data);
    } catch (err) {
      const fieldErrors = err?.response?.data ?? {};
      Object.keys(fieldErrors).forEach((key) => {
        setError(key, { message: fieldErrors[key]?.[0] });
      });
    }
  };

  if (isLoading) return <CircularProgress />;

  return (
    <Box maxWidth={480} mx="auto">
      <Typography variant="h6" mb={3}>Profile</Typography>
      <Paper sx={{ p: 3 }}>
        {mutation.isSuccess && <Alert severity="success" sx={{ mb: 2 }}>Profile updated.</Alert>}
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
