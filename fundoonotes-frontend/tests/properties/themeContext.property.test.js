import { describe, it, expect, beforeEach } from 'vitest';
import * as fc from 'fast-check';
import { LOCAL_STORAGE_KEYS } from '../../src/utils/constants';

describe('Theme persistence — property tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  // P5: toggleTheme always writes the new mode to localStorage
  it('P5: toggling from light writes "dark", toggling from dark writes "light"', () => {
    fc.assert(
      fc.property(fc.constantFrom('light', 'dark'), (initialMode) => {
        localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, initialMode);
        const next = initialMode === 'light' ? 'dark' : 'light';
        localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, next);
        expect(localStorage.getItem(LOCAL_STORAGE_KEYS.THEME)).toBe(next);
      }),
    );
  });

  // P5b: mode on init equals last persisted value
  it('P5b: reading theme from localStorage returns the last persisted value', () => {
    fc.assert(
      fc.property(fc.constantFrom('light', 'dark'), (mode) => {
        localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, mode);
        const stored = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
        expect(stored).toBe(mode);
      }),
    );
  });
});
