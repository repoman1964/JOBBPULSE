import { describe, expect, it } from 'vitest'
import { createMockApiClient } from '../app/services/api/mock/mockClient'

describe('mock auth', () => {
  it('signs in the seed contractor with email and password', async () => {
    const api = createMockApiClient()
    const session = await api.login('mike@johnsonoutdoor.example', 'devpassword')
    expect(session.contractor.email).toBe('mike@johnsonoutdoor.example')
    expect(session.accessToken).toBeTruthy()
  })

  it('rejects login before email confirmation', async () => {
    const api = createMockApiClient()
    await api.register({
      name: 'Alex Rivera',
      email: 'alex@example.com',
      password: 'secret123',
      companyName: 'Rivera Painting',
    })
    await expect(api.login('alex@example.com', 'secret123')).rejects.toMatchObject({
      code: 'email_not_verified',
    })
  })

  it('allows login after the confirmation token is used', async () => {
    const api = createMockApiClient()
    const registered = await api.register({
      name: 'Alex Rivera',
      email: 'alex@example.com',
      password: 'secret123',
      companyName: 'Rivera Painting',
    })
    const token = new URL(registered.verificationUrl || '').searchParams.get('token')
    expect(token).toBeTruthy()
    const verified = await api.verifyEmail(token!)
    expect(verified).toEqual({ email: 'alex@example.com', verified: true })
    const session = await api.login('alex@example.com', 'secret123')
    expect(session.contractor.email).toBe('alex@example.com')
    expect(session.company.name).toBe('Rivera Painting')
  })
})
