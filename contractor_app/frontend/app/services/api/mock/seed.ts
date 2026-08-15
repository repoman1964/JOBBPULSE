import type {
  Company,
  ContentPackage,
  Contractor,
  GeneratedAsset,
  Job,
  MediaAsset,
  SocialConnection,
} from '~/types/domain'

const COMPANY_ID = 'company-johnson'
const CONTRACTOR_ID = 'contractor-mike'

export const SEED_COMPANY: Company = {
  id: COMPANY_ID,
  name: 'Johnson Outdoor Living',
  contactName: 'Mike Johnson',
  phone: '(404) 555-0142',
  email: 'mike@johnsonoutdoor.example',
  website: 'https://johnsonoutdoor.example',
  serviceArea: 'Metro Atlanta',
  photoMinimums: { before: 2, progress: 0, after: 2 },
  photoMaximums: { before: 15, progress: 30, after: 15 },
  notificationSettings: {
    contentReadyForApproval: true,
    publishingComplete: true,
  },
}

export const SEED_CONTRACTOR: Contractor = {
  id: CONTRACTOR_ID,
  companyId: COMPANY_ID,
  name: 'Mike Johnson',
  email: 'mike@johnsonoutdoor.example',
  phone: '(404) 555-0142',
  role: 'owner',
}

/** Stable placeholder images (picsum seeds) for demo covers and photos. */
export function placeholder(seed: string, w = 800, h = 600): string {
  return `https://picsum.photos/seed/${encodeURIComponent(seed)}/${w}/${h}`
}

function photo(
  id: string,
  jobId: string,
  category: 'before' | 'progress' | 'after',
  seed: string,
  favorite = false,
): MediaAsset {
  const url = placeholder(seed, 900, 700)
  return {
    id,
    jobId,
    kind: 'photo',
    photoCategory: category,
    url,
    thumbnailUrl: placeholder(seed, 400, 300),
    mimeType: 'image/jpeg',
    byteSize: 240_000,
    durationMs: null,
    uploadStatus: 'complete',
    isFavorite: favorite,
    isDeleted: false,
    version: 1,
    createdAt: new Date().toISOString(),
  }
}

export function buildSeedJobs(): Job[] {
  return [
    {
      id: 'job-deck',
      companyId: COMPANY_ID,
      name: 'Johnson Deck Rebuild',
      serviceType: 'Deck rebuild',
      city: 'Marietta',
      region: 'GA',
      locationText: 'Marietta, GA',
      internalNote: '',
      assignedCrewMember: '',
      publicStatus: 'active',
      coverUrl: placeholder('deck-cover', 1000, 700),
      counts: { before: 4, progress: 7, after: 0 },
      hasVoice: false,
      createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
      updatedAt: new Date().toISOString(),
      submittedAt: null,
      approvedAt: null,
      publishedAt: null,
    },
    {
      id: 'job-kitchen',
      companyId: COMPANY_ID,
      name: 'Miller Kitchen Cabinets',
      serviceType: 'Cabinets',
      city: 'Roswell',
      region: 'GA',
      locationText: 'Roswell, GA',
      internalNote: '',
      assignedCrewMember: '',
      publicStatus: 'active',
      coverUrl: placeholder('kitchen-cover', 1000, 700),
      counts: { before: 5, progress: 3, after: 0 },
      hasVoice: false,
      createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
      updatedAt: new Date().toISOString(),
      submittedAt: null,
      approvedAt: null,
      publishedAt: null,
    },
    {
      id: 'job-paint',
      companyId: COMPANY_ID,
      name: 'Thompson Exterior Painting',
      serviceType: 'Exterior painting',
      city: 'Decatur',
      region: 'GA',
      locationText: 'Decatur, GA',
      internalNote: '',
      assignedCrewMember: '',
      publicStatus: 'ready_for_approval',
      coverUrl: placeholder('paint-cover', 1000, 700),
      counts: { before: 6, progress: 4, after: 8 },
      hasVoice: true,
      createdAt: new Date(Date.now() - 86400000 * 10).toISOString(),
      updatedAt: new Date().toISOString(),
      submittedAt: new Date(Date.now() - 86400000).toISOString(),
      approvedAt: null,
      publishedAt: null,
    },
  ]
}

export function buildSeedMedia(): MediaAsset[] {
  const media: MediaAsset[] = []

  // Deck: 4 before, 7 progress, 0 after
  for (let i = 1; i <= 4; i++) {
    media.push(photo(`deck-before-${i}`, 'job-deck', 'before', `deck-b-${i}`, i === 1))
  }
  for (let i = 1; i <= 7; i++) {
    media.push(photo(`deck-progress-${i}`, 'job-deck', 'progress', `deck-p-${i}`))
  }

  // Kitchen
  for (let i = 1; i <= 5; i++) {
    media.push(photo(`kit-before-${i}`, 'job-kitchen', 'before', `kit-b-${i}`))
  }
  for (let i = 1; i <= 3; i++) {
    media.push(photo(`kit-progress-${i}`, 'job-kitchen', 'progress', `kit-p-${i}`))
  }

  // Paint — full set + voice
  for (let i = 1; i <= 6; i++) {
    media.push(photo(`paint-before-${i}`, 'job-paint', 'before', `paint-b-${i}`, i === 2))
  }
  for (let i = 1; i <= 4; i++) {
    media.push(photo(`paint-progress-${i}`, 'job-paint', 'progress', `paint-p-${i}`))
  }
  for (let i = 1; i <= 8; i++) {
    media.push(photo(`paint-after-${i}`, 'job-paint', 'after', `paint-a-${i}`, i === 1))
  }
  media.push({
    id: 'paint-voice-1',
    jobId: 'job-paint',
    kind: 'audio',
    photoCategory: null,
    url: '',
    thumbnailUrl: '',
    mimeType: 'audio/webm',
    byteSize: 120_000,
    durationMs: 42_000,
    uploadStatus: 'complete',
    isFavorite: false,
    isDeleted: false,
    version: 1,
    createdAt: new Date().toISOString(),
  })

  return media
}

export function buildSeedSocial(): SocialConnection[] {
  return [
    { platform: 'facebook', status: 'connected', accountName: 'Johnson Outdoor Living', reason: null },
    { platform: 'instagram', status: 'connected', accountName: '@johnsonoutdoorliving', reason: null },
    { platform: 'google_business', status: 'not_connected', accountName: null, reason: 'Connection gated until provider verified' },
    { platform: 'tiktok', status: 'not_connected', accountName: null, reason: null },
    { platform: 'x', status: 'not_connected', accountName: null, reason: null },
    { platform: 'linkedin', status: 'not_connected', accountName: null, reason: null },
  ]
}

export function buildPackageForPaintJob(media: MediaAsset[]): ContentPackage {
  const befores = media.filter((m) => m.jobId === 'job-paint' && m.photoCategory === 'before' && !m.isDeleted)
  const afters = media.filter((m) => m.jobId === 'job-paint' && m.photoCategory === 'after' && !m.isDeleted)
  const before = befores.find((m) => m.isFavorite) || befores[0]
  const after = afters.find((m) => m.isFavorite) || afters[0]

  const description =
    'We refreshed this Decatur home with a full exterior repaint, careful prep, and durable finish for a clean curb-appeal upgrade.'

  const makeAsset = (
    id: string,
    destinationType: GeneratedAsset['destinationType'],
    title: string,
    body: string,
  ): GeneratedAsset => {
    const versionId = `${id}-v1`
    return {
      id,
      packageId: 'pkg-paint-1',
      destinationType,
      title,
      body,
      status: 'ready',
      activeVersionId: versionId,
      preview: {
        beforeUrl: before?.url,
        afterUrl: after?.url,
        coverUrl: after?.url || before?.url,
      },
      versions: [
        {
          id: versionId,
          version: 1,
          title,
          body,
          preview: {
            beforeUrl: before?.url,
            afterUrl: after?.url,
            coverUrl: after?.url || before?.url,
          },
          sourceMediaIds: [before?.id, after?.id].filter(Boolean) as string[],
          createdAt: new Date().toISOString(),
        },
      ],
    }
  }

  return {
    id: 'pkg-paint-1',
    jobId: 'job-paint',
    version: 1,
    status: 'ready_for_approval',
    projectDescription: description,
    featuredBeforeMediaId: before?.id ?? null,
    featuredAfterMediaId: after?.id ?? null,
    assets: [
      makeAsset(
        'asset-paint-fb',
        'facebook',
        'Facebook',
        'From worn to wow in Decatur — full exterior paint refresh for lasting curb appeal.',
      ),
      makeAsset(
        'asset-paint-ig',
        'instagram',
        'Instagram',
        'Exterior transformation complete in Decatur, GA. Fresh color, solid prep, clean finish. #JobbPulse',
      ),
      makeAsset(
        'asset-paint-site',
        'conversion_site',
        'Project Page',
        description,
      ),
      makeAsset(
        'asset-paint-portfolio',
        'portfolio_site',
        'JobbPulse Portfolio',
        description,
      ),
    ],
  }
}
