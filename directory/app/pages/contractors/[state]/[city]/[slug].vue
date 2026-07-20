<template>
  <div class="shell">
    <header class="header">
      <NuxtLink to="/" class="wordmark">Job<span>Pulse</span></NuxtLink>
      <span class="muted" style="font-size: 13px;">Contractor</span>
    </header>

    <section v-if="pending" class="hero">
      <p class="muted">Loading profile…</p>
    </section>

    <section v-else-if="contractor" class="hero">
      <p v-if="contractor.trade" class="muted meta-line">{{ contractor.trade }}</p>
      <h1>{{ contractor.company_name }}</h1>
      <p v-if="contractor.headline" class="headline">{{ contractor.headline }}</p>
      <p v-if="contractor.public_description" class="muted desc">
        {{ contractor.public_description }}
      </p>

      <div class="meta-row">
        <span v-if="contractor.contact_phone" class="muted">{{ contractor.contact_phone }}</span>
        <a
          v-if="contractor.website_url"
          :href="contractor.website_url"
          target="_blank"
          rel="noopener"
        >
          Website
        </a>
      </div>

      <div v-if="contractor.services?.length" class="block">
        <h2>Services</h2>
        <ul class="chips">
          <li v-for="s in contractor.services" :key="s.service_key">
            {{ s.display_name }}
          </li>
        </ul>
      </div>

      <div v-if="contractor.service_areas?.length" class="block">
        <h2>Service areas</h2>
        <ul class="chips">
          <li v-for="(a, i) in contractor.service_areas" :key="i">
            {{ a.display_name }}
          </li>
        </ul>
      </div>

      <div class="block">
        <h2>Recent projects</h2>
        <div v-if="!contractor.recent_projects?.length" class="muted">
          No published projects yet.
        </div>
        <div v-else class="project-list">
          <NuxtLink
            v-for="p in contractor.recent_projects"
            :key="p.slug"
            :to="p.public_path"
            class="project-row"
          >
            <strong>{{ p.public_title }}</strong>
            <span class="muted" style="font-size: 13px;">
              {{ [p.city, p.state].filter(Boolean).join(', ') }}
              <template v-if="p.service_key"> · {{ formatService(p.service_key) }}</template>
            </span>
          </NuxtLink>
        </div>
      </div>

      <div v-if="contractor.lead_form_enabled" class="block lead">
        <h2>Contact</h2>
        <p class="muted" style="font-size: 13px; margin-top: 0;">
          Lead form is available (MVP stub on the API). Reach out via phone or website above for now.
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const slug = computed(() => String(route.params.slug))
const api = usePublicApi()

const { data: contractor, pending, error } = await useAsyncData(
  () => `contractor-${slug.value}`,
  async () => {
    try {
      return await api.getContractor(slug.value)
    } catch (e: any) {
      throw createError({
        statusCode: e?.statusCode || 404,
        statusMessage: e?.statusMessage || 'Contractor not found',
      })
    }
  },
)

if (error.value && !contractor.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Contractor not found',
  })
}

function formatService(key: string) {
  return key.replace(/_/g, ' ')
}

useSeoMeta({
  title: () =>
    contractor.value?.seo_title ||
    (contractor.value ? `${contractor.value.company_name} | JobPulse` : 'Contractor | JobPulse'),
  description: () =>
    contractor.value?.seo_description ||
    contractor.value?.public_description?.slice(0, 160) ||
    'Contractor profile on JobPulse local directory',
  ogTitle: () => contractor.value?.company_name || 'Contractor',
  ogDescription: () => contractor.value?.public_description?.slice(0, 160) || '',
})
</script>

<style scoped>
.meta-line {
  margin: 0;
  font-size: 13px;
  text-transform: capitalize;
}
.headline {
  margin: 0 0 8px;
  font-size: 1.05rem;
}
.desc {
  margin: 0 0 16px;
  line-height: 1.55;
}
.meta-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  font-size: 14px;
}
.block {
  margin-top: 20px;
}
.block h2 {
  font-size: 0.95rem;
  margin: 0 0 10px;
}
.chips {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chips li {
  background: #f1f5f9;
  border: 1px solid var(--jp-border);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 13px;
}
.project-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.project-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 14px;
  border: 1px solid var(--jp-border);
  border-radius: 12px;
  background: #f8fafc;
  color: inherit;
}
.project-row:hover {
  border-color: var(--jp-primary);
}
</style>
