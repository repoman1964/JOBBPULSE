<script setup lang="ts">
import { TEAM, TRUST_ITEMS, COMPANY } from '~/utils/siteContent'

useSeoMeta({
  title: 'About ABC Painters | Acworth, GA',
  description:
    'Four-person residential painting crew based in Acworth since 2023. Licensed, insured, prep-first interiors, exteriors, and cabinets.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'About' }]" />
        <p class="section__eyebrow">About</p>
        <h1 class="page-hero__title">A four-person crew. Acworth since {{ COMPANY.foundedYear }}.</h1>
        <p class="section__lead">
          ABC Painters is a residential painting company — interiors, exteriors, and cabinets — for homeowners in
          Acworth, Kennesaw, and Cartersville.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container about-grid">
        <div>
          <h2>How we work</h2>
          <p>
            Owner <strong>Marcus Hale</strong> started ABC Painters in {{ COMPANY.foundedYear }} after too many
            homeowners got a one-coat roll over peeling paint and a vanishing subcontractor. The rule here is simple:
            scrape, sand, caulk, and prime before the pretty coat. If the wood is rotten, we say so before we paint
            over it.
          </p>
          <p>
            We employ four people. The estimator on the walkthrough is not a salesperson who disappears. Written
            quotes. Two-year workmanship warranty. Shop at {{ COMPANY.address }}, {{ COMPANY.city }},
            {{ COMPANY.state }} {{ COMPANY.postcode }}.
          </p>
          <ul class="chips">
            <li v-for="t in TRUST_ITEMS" :key="t.label">{{ t.label }}</li>
          </ul>
        </div>
        <img
          class="about-photo"
          src="/images/team.jpg"
          alt="ABC Painters crew"
          width="1200"
          height="675"
        />
      </div>
    </section>

    <section class="section section--tight">
      <div class="container">
        <h2>The crew</h2>
        <div class="card-grid card-grid--2">
          <article v-for="m in TEAM" :key="m.name" class="member">
            <h3>{{ m.name }}</h3>
            <p class="member__role">{{ m.role }}</p>
            <p>{{ m.years }}</p>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-grid {
  display: grid;
  gap: 2rem;
  align-items: start;
}

@media (min-width: 900px) {
  .about-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.about-photo {
  width: 100%;
  border-radius: var(--radius-lg);
  object-fit: cover;
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
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--navy);
}

.member {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.member h3 {
  color: var(--navy);
  margin-bottom: 0.2rem;
}

.member__role {
  color: var(--orange);
  font-weight: 700;
  margin-bottom: 0.4rem;
}
</style>
