import type { SocialPlatform } from '~/types/domain'

export const CONNECTABLE_PLATFORMS = [
  'facebook',
  'instagram',
  'google_business',
] as const satisfies readonly SocialPlatform[]

export type ConnectablePlatform = (typeof CONNECTABLE_PLATFORMS)[number]

export const PLATFORM_LABEL: Record<ConnectablePlatform, string> = {
  facebook: 'Facebook',
  instagram: 'Instagram',
  google_business: 'Google Business Profile',
}

export const PLATFORM_FIELD: Record<
  ConnectablePlatform,
  { label: string; placeholder: string; hint: string }
> = {
  facebook: {
    label: 'Facebook Page name',
    placeholder: 'Johnson Outdoor Living',
    hint: 'The Page JobbPulse will publish to.',
  },
  instagram: {
    label: 'Instagram username',
    placeholder: '@yourbusiness',
    hint: 'The handle JobbPulse will publish to.',
  },
  google_business: {
    label: 'Google Business Profile name',
    placeholder: 'Johnson Outdoor Living',
    hint: 'The listing JobbPulse will publish to.',
  },
}

export function formatSocialAccountName(platform: string, raw: string): string {
  const name = raw.trim()
  if (platform === 'instagram') {
    const handle = name.replace(/^@+/, '').trim()
    return handle ? `@${handle}` : ''
  }
  return name
}
