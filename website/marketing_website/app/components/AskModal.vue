<script setup lang="ts">
import { mailtoInquiry, validateInquiry } from '~/utils/inquire'

const config = useRuntimeConfig()
const buyUrl = config.public.buyUrl as string
const contactEmail = config.public.contactEmail as string
const { open, hide } = useAskModal()

const name = ref('')
const email = ref('')
const company = ref('')
const message = ref('')
const website = ref('')
const fieldError = ref('')
const fieldName = ref('')
const submitting = ref(false)
const sent = ref(false)
const fallbackHref = ref('')
const dialog = ref<HTMLElement | null>(null)
const firstField = ref<HTMLInputElement | null>(null)
const closeButton = ref<HTMLButtonElement | null>(null)

watch(open, (isOpen) => {
  if (typeof document === 'undefined') return
  document.body.style.overflow = isOpen ? 'hidden' : ''
  if (isOpen) {
    sent.value = false
    fallbackHref.value = ''
    fieldError.value = ''
    fieldName.value = ''
    nextTick(() => firstField.value?.focus())
  }
})

onBeforeUnmount(() => {
  if (typeof document !== 'undefined') document.body.style.overflow = ''
})

function close() {
  if (submitting.value) return
  hide()
}

function onKeydown(event: KeyboardEvent) {
  if (!open.value) return
  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    return
  }
  if (event.key !== 'Tab' || !dialog.value) return
  const focusable = dialog.value.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), textarea, input:not([type="hidden"])',
  )
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

function goBuy() {
  hide()
  navigateTo(buyUrl)
}

async function onSubmit(event: Event) {
  event.preventDefault()
  const payload = {
    name: name.value,
    email: email.value,
    company: company.value,
    message: message.value,
    website: website.value,
  }
  const parsed = validateInquiry(payload)
  if (!parsed.ok) {
    fieldError.value = parsed.error
    fieldName.value = parsed.field
    return
  }

  fieldError.value = ''
  fieldName.value = ''
  submitting.value = true

  try {
    await $fetch('/api/inquire', { method: 'POST', body: payload })
    sent.value = true
    name.value = ''
    email.value = ''
    company.value = ''
    message.value = ''
    nextTick(() => closeButton.value?.focus())
  } catch {
    fallbackHref.value = mailtoInquiry(contactEmail, {
      name: payload.name.trim(),
      email: payload.email.trim(),
      company: payload.company.trim(),
      message: payload.message.trim(),
    })
    nextTick(() => closeButton.value?.focus())
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="ask-overlay"
      @keydown="onKeydown"
    >
      <button class="ask-backdrop" type="button" tabindex="-1" aria-label="Close" @click="close" />
      <div
        ref="dialog"
        class="ask-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="ask-title"
        aria-describedby="ask-copy"
      >
        <button ref="closeButton" type="button" class="ask-close" @click="close">
          <span class="sr-only">Close</span>
          <span aria-hidden="true">×</span>
        </button>

        <div v-if="sent || fallbackHref" class="ask-success">
          <template v-if="sent">
            <p class="eyebrow">Got it</p>
            <h2 id="ask-title">We’ll write you back.</h2>
            <p id="ask-copy" class="muted">
              Thanks for the question. Check your email. That’s where the conversation continues.
            </p>
            <div class="ask-actions">
              <button type="button" class="btn btn-buy" @click="close">Close</button>
            </div>
          </template>
          <template v-else>
            <p class="eyebrow">One more step</p>
            <h2 id="ask-title">Send it from your email.</h2>
            <p id="ask-copy" class="muted">
              We couldn’t deliver that automatically. Open a draft to {{ contactEmail }} and send
              the question from there.
            </p>
            <div class="ask-actions">
              <a class="btn btn-buy" :href="fallbackHref">Open email draft</a>
              <button type="button" class="btn btn-secondary" @click="close">Close</button>
            </div>
          </template>
        </div>

        <form v-else class="ask-form" novalidate @submit="onSubmit">
          <p class="eyebrow">Talk with us</p>
          <h2 id="ask-title">Ask us about JobbPulse</h2>
          <p id="ask-copy" class="muted">
            Tell us what you want to know. We’ll reply by email. No sales call unless you ask for one.
          </p>

          <div class="buy-field">
            <label for="ask-name">Name <span class="req">*</span></label>
            <input
              id="ask-name"
              ref="firstField"
              v-model="name"
              type="text"
              name="name"
              autocomplete="name"
              maxlength="120"
              :aria-invalid="fieldName === 'name'"
              :aria-describedby="fieldName === 'name' ? 'ask-error' : undefined"
            >
          </div>

          <div class="buy-field">
            <label for="ask-email">Email <span class="req">*</span></label>
            <input
              id="ask-email"
              v-model="email"
              type="email"
              name="email"
              autocomplete="email"
              inputmode="email"
              maxlength="160"
              :aria-invalid="fieldName === 'email'"
              :aria-describedby="fieldName === 'email' ? 'ask-error' : undefined"
            >
          </div>

          <div class="buy-field">
            <label for="ask-company">Company <span class="opt">(optional)</span></label>
            <input
              id="ask-company"
              v-model="company"
              type="text"
              name="company"
              autocomplete="organization"
              maxlength="120"
              :aria-invalid="fieldName === 'company'"
              :aria-describedby="fieldName === 'company' ? 'ask-error' : undefined"
            >
          </div>

          <div class="buy-field">
            <label for="ask-message">Your question <span class="req">*</span></label>
            <textarea
              id="ask-message"
              v-model="message"
              name="message"
              rows="5"
              maxlength="4000"
              :aria-invalid="fieldName === 'message'"
              :aria-describedby="fieldName === 'message' ? 'ask-error' : undefined"
              placeholder="Pricing, setup, whether this fits your trade. Ask anything."
            />
          </div>

          <div class="ask-honeypot" aria-hidden="true">
            <label for="ask-website">Website</label>
            <input id="ask-website" v-model="website" type="text" name="website" tabindex="-1" autocomplete="off">
          </div>

          <p v-if="fieldError" id="ask-error" class="buy-error" role="alert">{{ fieldError }}</p>

          <div class="ask-actions">
            <button class="btn btn-buy" type="submit" :disabled="submitting">
              {{ submitting ? 'Sending…' : 'Send question' }}
            </button>
            <button class="btn btn-secondary" type="button" @click="goBuy">
              I’m ready to buy
            </button>
          </div>
          <p class="buy-hint">
            Ready to start now? Use “I’m ready to buy.” Otherwise send the question and we’ll take it from there.
          </p>
        </form>
      </div>
    </div>
  </Teleport>
</template>
