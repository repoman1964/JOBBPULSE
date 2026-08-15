<script setup lang="ts">
defineProps<{
  label: string
  variant?: 'default' | 'muted' | 'warn'
}>()
</script>

<template>
  <span
    class="status-pill"
    :class="{
      'status-pill--muted': variant === 'muted',
      'status-pill--warn': variant === 'warn',
    }"
  >
    {{ label }}
  </span>
</template>
