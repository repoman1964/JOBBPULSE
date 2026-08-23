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
      title: 'Red Clay | Painting · Metro Atlanta',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Exterior painting first, interiors as a second line. Written estimates. Licensed and insured across metro Atlanta.',
        },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap',
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      apiBase:
        process.env.NUXT_PUBLIC_API_BASE_URL ||
        (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'),
      companyName: 'Red Clay',
      phone: '404-555-0148',
      phoneTel: '+14045550148',
      email: 'hello@redclaypainting.com',
    },
  },
  css: ['~/assets/css/main.css', '~/assets/css/silo-pages.css'],
  vite: {
    server: {
      allowedHosts: true,
    },
  },
})
