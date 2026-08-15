<script setup lang="ts">
import { isFileVideo, vslEmbedSrc } from '~/utils/vsl'

const props = withDefaults(
  defineProps<{
    src?: string
    poster?: string
    title?: string
  }>(),
  {
    src: '',
    poster: '/images/jobs-page-clay.png',
    title: 'JobbPulse walkthrough',
  },
)

const fileSrc = computed(() => (isFileVideo(props.src) ? props.src.trim() : ''))
const embedSrc = computed(() => (fileSrc.value ? '' : vslEmbedSrc(props.src)))
</script>

<template>
  <div class="vsl-frame">
    <video
      v-if="fileSrc"
      :src="fileSrc"
      :poster="poster"
      :title="title"
      controls
      playsinline
      preload="none"
      controlslist="nodownload"
    >
      <a :href="fileSrc">Watch the video</a>
    </video>
    <iframe
      v-else-if="embedSrc"
      :src="embedSrc"
      :title="title"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      allowfullscreen
      loading="lazy"
    />
    <div v-else class="vsl-placeholder">
      <img :src="poster" alt="" width="1280" height="720">
      <div class="vsl-play" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7L8 5z" />
        </svg>
      </div>
      <p class="sr-only">{{ title }} — video coming soon</p>
    </div>
  </div>
</template>
