import React, { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import ArchiveOutlinedIcon from '@mui/icons-material/ArchiveOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import UnarchiveOutlinedIcon from '@mui/icons-material/UnarchiveOutlined';
import { useTheme as useMuiTheme } from '@mui/material/styles';
import { NOTE_COLORS } from '@/theme/colors';

export default function NoteCard({
  note,
  onClick,
  onArchive,
  onTrash,
  onShare,
  isShared = false,
  isArchivePage = false,
  accessLevel,
}) {
  const muiTheme = useMuiTheme();
  const isDark = muiTheme.palette.mode === 'dark';
  const colorDef = NOTE_COLORS.find((c) => c.value === note.color);
  const bgColor = colorDef && note.color !== 'default'
    ? (isDark ? colorDef.dark : colorDef.light)
    : undefined;

  const [hovered, setHovered] = useState(false);

  return (
    <Card
      onClick={() => onClick(note)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      sx={{
        bgcolor: bgColor
          ? (isDark ? `${bgColor}cc` : `${bgColor}dd`)
          : (isDark ? 'rgba(30, 30, 30, 0.72)' : 'rgba(255, 255, 255, 0.72)'),
        backdropFilter: 'blur(12px) saturate(160%)',
        cursor: 'pointer',
        mb: 2,
        borderRadius: 3,
        border: '1px solid',
        borderColor: hovered
          ? (isDark ? 'rgba(255,255,255,0.28)' : 'rgba(0,0,0,0.22)')
          : (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.6)'),
        boxShadow: hovered
          ? (isDark
              ? '0 8px 32px rgba(0,0,0,0.5), 0 1px 4px rgba(0,0,0,0.3)'
              : '0 8px 32px rgba(0,0,0,0.14), 0 1px 4px rgba(0,0,0,0.06)')
          : (isDark
              ? '0 2px 8px rgba(0,0,0,0.3)'
              : '0 2px 8px rgba(0,0,0,0.06)'),
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        transition: 'transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease',
        position: 'relative',
        overflow: 'visible',
      }}
    >
      {/* Color accent strip on the top edge */}
      {note.color !== 'default' && colorDef && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 16,
            right: 16,
            height: 3,
            borderRadius: '0 0 3px 3px',
            bgcolor: isDark ? colorDef.light : colorDef.dark,
            opacity: 0.6,
          }}
        />
      )}

      <CardContent sx={{ pb: '4px !important', pt: note.color !== 'default' ? 2 : 1.5, px: 2 }}>
        {note.title && (
          <Typography
            variant="subtitle2"
            fontWeight={600}
            gutterBottom
            sx={{ fontSize: 15, lineHeight: 1.4, color: 'text.primary' }}
          >
            {note.title}
          </Typography>
        )}
        {note.content && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              display: '-webkit-box',
              WebkitLineClamp: 10,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              whiteSpace: 'pre-wrap',
              fontSize: 13.5,
              lineHeight: 1.55,
            }}
          >
            {note.content}
          </Typography>
        )}
        {note.labels.length > 0 && (
          <Box display="flex" flexWrap="wrap" gap={0.5} mt={1.25}>
            {note.labels.map((l) => (
              <Chip
                key={l.id}
                label={l.title}
                size="small"
                sx={{
                  height: 22,
                  fontSize: 11,
                  fontWeight: 500,
                  bgcolor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(26,115,232,0.08)',
                  color: isDark ? 'rgba(255,255,255,0.7)' : 'primary.dark',
                  border: '1px solid',
                  borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(26,115,232,0.2)',
                  borderRadius: '6px',
                }}
              />
            ))}
          </Box>
        )}
        {isShared && accessLevel && (
          <Chip
            label={accessLevel === 'read' ? '👁 Read only' : '✏ Can edit'}
            size="small"
            sx={{
              mt: 0.75,
              height: 22,
              fontSize: 11,
              fontWeight: 500,
              bgcolor: accessLevel === 'read'
                ? 'rgba(251,188,4,0.12)'
                : 'rgba(26,115,232,0.1)',
              color: accessLevel === 'read' ? 'warning.dark' : 'primary.main',
              border: '1px solid',
              borderColor: accessLevel === 'read'
                ? 'rgba(251,188,4,0.3)'
                : 'rgba(26,115,232,0.2)',
            }}
          />
        )}
      </CardContent>

      {/* Action bar — visible on hover */}
      <CardActions
        sx={{
          opacity: hovered ? 1 : 0,
          transform: hovered ? 'translateY(0)' : 'translateY(4px)',
          transition: 'opacity 0.18s ease, transform 0.18s ease',
          pt: 0,
          pb: 0.75,
          px: 1,
          minHeight: 36,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <Tooltip title={isArchivePage ? 'Unarchive' : 'Archive'}>
          <IconButton
            size="small"
            onClick={() => onArchive(note.id)}
            aria-label={isArchivePage ? 'unarchive note' : 'archive note'}
            sx={{ color: 'text.secondary', '&:hover': { color: 'primary.main', bgcolor: 'action.hover' } }}
          >
            {isArchivePage
              ? <UnarchiveOutlinedIcon sx={{ fontSize: 17 }} />
              : <ArchiveOutlinedIcon sx={{ fontSize: 17 }} />}
          </IconButton>
        </Tooltip>
        {!isShared && (
          <Tooltip title="Delete">
            <IconButton
              size="small"
              onClick={() => onTrash(note.id)}
              aria-label="delete note"
              sx={{ color: 'text.secondary', '&:hover': { color: 'error.main', bgcolor: 'rgba(211,47,47,0.06)' } }}
            >
              <DeleteOutlinedIcon sx={{ fontSize: 17 }} />
            </IconButton>
          </Tooltip>
        )}
        {onShare && (
          <Tooltip title="Share">
            <IconButton
              size="small"
              onClick={() => onShare(note)}
              aria-label="share note"
              sx={{ color: 'text.secondary', '&:hover': { color: 'primary.main', bgcolor: 'action.hover' } }}
            >
              <PersonAddOutlinedIcon sx={{ fontSize: 17 }} />
            </IconButton>
          </Tooltip>
        )}
      </CardActions>
    </Card>
  );
}
