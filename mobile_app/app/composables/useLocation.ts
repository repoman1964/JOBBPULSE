/**
 * Quiet coarse geolocation for jobs.
 * Never captures or asks for street address — city/state/area only.
 */

export type CoarseLocation = {
  city?: string
  state?: string
  location_display?: string
}

/**
 * Reverse-geocode via OpenStreetMap Nominatim (dev-friendly, no API key).
 * Returns coarse city/state only — never a street line for storage.
 */
async function reverseGeocode(lat: number, lon: number): Promise<CoarseLocation> {
  try {
    const url =
      `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}` +
      `&zoom=10&addressdetails=1`
    const res = await fetch(url, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) return {}
    const data = (await res.json()) as {
      address?: Record<string, string>
      name?: string
    }
    const a = data.address || {}
    const city =
      a.city || a.town || a.village || a.municipality || a.county || undefined
    const state = a.state || a.region || undefined
    const area = a.suburb || a.neighbourhood || a.city_district
    let location_display: string | undefined
    if (area && city) location_display = `${area}, ${city}`
    else if (city && state) location_display = `${city}, ${state}`
    else if (city) location_display = city
    else if (state) location_display = state
    return { city, state, location_display }
  } catch {
    return {}
  }
}

export const useLocation = () => {
  const coarse = useState<CoarseLocation | null>('geo.coarse', () => null)
  const loading = useState<boolean>('geo.loading', () => false)
  const error = useState<string | null>('geo.error', () => null)

  async function captureCoarseLocation(): Promise<CoarseLocation | null> {
    if (!import.meta.client || !navigator.geolocation) {
      error.value = 'Geolocation unavailable'
      return null
    }
    loading.value = true
    error.value = null
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: false,
          timeout: 12000,
          maximumAge: 5 * 60 * 1000,
        })
      })
      const { latitude, longitude } = position.coords
      const result = await reverseGeocode(latitude, longitude)
      coarse.value = result
      return result
    } catch (e: any) {
      error.value = e?.message || 'Location permission denied'
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    coarse,
    loading,
    error,
    captureCoarseLocation,
  }
}
