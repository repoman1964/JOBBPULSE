<script setup lang="ts">
const api = useApi()
const { session } = useAuthSession()

const form = reactive({
  name: '',
  contactName: '',
  phone: '',
  email: '',
  website: '',
  serviceArea: '',
})
const original = ref('')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

const dirty = computed(() => JSON.stringify(form) !== original.value)

async function load() {
  loading.value = true
  try {
    const company = await api.getCompany()
    Object.assign(form, {
      name: company.name,
      contactName: company.contactName,
      phone: company.phone,
      email: company.email,
      website: company.website,
      serviceArea: company.serviceArea,
    })
    original.value = JSON.stringify(form)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load profile.'
  } finally {
    loading.value = false
  }
}

async function save() {
  error.value = ''
  saved.value = false
  if (!form.name.trim() || !form.contactName.trim()) {
    error.value = 'Business name and contact name are required.'
    return
  }
  saving.value = true
  try {
    const company = await api.updateCompany({ ...form })
    if (session.value) session.value.company = company
    original.value = JSON.stringify(form)
    saved.value = true
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not save changes.'
  } finally {
    saving.value = false
  }
}

onBeforeRouteLeave(() => {
  if (dirty.value && !confirm('You have unsaved changes. Leave without saving?')) {
    return false
  }
})

onMounted(load)
</script>

<template>
  <div>
    <JpHeader show-back back-to="/settings" />
    <main class="app-main">
      <h1 class="page-title">Business Profile</h1>
      <p v-if="loading" class="muted">Loading…</p>
      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <div v-if="saved" class="banner">Changes saved.</div>

      <form v-if="!loading" class="card stack" style="margin-top: 12px" @submit.prevent="save">
        <div class="field">
          <label for="name">Business name</label>
          <input id="name" v-model="form.name" type="text" required />
        </div>
        <div class="field">
          <label for="contact">Contact name</label>
          <input id="contact" v-model="form.contactName" type="text" required />
        </div>
        <div class="field">
          <label for="phone">Phone</label>
          <input id="phone" v-model="form.phone" type="tel" />
        </div>
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" />
        </div>
        <div class="field">
          <label for="website">Website</label>
          <input id="website" v-model="form.website" type="url" />
        </div>
        <div class="field">
          <label for="area">Service area</label>
          <input id="area" v-model="form.serviceArea" type="text" />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="saving || !dirty">
          {{ saving ? 'Saving…' : 'Save Changes' }}
        </button>
      </form>
    </main>
  </div>
</template>
