import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { filterNotesByQuery } from '../../src/utils/searchFilter';

const noteColorArb = fc.constantFrom(
  'default', 'red', 'orange', 'yellow', 'green',
  'teal', 'blue', 'purple', 'pink', 'brown', 'gray',
);

const noteArb = fc.record({
  id: fc.integer({ min: 1 }),
  title: fc.string(),
  content: fc.string(),
  color: noteColorArb,
  is_archived: fc.boolean(),
  is_trashed: fc.boolean(),
  labels: fc.array(fc.record({
    id: fc.integer({ min: 1 }),
    title: fc.string(),
    created_at: fc.string(),
    updated_at: fc.string(),
  })),
  created_at: fc.string(),
  updated_at: fc.string(),
});

describe('filterNotesByQuery — property tests', () => {
  // P3a: result is a subset of input
  it('P3a: result is always a subset of the input array', () => {
    fc.assert(
      fc.property(fc.array(noteArb), fc.string(), (notes, query) => {
        const result = filterNotesByQuery(notes, query);
        expect(result.every((n) => notes.includes(n))).toBe(true);
      }),
    );
  });

  // P3b: empty query returns all notes unchanged
  it('P3b: empty or whitespace-only query returns the original array', () => {
    fc.assert(
      fc.property(fc.array(noteArb), fc.constantFrom('', '   ', '\t'), (notes, query) => {
        const result = filterNotesByQuery(notes, query);
        expect(result).toBe(notes); // same reference
      }),
    );
  });

  // P3c: no false positives — every returned note matches the query
  it('P3c: no false positives — every result matches the query', () => {
    fc.assert(
      fc.property(fc.array(noteArb), fc.string({ minLength: 1 }), (notes, query) => {
        const q = query.trim().toLowerCase();
        if (!q) return;
        const result = filterNotesByQuery(notes, query);
        result.forEach((note) => {
          const matches =
            note.title.toLowerCase().includes(q) ||
            note.content.toLowerCase().includes(q);
          expect(matches).toBe(true);
        });
      }),
    );
  });

  // P3d: no false negatives — every matching note is in the result
  it('P3d: no false negatives — all matching notes are included', () => {
    fc.assert(
      fc.property(fc.array(noteArb), fc.string({ minLength: 1 }), (notes, query) => {
        const q = query.trim().toLowerCase();
        if (!q) return;
        const result = filterNotesByQuery(notes, query);
        const resultIds = new Set(result.map((n) => n.id));
        notes.forEach((note) => {
          const matches =
            note.title.toLowerCase().includes(q) ||
            note.content.toLowerCase().includes(q);
          if (matches) {
            expect(resultIds.has(note.id)).toBe(true);
          }
        });
      }),
    );
  });

  // P3e: order is preserved
  it('P3e: result preserves the original ordering', () => {
    fc.assert(
      fc.property(fc.array(noteArb), fc.string(), (notes, query) => {
        const result = filterNotesByQuery(notes, query);
        const resultIds = result.map((n) => n.id);
        const expectedIds = notes
          .filter((n) => result.includes(n))
          .map((n) => n.id);
        expect(resultIds).toEqual(expectedIds);
      }),
    );
  });
});
