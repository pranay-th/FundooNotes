import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import InputBase from '@mui/material/InputBase';
import Box from '@mui/material/Box';
import Avatar from '@mui/material/Avatar';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import MenuIcon from '@mui/icons-material/Menu';
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import LogoutIcon from '@mui/icons-material/Logout';
import { alpha, useTheme as useMuiTheme } from '@mui/material/styles';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import * as authApi from '@/api/authApi';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';

export default function TopNav({ onMenuClick, searchQuery, onSearchChange, onSearchClear }) {
  const { mode, toggleTheme } = useTheme();
  const { user, logout, refreshToken } = useAuth();
  const muiTheme = useMuiTheme();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const isDark = mode === 'dark';

  const handleLogout = async () => {
    setAnchorEl(null);
    try {
      if (refreshToken) await authApi.logout(refreshToken);
    } finally {
      logout();
      navigate(ROUTES.LOGIN);
    }
  };

  return (
    <AppBar position="static" elevation={0} sx={{ height: 64, color: 'text.primary' }}>
      <Toolbar sx={{ gap: 1, minHeight: '64px !important', px: { xs: 1, sm: 2 } }}>

        {/* Hamburger */}
        <IconButton onClick={onMenuClick} edge="start" aria-label="toggle sidebar" sx={{ mr: 0.5, color: 'text.secondary' }}>
          <MenuIcon />
        </IconButton>

        {/* Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2, flexShrink: 0 }}>
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #1a73e8 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(26,115,232,0.4)',
              flexShrink: 0,
            }}
          >
            <Typography sx={{ color: '#fff', fontSize: 16, fontWeight: 700, lineHeight: 1 }}>F</Typography>
          </Box>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              fontSize: 20,
              background: isDark
                ? 'linear-gradient(135deg, #8ab4f8 0%, #c084fc 100%)'
                : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              display: { xs: 'none', sm: 'block' },
              letterSpacing: '-0.5px',
            }}
          >
            FundooNotes
          </Typography>
        </Box>

        {/* Search bar */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            bgcolor: isDark
              ? alpha(muiTheme.palette.common.white, 0.07)
              : alpha(muiTheme.palette.common.black, 0.06),
            borderRadius: 3,
            px: 2,
            py: 0.75,
            flex: 1,
            maxWidth: 700,
            mx: 'auto',
            border: '1px solid transparent',
            transition: 'all 0.2s ease',
            '&:focus-within': {
              bgcolor: isDark ? alpha(muiTheme.palette.common.white, 0.1) : '#fff',
              borderColor: muiTheme.palette.primary.main,
              boxShadow: `0 2px 12px ${alpha(muiTheme.palette.primary.main, 0.15)}`,
            },
            '&:hover:not(:focus-within)': {
              bgcolor: isDark
                ? alpha(muiTheme.palette.common.white, 0.1)
                : alpha(muiTheme.palette.common.black, 0.08),
            },
          }}
        >
          <SearchIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 20, flexShrink: 0 }} />
          <InputBase
            placeholder="Search notes…"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            fullWidth
            inputProps={{ 'aria-label': 'search notes' }}
            sx={{ fontSize: 15 }}
          />
          {searchQuery && (
            <IconButton size="small" onClick={onSearchClear} aria-label="clear search" sx={{ ml: 0.5, p: 0.25 }}>
              <CloseIcon sx={{ fontSize: 18 }} />
            </IconButton>
          )}
        </Box>

        {/* Right actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 1 }}>
          <Tooltip title={isDark ? 'Light mode' : 'Dark mode'}>
            <IconButton onClick={toggleTheme} aria-label="toggle theme" sx={{ color: 'text.secondary' }}>
              {isDark ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Tooltip>

          <Tooltip title={user?.username ?? 'Account'}>
            <IconButton
              onClick={(e) => setAnchorEl(e.currentTarget)}
              aria-label="account menu"
              sx={{ p: 0.5 }}
            >
              <Avatar
                sx={{
                  width: 34,
                  height: 34,
                  background: 'linear-gradient(135deg, #1a73e8 0%, #8b5cf6 100%)',
                  fontSize: 14,
                  fontWeight: 700,
                  boxShadow: '0 2px 8px rgba(26,115,232,0.3)',
                }}
              >
                {user?.username?.[0]?.toUpperCase() ?? 'U'}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          PaperProps={{
            elevation: 4,
            sx: { borderRadius: 3, minWidth: 200, mt: 0.5, overflow: 'hidden' },
          }}
        >
          <Box sx={{ px: 2, py: 1.5 }}>
            <Typography variant="subtitle2">{user?.username}</Typography>
            <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
          </Box>
          <Divider />
          <MenuItem
            onClick={() => { setAnchorEl(null); navigate(ROUTES.PROFILE); }}
            sx={{ gap: 1.5, py: 1.25 }}
          >
            <PersonOutlineIcon fontSize="small" color="action" />
            <Typography variant="body2">Profile</Typography>
          </MenuItem>
          <MenuItem onClick={handleLogout} sx={{ gap: 1.5, py: 1.25, color: 'error.main' }}>
            <LogoutIcon fontSize="small" />
            <Typography variant="body2">Sign out</Typography>
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}
