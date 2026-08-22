export type ServiceDef = {
  slug: string
  service_key: string
  name: string
  short: string
  description: string
  longDescription: string
  bullets: string[]
  image: string
  heroDirection: string
  faqs: { q: string; a: string }[]
}

export type AreaDef = {
  slug: string
  city: string
  state: string
  note: string
  housing: string
  longDescription: string
  image: string
  testimonial: { author: string; text: string; job: string }
}

export type ProjectDef = {
  slug: string
  title: string
  city: string
  serviceSlug: string
  summary: string
  image: string
}

export const COMPANY = {
  name: 'ABC Painters',
  foundedYear: 2023,
  years: 3,
  teamSize: 4,
  address: '4321 Northeast Flanders',
  city: 'Acworth',
  state: 'GA',
  postcode: '30101',
} as const

export const SERVICES: ServiceDef[] = [
  {
    slug: 'interior-painting',
    service_key: 'interior_painting',
    name: 'Interior Painting',
    short: 'Walls, ceilings, trim, and doors that look finished — not rushed.',
    description:
      'Occupied-home interior painting across Acworth, Kennesaw, and Cartersville. We protect floors and furniture, cut clean lines, and leave rooms you can live in the same day the last coat dries.',
    longDescription:
      'ABC Painters handles interior painting for houses that people actually live in — not empty spec homes. We cover living rooms, bedrooms, hallways, kitchens, and trim work with a prep-first process: fill, sand, caulk, prime where it matters, then two coats of a quality interior product. Dust control and floor protection are part of the job, not extras. Most rooms are back in use the evening the last coat dries. We write the color, sheen, and rooms on the quote so nobody is guessing on paint day.',
    bullets: [
      'Walls, ceilings, trim, doors, and accent walls',
      'Furniture and floor protection in occupied homes',
      'Color matching and sheen recommendations',
      'Two-coat finish with primer where the substrate needs it',
    ],
    image: '/images/interior.jpg',
    heroDirection: 'Freshly painted living room with protected floors and natural window light',
    faqs: [
      {
        q: 'How long does an interior paint job take?',
        a: 'A typical three-bedroom interior is two to four days depending on repairs, number of colors, and whether ceilings and trim are included. We put a schedule on the written quote.',
      },
      {
        q: 'Do I need to move furniture?',
        a: 'Pull small valuables and wall hangings. We shift large furniture to the center, cover it, and put it back. Empty rooms move faster if you want a tighter timeline.',
      },
      {
        q: 'What paint do you use?',
        a: 'We spec washable interior paints from major lines (Sherwin-Williams, Benjamin Moore, or equivalent) at a sheen that matches the room — typically eggshell on walls, satin or semi-gloss on trim.',
      },
      {
        q: 'Will the house smell for days?',
        a: 'We use low-VOC products as a default. You’ll notice paint odor the day of the work; most rooms are livable that evening with windows cracked.',
      },
      {
        q: 'Do you paint cabinets as part of an interior job?',
        a: 'Cabinet refinishing is a separate service with its own prep and spray process. We can schedule it alongside wall work — ask on the estimate.',
      },
    ],
  },
  {
    slug: 'exterior-painting',
    service_key: 'exterior_painting',
    name: 'Exterior Painting',
    short: 'Prep the surface. Then paint. Georgia weather does the rest of the test.',
    description:
      'Full-house and trim-only exterior painting for north Cobb and Bartow County homes. Scraping, sanding, caulk, primer, and two finish coats — not a one-day roll over peeling paint.',
    longDescription:
      'Georgia sun, pollen, and summer storms will tell on a cheap exterior job inside a year. ABC Painters prices exterior painting around prep: scrape loose paint, sand, caulk gaps, prime bare wood and stains, then two finish coats. We work siding, trim, soffits, shutters, and doors. If the substrate is too far gone, we tell you before we open a can — we will not roll over rot and call it a warranty job. Most two-story homes take three to six days of weather-dependent work.',
    bullets: [
      'Siding, trim, soffits, shutters, and entry doors',
      'Scrape, sand, caulk, and prime before finish coats',
      'Weather window scheduling — we do not paint in the rain',
      'Two-year workmanship warranty on labor we complete',
    ],
    image: '/images/exterior.jpg',
    heroDirection: 'Painter on a ladder working the siding of a north Georgia ranch',
    faqs: [
      {
        q: 'When is the best time to paint a house in Acworth?',
        a: 'Spring and fall are the most reliable windows. We paint in summer when humidity and afternoon storms allow. We will not apply finish coats on wet siding.',
      },
      {
        q: 'Do you pressure wash first?',
        a: 'Yes, when the surface needs it. We wash, let the house dry, then scrape and prime. Washing is not a substitute for scraping peeling paint.',
      },
      {
        q: 'Can you match my current color?',
        a: 'Yes. We can pull a sample or scan an existing chip. If you want a new color, we can put sample boards on the house before the full job.',
      },
      {
        q: 'What if you find rotten wood?',
        a: 'We stop and show you. Small carpentry patches can often be handled in-house. Larger rot gets a written change before we paint over it.',
      },
      {
        q: 'Is the two-year warranty on the paint or the labor?',
        a: 'Workmanship. If our prep or application fails in two years, we come back. Manufacturer product warranties sit on top of that.',
      },
    ],
  },
  {
    slug: 'cabinets-and-trim',
    service_key: 'cabinets_and_trim',
    name: 'Cabinets & Trim',
    short: 'Doors off, sprayed, hardware back. A kitchen refresh without a full remodel.',
    description:
      'Cabinet painting and millwork finishing for kitchens, baths, and built-ins. Controlled spray, clean lines, and hardware reinstall so the room looks new without ripping out boxes.',
    longDescription:
      'Cabinet refinishing is not wall painting. ABC Painters takes doors and drawers off, labels every piece, sands, primes, and sprays in a controlled setup so you get a factory-smooth finish instead of brush marks. Boxes stay in place and get rolled or sprayed in the room under plastic. We reinstall hardware or swap it if you supply new pulls. Typical kitchens are four to seven days, with a period where the kitchen is limited — we plan that with you on the quote.',
    bullets: [
      'Kitchen and bath cabinet refinishing',
      'Doors and drawers sprayed; boxes finished in place',
      'Trim, built-ins, and stair rails',
      'Hardware removal, labeling, and reinstall',
    ],
    image: '/images/cabinets.jpg',
    heroDirection: 'Kitchen cabinets in progress with doors off and plastic sheeting down',
    faqs: [
      {
        q: 'Can I use the kitchen during cabinet painting?',
        a: 'Plan on a limited kitchen for several days. We stage work so the sink and fridge stay accessible when we can, but doors will be off and surfaces covered.',
      },
      {
        q: 'Will it chip like the last paint job?',
        a: 'Chipping is almost always a prep failure. We sand, degloss, and prime for adhesion. We do not brush one coat of wall paint onto slick cabinet doors.',
      },
      {
        q: 'Do you paint laminate cabinets?',
        a: 'Some laminates take a specialty bonding primer. We inspect first. If the surface will not hold, we say so instead of guaranteeing a finish that will peel.',
      },
      {
        q: 'Can you change hardware holes?',
        a: 'Yes, if you pick new hardware before we spray. Filling and recutting holes after finish is extra work and shows if it is rushed.',
      },
      {
        q: 'Is this cheaper than new cabinets?',
        a: 'Usually, if boxes are solid. If boxes are failing, replacement is the honest recommendation. We will tell you which side you are on.',
      },
    ],
  },
]

export const SERVICE_AREAS: AreaDef[] = [
  {
    slug: 'acworth',
    city: 'Acworth',
    state: 'GA',
    note: 'Home base · Cobb County',
    housing:
      'Mix of 1990s–2010s two-stories around Lake Allatoona, ranch homes near the historic downtown, and newer infill off Hwy 92.',
    longDescription:
      'ABC Painters is based in Acworth. Interior and exterior crews run from 4321 Northeast Flanders and cover the city first — downtown, the lake neighborhoods, and the Hwy 92 corridor. Response is typically fastest here because we are not driving across metro Atlanta. Homeowners call us for occupied-home interiors, full exteriors before listing, and kitchen cabinet refreshes. If you are in Acworth, we can usually walk the job the same week you call.',
    image: '/images/city-acworth.jpg',
    testimonial: {
      author: 'Sarah M.',
      text: 'They painted our whole interior while we stayed in the house. Floors stayed covered, trim lines were sharp, and they were gone when they said they would be.',
      job: 'Interior painting · March 2026',
    },
  },
  {
    slug: 'kennesaw',
    city: 'Kennesaw',
    state: 'GA',
    note: 'Cobb County',
    housing:
      'Larger two-story subdivisions, older cottages near Kennesaw Mountain, and 2000s tract homes off Barrett and Wade Green.',
    longDescription:
      'Kennesaw is a regular ABC Painters route — fifteen to twenty minutes from our Acworth shop. We paint interiors in occupied family homes, exteriors on two-story elevations that need proper ladder and lift work, and cabinet refinishing in kitchens that are dated but structurally sound. Neighborhoods off Barrett Parkway, near Kennesaw State, and around the mountain are all in range. Written quotes before we start; no surprise day-rate at the end of the week.',
    image: '/images/city-kennesaw.jpg',
    testimonial: {
      author: 'David R.',
      text: 'Exterior had peeling on the south wall. They scraped it properly instead of rolling over it. Two months of Georgia sun later, it still looks even.',
      job: 'Exterior painting · January 2026',
    },
  },
  {
    slug: 'cartersville',
    city: 'Cartersville',
    state: 'GA',
    note: 'Bartow County',
    housing:
      'Brick ranches, historic downtown homes, and newer subdivisions along 41 and toward Lake Allatoona’s north side.',
    longDescription:
      'Cartersville and Bartow County sit on our northern loop. ABC Painters takes interior, exterior, and cabinet jobs here by scheduled appointment — typically a site visit within a few days of your call, then a written quote. Older brick ranches often need trim and fascia work before the body coat; we call that out on the walkthrough. We do not treat Cartersville as a leftover market. If we book you, you get the same four-person crew we run in Acworth.',
    image: '/images/city-cartersville.jpg',
    testimonial: {
      author: 'Elena T.',
      text: 'Kitchen cabinets look new. They labeled every door, sprayed them off-site of the dust, and put the hardware back like it had never left.',
      job: 'Cabinets & trim · February 2026',
    },
  },
]

export const PROJECTS: ProjectDef[] = [
  {
    slug: 'acworth-two-story-exterior',
    title: 'Two-story exterior, Acworth',
    city: 'Acworth',
    serviceSlug: 'exterior-painting',
    summary: 'Full body, trim, and shutters. South wall scraped to sound paint before primer.',
    image: '/images/portfolio-acworth.jpg',
  },
  {
    slug: 'kennesaw-living-dining-interior',
    title: 'Living and dining interior, Kennesaw',
    city: 'Kennesaw',
    serviceSlug: 'interior-painting',
    summary: 'Greige walls, white crown, occupied home. Two colors, four days.',
    image: '/images/portfolio-kennesaw.jpg',
  },
  {
    slug: 'cartersville-kitchen-cabinets',
    title: 'Kitchen cabinet refinish, Cartersville',
    city: 'Cartersville',
    serviceSlug: 'cabinets-and-trim',
    summary: 'Doors sprayed, boxes finished in place, hardware swapped at reinstall.',
    image: '/images/portfolio-cartersville.jpg',
  },
]

export const TEAM = [
  { name: 'Marcus Hale', role: 'Owner & lead', years: 'Runs the quotes and the walkthroughs.' },
  { name: 'Elena Brooks', role: 'Lead painter', years: 'Interiors and cut-in that actually meets the trim.' },
  { name: 'DeShawn Carter', role: 'Exterior lead', years: 'Ladders, siding, and weather calls.' },
  { name: 'Priya Patel', role: 'Cabinets & finish', years: 'Spray setup, doors, and hardware maps.' },
] as const

export const REVIEWS = [
  {
    author: 'Sarah M.',
    location: 'Acworth',
    job: 'Interior painting',
    text: 'They painted our whole interior while we stayed in the house. Floors stayed covered, trim lines were sharp, and they were gone when they said they would be.',
  },
  {
    author: 'David R.',
    location: 'Kennesaw',
    job: 'Exterior painting',
    text: 'Exterior had peeling on the south wall. They scraped it properly instead of rolling over it. Two months of Georgia sun later, it still looks even.',
  },
  {
    author: 'Elena T.',
    location: 'Cartersville',
    job: 'Cabinets & trim',
    text: 'Kitchen cabinets look new. They labeled every door, sprayed them off-site of the dust, and put the hardware back like it had never left.',
  },
] as const

export const HOME_FAQS = [
  {
    q: 'Do you give a price over the phone?',
    a: 'We can ballpark from photos. A written quote needs a site visit so we can see prep, access, and colors. The visit is free.',
  },
  {
    q: 'Are you licensed and insured?',
    a: 'Yes. ABC Painters is licensed and insured for residential painting in Georgia. Proof is on the quote packet if you want it before we start.',
  },
  {
    q: 'Do you subcontract the work?',
    a: 'No. A four-person crew, directly employed. The people at the walkthrough are the people on the job.',
  },
  {
    q: 'What cities do you cover?',
    a: 'Acworth, Kennesaw, and Cartersville. If you are just outside that triangle, call — we will tell you honestly if the drive works.',
  },
  {
    q: 'How does the two-year warranty work?',
    a: 'If our workmanship fails within two years, we come back and make it right. It covers labor we performed, not storm damage or a substrate we already flagged.',
  },
  {
    q: 'Do I pick colors myself?',
    a: 'You can. We also help with samples on the wall or the siding so you are not guessing from a chip in fluorescent light.',
  },
] as const

export const FAQS = [
  ...HOME_FAQS,
  {
    q: 'What is included in prep?',
    a: 'Scrape, sand, caulk, and prime as the surface needs. We do not skip prep to hit a cheap number. If the house needs more carpentry than painting, we say so.',
  },
  {
    q: 'Do you paint decks and fences?',
    a: 'Stain and paint on decks or fences can be added to an exterior job. It is quoted separately because the prep is different.',
  },
  {
    q: 'How do payments work?',
    a: 'Deposit to hold the schedule, remainder on completion. We do not take the last check until you walk the job with us.',
  },
  {
    q: 'Can you start this week?',
    a: 'Sometimes in Acworth. Kennesaw and Cartersville are usually a scheduled slot. Call (555) 123-4567 and we will look at the board.',
  },
  {
    q: 'What if it rains mid-exterior?',
    a: 'We stop. Finish coats go on dry siding. The schedule flexes; we do not trap moisture under new paint.',
  },
  {
    q: 'Do you move a washer, fridge, or piano?',
    a: 'Appliances stay. We paint around them or ask you to pull them if you want the wall behind done. Pianos and safes stay put — we cut in around.',
  },
] as const

export const TRUST_ITEMS = [
  { label: 'Licensed & insured', sub: 'Georgia residential painting' },
  { label: 'Prep-first process', sub: 'Scrape, sand, caulk, prime' },
  { label: 'Written quotes', sub: 'Before any paint goes on' },
  { label: '2-year warranty', sub: 'Workmanship we stand behind' },
] as const

export function getService(slug: string) {
  return SERVICES.find((s) => s.slug === slug)
}

export function getArea(slug: string) {
  return SERVICE_AREAS.find((a) => a.slug === slug)
}

export function servicePath(slug: string) {
  return `/services/${slug}`
}

export function areaPath(slug: string) {
  return `/service-areas/${slug}`
}
