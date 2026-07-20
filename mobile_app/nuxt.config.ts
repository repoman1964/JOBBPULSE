// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false, // contractor app is mobile SPA / PWA-first
  app: {
    head: {
      title: 'JobPulse',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#185FA5' },
        { name: 'description', content: 'Turn completed jobs into marketing.' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'default' },
      ],
      link: [{ rel: 'manifest', href: '/manifest.webmanifest' }],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      appUrl: process.env.NUXT_PUBLIC_APP_URL || 'http://localhost:3000',
      directoryUrl: process.env.NUXT_PUBLIC_DIRECTORY_URL || 'http://localhost:3001',
    },
  },
  css: ['~/assets/css/main.css'],
})
