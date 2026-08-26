<script setup lang="ts">
import type { SocialConnection } from '~/types/domain'
import {
  CONNECTABLE_PLATFORMS,
  PLATFORM_FIELD,
  PLATFORM_LABEL,
  formatSocialAccountName,
  type ConnectablePlatform,
} from '~/utils/socialAccounts'

const api = useApi()
const route = useRoute()

const rows = ref<SocialConnection[]>([])
const drafts = reactive<Record<ConnectablePlatform, string>>({
  facebook: '',
  instagram: '',
  google_business: '',
})
const loading = ref(true)
const saving = ref<ConnectablePlatform | null>(null)
const error = ref('')
const notice = ref('')

const statusLabel: Record<string, string> = {
  connected: 'Connected',
  not_connected: 'Not connected',
  reconnect_required: 'Reconnect required',
  connection_pending: 'Connection pending',
  provider_unavailable: 'Unavailable',
}

function isConnectable(platform: string): platform is ConnectablePlatform {
  return (CONNECTABLE_PLATFORMS as readonly string[]).includes(platform)
}

function rowFor(platform: ConnectablePlatform): SocialConnection {
  return (
    rows.value.find((row) => row.platform === platform) || {
      platform,
      status: 'not_connected',
      accountName: null,
      reason: null,
    }
  )
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const list = await api.listSocialConnections()
    rows.value = list.filter((row) => isConnectable(row.platform))
    for (const platform of CONNECTABLE_PLATFORMS) {
      drafts[platform] = rowFor(platform).accountName || ''
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load social accounts.'
  } finally {
    loading.value = false
  }
}

function replaceRow(updated: SocialConnection) {
  const idx = rows.value.findIndex((row) => row.platform === updated.platform)
  if (idx >= 0) rows.value[idx] = updated
  else rows.value.push(updated)
  if (isConnectable(updated.platform)) {
    drafts[updated.platform] = updated.accountName || ''
  }
}

async function connect(platform: ConnectablePlatform) {
  error.value = ''
  notice.value = ''
  const accountName = formatSocialAccountName(platform, drafts[platform])
  if (!accountName) {
    error.value = `Enter the ${PLATFORM_FIELD[platform].label.toLowerCase()}.`
    return
  }
  saving.value = platform
  try {
    const updated = await api.connectSocialAccount(platform, accountName)
    replaceRow(updated)
    notice.value = `${PLATFORM_LABEL[platform]} connected.`
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not connect that account.'
  } finally {
    saving.value = null
  }
}

async function disconnect(platform: ConnectablePlatform) {
  error.value = ''
  notice.value = ''
  saving.value = platform
  try {
    const updated = await api.disconnectSocialAccount(platform)
    replaceRow(updated)
    notice.value = `${PLATFORM_LABEL[platform]} disconnected.`
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not disconnect that account.'
  } finally {
    saving.value = null
  }
}

onMounted(async () => {
  await load()
  const focus = route.query.platform
  if (typeof focus === 'string' && isConnectable(focus)) {
    document.getElementById(`account-${focus}`)?.focus()
  }
})
</script>

<template>
  <div>
    <JpHeader show-back back-to="/settings" />
    <main class="app-main">
      <h1 class="page-title">Social accounts</h1>
      <p class="muted" style="margin-top: 0">
        Pick a platform and enter the account JobbPulse should post to. We never ask for your
        Facebook, Instagram, or Google password.
      </p>
      <div v-if="notice" class="banner">{{ notice }}</div>
      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <p v-if="loading" class="muted">Loading…</p>

      <form
        v-for="platform in CONNECTABLE_PLATFORMS"
        v-else
        :key="platform"
        class="card stack"
        style="margin-top: 12px"
        @submit.prevent="connect(platform)"
      >
        <div class="social-head">
          <strong>{{ PLATFORM_LABEL[platform] }}</strong>
          <span class="conn" :class="{ on: rowFor(platform).status === 'connected' }">
            {{ statusLabel[rowFor(platform).status] || rowFor(platform).status }}
          </span>
        </div>
        <div class="field" style="margin-bottom: 0">
          <label :for="`account-${platform}`">{{ PLATFORM_FIELD[platform].label }}</label>
          <input
            :id="`account-${platform}`"
            v-model="drafts[platform]"
            type="text"
            :placeholder="PLATFORM_FIELD[platform].placeholder"
            autocomplete="off"
            :disabled="saving === platform"
          />
          <p class="muted" style="margin: 0; font-size: 0.8rem">
            {{ PLATFORM_FIELD[platform].hint }}
          </p>
        </div>
        <div class="actions">
          <button
            class="btn btn-primary"
            type="submit"
            :disabled="saving === platform"
          >
            {{
              saving === platform
                ? 'Saving…'
                : rowFor(platform).status === 'connected'
                  ? 'Update'
                  : 'Connect'
            }}
          </button>
          <button
            v-if="rowFor(platform).status === 'connected'"
            class="btn btn-secondary"
            type="button"
            :disabled="saving === platform"
            @click="disconnect(platform)"
          >
            Disconnect
          </button>
        </div>
      </form>
    </main>
  </div>
</template>

<style scoped>
.social-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.conn {
  color: var(--jp-text-dim);
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.conn.on {
  color: var(--jp-accent);
}

.actions {
  display: flex;
  gap: 10px;
}

.actions .btn {
  flex: 1;
}
</style>
