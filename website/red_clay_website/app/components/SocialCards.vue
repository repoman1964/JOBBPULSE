<script setup lang="ts">
export type SocialCard = {
  destination: string
  title: string
  body: string
  imageUrl?: string | null
}

const props = defineProps<{ posts: SocialCard[] }>()

const labels: Record<string, string> = {
  facebook: 'Facebook',
  instagram: 'Instagram',
  google_business: 'Google Business',
}

const ordered = computed(() => {
  const rank = ['facebook', 'instagram', 'google_business']
  return [...props.posts].sort(
    (a, b) => rank.indexOf(a.destination) - rank.indexOf(b.destination),
  )
})
</script>

<template>
  <div v-if="ordered.length" class="social-grid">
    <article v-for="post in ordered" :key="post.destination" class="social-card">
      <p class="section__eyebrow">{{ labels[post.destination] || post.destination }}</p>
      <img
        v-if="post.imageUrl"
        :src="post.imageUrl"
        :alt="post.title || labels[post.destination] || 'Social post'"
        width="600"
        height="600"
      />
      <h3>{{ post.title }}</h3>
      <p>{{ post.body }}</p>
    </article>
  </div>
</template>
