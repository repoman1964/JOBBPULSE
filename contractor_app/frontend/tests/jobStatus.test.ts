import { describe, expect, it } from 'vitest'
import {
  computePublicStatus,
  contextualAction,
  countsFromMedia,
  meetsMinimums,
  missingMinimums,
  previewKind,
  statusLabel,
} from '../app/utils/jobStatus'
import type { Job, MediaAsset } from '../app/types/domain'

const mins = { before: 2, progress: 0, after: 2 }

describe('meetsMinimums', () => {
  it('allows progress 0 when progress minimum is 0', () => {
    expect(meetsMinimums({ before: 2, progress: 0, after: 2 }, mins)).toBe(true)
  })

  it('fails when before is short', () => {
    expect(meetsMinimums({ before: 1, progress: 5, after: 2 }, mins)).toBe(false)
  })
})

describe('missingMinimums', () => {
  it('lists only unmet categories', () => {
    expect(missingMinimums({ before: 0, progress: 0, after: 1 }, mins)).toEqual([
      'before',
      'after',
    ])
  })
})

describe('computePublicStatus', () => {
  it('returns ready_to_finish when minima met', () => {
    expect(computePublicStatus({ before: 2, progress: 0, after: 2 }, mins, false)).toBe(
      'ready_to_finish',
    )
  })

  it('returns active when minima not met', () => {
    expect(computePublicStatus({ before: 1, progress: 0, after: 0 }, mins, false)).toBe('active')
  })
})

describe('statusLabel', () => {
  it('uses contextual active labels', () => {
    const job = {
      counts: { before: 4, progress: 7, after: 0 },
      publicStatus: 'active',
    } as Job
    expect(statusLabel('active', job)).toBe('Needs After Photos')
    expect(statusLabel('ready_for_approval')).toBe('Awaiting Approval')
  })
})

describe('contextualAction', () => {
  it('routes ready_for_approval to review', () => {
    const job = {
      id: 'job-1',
      publicStatus: 'ready_for_approval',
      counts: { before: 6, progress: 4, after: 8 },
    } as Job
    expect(contextualAction(job)).toMatchObject({
      label: 'Review Content',
      to: '/jobs/job-1/approval',
    })
  })
})

describe('previewKind', () => {
  it('uses a Google Business Profile preview for gbp posts', () => {
    expect(previewKind('google_business')).toBe('google_business')
  })

  it('keeps facebook and instagram dedicated previews', () => {
    expect(previewKind('facebook')).toBe('facebook')
    expect(previewKind('instagram')).toBe('instagram')
  })

  it('falls back to website for first-party destinations', () => {
    expect(previewKind('conversion_site')).toBe('website')
    expect(previewKind('portfolio_site')).toBe('website')
  })
})

describe('countsFromMedia', () => {
  it('counts only complete non-deleted photos', () => {
    const media = [
      {
        kind: 'photo',
        photoCategory: 'before',
        isDeleted: false,
        uploadStatus: 'complete',
      },
      {
        kind: 'photo',
        photoCategory: 'before',
        isDeleted: true,
        uploadStatus: 'complete',
      },
      {
        kind: 'photo',
        photoCategory: 'after',
        isDeleted: false,
        uploadStatus: 'pending',
      },
      {
        kind: 'audio',
        photoCategory: null,
        isDeleted: false,
        uploadStatus: 'complete',
      },
    ] as MediaAsset[]
    expect(countsFromMedia(media)).toEqual({ before: 1, progress: 0, after: 0 })
  })
})
