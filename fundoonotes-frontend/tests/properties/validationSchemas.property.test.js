import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import {
  registerSchema,
  loginSchema,
  otpSchema,
  noteSchema,
  inviteCollaboratorSchema,
} from '../../src/utils/validationSchemas';

describe('Validation schemas — property tests (Property 6)', () => {
  // Register schema
  it('registerSchema rejects when any required field is missing', () => {
    fc.assert(
      fc.property(
        fc.record({
          username: fc.oneof(fc.constant(''), fc.constant(undefined)),
          email: fc.string(),
          phone_number: fc.string(),
          password: fc.string(),
        }),
        (input) => {
          expect(registerSchema.isValidSync(input)).toBe(false);
        },
      ),
    );
  });

  it('registerSchema accepts valid input', () => {
    fc.assert(
      fc.property(
        fc.record({
          username: fc.string({ minLength: 3, maxLength: 50 }).filter((s) => /^[a-zA-Z0-9_]+$/.test(s)),
          email: fc.emailAddress(),
          phone_number: fc.constant('+12345678901'),
          password: fc.string({ minLength: 8 }),
        }),
        (input) => {
          expect(registerSchema.isValidSync(input)).toBe(true);
        },
      ),
    );
  });

  // Login schema
  it('loginSchema rejects empty email', () => {
    fc.assert(
      fc.property(fc.string({ minLength: 8 }), (password) => {
        expect(loginSchema.isValidSync({ email: '', password })).toBe(false);
      }),
    );
  });

  it('loginSchema accepts valid email + password', () => {
    fc.assert(
      fc.property(fc.emailAddress(), fc.string({ minLength: 1 }), (email, password) => {
        expect(loginSchema.isValidSync({ email, password })).toBe(true);
      }),
    );
  });

  // OTP schema
  it('otpSchema rejects non-6-digit strings', () => {
    fc.assert(
      fc.property(
        fc.string().filter((s) => !/^\d{6}$/.test(s)),
        (otp) => {
          expect(otpSchema.isValidSync({ otp })).toBe(false);
        },
      ),
    );
  });

  it('otpSchema accepts exactly 6 digits', () => {
    fc.assert(
      fc.property(
        fc.stringMatching(/^\d{6}$/),
        (otp) => {
          expect(otpSchema.isValidSync({ otp })).toBe(true);
        },
      ),
    );
  });

  // Note schema
  it('noteSchema rejects when both title and content are empty', () => {
    expect(noteSchema.isValidSync({ title: '', content: '' })).toBe(false);
    expect(noteSchema.isValidSync({ title: '  ', content: '  ' })).toBe(false);
  });

  it('noteSchema accepts when title is non-empty', () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }), (title) => {
        expect(noteSchema.isValidSync({ title: title.trim() || 'x', content: '' })).toBe(true);
      }),
    );
  });

  // InviteCollaborator schema
  it('inviteCollaboratorSchema rejects invalid email', () => {
    fc.assert(
      fc.property(
        fc.string().filter((s) => !s.includes('@')),
        (email) => {
          expect(
            inviteCollaboratorSchema.isValidSync({ collaborator_email: email, access_level: 'read' }),
          ).toBe(false);
        },
      ),
    );
  });

  it('inviteCollaboratorSchema accepts valid email + access_level', () => {
    fc.assert(
      fc.property(
        fc.emailAddress(),
        fc.constantFrom('read', 'read_write'),
        (email, access_level) => {
          expect(
            inviteCollaboratorSchema.isValidSync({ collaborator_email: email, access_level }),
          ).toBe(true);
        },
      ),
    );
  });
});
