/** Local themed demo photos for contractor cards. */

const BY_TRADE: Record<string, string> = {
  painting: '/placeholders/contractors/painting.jpg',
  paint: '/placeholders/contractors/painting.jpg',
  tree: '/placeholders/contractors/tree.jpg',
  tree_service: '/placeholders/contractors/tree.jpg',
  tree_removal: '/placeholders/contractors/tree.jpg',
  hardscape: '/placeholders/contractors/hardscape.jpg',
  hardscaping: '/placeholders/contractors/hardscape.jpg',
  landscape: '/placeholders/contractors/hardscape.jpg',
  landscaping: '/placeholders/contractors/hardscape.jpg',
  fence: '/placeholders/contractors/fence.jpg',
  fencing: '/placeholders/contractors/fence.jpg',
  deck: '/placeholders/contractors/hardscape.jpg',
  deck_building: '/placeholders/contractors/hardscape.jpg',
  cabinet_installation: '/placeholders/contractors/default.jpg',
  kitchen_cabinets: '/placeholders/contractors/default.jpg',
  bathroom_vanity: '/placeholders/contractors/default.jpg',
  pantry_built_ins: '/placeholders/contractors/default.jpg',
}

const BY_SLUG: Record<string, string> = {
  'red-clay-cabinet-installers': '/placeholders/contractors/default.jpg',
  'smith-painting-demo': '/placeholders/contractors/painting.jpg',
  'metro-tree-pros-demo': '/placeholders/contractors/tree.jpg',
  'peach-hardscapes-demo': '/placeholders/contractors/hardscape.jpg',
  'fenceline-atlanta': '/placeholders/contractors/fence.jpg',
  'fenceline-atlanta-demo': '/placeholders/contractors/fence.jpg',
}

const DEFAULT = '/placeholders/contractors/default.jpg'

const ROTATION = [
  '/placeholders/contractors/painting.jpg',
  '/placeholders/contractors/tree.jpg',
  '/placeholders/contractors/hardscape.jpg',
  '/placeholders/contractors/fence.jpg',
  '/placeholders/contractors/default.jpg',
]

function hashSlug(slug: string): number {
  let h = 0
  for (let i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0
  return h
}

/** Themed local placeholder for a contractor card media band. */
export function contractorCardImage(contractor: {
  slug?: string | null
  trade?: string | null
  services?: { service_key?: string }[] | null
}): string {
  const slug = contractor.slug || ''
  if (slug && BY_SLUG[slug]) return BY_SLUG[slug]

  const trade = (contractor.trade || '').toLowerCase().replace(/\s+/g, '_')
  if (trade && BY_TRADE[trade]) return BY_TRADE[trade]

  const key = contractor.services?.[0]?.service_key
  if (key) {
    const k = key.toLowerCase()
    if (BY_TRADE[k]) return BY_TRADE[k]
    if (k.includes('paint')) return BY_TRADE.painting
    if (k.includes('tree') || k.includes('stump')) return BY_TRADE.tree
    if (k.includes('fence')) return BY_TRADE.fencing
    if (k.includes('cabinet') || k.includes('vanity') || k.includes('pantry')) {
      return BY_TRADE.cabinet_installation
    }
    if (k.includes('hard') || k.includes('paver') || k.includes('landscape') || k.includes('deck')) {
      return BY_TRADE.hardscaping
    }
  }

  if (slug) return ROTATION[hashSlug(slug) % ROTATION.length]
  return DEFAULT
}
