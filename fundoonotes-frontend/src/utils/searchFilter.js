/**
 * filterNotesByQuery
 *
 * Filters a list of notes by a case-insensitive substring match against
 * each note's title and content.
 *
 * Preconditions:
 *   - notes is an array (may be empty)
 *   - query is a string (may be empty)
 * Postconditions:
 *   - IF query is empty or whitespace-only: returns the original notes array unchanged
 *   - IF query is non-empty: returns a subset of notes where
 *       note.title.toLowerCase().includes(q) OR note.content.toLowerCase().includes(q)
 *       where q = query.trim().toLowerCase()
 *   - The returned array preserves the original ordering of notes
 *   - No note in the returned array fails the match condition (no false positives)
 *   - No note that satisfies the match condition is absent from the result (no false negatives)
 */
export function filterNotesByQuery(notes, query) {
  const q = query.trim().toLowerCase();
  if (!q) return notes;
  return notes.filter(
    (note) =>
      note.title.toLowerCase().includes(q) ||
      note.content.toLowerCase().includes(q),
  );
}
