import React from 'react';
import Masonry from 'react-masonry-css';
import SkeletonCard from '@/components/common/SkeletonCard';
import EmptyState from '@/components/common/EmptyState';
import ErrorState from '@/components/common/ErrorState';
import NoteCard from './NoteCard';
import './NotesGrid.css';

const BREAKPOINT_COLS = {
  default: 4,
  1280: 3,
  960: 2,
  600: 1,
};

export default function NotesGrid({
  notes,
  isLoading,
  isError,
  onRetry,
  emptyMessage = 'Your notes will appear here',
  onNoteClick,
  onArchive,
  onTrash,
  onShare,
  isShared = false,
  getAccessLevel,
}) {
  if (isLoading) {
    return (
      <Masonry breakpointCols={BREAKPOINT_COLS} className="masonry-grid" columnClassName="masonry-column">
        {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
      </Masonry>
    );
  }

  if (isError) {
    return <ErrorState onRetry={onRetry} />;
  }

  if (notes.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <Masonry breakpointCols={BREAKPOINT_COLS} className="masonry-grid" columnClassName="masonry-column">
      {notes.map((note) => (
        <NoteCard
          key={note.id}
          note={note}
          onClick={onNoteClick}
          onArchive={onArchive}
          onTrash={onTrash}
          onShare={onShare}
          isShared={isShared}
          accessLevel={getAccessLevel?.(note)}
        />
      ))}
    </Masonry>
  );
}
