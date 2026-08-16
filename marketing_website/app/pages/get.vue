<script setup lang="ts">
import {
  offer,
  offerIncludes,
  priceIncludesShort,
} from '~/data/offer'
import { isValidEmail, persistCheckout, stripeCheckoutUrl } from '~/utils/checkout'

definePageMeta({
  layout: 'checkout',
})

const config = useRuntimeConfig()
const route = useRoute()
const stripeLink = (config.public.stripePaymentLink as string).trim()
const stripeReady = computed(() => Boolean(stripeLink))
const canceled = computed(() => route.query.canceled === '1')

const email = ref('')
const name = ref('')
const emailError = ref('')

useSeoMeta({
  title: 'Get JobbPulse',
  description: `Get ${offer.productName} for ${offer.priceLabel} ${offer.pricePeriod}. Pay with card via Stripe. Covered by the 90-Day Work Guarantee and 48 Hour Publishing Promise.`,
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Product',
        name: offer.productName,
        description:
          'JobbPulse turns finished jobs into social posts, website projects, and follow-up with new leads.',
        brand: { '@type': 'Brand', name: 'JobbPulse' },
        offers: {
          '@type': 'Offer',
          price: String(offer.price),
          priceCurrency: offer.priceCurrency,
          availability: 'https://schema.org/InStock',
          url: 'https://jobbpulse.com/get',
        },
      }),
    },
  ],
})

function readBuyer() {
  const nextEmail = email.value.trim()
  const nextName = name.value.trim()
  if (!nextEmail) {
    emailError.value = 'Enter the email where we should send your account setup.'
    return null
  }
  if (!isValidEmail(nextEmail)) {
    emailError.value = 'Enter a valid email address.'
    return null
  }
  emailError.value = ''
  return { email: nextEmail, name: nextName }
}

function onSubmit(event: Event) {
  event.preventDefault()
  const submitter = (event as SubmitEvent).submitter
  const method = submitter instanceof HTMLElement ? submitter.getAttribute('data-pay') : null
  const buyer = readBuyer()
  if (!buyer) return

  if (method === 'stripe' && stripeLink) {
    persistCheckout(buyer, 'stripe', offer.sku, offer.priceAmount)
    window.location.href = stripeCheckoutUrl(stripeLink, buyer)
  }
}
</script>

<template>
  <section class="buy">
    <div class="container buy-wrap">
      <div class="buy-intro">
        <h1>Finish the job. <span>Show your work <span class="buy-underline">everywhere.</span></span></h1>
        <div class="buy-leads">
          <p>Take the pictures. Talk for about 30 seconds.</p>
          <p>90-Day Work Guarantee · 48 Hour Publishing Promise</p>
        </div>
      </div>

      <div class="buy-grid">
        <aside class="buy-card">
          <div class="buy-highlight">
            <p class="buy-highlight-label">{{ offer.highlightLabel }}</p>
            <p class="buy-highlight-stat">{{ offer.highlightStat }}</p>
            <p class="buy-highlight-body">{{ offer.highlightBody }}</p>
          </div>
          <div class="buy-card-body">
            <div class="buy-plan">
              <div>
                <p class="buy-plan-label">{{ offer.planLabel }}</p>
                <p class="buy-plan-name">{{ offer.productName }}</p>
              </div>
              <div class="buy-price">
                <p class="buy-price-amount">{{ offer.priceLabel }}</p>
                <p class="buy-price-period">{{ offer.pricePeriod }}</p>
              </div>
            </div>
            <ul class="buy-checks">
              <li v-for="item in priceIncludesShort" :key="item">
                <span aria-hidden="true">✓</span>
                {{ item }}
              </li>
            </ul>
            <div class="buy-guarantee">
              <span class="buy-guarantee-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                  <path d="M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" stroke-linejoin="round" />
                </svg>
              </span>
              <div>
                <p class="buy-guarantee-title">{{ offer.guaranteeTitle }}</p>
                <p>{{ offer.guaranteeBody }}</p>
                <p class="buy-guarantee-refund">
                  <strong>{{ offer.guaranteeRefund }}</strong>
                </p>
              </div>
            </div>
            <div class="buy-guarantee">
              <span class="buy-guarantee-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                  <circle cx="12" cy="12" r="8.25" />
                  <path d="M12 7.5v5l3 1.75" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </span>
              <div>
                <p class="buy-guarantee-title">{{ offer.promiseTitle }}</p>
                <p>{{ offer.promiseBody }}</p>
                <p class="buy-guarantee-refund">
                  <strong>{{ offer.promiseMiss }}</strong>
                </p>
              </div>
            </div>
          </div>
        </aside>

        <div id="checkout" class="buy-card buy-checkout">
          <h2>Complete your purchase</h2>
          <p class="muted">
            We’ll use your email to send account setup instructions after payment.
          </p>

          <p v-if="canceled" class="buy-notice" role="status">
            Checkout was canceled. No charge was made — pick a payment method when you’re ready.
          </p>

          <form class="buy-form" novalidate @submit="onSubmit">
            <div class="buy-field">
              <label for="buyer-email">
                Email <span class="req">*</span>
              </label>
              <input
                id="buyer-email"
                v-model="email"
                name="email"
                type="email"
                required
                autocomplete="email"
                inputmode="email"
                placeholder="you@company.com"
                :aria-invalid="emailError ? 'true' : undefined"
                @input="emailError = ''"
              >
              <p v-if="emailError" id="email-error" class="buy-error" role="alert">{{ emailError }}</p>
              <p class="buy-hint">Account setup and receipt go here. No spam, ever.</p>
            </div>

            <div class="buy-field">
              <label for="buyer-name">
                Name <span class="opt">(optional)</span>
              </label>
              <input
                id="buyer-name"
                v-model="name"
                name="name"
                type="text"
                autocomplete="name"
                placeholder="Your name"
              >
            </div>

            <div class="buy-total">
              <div>
                <p>Total due today</p>
                <p class="buy-hint">Billed monthly · No annual lock-in</p>
              </div>
              <p class="buy-total-amount">{{ offer.priceLabel }}</p>
            </div>

            <fieldset class="buy-pay">
              <legend>Payment method</legend>

              <button
                type="submit"
                data-pay="stripe"
                class="pay-method"
                :disabled="!stripeReady"
                :aria-describedby="stripeReady ? undefined : 'stripe-unavailable'"
              >
                <span class="pay-icon pay-icon-stripe" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.591-7.305z" />
                  </svg>
                </span>
                <span class="pay-copy">
                  <span class="pay-title">Pay with card</span>
                  <span class="pay-sub">Secure checkout powered by Stripe</span>
                </span>
                <span class="pay-go" aria-hidden="true">→</span>
              </button>
              <p v-if="!stripeReady" id="stripe-unavailable" class="buy-hint">
                Stripe is not connected yet. Set
                <code>NUXT_PUBLIC_STRIPE_PAYMENT_LINK</code>
                before launch.
              </p>
            </fieldset>

            <p class="buy-legal">
              By completing purchase you agree to the
              <NuxtLink to="/terms">Terms</NuxtLink>,
              <NuxtLink to="/privacy">Privacy Policy</NuxtLink>,
              and
              <NuxtLink to="/refund">Guarantees</NuxtLink>.
              Payments are processed by Stripe.
              <span>We never store your full card number.</span>
            </p>
          </form>

          <div class="buy-included">
            <p class="buy-plan-label">What’s included</p>
            <ul>
              <li v-for="item in offerIncludes" :key="item">
                <span aria-hidden="true">✓</span>
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
