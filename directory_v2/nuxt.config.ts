// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: true,
  app: {
    head: {
      title: 'JobPulse — Local Project Portfolio',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Browse real projects completed by local contractors.',
        },
      ],
      link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      contractorAppUrl: process.env.NUXT_PUBLIC_APP_URL || 'http://localhost:3000',
      siteUrl: process.env.NUXT_PUBLIC_DIRECTORY_URL || 'http://localhost:3001',
    },
  },
  css: ['~/assets/css/main.css'],
})
