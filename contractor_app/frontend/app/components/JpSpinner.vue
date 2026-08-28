<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: 'sm' | 'md'
  }>(),
  { size: 'md' },
)
</script>

<template>
  <span class="jp-spinner" :class="`jp-spinner--${size}`" aria-hidden="true" />
</template>

<style scoped>
.jp-spinner {
  display: inline-block;
  flex-shrink: 0;
  border-radius: 50%;
  border: 2px solid var(--jp-card-border);
  border-top-color: var(--jp-accent);
  animation: jp-spin 0.7s linear infinite;
}

.jp-spinner--sm {
  width: 14px;
  height: 14px;
}

.jp-spinner--md {
  width: 22px;
  height: 22px;
}

@keyframes jp-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
