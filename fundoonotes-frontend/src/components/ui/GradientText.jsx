import React, { useState } from 'react';
import Typography from '@mui/material/Typography';
import { styled, keyframes } from '@mui/material/styles';

const shimmer = keyframes`
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
`;

const StyledText = styled(Typography, {
  shouldForwardProp: (prop) => !['hovered', 'duration'].includes(prop),
})(({ theme, hovered, duration = 0.8 }) => ({
  background: hovered
    ? 'linear-gradient(90deg, #1a73e8 0%, #8b5cf6 25%, #ec4899 50%, #8b5cf6 75%, #1a73e8 100%)'
    : theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, #8ab4f8 0%, #c084fc 100%)'
    : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)',
  backgroundSize: hovered ? '200% auto' : '100% auto',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  transition: `background ${duration}s ease, background-size ${duration}s ease`,
  animation: hovered ? `${shimmer} 2s linear infinite` : 'none',
  cursor: 'default',
  userSelect: 'none',
  fontWeight: 700,
  letterSpacing: '-0.05em',
  display: 'inline-block',
}));

/**
 * GradientText
 * 
 * An animated gradient text component that shimmers on hover.
 * Works seamlessly with MUI theme and typography system.
 */
export default function GradientText({ 
  children, 
  variant = 'h1',
  duration = 0.8,
  component,
  ...props 
}) {
  const [hovered, setHovered] = useState(false);

  return (
    <StyledText
      variant={variant}
      component={component || variant}
      hovered={hovered}
      duration={duration}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      {...props}
    >
      {children}
    </StyledText>
  );
}
