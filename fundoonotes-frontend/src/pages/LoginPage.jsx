import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Divider from '@mui/material/Divider';
import { Link as RouterLink } from 'react-router-dom';
import { useTheme as useMuiTheme } from '@mui/material/styles';
import LoginForm from '@/components/auth/LoginForm';
import OtpForm from '@/components/auth/OtpForm';
import { ROUTES } from '@/utils/constants';

export default function LoginPage() {
  const [step, setStep] = useState('credentials');
  const [pendingEmail, setPendingEmail] = useState('');
  const muiTheme = useMuiTheme();
  const isDark = muiTheme.palette.mode === 'dark';

  const handleLoginSuccess = (email) => {
    setPendingEmail(email);
    setStep('otp');
  };

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
      }}
    >
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, sm: 4.5 },
          width: '100%',
          maxWidth: 420,
          borderRadius: 4,
          border: '1px solid',
          borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
          boxShadow: isDark
            ? '0 24px 64px rgba(0,0,0,0.4)'
            : '0 24px 64px rgba(0,0,0,0.08)',
        }}
      >
        {/* Logo */}
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
          <Typography
            variant="h5"
            sx={{
              background: isDark
                ? 'linear-gradient(135deg, #8ab4f8 0%, #c084fc 100%)'
                : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              fontWeight: 700,
              letterSpacing: '-0.5px',
            }}
          >
            FundooNotes
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            {step === 'credentials' ? 'Sign in to your account' : 'Check your inbox'}
          </Typography>
        </Box>

        {step === 'credentials' ? (
          <>
            <LoginForm onSuccess={handleLoginSuccess} />
            <Divider sx={{ my: 2.5 }} />
            <Box display="flex" justifyContent="space-between">
              <Link component={RouterLink} to={ROUTES.RESET_PASSWORD} variant="body2" underline="hover">
                Forgot password?
              </Link>
              <Link component={RouterLink} to={ROUTES.REGISTER} variant="body2" underline="hover">
                Create account
              </Link>
            </Box>
          </>
        ) : (
          <OtpForm email={pendingEmail} />
        )}
      </Paper>
    </Box>
  );
}
