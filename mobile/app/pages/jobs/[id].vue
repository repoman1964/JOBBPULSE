<template>
  <div style="display: flex; flex-direction: column; height: 100vh; height: 100dvh;">
    <!-- Nav Bar -->
    <div class="nav-bar">
      <button class="nav-back" @click="navigateTo('/')">←</button>
      <div class="nav-title">Review & publish</div>
      <button class="nav-action" @click="publishAll" :disabled="publishing">
        {{ publishing ? '...' : 'Publish all' }}
      </button>
    </div>

    <!-- Content -->
    <div class="content" v-if="job">
      <!-- Job summary -->
      <div style="font-size: 12px; color: var(--jp-text-secondary);">
        {{ job.title || job.job_type }} · {{ job.city ? `${job.address || ''}, ${job.city}` : 'No location' }} · {{ formatDate(job.created_at) }}
      </div>

      <!-- Post Cards -->
      <div v-for="content in job.content" :key="content.id" class="post-preview-card">
        <div class="post-header">
          <div class="post-avatar" :style="{ background: getPlatformColor(content.platform) }">
            {{ getPlatformInitial(content.platform) }}
          </div>
          <div style="flex: 1;">
            <div style="font-size: 13px; font-weight: 500; color: var(--jp-text-primary);">
              {{ content.platform === 'blog' ? 'Blog post' : 'Your Business' }}
            </div>
            <div class="post-platform">{{ getPlatformLabel(content.platform) }}</div>
          </div>
          <span :class="['post-platform-tag', getPlatformTagClass(content.platform)]">
            {{ getPlatformTag(content.platform) }}
          </span>
        </div>

        <!-- Photo (for Facebook) -->
        <div v-if="content.platform === 'facebook' && job.photos.length > 0" class="post-img">
          <img :src="getPhotoUrl(job.photos[0].file_path)" :alt="job.title || 'Job photo'" />
        </div>

        <!-- Body -->
        <div class="post-body" :style="{ fontSize: content.platform === 'facebook' ? '12px' : '11px' }">
          <template v-if="editingContent === content.id">
            <textarea
              v-model="editBody"
              style="width: 100%; min-height: 80px; border: 1px solid var(--jp-border); border-radius: 6px; padding: 8px; font-size: 12px; font-family: inherit; resize: vertical;"
            ></textarea>
          </template>
          <template v-else>
            <strong v-if="content.title">{{ content.title }}</strong>
            <br v-if="content.title">
            <br v-if="content.title">
            {{ content.body }}
          </template>
        </div>

        <!-- Hashtags (FB + Blog) -->
        <div
          v-if="content.hashtags && content.platform !== 'gbp'"
          style="padding: 6px 12px; font-size: 11px; color: var(--jp-primary); background: var(--jp-primary-light);"
        >
          📍 {{ job.city || 'Location' }}{{ job.state ? `, ${job.state}` : '' }} · {{ content.hashtags }}
        </div>

        <!-- Actions -->
        <div class="post-actions">
          <button class="post-btn" @click="toggleEdit(content)">
            {{ editingContent === content.id ? 'Save' : 'Edit' }}
          </button>
          <button class="post-btn" @click="regenerate(content)" :disabled="regenerating">
            Regenerate
          </button>
          <button
            :class="['post-btn', { publish: !content.published }]"
            @click="publishSingle(content)"
            :disabled="content.published || publishing"
          >
            {{ content.published ? 'Published ✓' : 'Publish' }}
          </button>
        </div>
      </div>

      <!-- No content state -->
      <div v-if="!job.content || job.content.length === 0" style="text-align: center; padding: 32px; color: var(--jp-text-secondary);">
        <p>No generated content yet.</p>
        <button class="btn-secondary" style="margin-top: 12px;" @click="navigateTo(`/processing?jobId=${job.id}`)">
          Generate content →
        </button>
      </div>

      <button class="btn-primary" @click="publishAll" :disabled="publishing || allPublished">
        {{ allPublished ? 'All published ✓' : (publishing ? 'Publishing...' : 'Publish all & return home →') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-else class="processing-state">
      <div class="spinner"></div>
      <div style="font-size: 13px; color: var(--jp-text-secondary);">Loading job...</div>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const api = useApi()

const job = ref(null)
const editingContent = ref(null)
const editBody = ref('')
const publishing = ref(false)
const regenerating = ref(false)

const allPublished = computed(() => {
  if (!job.value?.content) return false
  return job.value.content.every(c => c.published)
})

const loadJob = async () => {
  try {
    const id = route.params.id
    job.value = await api.getJob(id)
  } catch (err) {
    console.error('Failed to load job:', err)
  }
}

onMounted(loadJob)

const getPhotoUrl = (filePath) => {
  return api.getPhotoUrl(filePath)
}

const getPlatformColor = (p) => {
  switch (p) {
    case 'facebook': return 'var(--jp-primary)'
    case 'gbp': return 'var(--jp-success)'
    case 'blog': return 'var(--jp-warning)'
    default: return 'var(--jp-primary)'
  }
}

const getPlatformInitial = (p) => {
  switch (p) {
    case 'facebook': return 'JP'
    case 'gbp': return 'G'
    case 'blog': return 'B'
    default: return '?'
  }
}

const getPlatformLabel = (p) => {
  switch (p) {
    case 'facebook': return 'Facebook Page'
    case 'gbp': return 'Google Business Profile'
    case 'blog': return 'Your website'
    default: return p
  }
}

const getPlatformTag = (p) => {
  switch (p) {
    case 'facebook': return 'FB'
    case 'gbp': return 'GBP'
    case 'blog': return 'Blog'
    default: return p
  }
}

const getPlatformTagClass = (p) => {
  switch (p) {
    case 'facebook': return 'tag-fb'
    case 'gbp': return 'tag-gbp'
    case 'blog': return 'tag-blog'
    default: return 'tag-fb'
  }
}

const toggleEdit = async (content) => {
  if (editingContent.value === content.id) {
    // Save
    try {
      await api.editContent(job.value.id, content.id, { body: editBody.value })
      content.body = editBody.value
      editingContent.value = null
    } catch (err) {
      alert('Save failed: ' + err.message)
    }
  } else {
    editingContent.value = content.id
    editBody.value = content.body
  }
}

const regenerate = async (content) => {
  regenerating.value = true
  try {
    await api.generateContent(job.value.id)
    await loadJob()
  } catch (err) {
    alert('Regenerate failed: ' + err.message)
  } finally {
    regenerating.value = false
  }
}

const publishSingle = async (content) => {
  publishing.value = true
  try {
    await api.publishContent(job.value.id, [content.platform])
    content.published = true
  } catch (err) {
    alert('Publish failed: ' + err.message)
  } finally {
    publishing.value = false
  }
}

const publishAll = async () => {
  publishing.value = true
  try {
    await api.publishContent(job.value.id)
    await loadJob()
    navigateTo('/')
  } catch (err) {
    alert('Publish failed: ' + err.message)
  } finally {
    publishing.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / 86400000)
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  return `${diffDays} days ago`
}
</script>
