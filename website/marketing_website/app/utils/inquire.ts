import { isValidEmail } from './checkout'

export type InquirePayload = {
  name: string
  email: string
  company: string
  message: string
  website?: string
}

export function validateInquiry(input: InquirePayload) {
  const name = input.name.trim()
  const email = input.email.trim()
  const company = input.company.trim()
  const message = input.message.trim()
  const website = (input.website || '').trim()

  if (website) {
    return { ok: true as const, spam: true as const }
  }

  if (!name) {
    return { ok: false as const, field: 'name' as const, error: 'Enter your name.' }
  }
  if (name.length > 120) {
    return { ok: false as const, field: 'name' as const, error: 'Use a shorter name.' }
  }
  if (!email) {
    return { ok: false as const, field: 'email' as const, error: 'Enter your email so we can write back.' }
  }
  if (!isValidEmail(email)) {
    return { ok: false as const, field: 'email' as const, error: 'Enter a valid email address.' }
  }
  if (company.length > 120) {
    return { ok: false as const, field: 'company' as const, error: 'Use a shorter company name.' }
  }
  if (!message) {
    return { ok: false as const, field: 'message' as const, error: 'What do you want to know about JobbPulse?' }
  }
  if (message.length < 8) {
    return { ok: false as const, field: 'message' as const, error: 'Add a bit more so we can reply usefully.' }
  }
  if (message.length > 4000) {
    return { ok: false as const, field: 'message' as const, error: 'Keep the question under 4,000 characters.' }
  }

  return {
    ok: true as const,
    spam: false as const,
    data: { name, email, company, message },
  }
}

export function mailtoInquiry(
  to: string,
  inquiry: { name: string; email: string; company: string; message: string },
) {
  const subject = `JobbPulse question from ${inquiry.name}`
  const body = [
    inquiry.message,
    '',
    '-',
    inquiry.name,
    inquiry.email,
    inquiry.company,
  ]
    .filter(Boolean)
    .join('\n')

  return `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
}
