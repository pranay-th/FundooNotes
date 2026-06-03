import * as yup from 'yup';

export const registerSchema = yup.object({
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters')
    .max(150, 'Username must be at most 150 characters'),
  email: yup
    .string()
    .required('Email is required')
    .email('Enter a valid email address'),
  phone_number: yup
    .string()
    .required('Phone number is required')
    .matches(/^\+?[1-9]\d{6,14}$/, 'Enter a valid phone number'),
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters'),
});

export const loginSchema = yup.object({
  email: yup
    .string()
    .required('Email is required')
    .email('Enter a valid email address'),
  password: yup
    .string()
    .required('Password is required'),
});

export const otpSchema = yup.object({
  otp: yup
    .string()
    .required('OTP is required')
    .matches(/^\d{6}$/, 'OTP must be a 6-digit number'),
});

export const noteSchema = yup.object({
  title: yup.string().max(255, 'Title must be at most 255 characters'),
  content: yup.string(),
}).test(
  'title-or-content',
  'Please add a title or some content',
  (value) => Boolean(value.title?.trim() || value.content?.trim()),
);

export const inviteCollaboratorSchema = yup.object({
  collaborator_email: yup
    .string()
    .required('Email is required')
    .email('Enter a valid email address'),
  access_level: yup
    .string()
    .required('Access level is required')
    .oneOf(['read', 'read_write'], 'Invalid access level'),
});
