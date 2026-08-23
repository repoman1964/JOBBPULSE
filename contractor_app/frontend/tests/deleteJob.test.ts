import { describe, expect, it } from 'vitest'
import { createMockApiClient } from '../app/services/api/mock/mockClient'

async function signedInClient() {
  const api = createMockApiClient()
  const { challengeId, devCode } = await api.requestChallenge('mike@johnsonoutdoor.example')
  await api.verifyChallenge(challengeId, devCode || '123456')
  return api
}

describe('deleteJob', () => {
  it('hides the job from the list and getJob', async () => {
    const api = await signedInClient()
    const before = await api.listJobs()
    expect(before.items.map((j) => j.id)).toContain('job-deck')

    await api.deleteJob('job-deck')

    const after = await api.listJobs()
    expect(after.items.map((j) => j.id)).not.toContain('job-deck')
    await expect(api.getJob('job-deck')).rejects.toMatchObject({ code: 'not_found' })
  })

  it('cannot load photos for a hidden job', async () => {
    const api = await signedInClient()
    const mediaBefore = await api.listMedia('job-deck')
    expect(mediaBefore.length).toBeGreaterThan(0)

    await api.deleteJob('job-deck')

    await expect(api.listMedia('job-deck')).rejects.toMatchObject({ code: 'not_found' })
  })
})
