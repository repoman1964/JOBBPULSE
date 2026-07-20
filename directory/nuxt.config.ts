// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: true, // public directory needs SEO / SSR
  app: {
    head: {
      title: 'JobPulse Local Directory',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Local project proof for home-service contractors — before and after work that actually happened.',
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      directoryUrl: process.env.NUXT_PUBLIC_DIRECTORY_URL || 'http://localhost:3001',
    },
  },
  css: ['~/assets/css/main.css'],
})
