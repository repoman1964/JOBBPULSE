<script setup lang="ts">
import { TRUST_CHIPS } from '~/utils/siteContent'

useSeoMeta({
  title: 'About Red Clay Cabinet Installers',
  description:
    'Metro Atlanta cabinet installers focused on clean kitchens, vanities, and built-ins. Licensed & insured.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">About</p>
        <h1 class="page-hero__title">Built for clean installs and clear communication</h1>
        <p class="section__lead">
          Red Clay Cabinet Installers is a metro Atlanta crew that measures carefully, protects your floors, and
          leaves the jobsite ready for real life—not a showroom fantasy.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container about-grid">
        <div>
          <h2>Our story</h2>
          <p>
            We’re named for Georgia red clay—the ground under the homes we work in. Owner
            <strong> Jordan Hale</strong> built Red Clay around a simple idea: cabinet install is a craft, not a
            side hustle. Homeowners deserve level lines, soft-close that works, and a crew that texts when they’re
            running five minutes late.
          </p>
          <p>
            Over a decade in, we’ve hung kitchens in Buckhead, vanities in Inman Park, and pantries in Decatur. We
            document finished work in our JobPulse contractor app so this website stays honest—proof from jobs we
            actually completed.
          </p>
          <ul class="chips">
            <li v-for="c in TRUST_CHIPS" :key="c">{{ c }}</li>
          </ul>
        </div>
        <aside class="about-card">
          <h3>At a glance</h3>
          <dl>
            <div>
              <dt>Owner</dt>
              <dd>Jordan Hale</dd>
            </div>
            <div>
              <dt>Based</dt>
              <dd>Atlanta, GA</dd>
            </div>
            <div>
              <dt>Focus</dt>
              <dd>Kitchens · Vanities · Built-ins</dd>
            </div>
            <div>
              <dt>Typical schedule</dt>
              <dd>2–3 week lead time</dd>
            </div>
          </dl>
          <NuxtLink class="btn btn--primary" to="/contact">Work with us</NuxtLink>
        </aside>
      </div>
    </section>

    <section class="section section--tight values">
      <div class="container">
        <h2 class="section__title">How we work</h2>
        <div class="card-grid card-grid--3">
          <article class="value">
            <h3>Protect the home</h3>
            <p>Floor protection, dust awareness, and a cleanup that respects occupied houses.</p>
          </article>
          <article class="value">
            <h3>Install true</h3>
            <p>Shims, levels, and hardware that last—not “good enough from the driveway.”</p>
          </article>
          <article class="value">
            <h3>Show the work</h3>
            <p>Finished jobs can publish from our field app to this site so neighbors see real proof.</p>
          </article>
        </div>
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

.about-grid {
  display: grid;
  gap: 2rem;
}

@media (min-width: 800px) {
  .about-grid {
    grid-template-columns: 1.4fr 1fr;
    align-items: start;
  }
}

.chips {
  list-style: none;
  padding: 0;
  margin: 1.25rem 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.chips li {
  background: var(--clay-soft);
  color: var(--clay-deep);
  font-weight: 700;
  font-size: 0.8rem;
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-pill);
}

.about-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.35rem;
  box-shadow: var(--shadow);
}

.about-card h3 {
  margin-top: 0;
}

.about-card dl {
  margin: 0 0 1.25rem;
}

.about-card dl > div {
  display: grid;
  grid-template-columns: 7.5rem 1fr;
  gap: 0.5rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.92rem;
}

.about-card dt {
  color: var(--muted);
  font-weight: 600;
}

.about-card dd {
  margin: 0;
  font-weight: 700;
}

.values {
  background: var(--clay-mist);
}

.value {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.15rem;
}

.value h3 {
  margin-top: 0;
}

.value p {
  margin: 0;
}
</style>
