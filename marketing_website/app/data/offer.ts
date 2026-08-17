export const offer = {
  productName: 'JobbPulse',
  sku: 'jobbpulse-core',
  price: 97,
  priceLabel: '$97',
  priceAmount: '97.00',
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
    "Once you approve a completed-job package, we'll publish it to all your connected social media accounts and to your website and our local JobbPulse directory listing within 48 hours.",
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
      text: 'We’ll turn those jobs into professional marketing content, keep your JobbPulse website supplied with fresh completed-project proof, and publish your approved content to the destinations included in your plan.',
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
      text: 'Once you approve a completed-job package, we’ll publish it to all your connected social media accounts and to your website and our local JobbPulse directory listing within 48 hours.',
    },
    {
      text: 'If we miss that deadline, your next month of JobbPulse is free.',
      emphasize: true,
    },
  ],
} as const

export const priceIncludesShort = [
  'Photos and a 30-second voice note',
  'Social posts from real completed jobs',
  'Fresh projects on your website',
  'A JobbPulse project page homeowners can see',
  'Approval before anything goes live',
  'Lead Desk follow-up when someone reaches out',
] as const

export const offerIncludes = [
  'Easy job capture',
  'Auto generated content',
  'Approve before posting',
  'Social publishing',
  'Website updates',
  'JobbPulse project page',
  'Missed-call follow-up',
  '90-Day Guarantee',
] as const
