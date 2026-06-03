import { http, HttpResponse } from 'msw';

const DJANGO = 'http://localhost:8000';
const COLLAB = 'http://localhost:8001';

// ── Auth ──────────────────────────────────────────────────────────────────────
const authHandlers = [
  http.post(`${DJANGO}/api/users/register/`, () =>
    HttpResponse.json({ message: 'Registered', payload: null, status: 201 }, { status: 201 }),
  ),
  http.post(`${DJANGO}/api/users/login/`, () =>
    HttpResponse.json({ message: 'OTP sent', payload: null, status: 200 }),
  ),
  http.post(`${DJANGO}/api/users/login/verify-otp/`, () =>
    HttpResponse.json({
      message: 'OK',
      payload: { access: 'access-token', refresh: 'refresh-token' },
      status: 200,
    }),
  ),
  http.post(`${DJANGO}/api/users/logout/`, () =>
    HttpResponse.json({ message: 'Logged out', payload: null, status: 200 }),
  ),
  http.get(`${DJANGO}/api/users/verify-email/`, () =>
    HttpResponse.json({ message: 'Verified', payload: null, status: 200 }),
  ),
  http.post(`${DJANGO}/api/users/reset-password/`, () =>
    HttpResponse.json({ message: 'Email sent', payload: null, status: 200 }),
  ),
  http.post(`${DJANGO}/api/users/reset-password-confirm/`, () =>
    HttpResponse.json({ message: 'Password reset', payload: null, status: 200 }),
  ),
  http.get(`${DJANGO}/api/users/profile/`, () =>
    HttpResponse.json({
      message: 'OK',
      payload: { id: 1, username: 'testuser', email: 'test@example.com', phone_number: '+1234567890', is_verified: true, created_at: '' },
      status: 200,
    }),
  ),
  http.put(`${DJANGO}/api/users/profile/`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      message: 'Updated',
      payload: { id: 1, ...body, is_verified: true, created_at: '' },
      status: 200,
    });
  }),
  http.post(`${DJANGO}/api/token/refresh/`, () =>
    HttpResponse.json({ access: 'new-access-token' }),
  ),
];

// ── Notes ─────────────────────────────────────────────────────────────────────
const notesHandlers = [
  http.get(`${DJANGO}/api/notes/`, () =>
    HttpResponse.json({ message: 'OK', payload: [], status: 200 }),
  ),
  http.post(`${DJANGO}/api/notes/`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      message: 'Created',
      payload: { id: 1, ...body, is_archived: false, is_trashed: false, labels: [], created_at: '', updated_at: '' },
      status: 201,
    }, { status: 201 });
  }),
  http.patch(`${DJANGO}/api/notes/:id/`, async ({ request, params }) => {
    const body = await request.json();
    return HttpResponse.json({
      message: 'Updated',
      payload: { id: Number(params.id), title: '', content: '', color: 'default', is_archived: false, is_trashed: false, labels: [], created_at: '', updated_at: '', ...body },
      status: 200,
    });
  }),
  http.delete(`${DJANGO}/api/notes/:id/`, () =>
    new HttpResponse(null, { status: 204 }),
  ),
];

// ── Labels ────────────────────────────────────────────────────────────────────
const labelsHandlers = [
  http.get(`${DJANGO}/api/labels/`, () =>
    HttpResponse.json({ message: 'OK', payload: [], status: 200 }),
  ),
  http.post(`${DJANGO}/api/labels/`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      message: 'Created',
      payload: { id: 1, title: body.title, created_at: '', updated_at: '' },
      status: 201,
    }, { status: 201 });
  }),
  http.patch(`${DJANGO}/api/labels/:id/`, async ({ request, params }) => {
    const body = await request.json();
    return HttpResponse.json({
      message: 'Updated',
      payload: { id: Number(params.id), title: body.title, created_at: '', updated_at: '' },
      status: 200,
    });
  }),
  http.delete(`${DJANGO}/api/labels/:id/`, () =>
    new HttpResponse(null, { status: 204 }),
  ),
];

// ── Collab ────────────────────────────────────────────────────────────────────
const collabHandlers = [
  http.get(`${COLLAB}/notes/shared`, () => HttpResponse.json([])),
  http.get(`${COLLAB}/notes/:id/collaborators`, () => HttpResponse.json([])),
  http.post(`${COLLAB}/notes/:id/collaborators`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ user_id: 2, username: 'other', email: body.collaborator_email, access_level: body.access_level, created_at: '' }, { status: 201 });
  }),
  http.patch(`${COLLAB}/notes/:id/collaborators/:userId`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ user_id: 2, username: 'other', email: 'other@example.com', access_level: body.access_level, created_at: '' });
  }),
  http.delete(`${COLLAB}/notes/:id/collaborators/:userId`, () =>
    new HttpResponse(null, { status: 204 }),
  ),
  http.patch(`${COLLAB}/notes/:id/content`, () =>
    HttpResponse.json({ message: 'Updated' }),
  ),
];

export const handlers = [
  ...authHandlers,
  ...notesHandlers,
  ...labelsHandlers,
  ...collabHandlers,
];
