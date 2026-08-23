<script setup lang="ts">
defineProps<{
  beforeUrl?: string | null
  afterUrl?: string | null
  beforeAlt?: string
  afterAlt?: string
}>()
</script>

<template>
  <div class="before-after">
    <figure v-if="beforeUrl">
      <img :src="beforeUrl" :alt="beforeAlt || 'Before'" width="900" height="675" />
      <figcaption>Before</figcaption>
    </figure>
    <figure v-if="afterUrl">
      <img :src="afterUrl" :alt="afterAlt || 'After'" width="900" height="675" />
      <figcaption>After</figcaption>
    </figure>
  </div>
</template>
