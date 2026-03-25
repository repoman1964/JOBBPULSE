/**
 * JobPulse — GPS location composable.
 * Uses browser Geolocation API + OpenStreetMap Nominatim for reverse geocoding.
 * (In Capacitor builds, this can be swapped with @capacitor/geolocation)
 */

interface LocationData {
  latitude: number
  longitude: number
  address: string
  city: string
  state: string
}

export const useLocation = () => {
  const location = ref<LocationData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const getCurrentLocation = async (): Promise<LocationData | null> => {
    loading.value = true
    error.value = null

    try {
      // Get GPS coordinates
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        if (!navigator.geolocation) {
          reject(new Error('Geolocation not supported'))
          return
        }
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        })
      })

      const { latitude, longitude } = position.coords

      // Reverse geocode using OSM Nominatim (free, no API key)
      let address = ''
      let city = ''
      let state = ''

      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18`,
          { headers: { 'User-Agent': 'JobPulse/1.0' } }
        )
        const data = await res.json()

        if (data.address) {
          const a = data.address
          const road = a.road || a.street || ''
          const houseNumber = a.house_number || ''
          address = [houseNumber, road].filter(Boolean).join(' ')
          city = a.city || a.town || a.village || a.municipality || ''
          state = a.state || ''
        }
      } catch {
        // Reverse geocoding failed — use coordinates only
        address = `${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° W`
      }

      location.value = { latitude, longitude, address, city, state }
      return location.value
    } catch (err: any) {
      error.value = err.message || 'Location unavailable'
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    location,
    loading,
    error,
    getCurrentLocation,
  }
}
