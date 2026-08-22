export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: true,
  app: {
    head: {
      title: 'ABC Painters | Interior & Exterior Painting in Acworth, GA',
      htmlAttrs: { lang: 'en' },
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Residential interior and exterior painting in Acworth, Kennesaw, and Cartersville, GA. Prep-first crews, written quotes, two-year workmanship warranty. Call (555) 123-4567.',
        },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
  runtimeConfig: {
    public: {
      companyName: process.env.NUXT_PUBLIC_COMPANY_NAME || 'ABC Painters',
      phone: process.env.NUXT_PUBLIC_PHONE || '555-123-4567',
      phoneTel: process.env.NUXT_PUBLIC_PHONE_TEL || '+15551234567',
      email: process.env.NUXT_PUBLIC_EMAIL || 'painter@abcpainters.com',
      address: '4321 Northeast Flanders',
      city: 'Acworth',
      state: 'GA',
      postcode: '30101',
    },
  },
  css: ['~/assets/css/main.css'],
  vite: {
    server: {
      allowedHosts: true,
    },
  },
})
