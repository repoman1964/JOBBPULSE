<script setup lang="ts">
const props = defineProps<{
  modelValue?: string
  placeholder?: string
}>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
  submit: []
}>()

const value = computed({
  get: () => props.modelValue || '',
  set: (v: string) => emit('update:modelValue', v),
})
</script>

<template>
  <form class="search-bar" @submit.prevent="emit('submit')">
    <input
      v-model="value"
      type="search"
      :placeholder="placeholder || 'Search projects…'"
      aria-label="Search"
    />
    <button class="btn btn-primary" type="submit">Search</button>
  </form>
</template>
