<script setup lang="ts">
import {
  SERVICES,
  SERVICE_AREAS,
  REVIEWS,
  FAQS,
  PROCESS_STEPS,
  servicePath,
  areaPath,
} from '~/utils/siteContent'

const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const demo = useDemoProjects()

useSeoMeta({
  title: 'Red Clay | Painting in Metro Atlanta',
  description:
    'Exterior painting first, interiors as a second line. Written estimates. Licensed and insured across metro Atlanta.',
})

await demo.fetchLiveList()
const jobs = computed(() => demo.carouselJobs())
</script>

<template>
  <div>
    <section class="hero">
      <img class="hero__img" src="/images/hero.jpg" alt="Freshly painted two-story house in metro Atlanta" />
      <div class="hero__veil" />
      <div class="container hero__copy">
        <p class="section__eyebrow">Exterior painting · Metro Atlanta</p>
        <h1>Paint that holds up to Georgia weather.</h1>
        <p class="hero__lead">
          Prep first. Then two coats. Written estimate before we open a can. We lead with exteriors — interiors when
          they fit the week.
        </p>
        <div class="hero__actions">
          <a class="hero__phone" :href="`tel:${phoneTel}`">{{ phone }}</a>
          <NuxtLink class="btn btn--ghost btn--lg" to="/book">Book an estimate</NuxtLink>
        </div>
        <div class="hero__form">
          <EstimateForm compact source-page-type="home" />
        </div>
      </div>
    </section>

    <TrustBar />

    <section class="section">
      <div class="container">
        <p class="section__eyebrow">Recent work</p>
        <h2>Jobs from the last few streets.</h2>
        <p class="section__lead">Click a project for before, after, and what we posted about it.</p>
        <ProjectCarousel :jobs="jobs" />
        <p class="section__more">
          <NuxtLink to="/work">See all work →</NuxtLink>
        </p>
      </div>
    </section>

    <section class="section" style="background: var(--card)">
      <div class="container">
        <p class="section__eyebrow">What we do</p>
        <h2>Four services. One standard of prep.</h2>
        <p class="section__lead">Exterior-led. Interior as a second line. No random add-on trades.</p>
        <div class="card-grid card-grid--2">
          <NuxtLink v-for="s in SERVICES" :key="s.slug" class="service-card" :to="servicePath(s.slug)">
            <img :src="s.image" :alt="s.name" width="800" height="450" />
            <div class="service-card__body">
              <p class="section__eyebrow">{{ s.name }}</p>
              <h3>{{ s.name }}</h3>
              <p>{{ s.short }}</p>
              <span class="service-card__more">Explore →</span>
            </div>
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__eyebrow">How it works</p>
        <h2>Walkthrough. Written quote. Then paint.</h2>
        <ol class="how__steps">
          <li v-for="step in PROCESS_STEPS" :key="step.num">
            <span class="how__num">{{ step.num }}</span>
            <h3>{{ step.title }}</h3>
            <p>{{ step.body }}</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="section" style="background: var(--card)">
      <div class="container">
        <p class="section__eyebrow">What people say</p>
        <h2>On-site reviews, not only Google.</h2>
        <div class="card-grid card-grid--3">
          <article v-for="r in REVIEWS.slice(0, 3)" :key="r.author" class="review">
            <p class="review__text">“{{ r.text }}”</p>
            <p>
              <strong>{{ r.author }}</strong>
              <span class="muted"> · {{ r.location }} · {{ r.job }}</span>
            </p>
          </article>
        </div>
        <p class="section__more"><NuxtLink to="/reviews">See all reviews →</NuxtLink></p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__eyebrow">Areas we cover</p>
        <h2>Metro Atlanta, neighborhood by neighborhood.</h2>
        <div class="chips">
          <NuxtLink v-for="a in SERVICE_AREAS" :key="a.slug" class="area-chip" :to="areaPath(a.slug)">
            {{ a.city }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="section" style="background: var(--card)">
      <div class="container">
        <p class="section__eyebrow">Common questions</p>
        <h2>What homeowners ask before we start.</h2>
        <div class="faq-list">
          <details v-for="(item, i) in FAQS" :key="item.q" class="faq" :open="i === 0">
            <summary>{{ item.q }}</summary>
            <p>{{ item.a }}</p>
          </details>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  min-height: min(90vh, 740px);
  display: flex;
  align-items: flex-end;
  color: #fff;
}

.hero__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero__veil {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(28, 26, 24, 0.72), rgba(28, 26, 24, 0.15));
}

.hero__copy {
  position: relative;
  padding: 4rem 0 3rem;
  max-width: 40rem;
  margin-right: auto;
}

.hero h1 {
  color: #fff;
}

.hero__lead {
  color: rgba(247, 244, 238, 0.88);
  font-size: 1.15rem;
  max-width: 32rem;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.25rem;
  margin: 1.5rem 0 1.75rem;
}

.hero__phone {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 600;
  color: var(--clay) !important;
  text-decoration: none !important;
}

.hero__form {
  max-width: 28rem;
}

.hero__form :deep(.estimate-form) {
  background: rgba(247, 244, 238, 0.94);
}

.section__more {
  margin-top: 2rem;
  font-weight: 600;
}
</style>
