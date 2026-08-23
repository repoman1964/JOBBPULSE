<script setup lang="ts">
import { SERVICES, SERVICE_AREAS, servicePath, areaPath } from '~/utils/siteContent'

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
        <p class="site-footer__wordmark">Red Clay</p>
        <p class="site-footer__tag">Painting · Metro Atlanta. Exterior first. Written estimates. A crew that shows up.</p>
        <p class="site-footer__cred">Licensed · Insured · Est. 2014</p>
      </div>
      <div>
        <h3 class="site-footer__heading">Services</h3>
        <ul class="site-footer__list">
          <li v-for="s in SERVICES" :key="s.slug">
            <NuxtLink :to="servicePath(s.slug)">{{ s.name }}</NuxtLink>
          </li>
        </ul>
      </div>
      <div>
        <h3 class="site-footer__heading">Areas</h3>
        <ul class="site-footer__list">
          <li v-for="a in SERVICE_AREAS" :key="a.slug">
            <NuxtLink :to="areaPath(a.slug)">{{ a.city }}</NuxtLink>
          </li>
        </ul>
      </div>
      <div>
        <h3 class="site-footer__heading">Get in touch</h3>
        <ul class="site-footer__list">
          <li><a class="site-footer__phone" :href="`tel:${phoneTel}`">{{ phone }}</a></li>
          <li><a :href="`mailto:${email}`">{{ email }}</a></li>
          <li><NuxtLink to="/book">Book an estimate</NuxtLink></li>
          <li>Mon–Fri 8:00–17:00</li>
        </ul>
      </div>
    </div>
    <div class="container site-footer__bottom">
      <span>© {{ year }} Red Clay.</span>
      <span>
        <NuxtLink to="/privacy">Privacy</NuxtLink>
        ·
        <NuxtLink to="/terms">Terms</NuxtLink>
        ·
        <NuxtLink to="/my-work">See your project</NuxtLink>
      </span>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: var(--charcoal);
  color: var(--on-dark);
  padding: 5rem 0 2.5rem;
  border-top: 1px solid var(--clay);
}

.site-footer a {
  color: rgba(247, 244, 238, 0.8);
  text-decoration: none;
}

.site-footer a:hover {
  color: #fff;
}

.site-footer__grid {
  display: grid;
  gap: 2rem;
}

@media (min-width: 900px) {
  .site-footer__grid {
    grid-template-columns: 1.3fr 1fr 1fr 1fr;
  }
}

.site-footer__wordmark {
  font-family: var(--serif);
  font-size: 1.5rem;
  color: #fff;
  margin: 0 0 0.5rem;
}

.site-footer__tag {
  max-width: 16rem;
  font-size: 0.9rem;
  color: rgba(247, 244, 238, 0.75);
}

.site-footer__cred {
  font-size: 0.8125rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--clay);
}

.site-footer__heading {
  font-family: var(--sans);
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--clay);
}

.site-footer__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.45rem;
}

.site-footer__phone {
  color: var(--clay) !important;
  font-size: 1.25rem;
  font-weight: 600;
}

.site-footer__bottom {
  margin-top: 3rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(247, 244, 238, 0.15);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  justify-content: space-between;
  font-size: 0.82rem;
  color: rgba(247, 244, 238, 0.55);
}
</style>
