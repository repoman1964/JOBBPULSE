export function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}

export function stripeCheckoutUrl(
  link: string,
  buyer: { email: string; name: string },
) {
  const url = new URL(link)
  url.searchParams.set('prefilled_email', buyer.email)
  if (buyer.name) url.searchParams.set('prefilled_name', buyer.name)
  url.searchParams.set('client_reference_id', buyer.email)
  return url.toString()
}

export function persistCheckout(
  buyer: { email: string; name: string },
  provider: string,
  product: string,
  amount: string,
) {
  try {
    sessionStorage.setItem(
      'jobbpulse_checkout',
      JSON.stringify({
        email: buyer.email,
        name: buyer.name,
        provider,
        product,
        amount,
        startedAt: new Date().toISOString(),
      }),
    )
  } catch {
    /* private mode */
  }
}
