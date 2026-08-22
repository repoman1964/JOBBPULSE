/** Static marketing content for Red Clay (demo Smart Website). */

export type ServiceDef = {
  slug: string
  service_key: string
  name: string
  short: string
  description: string
  bullets: string[]
  /** SEO body for /services/[slug] */
  longDescription: string
}

export type AreaDef = {
  slug: string
  city: string
  state: string
  note: string
  neighborhoods: string[]
  /** SEO body for /service-area/[city] */
  longDescription: string
}

export const SERVICES: ServiceDef[] = [
  {
    slug: 'kitchen-cabinets',
    service_key: 'kitchen_cabinets',
    name: 'Kitchen Cabinets',
    short: 'Full installs, refreshes, and soft-close upgrades.',
    description:
      'From box-store kits to custom shaker sets, we hang, level, and finish kitchens so doors close clean and lines stay true. Soft-close hardware, careful floor protection, and a tidy walkthrough every time.',
    bullets: [
      'New construction & remodel installs',
      'Soft-close hardware',
      'Island & appliance panel fitment',
      '2–5 day typical timeline',
    ],
    longDescription:
      'Red Clay installs kitchen cabinets for remodels and new construction across metro Atlanta. We set base and wall cabinets true, integrate islands and appliance panels, and finish with soft-close hardware so the kitchen feels solid on day one. Floor protection and a clean walkthrough are part of every job—not optional extras.',
  },
  {
    slug: 'bath-vanities',
    service_key: 'bathroom_vanity',
    name: 'Bath Vanities',
    short: 'Single and double vanities, mirrors, and trim-out.',
    description:
      'We remove the old vanity, set the new unit plumb, reconnect plumbing when needed, and leave the bath ready for everyday use—no half-finished mess.',
    bullets: [
      'Single & double vanities',
      'Mirror and top coordination',
      'Clean plumbing reconnect',
      'Same-day options on simple swaps',
    ],
    longDescription:
      'Bathroom vanity installation is a frequent Red Clay job—single and double units, coordinated mirrors, and careful reconnection of supply and drain lines. We protect tile and floors, set the cabinet plumb, and leave the room usable the same day whenever the scope allows.',
  },
  {
    slug: 'pantries-built-ins',
    service_key: 'pantry_built_ins',
    name: 'Pantries & Built-ins',
    short: 'Floor-to-ceiling storage that actually works.',
    description:
      'Custom pantry cabinets and built-ins designed around how you live—adjustable shelves, clean reveals, and finishes that match the rest of the home.',
    bullets: [
      'Floor-to-ceiling pantries',
      'Mudroom & closet systems',
      'Office built-ins',
      'Paint-grade or stain-grade options',
    ],
    longDescription:
      'Pantries and built-ins turn wasted wall space into storage that fits real households. We install floor-to-ceiling pantries, mudroom systems, and office cabinets with clean reveals and adjustable shelving—finished to match adjacent millwork when the project calls for it.',
  },
  {
    slug: 'cabinet-installation',
    service_key: 'cabinet_installation',
    name: 'Cabinet Installation',
    short: 'Professional install for any room that needs cabinets.',
    description:
      'General cabinet installation across kitchens, baths, laundry, and garages. Measure twice, protect the floors, and install like we own the home.',
    bullets: [
      'Laundry & garage cabinets',
      'Hardware upgrades',
      'Refacing support installs',
      'Licensed & insured crews',
    ],
    longDescription:
      'Beyond kitchens and baths, Red Clay handles cabinet installation in laundry rooms, garages, and utility spaces—plus hardware upgrades and support installs for refacing projects. Same standards everywhere: level, secure, and tidy.',
  },
]

export const SERVICE_AREAS: AreaDef[] = [
  {
    slug: 'atlanta',
    city: 'Atlanta',
    state: 'GA',
    note: 'Buckhead, Inman Park, Midtown, East Atlanta',
    neighborhoods: ['Buckhead', 'Inman Park', 'Midtown', 'East Atlanta', 'Grant Park', 'Virginia-Highland'],
    longDescription:
      'Atlanta is our home base. Red Clay installs kitchen cabinets, bath vanities, and built-ins for homeowners from Buckhead to Inman Park and across intown neighborhoods. Expect careful floor protection in finished homes and clear scheduling for remodel and new-construction installs.',
  },
  {
    slug: 'decatur',
    city: 'Decatur',
    state: 'GA',
    note: 'Intown & near-east suburbs',
    neighborhoods: ['Oakhurst', 'Winnona Park', 'Downtown Decatur', 'Medlock Park'],
    longDescription:
      'Decatur and near-east Atlanta are a core part of our service area. We regularly install kitchens, vanities, and custom pantries in bungalows and renovated homes—tight access, tidy jobsite habits, and neighborhood-friendly schedules included.',
  },
  {
    slug: 'marietta',
    city: 'Marietta',
    state: 'GA',
    note: 'Cobb County & East Cobb',
    neighborhoods: ['East Cobb', 'Historic Marietta', 'West Cobb', 'Smyrna-adjacent'],
    longDescription:
      'Marietta and Cobb County homeowners call Red Clay for kitchen cabinet installs, vanity upgrades, and built-in storage. We serve East Cobb and the broader Marietta area with licensed crews and free estimates.',
  },
  {
    slug: 'roswell',
    city: 'Roswell',
    state: 'GA',
    note: 'North Fulton',
    neighborhoods: ['Historic Roswell', 'East Roswell', 'North Fulton'],
    longDescription:
      'In Roswell and North Fulton, Red Clay handles kitchen cabinet installation, bath vanities, and pantry built-ins for remodels and upgrades. Free estimates and a clear install plan before we open the first box.',
  },
  {
    slug: 'sandy-springs',
    city: 'Sandy Springs',
    state: 'GA',
    note: 'Perimeter & nearby',
    neighborhoods: ['Perimeter', 'North Springs', 'Dunwoody-adjacent'],
    longDescription:
      'Sandy Springs is in our regular north-metro rotation. We install cabinets and vanities for condo and single-family remodels near the Perimeter—with the same soft-close, level-line standards we use intown.',
  },
  {
    slug: 'brookhaven',
    city: 'Brookhaven',
    state: 'GA',
    note: 'By request',
    neighborhoods: ['Brookhaven Village', 'Ashford Park', 'Drew Valley'],
    longDescription:
      'Brookhaven projects are scheduled by request alongside nearby Atlanta and Decatur work. Kitchen cabinets, vanities, and built-ins are all available—tell us the address and we’ll confirm timing on the estimate.',
  },
]

export const REVIEWS = [
  {
    author: 'Priya M.',
    location: 'Marietta',
    rating: 5,
    text: 'Kitchen looks magazine-ready. Crew was careful with our floors and cleaned up every night.',
  },
  {
    author: 'Tom R.',
    location: 'Atlanta',
    rating: 5,
    text: 'Vanity and mirror install same day. Explained every step and left the bath spotless.',
  },
  {
    author: 'Elena V.',
    location: 'Decatur',
    rating: 5,
    text: 'Pantry built-in solved our chaos. On time, tidy, and the shelves are finally useful.',
  },
  {
    author: 'Marcus W.',
    location: 'Sandy Springs',
    rating: 5,
    text: 'Soft-close upgrade changed the whole kitchen feel. Fair price and clear communication.',
  },
] as const

export const FAQS = [
  {
    q: 'How long does a kitchen cabinet install take?',
    a: 'Most full kitchen installs take two to five days depending on layout, appliances, and whether walls need patching after tear-out. We give a clear schedule after measure.',
  },
  {
    q: 'Do you supply cabinets or only install?',
    a: 'We install cabinets you purchase or coordinate with suppliers you prefer. Ask us during the estimate—we’ll tell you what works best for your timeline and budget.',
  },
  {
    q: 'Are you licensed and insured?',
    a: 'Yes. Red Clay is licensed and insured for residential cabinet installation across metro Atlanta.',
  },
  {
    q: 'What areas do you serve?',
    a: 'Atlanta, Decatur, Marietta, Roswell, Sandy Springs, and nearby north-metro communities. If you’re just outside that ring, call—we often can make it work.',
  },
  {
    q: 'How do I get an estimate?',
    a: 'Use the free estimate form, call us, or text. We’ll confirm scope, photos if you have them, and a site measure when needed.',
  },
] as const

export const TRUST_CHIPS = [
  '12 Years in Business',
  'Licensed & Insured',
  'Metro Atlanta',
  'Free Estimates',
] as const

/** Fallback cards if API is offline (aligned with JobPulse red-clay-seed). */
export const FALLBACK_JOBS = [
  {
    id: 'fallback-1',
    slug: 'kitchen-cabinets-atlanta-buckhead-kitchen',
    public_title: 'Kitchen Cabinet Install in Buckhead',
    short_summary:
      'Full kitchen cabinet install: white shaker, soft-close, floors protected throughout.',
    public_summary:
      'Full kitchen cabinet install in Buckhead: removed the old boxes, leveled everything, and hung white shaker uppers and lowers with soft-close. Floors protected throughout; finished in three days with a two-person crew.',
    service_name: 'Kitchen Cabinets',
    location_display: 'Buckhead, Atlanta, GA',
    city: 'Atlanta',
    state: 'GA',
    featured: true,
    published_at: new Date(Date.now() - 4 * 86400000).toISOString(),
    primary_image_url: '/portfolio/buckhead-kitchen-after.jpg',
    has_before: true,
    has_after: true,
  },
  {
    id: 'fallback-2',
    slug: 'bathroom-vanity-atlanta-inman-vanity',
    public_title: 'Double Vanity Install in Inman Park',
    short_summary: 'Worn oak double vanity swapped for a fresh white unit—plumbed, leveled, and caulked.',
    public_summary:
      'Swapped a worn oak double vanity for a fresh white unit in Inman Park. Plumbed, leveled, and caulked; left the bath spotless for the homeowners.',
    service_name: 'Bath Vanities',
    location_display: 'Inman Park, Atlanta, GA',
    city: 'Atlanta',
    state: 'GA',
    featured: false,
    published_at: new Date(Date.now() - 11 * 86400000).toISOString(),
    primary_image_url: '/portfolio/inman-vanity-after.jpg',
    has_before: true,
    has_after: true,
  },
  {
    id: 'fallback-3',
    slug: 'pantry-built-ins-decatur-decatur-pantry',
    public_title: 'Custom Pantry Built-In in Decatur',
    short_summary: 'Floor-to-ceiling pantry with adjustable shelves for real everyday storage.',
    public_summary:
      'Floor-to-ceiling pantry built-in with adjustable shelves in Decatur. Client can finally see their dry goods and stop the hallway clutter.',
    service_name: 'Pantries & Built-ins',
    location_display: 'Decatur, GA',
    city: 'Decatur',
    state: 'GA',
    featured: true,
    published_at: new Date(Date.now() - 18 * 86400000).toISOString(),
    primary_image_url: '/portfolio/decatur-pantry-after.jpg',
    has_before: true,
    has_after: true,
  },
  {
    id: 'fallback-4',
    slug: 'kitchen-cabinets-marietta-marietta-kitchen',
    public_title: 'Soft-Close Kitchen Refresh in Marietta',
    short_summary: 'Sage green shaker kitchen with soft-close hardware and clean appliance fit.',
    public_summary:
      'Kitchen cabinet refresh in Marietta: sage green shaker set, soft-close hardware, and careful fit around stainless appliances for a quieter finish.',
    service_name: 'Kitchen Cabinets',
    location_display: 'Marietta, GA',
    city: 'Marietta',
    state: 'GA',
    featured: false,
    published_at: new Date(Date.now() - 27 * 86400000).toISOString(),
    primary_image_url: '/portfolio/marietta-kitchen-after.jpg',
    has_before: true,
    has_after: true,
  },
  {
    id: 'fallback-5',
    slug: 'cabinet-installation-sandy-springs-sandy-springs-laundry',
    public_title: 'Laundry Cabinet Install in Sandy Springs',
    short_summary: 'Uppers, lowers, and folding counter where wire shelves used to lose the war.',
    public_summary:
      'Utility-room cabinet install in Sandy Springs: uppers, lowers, folding counter, and storage for the mess that used to live on wire shelves.',
    service_name: 'Cabinet Installation',
    location_display: 'Sandy Springs, GA',
    city: 'Sandy Springs',
    state: 'GA',
    featured: false,
    published_at: new Date(Date.now() - 35 * 86400000).toISOString(),
    primary_image_url: '/portfolio/sandy-springs-laundry-after.jpg',
    has_before: true,
    has_after: true,
  },
  {
    id: 'fallback-6',
    slug: 'kitchen-cabinets-roswell-roswell-island',
    public_title: 'Kitchen Island & Cabinets in Roswell',
    short_summary: 'White perimeter cabinets plus walnut island with soft-close and quartz tops.',
    public_summary:
      'Full kitchen cabinet install in Roswell with white perimeter cabinets and a walnut island—soft-close drawers, quartz tops, clean appliance panels.',
    service_name: 'Kitchen Cabinets',
    location_display: 'Roswell, GA',
    city: 'Roswell',
    state: 'GA',
    featured: true,
    published_at: new Date(Date.now() - 9 * 86400000).toISOString(),
    primary_image_url: '/portfolio/roswell-island-after.jpg',
    has_before: true,
    has_after: true,
  },
] as const

/** Local before/after paths for offline portfolio detail pages. */
export const FALLBACK_MEDIA: Record<string, { before: string; after: string }> = {
  'kitchen-cabinets-atlanta-buckhead-kitchen': {
    before: '/portfolio/buckhead-kitchen-before.jpg',
    after: '/portfolio/buckhead-kitchen-after.jpg',
  },
  'bathroom-vanity-atlanta-inman-vanity': {
    before: '/portfolio/inman-vanity-before.jpg',
    after: '/portfolio/inman-vanity-after.jpg',
  },
  'pantry-built-ins-decatur-decatur-pantry': {
    before: '/portfolio/decatur-pantry-before.jpg',
    after: '/portfolio/decatur-pantry-after.jpg',
  },
  'kitchen-cabinets-marietta-marietta-kitchen': {
    before: '/portfolio/marietta-kitchen-before.jpg',
    after: '/portfolio/marietta-kitchen-after.jpg',
  },
  'cabinet-installation-sandy-springs-sandy-springs-laundry': {
    before: '/portfolio/sandy-springs-laundry-before.jpg',
    after: '/portfolio/sandy-springs-laundry-after.jpg',
  },
  'kitchen-cabinets-roswell-roswell-island': {
    before: '/portfolio/roswell-island-before.jpg',
    after: '/portfolio/roswell-island-after.jpg',
  },
}

/* ——— SEO silo helpers ——— */

export function getService(slug: string): ServiceDef | undefined {
  return SERVICES.find((s) => s.slug === slug)
}

export function getArea(slug: string): AreaDef | undefined {
  return SERVICE_AREAS.find((a) => a.slug === slug)
}

export function servicePath(slug: string) {
  return `/services/${slug}`
}

export function areaPath(slug: string) {
  return `/service-area/${slug}`
}

/** Location × service leaf (local SEO money page). */
export function areaServicePath(areaSlug: string, serviceSlug: string) {
  return `/service-area/${areaSlug}/${serviceSlug}`
}

export function serviceInAreaTitle(service: ServiceDef, area: AreaDef) {
  return `${service.name} in ${area.city}, ${area.state}`
}

export function serviceInAreaDescription(service: ServiceDef, area: AreaDef) {
  return `${service.name} installation in ${area.city}, ${area.state}. ${service.short} Free estimates from Red Clay Cabinet Installers.`
}

export function serviceInAreaIntro(service: ServiceDef, area: AreaDef) {
  return `Looking for ${service.name.toLowerCase()} in ${area.city}? Red Clay Cabinet Installers serves ${area.note.toLowerCase()} with licensed crews, clean jobsite habits, and free estimates. ${service.description}`
}

export function reviewsForArea(city: string) {
  return REVIEWS.filter((r) => r.location.toLowerCase() === city.toLowerCase())
}

export function projectImageStyle(title: string): string {
  let h = 0
  for (let i = 0; i < title.length; i++) h = (h * 31 + title.charCodeAt(i)) >>> 0
  const palettes = [
    ['#8b3a20', '#d4a574'],
    ['#5c4033', '#c4a484'],
    ['#6b2c18', '#e8c4a8'],
    ['#7a4b32', '#f0d9c4'],
  ]
  const [a, b] = palettes[h % palettes.length]
  return `linear-gradient(145deg, ${a} 0%, ${b} 100%)`
}

export function formatPhoneDisplay(phone: string) {
  const digits = phone.replace(/\D/g, '')
  if (digits.length === 10) {
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
  }
  return phone
}

export function formatRelativeDate(iso?: string | null) {
  if (!iso) return 'Recently completed'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'Recently completed'
  const days = Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24))
  if (days <= 0) return 'Completed today'
  if (days === 1) return 'Completed yesterday'
  if (days < 14) return `Completed ${days} days ago`
  if (days < 45) return `Completed ${Math.floor(days / 7)} weeks ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
