import { djangoClient } from './axiosInstances';

export async function register(payload) {
  await djangoClient.post('/api/users/register/', payload);
}

export async function login(payload) {
  // Backend LoginSerializer uses 'username' field for the email value
  await djangoClient.post('/api/users/login/', {
    username: payload.email,
    password: payload.password,
  });
}

export async function verifyOtp(payload) {
  // Backend OTPVerifySerializer uses 'username' field for the email value
  const { data } = await djangoClient.post(
    '/api/users/login/verify-otp/',
    { username: payload.email, otp: payload.otp },
  );
  return data.payload;
}

export async function logout(refreshToken) {
  await djangoClient.post('/api/users/logout/', { refresh: refreshToken });
}

export async function verifyEmail(token) {
  await djangoClient.get(`/api/users/verify-email/?token=${token}`);
}

export async function resetPassword(email) {
  await djangoClient.post('/api/users/reset-password/', { email });
}

export async function resetPasswordConfirm(token, password) {
  await djangoClient.post('/api/users/reset-password-confirm/', { token, password });
}

export async function getProfile() {
  const { data } = await djangoClient.get('/api/users/profile/');
  return data.payload;
}

export async function getProfileWithToken(accessToken) {
  const { data } = await djangoClient.get('/api/users/profile/', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return data.payload;
}

export async function updateProfile(payload) {
  const { data } = await djangoClient.put('/api/users/profile/', payload);
  return data.payload;
}
