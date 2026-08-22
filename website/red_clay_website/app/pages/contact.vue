<script setup lang="ts">
import { SERVICES } from '~/utils/siteContent'

const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const email = config.public.email as string
const route = useRoute()

// Prefill service from query when linked from services page
const prefillKey = computed(() => String(route.query.service || ''))
const prefillLabel = computed(() => {
  const s = SERVICES.find((x) => x.service_key === prefillKey.value)
  return s?.name
})

useSeoMeta({
  title: 'Contact & Free Estimate | Red Clay',
  description: 'Request a free cabinet installation estimate in metro Atlanta. Call or use the form.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">Contact</p>
        <h1 class="page-hero__title">Free estimate</h1>
        <p class="section__lead">
          Tell us about the room. Prefer the phone?
          <a :href="`tel:${phoneTel}`"><strong>{{ phone }}</strong></a>
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container contact-grid">
        <div>
          <p v-if="prefillLabel" class="badge" style="margin-bottom: 0.75rem">
            Interested in: {{ prefillLabel }}
          </p>
          <EstimateForm source-page-type="contact" />
        </div>
        <aside class="contact-aside">
          <h2>Other ways to reach us</h2>
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
              <strong>Hours</strong>
              <span class="muted">Mon–Fri 8am–5pm · Sat by appointment</span>
            </li>
            <li>
              <strong>Area</strong>
              <span class="muted">Metro Atlanta, GA</span>
            </li>
          </ul>
          <p class="muted contact-aside__note">
            Form leads post to JobPulse when the API is running—same lead pipeline as the public directory.
          </p>
        </aside>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-hero {
  padding: 2.5rem 0 1rem;
  background: var(--clay-mist);
  border-bottom: 1px solid var(--border);
}

.page-hero__title {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
}

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
  box-shadow: var(--shadow);
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

.contact-aside__note {
  margin: 1.25rem 0 0;
  font-size: 0.85rem;
}
</style>
