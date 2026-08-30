import { afterEach, describe, expect, it, vi } from 'vitest'
import { normalizeUploadContentType, putToPresignedUrl } from '../app/utils/presignedUpload'

describe('normalizeUploadContentType', () => {
  it('strips MediaRecorder codec parameters so they match signed S3 headers', () => {
    expect(normalizeUploadContentType('audio/webm;codecs=opus')).toBe('audio/webm')
    expect(normalizeUploadContentType('audio/mp4;codecs=mp4a.40.2')).toBe('audio/mp4')
    expect(normalizeUploadContentType('audio/webm')).toBe('audio/webm')
    expect(normalizeUploadContentType('')).toBe('')
  })
})

describe('putToPresignedUrl', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('does not fetch mock:// upload URLs', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    await putToPresignedUrl('mock://upload/media-1', new Blob(['img']), 'image/jpeg')

    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('PUTs the file bytes with the signed Content-Type and no credentials', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 })
    vi.stubGlobal('fetch', fetchMock)

    const body = new Blob(['jpeg-bytes'], { type: 'image/jpeg' })
    const url = 'https://example.r2.cloudflarestorage.com/jobbpulse/photos/abc?X-Amz-Signature=sig'

    await putToPresignedUrl(url, body, 'image/jpeg')

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [calledUrl, init] = fetchMock.mock.calls[0]
    expect(calledUrl).toBe(url)
    expect(init.method).toBe('PUT')
    expect(init.body).toBe(body)
    expect(init.credentials).not.toBe('include')
    expect(init.headers['Content-Type']).toBe('image/jpeg')
    expect(init.headers.Authorization).toBeUndefined()
  })

  it('strips codec parameters from the signed Content-Type header', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200 })
    vi.stubGlobal('fetch', fetchMock)

    await putToPresignedUrl(
      'http://127.0.0.1:9000/jobpulse/voice.webm?X-Amz-Signature=sig',
      new Blob(['opus']),
      'audio/webm;codecs=opus',
    )

    expect(fetchMock.mock.calls[0][1].headers['Content-Type']).toBe('audio/webm')
  })

  it('throws when R2 rejects the upload', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 403, statusText: 'Forbidden' }),
    )

    await expect(
      putToPresignedUrl(
        'https://example.r2.cloudflarestorage.com/jobbpulse/photos/abc',
        new Blob(['x']),
        'image/jpeg',
      ),
    ).rejects.toThrow(/could not upload/i)
  })
})
