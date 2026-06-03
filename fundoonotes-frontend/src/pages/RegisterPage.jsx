import React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Divider from '@mui/material/Divider';
import { Link as RouterLink } from 'react-router-dom';
import { useTheme as useMuiTheme } from '@mui/material/styles';
import RegisterForm from '@/components/auth/RegisterForm';
import { ROUTES } from '@/utils/constants';

export default function RegisterPage() {
  const muiTheme = useMuiTheme();
  const isDark = muiTheme.palette.mode === 'dark';

  return (
    <Box
      minHeight="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      sx={{
        background: isDark
          ? 'linear-gradient(135deg, #131416 0%, #1a1d2e 50%, #0f1117 100%)'
          : 'linear-gradient(135deg, #e8f0fe 0%, #f0f4f9 50%, #e3f2fd 100%)',
        px: 2,
        py: 4,
      }}
    >
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, sm: 4.5 },
          width: '100%',
          maxWidth: 440,
          borderRadius: 4,
          border: '1px solid',
          borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
          boxShadow: isDark
            ? '0 24px 64px rgba(0,0,0,0.4)'
            : '0 24px 64px rgba(0,0,0,0.08)',
        }}
      >
        <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #1a73e8 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 16px rgba(26,115,232,0.35)',
              mb: 1.5,
            }}
          >
            <Typography sx={{ color: '#fff', fontSize: 24, fontWeight: 700, lineHeight: 1 }}>F</Typography>
          </Box>
          <Typography variant="h5" fontWeight={700} letterSpacing="-0.5px">Create your account</Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            Join FundooNotes today
          </Typography>
        </Box>
        <RegisterForm />
        <Divider sx={{ my: 2.5 }} />
        <Typography variant="body2" textAlign="center">
          Already have an account?{' '}
          <Link component={RouterLink} to={ROUTES.LOGIN} underline="hover" fontWeight={500}>
            Sign in
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
}
