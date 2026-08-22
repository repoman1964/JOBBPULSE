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
        <div class="site-footer__brand">
          <span class="site-footer__mark" aria-hidden="true">RC</span>
          <div>
            <strong>Red Clay Cabinet Installers</strong>
            <p class="site-footer__tag">Kitchen cabinets, vanities &amp; built-ins across metro Atlanta.</p>
          </div>
        </div>
        <ul class="site-footer__list" style="margin-top: 1rem">
          <li><NuxtLink to="/portfolio">Portfolio</NuxtLink></li>
          <li><NuxtLink to="/about">About</NuxtLink></li>
          <li><NuxtLink to="/reviews">Reviews</NuxtLink></li>
          <li><NuxtLink to="/faq">FAQ</NuxtLink></li>
          <li><NuxtLink to="/contact">Contact</NuxtLink></li>
        </ul>
      </div>

      <div>
        <h3 class="site-footer__heading">Services</h3>
        <ul class="site-footer__list">
          <li><NuxtLink to="/services">All services</NuxtLink></li>
          <li v-for="s in SERVICES" :key="s.slug">
            <NuxtLink :to="servicePath(s.slug)">{{ s.name }}</NuxtLink>
          </li>
        </ul>
      </div>

      <div>
        <h3 class="site-footer__heading">Locations</h3>
        <ul class="site-footer__list">
          <li><NuxtLink to="/service-area">All service areas</NuxtLink></li>
          <li v-for="a in SERVICE_AREAS" :key="a.slug">
            <NuxtLink :to="areaPath(a.slug)">{{ a.city }}, {{ a.state }}</NuxtLink>
          </li>
        </ul>
      </div>

      <div>
        <h3 class="site-footer__heading">Contact</h3>
        <ul class="site-footer__list">
          <li><a :href="`tel:${phoneTel}`">{{ phone }}</a></li>
          <li><a :href="`mailto:${email}`">{{ email }}</a></li>
          <li class="muted">Metro Atlanta, GA</li>
        </ul>
        <NuxtLink class="btn btn--primary" to="/contact" style="margin-top: 0.75rem">Request estimate</NuxtLink>
      </div>
    </div>
    <div class="container site-footer__bottom">
      <span>© {{ year }} Red Clay Cabinet Installers. Demo site for JobPulse.</span>
      <span class="site-footer__jp">Recent work powered by JobPulse</span>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: var(--ink);
  color: #f5ebe3;
  padding: 3rem 0 1.5rem;
  margin-top: 2rem;
}

.site-footer a {
  color: #f5ebe3;
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
    grid-template-columns: 1.3fr 1fr 1fr 1fr;
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
  border-radius: 10px;
  background: var(--clay);
  color: #fff;
  font-weight: 800;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.site-footer__tag {
  color: #cbb8aa;
  margin: 0.25rem 0 0;
  font-size: 0.92rem;
}

.site-footer__heading {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #cbb8aa;
  margin-bottom: 0.75rem;
}

.site-footer__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.4rem;
}

.site-footer__list a {
  text-decoration: none;
  font-weight: 600;
}

.site-footer__list a:hover {
  color: #fff;
  text-decoration: underline;
}

.site-footer__bottom {
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #a89080;
}

.site-footer__jp {
  color: #d4b8a4;
  font-weight: 600;
}
</style>
