// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: true,
  // Cloudflare Pages (Git / wrangler pages deploy)
  // Output: dist/  (+ dist/_worker.js for SSR)
  nitro: {
    preset: 'cloudflare-pages',
  },
  app: {
    head: {
      title: 'Red Clay Cabinet Installers | Metro Atlanta',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Kitchen cabinets, bath vanities, and built-ins installed clean across metro Atlanta. Free estimates. Licensed & insured.',
        },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      contractorSlug: process.env.NUXT_PUBLIC_CONTRACTOR_SLUG || 'red-clay-cabinet-installers',
      directoryUrl: process.env.NUXT_PUBLIC_DIRECTORY_URL || 'http://localhost:3001',
      companyName: 'Red Clay Cabinet Installers',
      phone: '404-555-0148',
      phoneTel: '+14045550148',
      email: 'hello@redclaycabinets.demo',
    },
  },
  css: ['~/assets/css/main.css', '~/assets/css/silo-pages.css'],
  vite: {
    server: {
      allowedHosts: true,
    },
  },
})
