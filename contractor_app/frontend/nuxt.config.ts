// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,
  modules: ['@pinia/nuxt'],
  css: ['~/assets/css/main.css'],
  // Listen on all interfaces so ngrok / LAN can reach the dev server
  devServer: {
    host: '0.0.0.0',
    port: 3000,
  },
  // Vite blocks unknown Host headers unless allowed (LAN IP / QR code / ngrok mobile testing)
  vite: {
    server: {
      // true = allow phone/LAN Host headers from the Nuxt QR network URL
      allowedHosts: true,
    },
  },
  runtimeConfig: {
    public: {
      apiMode: process.env.NUXT_PUBLIC_API_MODE || 'mock',
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    },
  },
  app: {
    head: {
      title: 'JobbPulse',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#0a0a0a' },
        { name: 'description', content: 'Document the job. JobbPulse creates and publishes the content.' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
  typescript: {
    strict: true,
    typeCheck: false,
  },
})
