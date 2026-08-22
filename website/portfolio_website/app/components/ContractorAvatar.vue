<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    name?: string | null
    size?: 'sm' | 'md'
  }>(),
  { size: 'sm' },
)

const initials = computed(() => {
  const raw = (props.name || '?').trim()
  if (!raw) return '?'
  const parts = raw.split(/\s+/).filter(Boolean)
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})

/** Stable soft hue from name so avatars feel distinct without photos. */
const bg = computed(() => {
  const s = props.name || 'X'
  let hash = 0
  for (let i = 0; i < s.length; i++) hash = (hash * 31 + s.charCodeAt(i)) >>> 0
  const hue = hash % 360
  return `hsl(${hue} 38% 42%)`
})
</script>

<template>
  <span
    class="contractor-avatar"
    :class="`contractor-avatar--${size}`"
    :style="{ background: bg }"
    aria-hidden="true"
  >
    {{ initials }}
  </span>
</template>
