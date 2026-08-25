export const offer = {
  productName: 'JobbPulse',
  sku: 'jobbpulse-core',
  price: 197,
  priceLabel: '$197',
  priceAmount: '197.00',
  priceCurrency: 'USD',
  pricePeriod: 'per month',
  planLabel: 'Founder plan',
  highlightLabel: 'Marketing Everywhere',
  highlightStat: '30 secs',
  highlightBody:
    'Take a few photos. Talk for about 30 seconds. JobbPulse takes it from there.',
  guaranteeTitle: 'The JobbPulse 90-Day Work Guarantee',
  guaranteeBody:
    "Give JobbPulse 90 days and actually put it to work. Submit at least four completed jobs with the required photos and short voice description. Do that and if you don't see how easy it is to turn your completed jobs into consistent marketing and builds you a stronger online presence, tell us.",
  guaranteeRefund: 'We’ll refund every monthly payment from those first 90 days.',
  promiseTitle: 'The 48 Hour Publishing Promise',
  promiseBody:
    "Once you approve a completed-job package, we'll publish it within 48 hours to your Facebook Page, Instagram, Google Business Profile, 3–5 local homeowners groups, your website (home carousel and a page for that job), and the JobbPulse directory.",
  promiseMiss: "If we don't, your next month of JobbPulse is free.",
} as const

export const workGuarantee = {
  title: 'The JobbPulse 90-Day Work Guarantee',
  paragraphs: [
    { text: 'Give JobbPulse 90 days and actually put it to work.' },
    {
      text: 'Complete your onboarding and submit at least four completed jobs with the required before-and-after photos and short voice description.',
    },
    {
      text: 'We’ll turn those jobs into professional marketing content, add them to your website carousel and a job page, post them to your Facebook Page, Instagram, Google Business Profile and 3–5 local homeowners groups, list them on the JobbPulse directory, and keep those social accounts active between jobs.',
    },
    {
      text: 'If you do your part and, by the end of your first 90 days, you don’t believe JobbPulse has made it substantially easier to turn your completed work into consistent marketing while building a stronger online presence for your business, tell us.',
    },
    {
      text: 'We’ll refund every monthly JobbPulse payment you made during those first 90 days.',
      emphasize: true,
    },
    { text: 'No complicated performance claims.' },
    {
      text: 'No pretending we can guarantee how many homeowners will call you or how many jobs you’ll close.',
    },
    { text: 'You give JobbPulse a fair shot.' },
    { text: 'We do what we promised.' },
    { text: 'Then you decide whether it earned its place in your business.' },
  ],
} as const

export const publishingPromise = {
  title: 'The 48 Hour Publishing Promise',
  paragraphs: [
    { text: 'And we back the ongoing service with another promise.' },
    {
      text: 'Once you approve a completed-job package, we’ll publish it within 48 hours to your Facebook Page, Instagram, Google Business Profile, 3–5 local homeowners groups, your website (home carousel and a page for that job), and the JobbPulse directory.',
    },
    {
      text: 'If we miss that deadline, your next month of JobbPulse is free.',
      emphasize: true,
    },
  ],
} as const

export const priceIncludesShort = [
  'Photos and a 30-second voice note',
  'Facebook Page, Instagram, and Google Business posts',
  'Posts to 3–5 local homeowners groups',
  'Recent-jobs carousel and a job page on your website',
  'A JobbPulse directory project page',
  'Seasonal posts between jobs',
  'Approval before anything goes live',
  'Lead Desk follow-up when someone reaches out',
] as const

export const offerIncludes = [
  'Easy job capture',
  'Auto generated content',
  'Approve before posting',
  'Facebook, Instagram, Google Business',
  'Local homeowners groups',
  'Website carousel and job pages',
  'JobbPulse directory page',
  'Seasonal social cadence',
  'Missed-call follow-up',
  '90-Day Guarantee',
] as const
