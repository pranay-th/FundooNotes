import React from 'react';
import Box from '@mui/material/Box';
import { useTheme } from '@mui/material/styles';

/**
 * DitheredBackground
 *
 * Full-page background with a scenic image + dithered dot-matrix overlay.
 * The image is fixed so it doesn't scroll with content.
 * A semi-transparent frosted overlay keeps text legible in both light/dark modes.
 *
 * Applied at layout level so it spans the entire viewport behind nav and sidebar.
 */
export default function DitheredBackground({ children, ...props }) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  // Unsplash: misty mountain forest — calm, neutral tones that work in both modes
  const IMAGE_URL =
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?q=80&w=2070&auto=format&fit=crop';

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100%',
        // The ::before holds the background image (fixed, full-viewport)
        '&::before': {
          content: '""',
          position: 'fixed',
          inset: 0,
          zIndex: 0,
          backgroundImage: `url("${IMAGE_URL}")`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          // Dithered dot-matrix pattern sits on top of the image
          backgroundBlendMode: 'normal',
          // Frosted glass tint so text stays readable
          filter: isDark ? 'brightness(0.35) saturate(0.7)' : 'brightness(0.75) saturate(0.85)',
        },
        // ::after adds the dithered dot grid over the image
        '&::after': {
          content: '""',
          position: 'fixed',
          inset: 0,
          zIndex: 1,
          pointerEvents: 'none',
          backgroundImage: isDark
            ? 'radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)'
            : 'radial-gradient(circle, rgba(0,0,0,0.08) 1px, transparent 1px)',
          backgroundSize: '6px 6px',
        },
      }}
      {...props}
    >
      {/* Content sits above both layers */}
      <Box sx={{ position: 'relative', zIndex: 2 }}>
        {children}
      </Box>
    </Box>
  );
}
