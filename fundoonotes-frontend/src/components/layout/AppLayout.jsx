import React, { Component } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { Outlet, useNavigate } from 'react-router-dom';
import TopNav from './TopNav';
import Sidebar from './Sidebar';
import { useUI } from '@/context/UIContext';
import { useLabels } from '@/hooks/useLabels';
import { ROUTES } from '@/utils/constants';
import ChatbotFAB from '@/components/chatbot/ChatbotFAB';

const SIDEBAR_EXPANDED = 240;
const SIDEBAR_COLLAPSED = 64;
const TOPNAV_HEIGHT = 64;

// ── Error Boundary ────────────────────────────────────────────────────────────
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return (
        <Box p={4} textAlign="center">
          <Typography variant="h6" gutterBottom>Something went wrong.</Typography>
          <Button variant="outlined" onClick={() => window.location.reload()}>
            Reload page
          </Button>
        </Box>
      );
    }
    return this.props.children;
  }
}

export default function AppLayout() {
  const { sidebarOpen, setSidebarOpen, searchQuery, setSearchQuery, setActiveLabelId } = useUI();
  const { data: labels = [] } = useLabels();
  const navigate = useNavigate();

  const sidebarWidth = sidebarOpen ? SIDEBAR_EXPANDED : SIDEBAR_COLLAPSED;

  const handleLabelClick = (id) => {
    setActiveLabelId(id);
    navigate(ROUTES.LABEL(id));
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Fixed top nav */}
      <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1200 }}>
        <TopNav
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearchClear={() => setSearchQuery('')}
        />
      </Box>

      {/* Body below top nav */}
      <Box sx={{ display: 'flex', flex: 1, mt: `${TOPNAV_HEIGHT}px` }}>
        {/* Fixed sidebar */}
        <Box
          sx={{
            position: 'fixed',
            top: TOPNAV_HEIGHT,
            left: 0,
            bottom: 0,
            width: sidebarWidth,
            transition: 'width 0.2s ease',
            zIndex: 1100,
            bgcolor: 'background.default',
            overflowX: 'hidden',
          }}
        >
          <Sidebar
            open={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            labels={labels}
            activeLabelId={null}
            onLabelClick={handleLabelClick}
          />
        </Box>

        {/* Main content — offset by sidebar width */}
        <Box
          component="main"
          sx={{
            flex: 1,
            ml: `${sidebarWidth}px`,
            transition: 'margin-left 0.2s ease',
            p: { xs: 2, sm: 3 },
            minWidth: 0,
          }}
        >
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </Box>
      </Box>

      {/* AI chatbot floating action button — available on all protected pages */}
      <ChatbotFAB />
    </Box>
  );
}
