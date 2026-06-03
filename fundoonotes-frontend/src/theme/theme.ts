import { createTheme } from '@mui/material/styles';

const sharedTypography = {
  fontFamily: '"Google Sans", "Roboto", "Helvetica", "Arial", sans-serif',
  h5: { fontWeight: 600, letterSpacing: '-0.5px' },
  h6: { fontWeight: 600, letterSpacing: '-0.3px' },
  subtitle1: { fontWeight: 500 },
  subtitle2: { fontWeight: 600 },
  body2: { lineHeight: 1.55 },
  button: { textTransform: 'none' as const, fontWeight: 500, letterSpacing: '0.01em' },
};

const sharedShape = { borderRadius: 10 };

const sharedComponents = {
  MuiButton: {
    defaultProps: { disableElevation: true },
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '8px 20px',
        fontSize: '0.875rem',
      },
      containedPrimary: {
        background: 'linear-gradient(135deg, #1a73e8 0%, #1557b0 100%)',
        '&:hover': {
          background: 'linear-gradient(135deg, #1c7fe8 0%, #1a64c9 100%)',
          transform: 'translateY(-1px)',
          boxShadow: '0 4px 12px rgba(26,115,232,0.35)',
        },
        transition: 'transform 0.15s ease, box-shadow 0.15s ease',
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        backgroundImage: 'none',
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: 'none',
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 6,
        fontWeight: 500,
      },
    },
  },
  MuiTextField: {
    defaultProps: { variant: 'outlined' as const },
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
          '& fieldset': { transition: 'border-color 0.2s' },
        },
      },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 16,
        backgroundImage: 'none',
      },
    },
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        borderRadius: 6,
        fontSize: '0.75rem',
      },
    },
  },
};

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1a73e8',
      light: '#4a90e2',
      dark: '#1557b0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#fbbc04',
      light: '#fdd663',
      dark: '#b5850a',
    },
    background: {
      default: '#f0f4f9',
      paper: '#ffffff',
    },
    text: {
      primary: '#1a1c1e',
      secondary: '#5f6368',
    },
    divider: 'rgba(0,0,0,0.08)',
    action: {
      hover: 'rgba(26,115,232,0.06)',
      selected: 'rgba(26,115,232,0.1)',
    },
  },
  typography: sharedTypography,
  shape: sharedShape,
  components: {
    ...sharedComponents,
    MuiAppBar: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          backgroundColor: 'rgba(240,244,249,0.85)',
          borderBottom: '1px solid rgba(0,0,0,0.08)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '0 24px 24px 0',
          transition: 'background 0.15s ease',
          '&.Mui-selected': {
            background: 'linear-gradient(90deg, rgba(26,115,232,0.15) 0%, rgba(26,115,232,0.08) 100%)',
            borderLeft: '3px solid #1a73e8',
            paddingLeft: '13px',
            '&:hover': {
              background: 'linear-gradient(90deg, rgba(26,115,232,0.18) 0%, rgba(26,115,232,0.1) 100%)',
            },
          },
        },
      },
    },
  },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#8ab4f8',
      light: '#aecbfa',
      dark: '#669df6',
      contrastText: '#202124',
    },
    secondary: {
      main: '#fdd663',
      light: '#fde293',
      dark: '#fbbc04',
    },
    background: {
      default: '#131416',
      paper: '#1e2124',
    },
    text: {
      primary: '#e8eaed',
      secondary: '#9aa0a6',
    },
    divider: 'rgba(255,255,255,0.08)',
    action: {
      hover: 'rgba(138,180,248,0.08)',
      selected: 'rgba(138,180,248,0.14)',
    },
  },
  typography: sharedTypography,
  shape: sharedShape,
  components: {
    ...sharedComponents,
    MuiButton: {
      ...(sharedComponents.MuiButton ?? {}),
      styleOverrides: {
        ...(sharedComponents.MuiButton?.styleOverrides ?? {}),
        containedPrimary: {
          background: 'linear-gradient(135deg, #8ab4f8 0%, #669df6 100%)',
          color: '#202124',
          '&:hover': {
            background: 'linear-gradient(135deg, #aecbfa 0%, #8ab4f8 100%)',
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(138,180,248,0.3)',
          },
          transition: 'transform 0.15s ease, box-shadow 0.15s ease',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          backgroundColor: 'rgba(19,20,22,0.85)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '0 24px 24px 0',
          transition: 'background 0.15s ease',
          '&.Mui-selected': {
            background: 'linear-gradient(90deg, rgba(138,180,248,0.18) 0%, rgba(138,180,248,0.08) 100%)',
            borderLeft: '3px solid #8ab4f8',
            paddingLeft: '13px',
            '&:hover': {
              background: 'linear-gradient(90deg, rgba(138,180,248,0.22) 0%, rgba(138,180,248,0.12) 100%)',
            },
          },
        },
      },
    },
  },
});
