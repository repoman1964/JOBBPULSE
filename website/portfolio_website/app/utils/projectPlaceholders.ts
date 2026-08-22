/** Local themed demo photos for project cards (home-service stock). */

const BY_SERVICE: Record<string, string> = {
  exterior_paint: '/placeholders/exterior-paint.jpg',
  painting: '/placeholders/exterior-paint.jpg',
  interior_painting: '/placeholders/interior-paint.jpg',
  paver_patio: '/placeholders/paver-patio.jpg',
  hardscaping: '/placeholders/paver-patio.jpg',
  landscape_installation: '/placeholders/landscaping.jpg',
  landscaping: '/placeholders/landscaping.jpg',
  tree_removal: '/placeholders/tree-removal.jpg',
  stump_removal: '/placeholders/tree-removal.jpg',
  tree_service: '/placeholders/tree-removal.jpg',
  fencing: '/placeholders/fence.jpg',
  fence: '/placeholders/fence.jpg',
  deck_building: '/placeholders/deck.jpg',
  deck: '/placeholders/deck.jpg',
  roofing: '/placeholders/roofing.jpg',
  // Cabinets use default stock until dedicated kitchen photos are added
  kitchen_cabinets: '/placeholders/default-project.jpg',
  bathroom_vanity: '/placeholders/default-project.jpg',
  pantry_built_ins: '/placeholders/default-project.jpg',
  cabinet_installation: '/placeholders/default-project.jpg',
}

const DEFAULT = '/placeholders/default-project.jpg'

const ROTATION = [
  '/placeholders/exterior-paint.jpg',
  '/placeholders/paver-patio.jpg',
  '/placeholders/landscaping.jpg',
  '/placeholders/fence.jpg',
  '/placeholders/deck.jpg',
  '/placeholders/interior-paint.jpg',
  '/placeholders/tree-removal.jpg',
  '/placeholders/roofing.jpg',
  '/placeholders/default-project.jpg',
]

function hashSlug(slug: string): number {
  let h = 0
  for (let i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0
  return h
}

/** Themed local placeholder for a service / project. */
export function placeholderForProject(serviceKey?: string | null, slug?: string | null): string {
  if (serviceKey && BY_SERVICE[serviceKey]) return BY_SERVICE[serviceKey]
  if (slug) return ROTATION[hashSlug(slug) % ROTATION.length]
  return DEFAULT
}

/**
 * Image for a project card.
 * Prefer real media; seed demo 1×1 stubs under /demo/ fall back to local placeholders.
 */
export function projectCardImage(project: {
  primary_image_url?: string | null
  service_key?: string | null
  slug?: string
}): string {
  const url = project.primary_image_url
  if (url && !url.includes('/demo/')) return url
  return placeholderForProject(project.service_key, project.slug)
}
