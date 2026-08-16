<script setup lang="ts">
import { offer } from '~/data/offer'

const year = new Date().getFullYear()
</script>

<template>
  <div class="site checkout-site">
    <div class="checkout-bar">
      <div class="container checkout-bar-inner">
        <NuxtLink class="checkout-back" to="/">
          <span aria-hidden="true">←</span>
          Back to JobbPulse
        </NuxtLink>
        <p class="checkout-secure">
          Secure checkout · {{ offer.priceLabel }} {{ offer.pricePeriod }}
        </p>
      </div>
    </div>
    <main class="site-main">
      <slot />
    </main>
    <footer class="checkout-footer">
      <div class="container checkout-footer-inner">
        <p>© {{ year }} JobbPulse. All rights reserved.</p>
        <nav aria-label="Legal">
          <NuxtLink to="/privacy">Privacy</NuxtLink>
          <NuxtLink to="/terms">Terms</NuxtLink>
          <NuxtLink to="/refund">Refund</NuxtLink>
        </nav>
      </div>
    </footer>
  </div>
</template>
