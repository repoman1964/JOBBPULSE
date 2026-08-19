import { validateInquiry } from '~/utils/inquire'

type Inquiry = {
  name: string
  email: string
  company: string
  message: string
}

export default defineEventHandler(async (event) => {
  const body = await readBody(event).catch(() => null)
  if (!body || typeof body !== 'object') {
    throw createError({ statusCode: 400, statusMessage: 'Send a question we can read.' })
  }

  const parsed = validateInquiry({
    name: String((body as Inquiry).name || ''),
    email: String((body as Inquiry).email || ''),
    company: String((body as Inquiry).company || ''),
    message: String((body as Inquiry).message || ''),
    website: String((body as { website?: string }).website || ''),
  })

  if (!parsed.ok) {
    throw createError({ statusCode: 400, statusMessage: parsed.error, data: { field: parsed.field } })
  }

  if (parsed.spam) {
    return { ok: true }
  }

  const delivered = await deliverInquiry(parsed.data)
  if (!delivered.ok) {
    throw createError({
      statusCode: 503,
      statusMessage: delivered.reason,
      data: { fallback: 'mailto' },
    })
  }

  return { ok: true }
})

function fromAddress(from: string) {
  if (from.includes('<')) return from
  return `JobbPulse <${from}>`
}

async function deliverInquiry(inquiry: Inquiry) {
  const config = useRuntimeConfig()
  const webhook = String(config.inquiryWebhookUrl || '').trim()
  const resendKey = String(config.resendApiKey || '').trim()
  const contact = String(config.public.contactEmail || 'hello@jobbpulse.com').trim()
  const to = String(config.inquiryToEmail || contact).trim()
  const from = String(config.inquiryFromEmail || 'onboarding@resend.dev').trim()

  if (webhook) {
    const response = await fetch(webhook, {
      method: 'POST',
      headers: { 'content-type': 'application/json', accept: 'application/json' },
      body: JSON.stringify({
        source: 'jobbpulse-marketing',
        submittedAt: new Date().toISOString(),
        ...inquiry,
      }),
    }).catch(() => null)

    if (response?.ok) return { ok: true as const }
    return { ok: false as const, reason: 'We could not deliver that question just now.' }
  }

  if (resendKey) {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        authorization: `Bearer ${resendKey}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        from: fromAddress(from),
        to: [to],
        reply_to: inquiry.email,
        subject: `Question from ${inquiry.name}`,
        text: [
          inquiry.message,
          '',
          inquiry.name,
          inquiry.email,
          inquiry.company,
        ]
          .filter(Boolean)
          .join('\n'),
      }),
    }).catch(() => null)

    if (response?.ok) return { ok: true as const }

    const detail = await response?.text().catch(() => '')
    console.error('Resend send failed', response?.status, detail)
    return { ok: false as const, reason: 'We could not email that question just now.' }
  }

  return {
    ok: false as const,
    reason: 'Question delivery is not configured yet.',
  }
}
