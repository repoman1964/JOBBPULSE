<script setup lang="ts">
import {
  SERVICES,
  SERVICE_AREAS,
  TRUST_ITEMS,
  REVIEWS,
  HOME_FAQS,
  PROJECTS,
  TEAM,
  servicePath,
  areaPath,
} from '~/utils/siteContent'

const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string

useSeoMeta({
  title: 'ABC Painters | Interior & Exterior Painting in Acworth, GA',
  description:
    'Residential painters in Acworth, Kennesaw, and Cartersville. Prep-first interiors, exteriors, and cabinets. Written quotes. Two-year workmanship warranty.',
})
</script>

<template>
  <div>
    <section class="hero">
      <div class="container hero__inner">
        <div class="hero__copy">
          <p class="section__eyebrow">Residential painting · Acworth, GA</p>
          <h1>House painting done properly. Quoted before we start.</h1>
          <p class="hero__lead">
            Interior, exterior, and cabinets for homeowners in Acworth, Kennesaw, and Cartersville. A four-person
            crew, no random subs, prep before paint.
          </p>
          <div class="hero__actions">
            <a class="btn btn--primary btn--lg" :href="`tel:${phoneTel}`">Call {{ phone }}</a>
            <NuxtLink class="btn btn--secondary btn--lg" to="/contact">Free estimate</NuxtLink>
          </div>
          <p class="hero__trust">LICENSED · INSURED · PREP-FIRST · 2-YEAR WARRANTY</p>
        </div>
        <div class="hero__media">
          <img
            class="hero-photo"
            src="/images/hero.jpg"
            alt="ABC Painters crew painting a two-story house in north Georgia"
            width="1200"
            height="675"
          />
        </div>
      </div>
    </section>

    <section class="trust-bar">
      <div class="container trust-bar__grid">
        <div v-for="item in TRUST_ITEMS" :key="item.label" class="trust-bar__item">
          <strong>{{ item.label }}</strong>
          <span>{{ item.sub }}</span>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__eyebrow">What we do</p>
        <h2>Three services. One crew.</h2>
        <p class="section__lead">
          We paint houses people live in. Walls, siding, and cabinets — not a dozen unrelated trades.
        </p>
        <div class="card-grid card-grid--3">
          <NuxtLink v-for="s in SERVICES" :key="s.slug" class="service-card" :to="servicePath(s.slug)">
            <img :src="s.image" :alt="s.name" width="800" height="600" />
            <div class="service-card__body">
              <h3>{{ s.name }}</h3>
              <p>{{ s.short }}</p>
              <span class="service-card__more">Learn more →</span>
            </div>
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="section how">
      <div class="container">
        <p class="section__eyebrow">How it works</p>
        <h2>Walkthrough. Written quote. Then paint.</h2>
        <p class="section__lead">No open-ended hourly rate. You know the number before we open a can.</p>
        <ol class="how__steps">
          <li>
            <span class="how__num">01</span>
            <h3>You call</h3>
            <p>A real person picks up. We ask rooms, surfaces, and timing — then set a walkthrough.</p>
          </li>
          <li>
            <span class="how__num">02</span>
            <h3>We quote on site</h3>
            <p>We look at prep, not just square footage. You get a written price before anything starts.</p>
          </li>
          <li>
            <span class="how__num">03</span>
            <h3>We paint and walk it</h3>
            <p>The same four people who quoted the job do the work, clean up, and walk it with you.</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__eyebrow">Portfolio</p>
        <h2>Recent jobs</h2>
        <p class="section__lead">Acworth, Kennesaw, and Cartersville — one project in each city we actually cover.</p>
        <div class="card-grid card-grid--3">
          <article v-for="p in PROJECTS" :key="p.slug" class="project-card">
            <img :src="p.image" :alt="p.title" width="800" height="600" />
            <div class="project-card__body">
              <h3>{{ p.title }}</h3>
              <p>{{ p.summary }}</p>
            </div>
          </article>
        </div>
        <p class="center-link">
          <NuxtLink to="/portfolio">See all portfolio work →</NuxtLink>
        </p>
      </div>
    </section>

    <section class="section reviews">
      <div class="container">
        <p class="section__eyebrow">What people say</p>
        <h2>Neighbors, not marketing copy.</h2>
        <div class="card-grid card-grid--3">
          <article v-for="r in REVIEWS" :key="r.author" class="review-card">
            <div class="review-card__stars" aria-label="5 stars">★★★★★</div>
            <p class="review-card__text">“{{ r.text }}”</p>
            <p class="review-card__by">
              <strong>{{ r.author }}</strong>
              <span class="muted"> · {{ r.location }} · {{ r.job }}</span>
            </p>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__eyebrow">Areas we cover</p>
        <h2>Three cities. That’s the list.</h2>
        <p class="section__lead">
          We do not advertise a 40-mile radius we cannot actually service. If you are in one of these three, we
          cover you.
        </p>
        <div class="area-chips">
          <NuxtLink v-for="a in SERVICE_AREAS" :key="a.slug" class="area-chip" :to="areaPath(a.slug)">
            {{ a.city }}, {{ a.state }}
          </NuxtLink>
        </div>
        <p class="center-link">
          <NuxtLink to="/service-areas">Service areas overview →</NuxtLink>
        </p>
      </div>
    </section>

    <section class="section team-preview">
      <div class="container team-preview__grid">
        <div>
          <p class="section__eyebrow">Real people</p>
          <h2>The crew at your door.</h2>
          <p>
            Four people, directly employed, based in Acworth since 2023. No rotating subcontractors. Every job is
            signed off by the owner.
          </p>
          <ul class="team-list">
            <li v-for="m in TEAM" :key="m.name">
              <strong>{{ m.name }}</strong>
              <span>{{ m.role }}</span>
            </li>
          </ul>
          <NuxtLink class="btn btn--secondary" to="/about">Meet the crew</NuxtLink>
        </div>
        <img
          class="team-preview__photo"
          src="/images/team.jpg"
          alt="ABC Painters four-person crew beside the work van"
          width="1200"
          height="675"
        />
      </div>
    </section>

    <section class="section faq-home">
      <div class="container faq-home__inner">
        <p class="section__eyebrow">FAQ</p>
        <h2>Straight answers</h2>
        <div class="faq-list">
          <details v-for="(item, i) in HOME_FAQS" :key="item.q" :open="i === 0">
            <summary>{{ item.q }}</summary>
            <p>{{ item.a }}</p>
          </details>
        </div>
        <p class="center-link">
          <NuxtLink to="/faq">Full FAQ →</NuxtLink>
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  background: var(--bg);
  padding: 2.5rem 0 0;
}

.hero__inner {
  display: grid;
  gap: 1.75rem;
  align-items: center;
}

@media (min-width: 960px) {
  .hero__inner {
    grid-template-columns: 1fr 1fr;
    min-height: 34rem;
  }
}

.hero__lead {
  font-size: 1.25rem;
  max-width: 32rem;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.5rem 0 1rem;
}

.hero__trust {
  font-size: 0.8125rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.hero__media {
  border-radius: var(--radius-lg) 0 0 var(--radius-lg);
  overflow: hidden;
  min-height: 16rem;
}

@media (min-width: 960px) {
  .hero__media {
    margin-right: calc(-1 * (100vw - min(100vw, var(--max))) / 2);
    min-height: 36rem;
  }
}

.hero__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  min-height: 16rem;
}

.trust-bar {
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 2rem 0;
}

.trust-bar__grid {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: 1fr 1fr;
}

@media (min-width: 800px) {
  .trust-bar__grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.trust-bar__item {
  display: grid;
  gap: 0.15rem;
}

.trust-bar__item strong {
  color: var(--navy);
}

.trust-bar__item span {
  color: var(--muted);
  font-size: 0.875rem;
}

.service-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  text-decoration: none !important;
  color: inherit;
  display: flex;
  flex-direction: column;
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
}

.service-card:hover {
  border-color: var(--orange);
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.service-card img {
  width: 100%;
  height: 11rem;
  object-fit: cover;
}

.service-card__body {
  padding: 1.5rem;
}

.service-card h3 {
  color: var(--navy);
  font-size: 1.35rem;
}

.service-card__more {
  font-weight: 700;
  color: var(--orange);
  font-size: 0.9rem;
}

.how {
  background: var(--surface);
}

.how__steps {
  list-style: none;
  padding: 0;
  margin: 2.5rem 0 0;
  display: grid;
  gap: 1.5rem;
}

@media (min-width: 800px) {
  .how__steps {
    grid-template-columns: repeat(3, 1fr);
  }
}

.how__num {
  display: block;
  font-size: 4.5rem;
  font-weight: 800;
  color: var(--orange);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.how__steps h3 {
  color: var(--navy);
  margin-top: 0.75rem;
}

.project-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.project-card img {
  width: 100%;
  height: 12rem;
  object-fit: cover;
}

.project-card__body {
  padding: 1.15rem 1.25rem 1.35rem;
}

.project-card h3 {
  font-size: 1.15rem;
  color: var(--navy);
}

.reviews {
  background: var(--bg);
}

.review-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
}

.review-card__stars {
  color: var(--orange);
  letter-spacing: 0.1em;
}

.review-card__text {
  color: var(--ink);
  font-weight: 500;
  margin: 1rem 0;
}

.area-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.area-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.65rem 1.1rem;
  font-weight: 600;
  color: var(--navy);
  text-decoration: none !important;
}

.area-chip:hover {
  border-color: var(--orange);
  color: var(--orange);
}

.team-preview {
  background: var(--surface);
}

.team-preview__grid {
  display: grid;
  gap: 2rem;
  align-items: center;
}

@media (min-width: 900px) {
  .team-preview__grid {
    grid-template-columns: 1fr 1.2fr;
  }
}

.team-preview__photo {
  width: 100%;
  border-radius: var(--radius-lg);
  object-fit: cover;
  min-height: 16rem;
}

.team-list {
  list-style: none;
  padding: 0;
  margin: 1.25rem 0 1.5rem;
  display: grid;
  gap: 0.65rem;
}

.team-list li {
  display: grid;
}

.team-list span {
  color: var(--muted);
  font-size: 0.92rem;
}

.faq-home__inner {
  max-width: 46rem;
}

.faq-list {
  display: grid;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.faq-list details {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.9rem 1rem;
}

.faq-list summary {
  font-weight: 700;
  cursor: pointer;
}

.faq-list p {
  margin: 0.65rem 0 0.2rem;
}

.center-link {
  margin: 1.75rem 0 0;
  font-weight: 700;
}

.center-link a {
  color: var(--navy);
  text-decoration: underline;
  text-underline-offset: 6px;
}
</style>
