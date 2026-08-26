import { describe, expect, it } from 'vitest'
import { createMockApiClient } from '../app/services/api/mock/mockClient'
import { formatSocialAccountName } from '../app/utils/socialAccounts'

describe('formatSocialAccountName', () => {
  it('prefixes instagram handles with @', () => {
    expect(formatSocialAccountName('instagram', 'johnsonoutdoorliving')).toBe(
      '@johnsonoutdoorliving',
    )
    expect(formatSocialAccountName('instagram', '@already')).toBe('@already')
  })

  it('leaves facebook page names unchanged', () => {
    expect(formatSocialAccountName('facebook', 'Johnson Outdoor Living')).toBe(
      'Johnson Outdoor Living',
    )
  })
})

describe('mock social connect', () => {
  it('connects and disconnects instagram', async () => {
    const api = createMockApiClient()
    await api.login('mike@johnsonoutdoor.example', 'devpassword')
    const connected = await api.connectSocialAccount('instagram', 'newhandle')
    expect(connected).toMatchObject({
      platform: 'instagram',
      status: 'connected',
      accountName: '@newhandle',
    })
    const listed = await api.listSocialConnections()
    expect(listed.find((row) => row.platform === 'instagram')?.accountName).toBe('@newhandle')
    const gone = await api.disconnectSocialAccount('instagram')
    expect(gone.status).toBe('not_connected')
    expect(gone.accountName).toBeNull()
  })
})
