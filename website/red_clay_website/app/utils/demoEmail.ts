export const DEMO_EMAIL_COOKIE = 'red_clay_demo_email'
export const DEMO_EMAIL_MAX_AGE = 7 * 24 * 60 * 60

export function isValidEmail(value: string): boolean {
  const email = value.trim().toLowerCase()
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)
}

export function normalizeEmail(value: string): string {
  return value.trim().toLowerCase()
}
