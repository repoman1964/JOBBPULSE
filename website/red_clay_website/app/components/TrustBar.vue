<script setup lang="ts">
import { TRUST_ITEMS } from '~/utils/siteContent'
</script>

<template>
  <section class="trust-bar">
    <div class="container trust-bar__grid">
      <div v-for="item in TRUST_ITEMS" :key="item.label" class="trust-bar__item">
        <strong>{{ item.label }}</strong>
        <span>{{ item.sub }}</span>
      </div>
    </div>
  </section>
</template>
