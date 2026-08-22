<script setup lang="ts">
import { SERVICES, COMPANY } from '~/utils/siteContent'

const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const email = config.public.email as string
const route = useRoute()

const prefillKey = computed(() => String(route.query.service || ''))
const prefillLabel = computed(() => SERVICES.find((x) => x.service_key === prefillKey.value)?.name)

useSeoMeta({
  title: 'Contact & Free Estimate | ABC Painters',
  description: 'Request a free painting estimate in Acworth, Kennesaw, or Cartersville, GA. Call (555) 123-4567.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Contact' }]" />
        <p class="section__eyebrow">Contact</p>
        <h1 class="page-hero__title">Free estimate</h1>
        <p class="section__lead">
          Tell us about the house. Prefer the phone?
          <a :href="`tel:${phoneTel}`"><strong>{{ phone }}</strong></a>
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container contact-grid">
        <div>
          <p v-if="prefillLabel" class="badge" style="margin-bottom: 0.75rem">Interested in: {{ prefillLabel }}</p>
          <EstimateForm />
        </div>
        <aside class="contact-aside">
          <h2>Shop &amp; hours</h2>
          <ul>
            <li>
              <strong>Phone</strong>
              <a :href="`tel:${phoneTel}`">{{ phone }}</a>
            </li>
            <li>
              <strong>Email</strong>
              <a :href="`mailto:${email}`">{{ email }}</a>
            </li>
            <li>
              <strong>Address</strong>
              <span class="muted">{{ COMPANY.address }}<br />{{ COMPANY.city }}, {{ COMPANY.state }} {{ COMPANY.postcode }}</span>
            </li>
            <li>
              <strong>Hours</strong>
              <span class="muted">Mon–Fri 7am–7pm · Sat by appointment</span>
            </li>
          </ul>
        </aside>
      </div>
    </section>
  </div>
</template>

<style scoped>
.contact-grid {
  display: grid;
  gap: 1.75rem;
}

@media (min-width: 800px) {
  .contact-grid {
    grid-template-columns: 1.35fr 0.9fr;
    align-items: start;
  }
}

.contact-aside {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.contact-aside h2 {
  margin-top: 0;
  font-size: 1.15rem;
}

.contact-aside ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.85rem;
}

.contact-aside li {
  display: grid;
  gap: 0.15rem;
}

.contact-aside strong {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}
</style>
