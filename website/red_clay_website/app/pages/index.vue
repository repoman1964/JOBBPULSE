<script setup lang="ts">
import { SERVICES, SERVICE_AREAS, TRUST_CHIPS, REVIEWS, servicePath, areaPath } from '~/utils/siteContent'

const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string

useSeoMeta({
  title: 'Red Clay Cabinet Installers | Metro Atlanta Cabinets',
  description:
    'Kitchen cabinets, bath vanities, and built-ins installed clean across metro Atlanta. Free estimates. Licensed & insured.',
})
</script>

<template>
  <div>
    <!-- ABOVE THE FOLD: hero + live recent jobs widget -->
    <section class="hero">
      <div class="hero__bg" aria-hidden="true" />
      <div class="container hero__inner">
        <div class="hero__copy">
          <p class="hero__eyebrow">Metro Atlanta · Cabinet installation</p>
          <h1 class="hero__title">
            Cabinets installed clean.<br />
            Proof that updates itself.
          </h1>
          <p class="hero__lead">
            Red Clay hangs kitchens, vanities, and built-ins the right way—then every finished job can land
            on this site from our contractor app. Real work. Real neighborhoods. No catalog fiction.
          </p>
          <div class="hero__actions">
            <NuxtLink class="btn btn--primary btn--lg" to="/contact">Get a free estimate</NuxtLink>
            <a class="btn btn--ghost btn--lg" :href="`tel:${phoneTel}`">Call {{ phone }}</a>
          </div>
          <ul class="hero__trust">
            <li v-for="chip in TRUST_CHIPS" :key="chip">{{ chip }}</li>
          </ul>
        </div>

        <div class="hero__widget">
          <RecentJobsWidget :limit="3" />
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container">
        <p class="section__eyebrow">What we install</p>
        <h2 class="section__title">Services built for real homes</h2>
        <p class="section__lead">
          Measure carefully, protect floors, leave the jobsite clean. Pick a service or tell us your project on the estimate form.
        </p>
        <div class="card-grid card-grid--2 card-grid--4">
          <NuxtLink
            v-for="s in SERVICES"
            :key="s.slug"
            class="service-tile"
            :to="servicePath(s.slug)"
          >
            <h3>{{ s.name }}</h3>
            <p>{{ s.short }}</p>
            <span class="service-tile__more">Learn more →</span>
          </NuxtLink>
        </div>
        <p class="home-silo-areas muted">
          Serving
          <template v-for="(a, i) in SERVICE_AREAS" :key="a.slug">
            <NuxtLink :to="areaPath(a.slug)">{{ a.city }}</NuxtLink><span v-if="i < SERVICE_AREAS.length - 1">, </span>
          </template>
          ·
          <NuxtLink to="/service-area">All service areas</NuxtLink>
        </p>
      </div>
    </section>

    <section class="section how">
      <div class="container how__grid">
        <div>
          <p class="section__eyebrow">How it works</p>
          <h2 class="section__title">From estimate to finished room</h2>
          <ol class="how__steps">
            <li>
              <strong>Talk scope</strong>
              <span>Share photos, plans, or a quick walkthrough. We confirm timeline and install approach.</span>
            </li>
            <li>
              <strong>We install</strong>
              <span>Leveled, plumbed, and finished with soft-close where it counts—floors protected.</span>
            </li>
            <li>
              <strong>Proof goes live</strong>
              <span>Crew documents the job in JobPulse. Approved work can appear here automatically.</span>
            </li>
          </ol>
        </div>
        <div class="how__panel">
          <h3>Why homeowners call Red Clay</h3>
          <ul>
            <li>Clear communication and tidy jobsite habits</li>
            <li>Kitchen, bath, and built-in specialists—not a general handyman crew</li>
            <li>Portfolio of metro Atlanta installs you can browse by neighborhood</li>
            <li>Licensed, insured, free estimates</li>
          </ul>
          <NuxtLink class="btn btn--secondary" to="/about">About our crew</NuxtLink>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container">
        <div class="reviews-head">
          <div>
            <p class="section__eyebrow">Reviews</p>
            <h2 class="section__title">Neighbors talk about the work</h2>
          </div>
          <NuxtLink class="btn btn--secondary" to="/reviews">All reviews</NuxtLink>
        </div>
        <div class="card-grid card-grid--3">
          <article v-for="r in REVIEWS.slice(0, 3)" :key="r.author" class="review-card">
            <div class="review-card__stars" aria-label="5 stars">★★★★★</div>
            <p class="review-card__text">“{{ r.text }}”</p>
            <p class="review-card__by">
              <strong>{{ r.author }}</strong>
              <span class="muted"> · {{ r.location }}</span>
            </p>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-band">
      <div class="container cta-band__inner">
        <div>
          <h2 class="cta-band__title">Ready for cabinets that fit right?</h2>
          <p class="cta-band__lead">Tell us about the room. We’ll follow up with next steps—usually within a business day.</p>
        </div>
        <div class="cta-band__actions">
          <NuxtLink class="btn btn--primary btn--lg" to="/contact">Free estimate</NuxtLink>
          <a class="btn btn--ghost btn--lg" :href="`tel:${phoneTel}`">{{ phone }}</a>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  padding: 1.5rem 0 2rem;
  overflow: hidden;
  min-height: calc(100vh - var(--header-h));
  display: flex;
  align-items: stretch;
}

.hero__bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 10% 20%, rgba(181, 74, 42, 0.35), transparent 55%),
    radial-gradient(ellipse 60% 50% at 90% 80%, rgba(92, 64, 51, 0.35), transparent 50%),
    linear-gradient(155deg, #3a241c 0%, #6b2c18 42%, #b54a2a 100%);
  z-index: 0;
}

.hero__inner {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 1.5rem;
  align-items: start;
  width: 100%;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

@media (min-width: 960px) {
  .hero__inner {
    grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.15fr);
    gap: 1.75rem;
    align-items: center;
  }
}

.hero__copy {
  color: #fff;
  padding: 0.5rem 0;
}

.hero__eyebrow {
  margin: 0 0 0.65rem;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f3c9b4;
}

.hero__title {
  font-size: clamp(1.85rem, 4.2vw, 2.75rem);
  color: #fff;
  margin: 0 0 0.85rem;
  letter-spacing: -0.02em;
}

.hero__lead {
  color: rgba(255, 245, 238, 0.9);
  font-size: 1.05rem;
  max-width: 32rem;
  margin-bottom: 1.25rem;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-bottom: 1.25rem;
}

.hero__trust {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.hero__trust li {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #fff;
}

.hero__widget {
  min-width: 0;
}

.service-tile {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.15rem;
  text-decoration: none !important;
  color: inherit;
  box-shadow: var(--shadow);
  transition: border-color 0.15s, transform 0.15s;
}

.service-tile:hover {
  border-color: var(--clay);
  transform: translateY(-2px);
}

.service-tile h3 {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
}

.service-tile p {
  margin: 0 0 0.75rem;
  font-size: 0.92rem;
}

.service-tile__more {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--clay-dark);
}

.home-silo-areas {
  margin: 1.25rem 0 0;
  font-size: 0.92rem;
  line-height: 1.6;
}

.home-silo-areas a {
  font-weight: 700;
}

.how {
  background: var(--clay-mist);
}

.how__grid {
  display: grid;
  gap: 2rem;
}

@media (min-width: 800px) {
  .how__grid {
    grid-template-columns: 1.2fr 1fr;
    align-items: start;
  }
}

.how__steps {
  list-style: none;
  padding: 0;
  margin: 1.25rem 0 0;
  display: grid;
  gap: 1rem;
  counter-reset: step;
}

.how__steps li {
  display: grid;
  gap: 0.2rem;
  padding-left: 2.75rem;
  position: relative;
}

.how__steps li::before {
  counter-increment: step;
  content: counter(step);
  position: absolute;
  left: 0;
  top: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--clay);
  color: #fff;
  font-weight: 800;
  font-size: 0.9rem;
  display: grid;
  place-items: center;
}

.how__steps strong {
  color: var(--ink);
  font-size: 1.05rem;
}

.how__steps span {
  color: var(--muted);
  font-size: 0.95rem;
}

.how__panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.35rem;
  box-shadow: var(--shadow);
}

.how__panel h3 {
  margin-top: 0;
}

.how__panel ul {
  margin: 0 0 1.25rem;
  padding-left: 1.15rem;
  color: var(--muted);
}

.how__panel li {
  margin-bottom: 0.4rem;
}

.reviews-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.review-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.15rem;
  box-shadow: var(--shadow);
}

.review-card__stars {
  color: #d97706;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.review-card__text {
  color: var(--ink);
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
}

.review-card__by {
  margin: 0;
  font-size: 0.88rem;
}

.cta-band {
  background: linear-gradient(135deg, #3a241c, #8b3a20 55%, #b54a2a);
  color: #fff;
}

.cta-band__inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
}

.cta-band__title {
  color: #fff;
  margin: 0 0 0.4rem;
  font-size: clamp(1.4rem, 3vw, 1.85rem);
}

.cta-band__lead {
  color: rgba(255, 245, 238, 0.9);
  margin: 0;
  max-width: 32rem;
}

.cta-band__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}
</style>
