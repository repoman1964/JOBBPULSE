/** Static marketing content for Red Clay painting. */

export type ServiceDef = {
  slug: string
  service_key: string
  name: string
  short: string
  description: string
  bullets: string[]
  longDescription: string
  image: string
  faqs: { q: string; a: string }[]
}

export type AreaDef = {
  slug: string
  city: string
  state: string
  note: string
  neighborhoods: string[]
  longDescription: string
  image: string
}

export type SocialPost = {
  destination: 'facebook' | 'instagram' | 'google_business'
  title: string
  body: string
  imageUrl: string
}

export type DummyJob = {
  slug: string
  publicTitle: string
  publicSummary: string
  serviceType: string
  city: string
  publishedAt: string
  primaryImageUrl: string
  hasBefore: boolean
  hasAfter: boolean
  beforeUrl: string
  afterUrl: string
  socialPosts: SocialPost[]
}

export const COMPANY = {
  name: 'Red Clay',
  tagline: 'Painting · Metro Atlanta',
  phone: '404-555-0148',
  phoneTel: '+14045550148',
  email: 'hello@redclaypainting.com',
} as const

export const NAV_LABELS = ['Home', 'Services', 'Work', 'Areas', 'About', 'Contact', 'Book an estimate'] as const

export const PUBLIC_CHROME_COPY = [
  'Red Clay',
  'Painting · Metro Atlanta',
  'Licensed & insured',
  'Written estimates',
  'Metro Atlanta',
  'On-site reviews',
  'Ready for a quote?',
  'See your project',
  'Book an estimate',
] as const

export const SERVICES: ServiceDef[] = [
  {
    slug: 'exterior-painting',
    service_key: 'exterior_painting',
    name: 'Exterior painting',
    short: 'Prep the surface. Then paint. Georgia weather does the rest of the test.',
    description:
      'Full-house and trim-only exterior painting across metro Atlanta. Scrape, sand, caulk, prime, then two finish coats — not a one-day roll over peeling paint.',
    bullets: [
      'Siding, trim, soffits, shutters, and entry doors',
      'Wash, scrape, sand, caulk, and prime before finish coats',
      'Weather-window scheduling — we do not paint wet siding',
      'Written estimate before a brush hits the house',
    ],
    longDescription:
      'Georgia sun, pollen, and summer storms will tell on a cheap exterior job inside a year. Red Clay prices exterior painting around prep: wash when it needs it, scrape loose paint, sand, caulk gaps, prime bare wood and stains, then two finish coats. We work siding, trim, soffits, shutters, and doors. If the substrate is too far gone, we tell you before we open a can.',
    image: '/images/exterior.jpg',
    faqs: [
      {
        q: 'When is the best time to paint a house in Atlanta?',
        a: 'Spring and fall are the most reliable windows. We paint in summer when humidity and afternoon storms allow. We will not apply finish coats on wet siding.',
      },
      {
        q: 'Do you pressure wash first?',
        a: 'When the surface needs it. We wash, let the house dry, then scrape and prime. Washing is not a substitute for scraping peeling paint.',
      },
      {
        q: 'Can you match my current color?',
        a: 'Yes. We can pull a sample or scan an existing chip. If you want a new color, we can put sample boards on the house before the full job.',
      },
      {
        q: 'What if you find rotten wood?',
        a: 'We stop and show you. Small carpentry patches can often be handled in-house. Larger rot gets a written change before we paint over it.',
      },
    ],
  },
  {
    slug: 'trim-and-siding',
    service_key: 'trim_and_siding',
    name: 'Trim and siding',
    short: 'Fascia, soffit, siding, and exterior trim that look finished from the curb.',
    description:
      'Focused exterior millwork and siding work: fascia, soffits, window trim, and siding that need more than a quick roll.',
    bullets: [
      'Fascia, soffits, and eave lines',
      'Window and door casing',
      'Fiber cement and wood siding',
      'Color breaks and accent trim',
    ],
    longDescription:
      'A house can look tired even when the body paint is recent — fascia, soffits, and window trim take the weather first. Red Clay handles those lines as their own job or as part of a full exterior. We scrape, prime, and finish so the edges read sharp from the street.',
    image: '/images/trim.jpg',
    faqs: [
      {
        q: 'Can you paint just the trim?',
        a: 'Yes. Trim-and-siding work is a common request when the body color still looks right.',
      },
      {
        q: 'Do you paint fiber cement?',
        a: 'Yes. We prep and prime as the manufacturer expects. Chalky or failed coatings get extra attention before finish coats.',
      },
      {
        q: 'Will you paint the soffits from the inside of the eave?',
        a: 'We paint visible soffit faces. Enclosed attic spaces stay closed unless you ask for something specific.',
      },
    ],
  },
  {
    slug: 'decks-and-fences',
    service_key: 'decks_and_fences',
    name: 'Decks and fences',
    short: 'Stain or paint that soaks in, not a film that peels next summer.',
    description:
      'Deck and fence staining and painting for backyards that get real use. Wash, brighten where needed, then a finish that matches the wood and the weather.',
    bullets: [
      'Decks, rails, and stair treads',
      'Privacy fences and gates',
      'Transparent, semi-transparent, and solid stains',
      'Painted fence options when stain is the wrong call',
    ],
    longDescription:
      'A deck that peels in twelve months was finished too fast. Red Clay washes, lets the wood dry, and chooses stain or paint based on the species and how beat-up the boards are. Rails and treads get the coats they need; we do not skip the underside of the top rail because nobody photographs it.',
    image: '/images/deck.jpg',
    faqs: [
      {
        q: 'Stain or paint?',
        a: 'Stain if the wood can still take it. Solid stain or paint when the surface is already coated or too weathered for a clear product.',
      },
      {
        q: 'How long before we can walk on it?',
        a: 'Most stains are walkable the same evening if the weather holds. We put the recoat and foot-traffic window on the quote.',
      },
      {
        q: 'Do you replace bad boards?',
        a: 'Small swaps, sometimes. A failing structure is a carpenter’s job — we will tell you before we stain over it.',
      },
    ],
  },
  {
    slug: 'interior-painting',
    service_key: 'interior_painting',
    name: 'Interior painting',
    short: 'Walls, ceilings, trim, and doors in houses people actually live in.',
    description:
      'Occupied-home interiors across metro Atlanta. We protect floors and furniture, cut clean lines, and leave rooms you can use the evening the last coat dries.',
    bullets: [
      'Walls, ceilings, trim, doors, and accent walls',
      'Furniture and floor protection',
      'Color and sheen recommendations',
      'Two-coat finish with primer where the substrate needs it',
    ],
    longDescription:
      'Interior painting is our second line, not the thing we lead with. When we take an interior, we treat it like an occupied home: dust control, floor protection, and a schedule you can live around. Living rooms, bedrooms, hallways, kitchens, and trim — written on the quote so nobody is guessing on paint day.',
    image: '/images/interior.jpg',
    faqs: [
      {
        q: 'How long does an interior take?',
        a: 'A typical three-bedroom interior is two to four days depending on repairs, number of colors, and whether ceilings and trim are included.',
      },
      {
        q: 'Do I need to move furniture?',
        a: 'Pull small valuables and wall hangings. We shift large furniture to the center, cover it, and put it back.',
      },
      {
        q: 'What paint do you use?',
        a: 'Washable interiors from major lines at a sheen that matches the room — typically eggshell on walls, satin or semi-gloss on trim.',
      },
    ],
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
      'Atlanta is our home base. Red Clay paints exteriors, trim, and interiors for homeowners from Buckhead to Inman Park. Expect floor and landscape protection in finished neighborhoods and a schedule that respects occupied homes.',
    image: '/images/atlanta.jpg',
  },
  {
    slug: 'decatur',
    city: 'Decatur',
    state: 'GA',
    note: 'Intown and near-east suburbs',
    neighborhoods: ['Oakhurst', 'Winnona Park', 'Downtown Decatur', 'Medlock Park'],
    longDescription:
      'Decatur bungalows and renovated cottages are a regular week for us. Tight lots, old wood, and neighbors close by — we work clean and keep the job contained.',
    image: '/images/decatur.jpg',
  },
  {
    slug: 'marietta',
    city: 'Marietta',
    state: 'GA',
    note: 'Cobb County and East Cobb',
    neighborhoods: ['East Cobb', 'Historic Marietta', 'West Cobb', 'Smyrna-adjacent'],
    longDescription:
      'Marietta and Cobb County homeowners call Red Clay for full exteriors, decks, and trim. Licensed crew, written estimates, and weather-honest scheduling.',
    image: '/images/marietta.jpg',
  },
  {
    slug: 'roswell',
    city: 'Roswell',
    state: 'GA',
    note: 'North Fulton',
    neighborhoods: ['Historic Roswell', 'East Roswell', 'North Fulton'],
    longDescription:
      'In Roswell and North Fulton we handle exteriors, fascia and soffit work, and interiors for remodels. A clear plan before we open a can.',
    image: '/images/roswell.jpg',
  },
  {
    slug: 'sandy-springs',
    city: 'Sandy Springs',
    state: 'GA',
    note: 'Perimeter and nearby',
    neighborhoods: ['Perimeter', 'North Springs', 'Dunwoody-adjacent'],
    longDescription:
      'Sandy Springs is in our north-metro rotation — condos and single-family exteriors near the Perimeter, same prep standards we use intown.',
    image: '/images/sandy-springs.jpg',
  },
  {
    slug: 'brookhaven',
    city: 'Brookhaven',
    state: 'GA',
    note: 'By request',
    neighborhoods: ['Brookhaven Village', 'Ashford Park', 'Drew Valley'],
    longDescription:
      'Brookhaven projects are scheduled alongside nearby Atlanta and Decatur work. Exterior, trim, decks, and interiors — tell us the address and we will confirm timing on the estimate.',
    image: '/images/brookhaven.jpg',
  },
]

export const REVIEWS = [
  {
    author: 'Priya M.',
    location: 'Atlanta',
    job: 'Exterior painting',
    date: 'March 2026',
    rating: 5,
    text: 'They scraped what needed scraping and did not try to roll over the failed coat. Two-story colonial, done in a week of actual weather, not a promise.',
  },
  {
    author: 'Tom R.',
    location: 'Decatur',
    job: 'Interior painting',
    date: 'January 2026',
    rating: 5,
    text: 'Lived in the house the whole time. Floors stayed covered, furniture went back, and the cut lines on the trim are actually straight.',
  },
  {
    author: 'Elena V.',
    location: 'Marietta',
    job: 'Deck stain',
    date: 'April 2026',
    rating: 5,
    text: 'Deck had been peeling for two summers. They washed, waited, and stained it so it looks like wood again — not plastic.',
  },
  {
    author: 'Marcus W.',
    location: 'Roswell',
    job: 'Trim and siding',
    date: 'February 2026',
    rating: 5,
    text: 'Fascia and soffits were the tired part. They treated it as its own job, not an afterthought on a body-paint quote.',
  },
] as const

export const FAQS = [
  {
    q: 'Do you paint interiors?',
    a: 'Yes, as a second line. Exterior work is what we lead with. If the interior is a good fit for the schedule, we write it on the same estimate.',
  },
  {
    q: 'How do estimates work?',
    a: 'Call, book a time, or send the form. We walk the house, talk prep, and send a written number before anything starts. No open-ended hourly rate.',
  },
  {
    q: 'Are you licensed and insured?',
    a: 'Yes. Licensed and insured for residential painting in metro Atlanta.',
  },
  {
    q: 'What areas do you serve?',
    a: 'Atlanta, Decatur, Marietta, Roswell, Sandy Springs, and Brookhaven. If you are just outside that ring, call — we often can make it work.',
  },
  {
    q: 'How long does an exterior take?',
    a: 'Most two-story homes take three to six days of weather-dependent work. We put a window on the quote and we do not paint in the rain.',
  },
  {
    q: 'Will you paint over peeling paint?',
    a: 'No. We scrape, sand, and prime failed coatings. If the substrate is too far gone, we tell you before we start.',
  },
] as const

export const TRUST_ITEMS = [
  { label: 'Licensed & insured', sub: 'Residential painting, metro Atlanta' },
  { label: 'Written estimates', sub: 'A number before we open a can' },
  { label: 'Metro Atlanta', sub: 'Six cities we work every week' },
  { label: 'On-site reviews', sub: 'Words from houses we actually painted' },
] as const

export const TRUST_CHIPS = [
  'Licensed & insured',
  'Written estimates',
  'Metro Atlanta',
  'On-site reviews',
] as const

export const PROCESS_STEPS = [
  {
    num: '01',
    title: 'You call',
    body: 'A person picks up. We ask the house, the surfaces, and the timing, then set a walkthrough.',
  },
  {
    num: '02',
    title: 'We quote on site',
    body: 'We look at prep, not just square footage. You get a written price before anything starts.',
  },
  {
    num: '03',
    title: 'We paint and walk it',
    body: 'The crew that quoted it runs the job. We walk the house with you before we call it done.',
  },
] as const

function social(
  destination: SocialPost['destination'],
  title: string,
  body: string,
  imageUrl: string,
): SocialPost {
  return { destination, title, body, imageUrl }
}

export const DUMMY_JOBS: DummyJob[] = [
  {
    slug: 'demo-exterior-atlanta',
    publicTitle: 'Exterior painting in Atlanta',
    publicSummary:
      'Two-story colonial in Buckhead. Full body and trim, scraped failed coatings, primed, two finish coats. Clay-red door stayed as the accent.',
    serviceType: 'Exterior painting',
    city: 'Atlanta',
    publishedAt: '2026-08-12T15:00:00Z',
    primaryImageUrl: '/work/demo-exterior-atlanta-after.jpg',
    hasBefore: true,
    hasAfter: true,
    beforeUrl: '/work/demo-exterior-atlanta-before.jpg',
    afterUrl: '/work/demo-exterior-atlanta-after.jpg',
    socialPosts: [
      social(
        'facebook',
        'Buckhead colonial, body and trim',
        'Failed coatings came off first. Then primer, then two finish coats. The door stayed clay-red.',
        '/work/demo-exterior-atlanta-after.jpg',
      ),
      social(
        'instagram',
        'Atlanta exterior, done once',
        'Prep you can see in the before. Finish you can see from the street.',
        '/work/demo-exterior-atlanta-after.jpg',
      ),
      social(
        'google_business',
        'Exterior painting in Atlanta',
        'Full-house exterior in Buckhead. Written estimate, licensed crew, walkthrough at the end.',
        '/work/demo-exterior-atlanta-after.jpg',
      ),
    ],
  },
  {
    slug: 'demo-interior-decatur',
    publicTitle: 'Interior painting in Decatur',
    publicSummary:
      'Oakhurst bungalow living room and hall. Occupied home, floors protected, furniture shifted and returned. Eggshell walls, satin trim.',
    serviceType: 'Interior painting',
    city: 'Decatur',
    publishedAt: '2026-08-02T15:00:00Z',
    primaryImageUrl: '/work/demo-interior-decatur-after.jpg',
    hasBefore: true,
    hasAfter: true,
    beforeUrl: '/work/demo-interior-decatur-before.jpg',
    afterUrl: '/work/demo-interior-decatur-after.jpg',
    socialPosts: [
      social(
        'facebook',
        'Decatur bungalow interior',
        'Lived-in house, not an empty spec. Floors stayed covered. Rooms usable the evening the last coat dried.',
        '/work/demo-interior-decatur-after.jpg',
      ),
      social(
        'instagram',
        'Cut lines, then we leave',
        'Eggshell walls. Satin trim. Furniture back where it started.',
        '/work/demo-interior-decatur-after.jpg',
      ),
      social(
        'google_business',
        'Interior painting in Decatur',
        'Living room and hall in Oakhurst. Occupied-home interior, written quote before we started.',
        '/work/demo-interior-decatur-after.jpg',
      ),
    ],
  },
  {
    slug: 'demo-deck-marietta',
    publicTitle: 'Deck stain in Marietta',
    publicSummary:
      'East Cobb deck and rails. Washed, dried, then a semi-transparent stain that reads as wood instead of a peeling film.',
    serviceType: 'Decks and fences',
    city: 'Marietta',
    publishedAt: '2026-07-22T15:00:00Z',
    primaryImageUrl: '/work/demo-deck-marietta-after.jpg',
    hasBefore: true,
    hasAfter: true,
    beforeUrl: '/work/demo-deck-marietta-before.jpg',
    afterUrl: '/work/demo-deck-marietta-after.jpg',
    socialPosts: [
      social(
        'facebook',
        'Marietta deck, stained properly',
        'Gray boards had two summers of failed film. We washed, waited, and stained it so it looks like cedar again.',
        '/work/demo-deck-marietta-after.jpg',
      ),
      social(
        'instagram',
        'Wood, not plastic',
        'Semi-transparent stain on an East Cobb deck. Rails included.',
        '/work/demo-deck-marietta-after.jpg',
      ),
      social(
        'google_business',
        'Deck staining in Marietta',
        'Deck and fence stain in East Cobb. Wash, dry, finish. Written estimate.',
        '/work/demo-deck-marietta-after.jpg',
      ),
    ],
  },
  {
    slug: 'demo-trim-roswell',
    publicTitle: 'Trim and siding in Roswell',
    publicSummary:
      'North Fulton ranch. Fascia, soffits, shutters, and window trim. Body color stayed; the edges got the work.',
    serviceType: 'Trim and siding',
    city: 'Roswell',
    publishedAt: '2026-07-08T15:00:00Z',
    primaryImageUrl: '/work/demo-trim-roswell-after.jpg',
    hasBefore: true,
    hasAfter: true,
    beforeUrl: '/work/demo-trim-roswell-before.jpg',
    afterUrl: '/work/demo-trim-roswell-after.jpg',
    socialPosts: [
      social(
        'facebook',
        'Roswell fascia and soffits',
        'The body paint was fine. The eaves were not. Trim-only job, finished in three days.',
        '/work/demo-trim-roswell-after.jpg',
      ),
      social(
        'instagram',
        'Edges first',
        'White fascia, clean soffits, charcoal shutters. North Fulton ranch.',
        '/work/demo-trim-roswell-after.jpg',
      ),
      social(
        'google_business',
        'Trim painting in Roswell',
        'Fascia, soffits, and shutters in North Fulton. Licensed crew, written estimate.',
        '/work/demo-trim-roswell-after.jpg',
      ),
    ],
  },
]

export function getDummyJob(slug: string): DummyJob | undefined {
  return DUMMY_JOBS.find((j) => j.slug === slug)
}

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

export function areaServicePath(areaSlug: string, serviceSlug: string) {
  return `/service-area/${areaSlug}/${serviceSlug}`
}

export function serviceInAreaTitle(service: ServiceDef, area: AreaDef) {
  return `${service.name} in ${area.city}, ${area.state}`
}

export function serviceInAreaDescription(service: ServiceDef, area: AreaDef) {
  return `${service.name} in ${area.city}, ${area.state}. ${service.short} Written estimates from Red Clay.`
}

export function serviceInAreaIntro(service: ServiceDef, area: AreaDef) {
  return `Looking for ${service.name.toLowerCase()} in ${area.city}? Red Clay serves ${area.note.toLowerCase()} with a licensed crew, clean jobsite habits, and a written estimate. ${service.description}`
}

export function reviewsForArea(city: string) {
  return REVIEWS.filter((r) => r.location.toLowerCase() === city.toLowerCase())
}

export function formatPhoneDisplay(phone: string) {
  const digits = phone.replace(/\D/g, '')
  if (digits.length === 10) return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
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
