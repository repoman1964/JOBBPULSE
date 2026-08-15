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
      contactEmail: process.env.NUXT_PUBLIC_CONTACT_EMAIL || 'hello@jobbpulse.com',
    },
  },
  css: ['~/assets/css/main.css'],
  vite: {
    server: {
      allowedHosts: true,
    },
  },
  nitro: {
    // Workers Builds auto-selects cloudflare-module when wrangler.jsonc exists.
    // This site is prerendered assets only (same as dailydialz-website).
    preset: 'static',
    cloudflare: {
      deployConfig: false,
    },
    prerender: {
      crawlLinks: true,
      routes: ['/', '/privacy', '/terms'],
    },
  },
})
