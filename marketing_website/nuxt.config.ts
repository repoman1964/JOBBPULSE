export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  ssr: true,
  app: {
    head: {
      title: 'JobbPulse | Marketing from the jobs you already finish',
      htmlAttrs: { lang: 'en' },
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Take a few photos, talk for 30 seconds, and JobbPulse turns the job into social posts, a fresh contractor website, and follow-up with new leads.',
        },
        { name: 'theme-color', content: '#1c1915' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap',
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      appUrl: process.env.NUXT_PUBLIC_APP_URL || 'http://localhost:3000',
      buyUrl: process.env.NUXT_PUBLIC_BUY_URL || '/get',
      contactEmail: process.env.NUXT_PUBLIC_CONTACT_EMAIL || 'hello@jobbpulse.com',
      vslUrl: process.env.NUXT_PUBLIC_VSL_URL || '',
      vslPoster: process.env.NUXT_PUBLIC_VSL_POSTER || '/images/jobs-page-clay.png',
      thankYouVideoUrl: process.env.NUXT_PUBLIC_THANK_YOU_VIDEO_URL || '',
      thankYouVideoPoster:
        process.env.NUXT_PUBLIC_THANK_YOU_VIDEO_POSTER || '/images/jobs-page-clay.png',
      stripePaymentLink:
        process.env.NUXT_PUBLIC_STRIPE_PAYMENT_LINK ||
        'https://buy.stripe.com/7sY14ofxp4Sb8DvcEngrS0a',
    },
  },
  routeRules: {
    '/get/success': { redirect: { to: '/thank-you', statusCode: 301 } },
  },
  css: ['~/assets/css/main.css'],
  vite: {
    server: {
      allowedHosts: true,
    },
  },
  nitro: {
    // Workers Builds selects cloudflare-module when wrangler.jsonc is present.
    // Use that preset so `nuxt build` emits .output/server/index.mjs for wrangler.
    preset: 'cloudflare-module',
    cloudflare: {
      nodeCompat: true,
    },
    prerender: {
      crawlLinks: true,
      routes: ['/', '/privacy', '/terms', '/get', '/buy', '/thank-you', '/get/success', '/refund'],
    },
  },
})
