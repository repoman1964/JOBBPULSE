import { describe, expect, it } from 'vitest'
import { resolveEngineApiBase } from '../app/services/api/httpClient'

describe('resolveEngineApiBase', () => {
  it('sends loopback API calls same-origin so the Nuxt proxy can forward them', () => {
    expect(resolveEngineApiBase('http://localhost:8000', 'http://localhost:3000')).toBe(
      'http://localhost:3000/api/v1',
    )
    expect(resolveEngineApiBase('http://127.0.0.1:8000', 'http://10.0.0.180:3000')).toBe(
      'http://10.0.0.180:3000/api/v1',
    )
  })

  it('keeps a remote engine host unchanged', () => {
    expect(
      resolveEngineApiBase('https://jobbpulse-api.onrender.com', 'https://app.jobbpulse.com'),
    ).toBe('https://jobbpulse-api.onrender.com/api/v1')
  })
})
