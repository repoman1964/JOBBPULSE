<script setup lang="ts">
import { SERVICES, SERVICE_AREAS, COMPANY, servicePath, areaPath } from '~/utils/siteContent'

const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const email = config.public.email as string
const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="container site-footer__grid">
      <div>
        <div class="site-footer__brand">
          <span class="site-footer__mark" aria-hidden="true">ABC</span>
          <div>
            <strong>{{ COMPANY.name }}</strong>
            <p class="site-footer__tag">
              Local, licensed painters serving Acworth, Kennesaw, and Cartersville since {{ COMPANY.foundedYear }}.
            </p>
            <p class="site-footer__chip">LICENSED · INSURED · 2-YEAR WARRANTY</p>
          </div>
        </div>
      </div>

      <div>
        <h3 class="site-footer__heading">Services</h3>
        <ul class="site-footer__list">
          <li><NuxtLink to="/services">All services</NuxtLink></li>
          <li v-for="s in SERVICES" :key="s.slug">
            <NuxtLink :to="servicePath(s.slug)">{{ s.name }}</NuxtLink>
          </li>
          <li><NuxtLink to="/portfolio">Portfolio</NuxtLink></li>
        </ul>
      </div>

      <div>
        <h3 class="site-footer__heading">Areas covered</h3>
        <ul class="site-footer__list">
          <li><NuxtLink to="/service-areas">All service areas</NuxtLink></li>
          <li v-for="a in SERVICE_AREAS" :key="a.slug">
            <NuxtLink :to="areaPath(a.slug)">{{ a.city }}, {{ a.state }}</NuxtLink>
          </li>
        </ul>
      </div>

      <div>
        <h3 class="site-footer__heading">Get in touch</h3>
        <ul class="site-footer__list">
          <li>
            <a class="site-footer__phone" :href="`tel:${phoneTel}`">{{ phone }}</a>
          </li>
          <li><a :href="`mailto:${email}`">{{ email }}</a></li>
          <li>Mon–Fri 7:00–19:00 for estimates</li>
          <li>{{ COMPANY.address }}</li>
          <li>{{ COMPANY.postcode }} {{ COMPANY.city }}, {{ COMPANY.state }}</li>
        </ul>
      </div>
    </div>
    <div class="container site-footer__bottom">
      <span>© {{ year }} {{ COMPANY.name }}.</span>
      <span>
        <NuxtLink to="/privacy">Privacy</NuxtLink>
        ·
        <NuxtLink to="/terms">Terms</NuxtLink>
        ·
        <NuxtLink to="/faq">FAQ</NuxtLink>
      </span>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: var(--navy);
  color: var(--on-dark);
  padding: 4rem 0 1.5rem;
}

.site-footer a {
  color: rgba(250, 250, 247, 0.85);
}

.site-footer a:hover {
  color: #fff;
}

.site-footer__grid {
  display: grid;
  gap: 2rem;
}

@media (min-width: 640px) {
  .site-footer__grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 960px) {
  .site-footer__grid {
    grid-template-columns: 1.4fr 1fr 1fr 1.1fr;
  }
}

.site-footer__brand {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.site-footer__mark {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius);
  background: var(--orange);
  color: #fff;
  font-weight: 800;
  font-size: 0.7rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.site-footer__tag {
  color: rgba(250, 250, 247, 0.8);
  margin: 0.25rem 0 0.6rem;
  font-size: 0.92rem;
  max-width: 16rem;
}

.site-footer__chip {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  color: var(--on-dark);
  border: 1px solid var(--orange);
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-family: ui-monospace, monospace;
}

.site-footer__heading {
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--orange);
  margin-bottom: 0.75rem;
}

.site-footer__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.45rem;
  color: rgba(250, 250, 247, 0.8);
  font-size: 0.95rem;
}

.site-footer__phone {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--orange) !important;
  text-decoration: none !important;
}

.site-footer__bottom {
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(250, 250, 247, 0.15);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  justify-content: space-between;
  font-size: 0.82rem;
  color: rgba(250, 250, 247, 0.6);
}
</style>
