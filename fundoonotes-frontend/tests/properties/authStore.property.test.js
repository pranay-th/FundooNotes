import { describe, it, expect, beforeEach } from 'vitest';
import * as fc from 'fast-check';
import {
  setTokens,
  clearTokens,
  getAccessToken,
  getRefreshToken,
  getUser,
} from '../../src/utils/tokenStorage';
import { LOCAL_STORAGE_KEYS } from '../../src/utils/constants';

const tokenArb = fc.record({
  access: fc.string({ minLength: 10 }),
  refresh: fc.string({ minLength: 10 }),
});

const userArb = fc.record({
  id: fc.integer({ min: 1 }),
  username: fc.string({ minLength: 1 }),
  email: fc.emailAddress(),
  phone_number: fc.string({ minLength: 7 }),
  is_verified: fc.boolean(),
  created_at: fc.string(),
});

describe('Auth token storage — property tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  // P1: login persists tokens to localStorage exactly
  it('P1: setTokens persists access token, refresh token, and user to localStorage', () => {
    fc.assert(
      fc.property(tokenArb, userArb, (tokens, user) => {
        setTokens(tokens, user);
        expect(getAccessToken()).toBe(tokens.access);
        expect(getRefreshToken()).toBe(tokens.refresh);
        expect(getUser()).toEqual(user);
        expect(localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN)).toBe(tokens.access);
        expect(localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN)).toBe(tokens.refresh);
      }),
    );
  });

  // P1b: clearTokens removes all auth keys
  it('P1b: clearTokens removes all auth keys from localStorage', () => {
    fc.assert(
      fc.property(tokenArb, userArb, (tokens, user) => {
        setTokens(tokens, user);
        clearTokens();
        expect(getAccessToken()).toBeNull();
        expect(getRefreshToken()).toBeNull();
        expect(getUser()).toBeNull();
        expect(localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN)).toBeNull();
        expect(localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN)).toBeNull();
        expect(localStorage.getItem(LOCAL_STORAGE_KEYS.USER)).toBeNull();
      }),
    );
  });
});
