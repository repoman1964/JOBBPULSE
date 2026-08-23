<script setup lang="ts">
const route = useRoute()
await navigateTo(`/work/${route.params.slug}`, { redirectCode: 301 })
</script>
